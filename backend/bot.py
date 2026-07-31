"""
JAC MOTORS ANGREN — Telegram Bot (Webhook version for Render)
===============================================================
Использует webhook для приёма callback_query.
Flask и Telegram работают в ОДНОМ процессе. Без polling, без threading.
"""

import json, time, random, threading, signal, sys, os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================ CONFIG ================
BOT_TOKEN = "8854046020:AAHtK4ZTZLDt5_TowHAUIXFVBmcuYNxZdE8"
MANAGERS_FILE = "managers.json"
AUTO_REJECT = 60
RATE_MAX = 2
RATE_WINDOW = 20 * 60

# ================ STATE ================
pending = {}     # lead_id -> {...}
rate_ips = {}    # ip -> [timestamps]
manager_ids = []

def load_mgr():
    global manager_ids
    try:
        with open(MANAGERS_FILE) as f:
            manager_ids = json.load(f).get('manager_ids', [])
    except:
        save_mgr()

def save_mgr():
    with open(MANAGERS_FILE, 'w') as f:
        json.dump({'manager_ids': manager_ids}, f)

load_mgr()

# ================ FLASK ================
app = Flask(__name__)
CORS(app)

bot = Bot(token=BOT_TOKEN)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# ================ HELPERS ================
def keyboard(lead_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{lead_id}"),
        InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{lead_id}")
    ]])

def msg_text(lead):
    return (
        f"🆕 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"🚗 <b>Модель:</b> {lead['model']}\n"
        f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n"
        f"⏰ <b>Время:</b> {lead['time']}\n\n"
        f"<i>Нажмите ✅ чтобы увидеть контакты\n"
        f"У вас есть 1 минута</i>"
    )

def accepted_msg(lead):
    return (
        f"✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
        f"👤 <b>Имя:</b> {lead['name']}\n"
        f"📞 <b>Телефон:</b> <code>{lead['phone']}</code>\n"
        f"🚗 <b>Модель:</b> {lead['model']}\n"
        f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n\n"
        f"<i>Свяжитесь с клиентом!</i>"
    )

# ================ ROUTING ================
def send_to_random(lead_id):
    lead = pending.get(lead_id)
    if not lead or not manager_ids:
        return
    available = [m for m in manager_ids if m not in lead.get('rejected_by', [])]
    if not available:
        pending.pop(lead_id, None)
        print(f"All managers rejected lead {lead_id}")
        return

    mgr = random.choice(available)
    lead['current_manager'] = mgr
    lead['sent_at'] = time.time()
    try:
        msg = bot.send_message(
            chat_id=mgr,
            text=msg_text(lead),
            reply_markup=keyboard(lead_id),
            parse_mode='HTML'
        )
        lead['message_id'] = msg.message_id
        lead['chat_id'] = mgr
        print(f"Sent lead {lead_id} to manager {mgr}")
    except Exception as e:
        print(f"Error sending to {mgr}: {e}")
        lead.setdefault('rejected_by', []).append(mgr)
        send_to_random(lead_id)

def auto_reject(lead_id):
    time.sleep(AUTO_REJECT)
    lead = pending.get(lead_id)
    if not lead or lead.get('status') != 'pending':
        return
    mid = lead.get('current_manager')
    if mid:
        try:
            bot.edit_message_text(
                chat_id=mid,
                message_id=lead['message_id'],
                text=msg_text(lead) + "\n\n⏰ <b>Время истекло — передано другому</b>",
                parse_mode='HTML'
            )
        except:
            pass
        lead.setdefault('rejected_by', []).append(mid)
    send_to_random(lead_id)

# ================ TELEGRAM HANDLERS ================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in manager_ids:
        manager_ids.append(uid)
        save_mgr()
    await update.message.reply_text(
        f"👋 Вы зарегистрированы как менеджер JAC MOTORS ANGREN!\n"
        f"ID: <code>{uid}</code>\n"
        f"/managers — список\n/remove — удалить себя",
        parse_mode='HTML'
    )

async def managers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if manager_ids:
        await update.message.reply_text("📋 " + "\n".join(f"• <code>{m}</code>" for m in manager_ids), parse_mode='HTML')
    else:
        await update.message.reply_text("Нет менеджеров. Отправьте /start")

async def remove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in manager_ids:
        manager_ids.remove(uid)
        save_mgr()
        await update.message.reply_text("Удалены из менеджеров.")
    else:
        await update.message.reply_text("Вас нет в списке.")

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cb = update.callback_query
    data = cb.data
    mid = update.effective_user.id
    parts = data.split('_', 1)
    if len(parts) < 2:
        await cb.answer()
        return
    action, lead_id = parts[0], parts[1]
    lead = pending.get(lead_id)

    if not lead:
        await cb.answer("Заявка уже неактивна")
        return

    if action == 'accept':
        lead['status'] = 'accepted'
        await cb.edit_message_text(accepted_msg(lead), parse_mode='HTML')
        await cb.answer("✅ Принято!")
        pending.pop(lead_id, None)

    elif action == 'reject':
        lead.setdefault('rejected_by', []).append(mid)
        try:
            await cb.edit_message_text(
                msg_text(lead) + "\n\n❌ <b>Вы отказались — другой менеджер</b>",
                parse_mode='HTML'
            )
        except:
            pass
        await cb.answer("Передано другому")
        send_to_random(lead_id)
        # Restart timer for new manager
        threading.Thread(target=auto_reject, args=(lead_id,), daemon=True).start()

telegram_app.add_handler(CommandHandler('start', start))
telegram_app.add_handler(CommandHandler('managers', managers_cmd))
telegram_app.add_handler(CommandHandler('remove', remove_cmd))
telegram_app.add_handler(CallbackQueryHandler(callback))

# ================ FLASK ROUTES ================
@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True) if request.is_json else {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    model = data.get('model', '') or 'Не указана'
    comment = data.get('comment', '').strip()

    if not name or not phone:
        return jsonify({'ok': False, 'error': 'Имя и телефон обязательны'}), 400

    ip = request.remote_addr or '0.0.0.0'
    now = time.time()
    # Rate limit disabled for testing
    # rate_ips.setdefault(ip, [])
    # rate_ips[ip] = [t for t in rate_ips[ip] if now - t < RATE_WINDOW]
    # if len(rate_ips[ip]) >= RATE_MAX:
    #     return jsonify({'ok': False, 'error': 'Лимит: 2 заявки за 20 минут'}), 429
    # rate_ips[ip].append(now)

    lid = f"lead_{int(now)}_{random.randint(1000,9999)}"
    lead = {
        'id': lid, 'name': name, 'phone': phone, 'model': model,
        'comment': comment, 'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'status': 'pending', 'rejected_by': [], 'current_manager': None,
        'message_id': None, 'chat_id': None, 'sent_at': None
    }
    pending[lid] = lead
    send_to_random(lid)
    threading.Thread(target=auto_reject, args=(lid,), daemon=True).start()

    return jsonify({'ok': True, 'message': 'Заявка отправлена!'})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram sends updates here. No polling needed."""
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        telegram_app.process_update(update)
    except Exception as e:
        print(f"Webhook error: {e}")
    return 'ok', 200

@app.route('/health')
def health():
    return jsonify({'ok': True, 'managers': len(manager_ids), 'pending': len(pending)})

@app.route('/')
def index():
    return jsonify({'service': 'JAC MOTORS ANGREN Bot API'})

# ================ MAIN ================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 JAC MOTORS ANGREN — Bot Backend (Webhook)")
    print(f"📋 Managers: {len(manager_ids)}")
    print("=" * 60)
    # Always run Flask on port from env or 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
