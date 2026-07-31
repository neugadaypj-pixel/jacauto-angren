"""
JAC MOTORS ANGREN — Telegram Bot (FIXED)
Uses asyncio.run() for polling, Flask in daemon thread.
"""

import json, time, random, os, asyncio, threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================ CONFIG ================
BOT_TOKEN = "8854046020:AAHtK4ZTZLDt5_TowHAUIXFVBmcuYNxZdE8"
MANAGERS_FILE = "managers.json"
AUTO_REJECT = 60

# ================ STATE ================
pending = {}
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

app = Flask(__name__)
CORS(app)

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
        f"<i>Нажмите ✅ чтобы увидеть контакты\nУ вас есть 1 минута</i>"
    )

def accepted_msg_text(lead):
    return (
        f"✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
        f"👤 <b>Имя:</b> {lead['name']}\n"
        f"📞 <b>Телефон:</b> <code>{lead['phone']}</code>\n"
        f"🚗 <b>Модель:</b> {lead['model']}\n"
        f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n\n"
        f"<i>Свяжитесь с клиентом!</i>"
    )

# ================ BOT ================
bot = Bot(token=BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in manager_ids:
        manager_ids.append(uid)
        save_mgr()
    await update.message.reply_text(f"✅ Вы — менеджер JAC MOTORS ANGREN!\nID: <code>{uid}</code>", parse_mode='HTML')

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cb = update.callback_query
    data = cb.data
    mid = update.effective_user.id
    parts = data.split('_', 1)
    if len(parts) < 2: await cb.answer(); return
    action, lead_id = parts[0], parts[1]
    lead = pending.get(lead_id)
    if not lead: await cb.answer("Неактивно"); return

    if action == 'accept':
        lead['status'] = 'accepted'
        await cb.edit_message_text(accepted_msg_text(lead), parse_mode='HTML')
        await cb.answer("✅ Принято!")
        pending.pop(lead_id, None)
    elif action == 'reject':
        lead.setdefault('rejected_by', []).append(mid)
        try:
            await cb.edit_message_text(msg_text(lead) + "\n\n❌ <b>Отказано — другой менеджер</b>", parse_mode='HTML')
        except: pass
        await cb.answer("Передано")
        send_to_random_sync(lead_id)
        threading.Thread(target=auto_reject, args=(lead_id,), daemon=True).start()

def build_app():
    app_tg = Application.builder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler('start', start))
    app_tg.add_handler(CallbackQueryHandler(callback))
    return app_tg

# ================ ROUTING ================
def send_to_random_sync(lead_id):
    lead = pending.get(lead_id)
    if not lead or not manager_ids: return
    available = [m for m in manager_ids if m not in lead.get('rejected_by', [])]
    if not available: pending.pop(lead_id, None); return
    mgr = random.choice(available)
    lead['current_manager'] = mgr
    try:
        msg = bot.send_message(chat_id=mgr, text=msg_text(lead), reply_markup=keyboard(lead_id), parse_mode='HTML')
        lead['message_id'] = msg.message_id
    except Exception as e:
        print(f"Send error: {e}")
        lead.setdefault('rejected_by', []).append(mgr)
        send_to_random_sync(lead_id)

def auto_reject(lead_id):
    time.sleep(AUTO_REJECT)
    lead = pending.get(lead_id)
    if not lead or lead.get('status') != 'pending': return
    mid = lead.get('current_manager')
    if mid:
        try: bot.edit_message_text(chat_id=mid, message_id=lead['message_id'], text=msg_text(lead) + "\n\n⏰ <b>Время истекло</b>", parse_mode='HTML')
        except: pass
        lead.setdefault('rejected_by', []).append(mid)
    send_to_random_sync(lead_id)

# ================ FLASK ================
@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(force=True) if request.is_json else {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    model = data.get('model', '') or 'Не указана'
    comment = data.get('comment', '').strip()
    if not name or not phone:
        return jsonify({'ok': False, 'error': 'Имя и телефон обязательны'}), 400
    lid = f"lead_{int(time.time())}_{random.randint(1000,9999)}"
    lead = {'id': lid, 'name': name, 'phone': phone, 'model': model, 'comment': comment,
            'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'status': 'pending', 'rejected_by': [], 'current_manager': None, 'message_id': None}
    pending[lid] = lead
    send_to_random_sync(lid)
    threading.Thread(target=auto_reject, args=(lid,), daemon=True).start()
    return jsonify({'ok': True, 'message': 'Заявка отправлена!'})

@app.route('/health')
def health():
    return jsonify({'ok': True, 'managers': len(manager_ids), 'pending': len(pending), 'manager_ids': manager_ids})

@app.route('/')
def index():
    return jsonify({'service': 'JAC MOTORS ANGREN Bot API'})

# ================ MAIN ================
if __name__ == '__main__':
    print(f"🚀 Starting... Managers: {manager_ids}")
    # Run Flask in daemon thread
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    time.sleep(2)
    # Run Telegram polling in main thread (this works on Python 3.14)
    app_tg = build_app()
    print("🤖 Polling started...")
    app_tg.run_polling()
