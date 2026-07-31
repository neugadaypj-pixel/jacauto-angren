"""
JAC MOTORS ANGREN — Telegram Bot FINAL
Polling + Flask. Managers from Google Sheets.
"""

import json, time, random, os, asyncio, threading, urllib.request
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8854046020:AAHtK4ZTZLDt5_TowHAUIXFVBmcuYNxZdE8"
MANAGERS_FILE = "managers.json"
AUTO_REJECT = 60

pending = {}
manager_ids = []

def load_mgr():
    global manager_ids
    try:
        with open(MANAGERS_FILE) as f:
            manager_ids = json.load(f).get('manager_ids', [])
    except: save_mgr()

def save_mgr():
    os.makedirs(os.path.dirname(os.path.abspath(MANAGERS_FILE)) or '.', exist_ok=True)
    with open(MANAGERS_FILE, 'w') as f:
        json.dump({'manager_ids': manager_ids}, f)

def fetch_managers_from_sheets():
    """Download manager IDs from Google Sheets CSV.
    Format: column A = manager_id, column B = manager_name (optional)"""
    global manager_ids
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgam8czC85ktRCxfKNpyL_eV2E0rA96xSvYDNrcXD0CNJk-3X7qP0ISNQr0qRmPx5CctG0d6qeHaEN/pub?output=csv"
        with urllib.request.urlopen(url, timeout=10) as resp:
            csv_data = resp.read().decode('utf-8')
        ids = []
        for line in csv_data.strip().split('\n')[1:]:
            parts = line.strip().split(',')
            col_a = parts[0].strip() if parts else ''
            col_b = parts[1].strip() if len(parts) > 1 else ''
            if col_a.isdigit():
                ids.append(int(col_a))
            name = col_b if col_b else f"ID:{col_a}"
        if ids:
            manager_ids = ids
            print(f"📋 Loaded {len(ids)} managers from Google Sheets")
            return True
    except Exception as e:
        print(f"⚠ Sheets fetch failed: {e}")
    return False

fetch_managers_from_sheets()

app = Flask(__name__)
CORS(app)

bot = Bot(token=BOT_TOKEN)

def keyboard(lead_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Принять", callback_data=f"accept_{lead_id}"),
        InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{lead_id}")
    ]])

def msg_text(lead):
    return (f"🆕 <b>НОВАЯ ЗАЯВКА</b>\n\n"
            f"🚗 <b>Модель:</b> {lead['model']}\n"
            f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n"
            f"⏰ <b>Время:</b> {lead['time']}\n\n"
            f"<i>Нажмите ✅ чтобы увидеть контакты\nУ вас есть 1 минута</i>")

def accepted_msg_text(lead):
    return (f"✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
            f"👤 <b>Имя:</b> {lead['name']}\n"
            f"📞 <b>Телефон:</b> <code>{lead['phone']}</code>\n"
            f"🚗 <b>Модель:</b> {lead['model']}\n"
            f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n\n"
            f"<i>Свяжитесь с клиентом!</i>")

# ================ BOT HANDLERS ================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    global manager_ids
    if uid not in manager_ids:
        manager_ids.append(uid)
        save_mgr()
    await update.message.reply_text(f"✅ Менеджер зарегистрирован!\nID: <code>{uid}</code>\n/managers — список\n/remove — удалить", parse_mode='HTML')

async def managers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global manager_ids
    if manager_ids:
        await update.message.reply_text("📋 " + "\n".join(f"• <code>{m}</code>" for m in manager_ids), parse_mode='HTML')
    else:
        await update.message.reply_text("Нет менеджеров.")

async def remove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    global manager_ids
    if uid in manager_ids:
        manager_ids.remove(uid)
        save_mgr()
        await update.message.reply_text("Удалены.")
    else:
        await update.message.reply_text("Вас нет в списке.")

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
        try: await cb.edit_message_text(msg_text(lead) + "\n\n❌ <b>Отказано — другой менеджер</b>", parse_mode='HTML')
        except: pass
        await cb.answer("Передано")
        print(f"REJECT by {mid}. Rejected list: {lead['rejected_by']}. All managers: {manager_ids}")
        # Call routing SYNCHRONOUSLY from callback
        send_to_next(lead_id)
        threading.Thread(target=auto_reject, args=(lead_id,), daemon=True).start()

def build_app():
    app_tg = Application.builder().token(BOT_TOKEN).build()
    app_tg.add_handler(CommandHandler('start', start))
    app_tg.add_handler(CommandHandler('managers', managers_cmd))
    app_tg.add_handler(CommandHandler('remove', remove_cmd))
    app_tg.add_handler(CallbackQueryHandler(callback))
    return app_tg

# ================ ROUTING ================
def send_to_next(lead_id):
    """Send lead to next available manager. Uses global manager_ids."""
    global manager_ids, pending
    lead = pending.get(lead_id)
    if not lead:
        print(f"ROUTE {lead_id}: lead not found")
        return
    print(f"ROUTE {lead_id}: rejected_by={lead.get('rejected_by', [])}, all_managers={manager_ids}")
    available = [m for m in manager_ids if m not in lead.get('rejected_by', [])]
    if not available:
        print(f"ROUTE {lead_id}: no available managers. Dropping lead.")
        pending.pop(lead_id, None)
        return
    mgr = random.choice(available)
    lead['current_manager'] = mgr
    print(f"ROUTE {lead_id}: sending to {mgr}")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        msg = loop.run_until_complete(bot.send_message(chat_id=mgr, text=msg_text(lead), reply_markup=keyboard(lead_id), parse_mode='HTML'))
        loop.close()
        lead['message_id'] = msg.message_id
        print(f"ROUTE {lead_id}: sent OK, msg_id={msg.message_id}")
    except Exception as e:
        print(f"ROUTE {lead_id}: error {e}")
        lead.setdefault('rejected_by', []).append(mgr)
        send_to_next(lead_id)

def auto_reject(lead_id):
    time.sleep(AUTO_REJECT)
    lead = pending.get(lead_id)
    if not lead or lead.get('status') != 'pending': return
    mid = lead.get('current_manager')
    if mid:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.edit_message_text(chat_id=mid, message_id=lead['message_id'], text=msg_text(lead) + "\n\n⏰ <b>Время истекло</b>", parse_mode='HTML'))
            loop.close()
        except: pass
        lead.setdefault('rejected_by', []).append(mid)
    send_to_next(lead_id)

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
    send_to_next(lid)
    threading.Thread(target=auto_reject, args=(lid,), daemon=True).start()
    return jsonify({'ok': True, 'message': 'Заявка отправлена!'})

@app.route('/health')
def health():
    return jsonify({'ok': True, 'managers': len(manager_ids), 'pending': len(pending), 'manager_ids': manager_ids})

@app.route('/')
def index():
    return jsonify({'service': 'JAC MOTORS ANGREN Bot API'})

if __name__ == '__main__':
    print(f"🚀 Managers: {manager_ids}")
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False), daemon=True).start()
    time.sleep(2)
    app_tg = build_app()
    print("🤖 Polling started...")
    app_tg.run_polling()
