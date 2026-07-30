"""
JAC MOTORS ANGREN — Telegram Bot Backend
Handles contact form submissions and routes to random users.
"""

import os
import time
import threading
import random
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = "8854046020:AAHtK4ZTZLDt5_TowHAUIXFVBmcuYNxZdE8"

# List of users who can accept/reject leads (telegram user IDs)
# Replace with real user IDs of managers/sales people
MANAGER_IDS = [
    123456789,  # Manager 1 — REPLACE WITH REAL ID
    987654321,  # Manager 2 — REPLACE WITH REAL ID
]

# How long a lead waits before auto-reject (seconds)
AUTO_REJECT_TIMEOUT = 60

# Rate limiting: max submissions per IP per 20 minutes
RATE_LIMIT_MAX = 2
RATE_LIMIT_WINDOW = 20 * 60  # seconds

# ============================================================
# STATE
# ============================================================
app = Flask(__name__)
CORS(app, origins=['https://neugadaypj-pixel.github.io', 'https://jacauto.uz', 'http://localhost:*'])
bot = Bot(token=BOT_TOKEN)

# In-memory store
pending_leads = {}     # {lead_id: {...}}
rate_limit = {}        # {ip: [(timestamp,), ...]}
managers_file = "managers.json"

# Load/save managers dynamically
def load_managers():
    global MANAGER_IDS
    try:
        with open(managers_file, 'r') as f:
            data = json.load(f)
            MANAGER_IDS = data.get('manager_ids', MANAGER_IDS)
    except:
        save_managers()

def save_managers():
    with open(managers_file, 'w') as f:
        json.dump({'manager_ids': MANAGER_IDS}, f)

load_managers()

# ============================================================
# RATE LIMIT CHECK
# ============================================================
def check_rate_limit(ip):
    """Return True if allowed, False if rate-limited."""
    now = time.time()
    if ip not in rate_limit:
        rate_limit[ip] = []
    # Clean old entries
    rate_limit[ip] = [t for t in rate_limit[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(rate_limit[ip]) >= RATE_LIMIT_MAX:
        return False
    rate_limit[ip].append(now)
    return True

# ============================================================
# TELEGRAM KEYBOARDS
# ============================================================
def accept_reject_keyboard(lead_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{lead_id}"),
            InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{lead_id}")
        ]
    ])

def format_lead_message(lead):
    return (
        f"🆕 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"👤 <b>Имя:</b> {lead['name']}\n"
        f"📞 <b>Телефон:</b> {lead['phone']}\n"
        f"🚗 <b>Модель:</b> {lead['model']}\n"
        f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n"
        f"⏰ <b>Время:</b> {lead['time']}\n\n"
        f"<i>У вас есть 1 минута чтобы ответить</i>"
    )

# ============================================================
# SEND LEAD TO RANDOM MANAGER
# ============================================================
def send_to_random_manager(lead_id):
    lead = pending_leads.get(lead_id)
    if not lead or not MANAGER_IDS:
        return

    # Pick a random manager who hasn't already rejected this lead
    available = [mid for mid in MANAGER_IDS if mid not in lead.get('rejected_by', [])]
    if not available:
        # All managers rejected — notify
        pending_leads.pop(lead_id, None)
        return

    manager_id = random.choice(available)
    lead['current_manager'] = manager_id
    lead['sent_at'] = time.time()

    try:
        msg = bot.send_message(
            chat_id=manager_id,
            text=format_lead_message(lead),
            reply_markup=accept_reject_keyboard(lead_id),
            parse_mode='HTML'
        )
        lead['message_id'] = msg.message_id
    except Exception as e:
        print(f"Failed to send to manager {manager_id}: {e}")
        # Try another
        lead.setdefault('rejected_by', []).append(manager_id)
        send_to_random_manager(lead_id)

# ============================================================
# AUTO-REJECT TIMER
# ============================================================
def auto_reject_timer(lead_id):
    time.sleep(AUTO_REJECT_TIMEOUT)
    lead = pending_leads.get(lead_id)
    if not lead:
        return
    if lead.get('status') == 'pending':
        # Auto reject current manager
        mid = lead.get('current_manager')
        if mid:
            try:
                bot.edit_message_text(
                    chat_id=mid,
                    message_id=lead['message_id'],
                    text=format_lead_message(lead) + "\n\n⏰ <b>Время истекло — передано другому</b>",
                    parse_mode='HTML'
                )
            except:
                pass
            lead.setdefault('rejected_by', []).append(mid)
        # Send to next
        send_to_random_manager(lead_id)
        threading.Thread(target=auto_reject_timer, args=(lead_id,), daemon=True).start()

# ============================================================
# API: Submit lead form
# ============================================================
@app.route('/api/submit', methods=['POST'])
def submit_lead():
    if not request.is_json:
        return jsonify({'ok': False, 'error': 'JSON required'}), 400

    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    model = data.get('model', '').strip() or 'Не указана'
    comment = data.get('comment', '').strip()

    if not name or not phone:
        return jsonify({'ok': False, 'error': 'Имя и телефон обязательны'}), 400

    # Rate limit check
    ip = request.remote_addr or request.headers.get('X-Forwarded-For', '0.0.0.0')
    if not check_rate_limit(ip):
        return jsonify({'ok': False, 'error': 'Слишком много заявок. Попробуйте позже (лимит: 2 за 20 минут)'}), 429

    lead_id = f"lead_{int(time.time())}_{random.randint(1000, 9999)}"
    lead = {
        'id': lead_id,
        'name': name,
        'phone': phone,
        'model': model,
        'comment': comment,
        'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'status': 'pending',
        'rejected_by': [],
        'current_manager': None,
        'message_id': None,
        'sent_at': None,
    }
    pending_leads[lead_id] = lead

    # Start routing
    send_to_random_manager(lead_id)
    # Start auto-reject timer
    threading.Thread(target=auto_reject_timer, args=(lead_id,), daemon=True).start()

    return jsonify({'ok': True, 'message': 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.'})

# ============================================================
# TELEGRAM: Handle /start and callback queries
# ============================================================
@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint — receives updates."""
    try:
        data = request.get_json(force=True)
    except:
        return 'ok', 200

    if 'callback_query' in data:
        handle_callback(data['callback_query'])
    elif 'message' in data:
        handle_message(data['message'])

    return 'ok', 200

def handle_message(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == '/start':
        bot.send_message(
            chat_id=chat_id,
            text=(
                "👋 <b>Добро пожаловать в JAC MOTORS ANGREN!</b>\n\n"
                "Вы зарегистрированы как менеджер по заявкам.\n"
                "Когда клиент оставит заявку, вы получите уведомление с кнопками:\n"
                "✅ Принять — увидите контакты клиента\n"
                "❌ Отказать — заявка уйдёт другому менеджеру\n\n"
                "<i>Ваш ID: {}</i>".format(chat_id)
            ),
            parse_mode='HTML'
        )
        # Auto-register as manager
        if chat_id not in MANAGER_IDS:
            MANAGER_IDS.append(chat_id)
            save_managers()

    elif text == '/managers':
        if MANAGER_IDS:
            ids = '\n'.join([f"• <code>{mid}</code>" for mid in MANAGER_IDS])
            bot.send_message(chat_id=chat_id, text=f"📋 <b>Менеджеры:</b>\n\n{ids}", parse_mode='HTML')
        else:
            bot.send_message(chat_id=chat_id, text="Пока нет зарегистрированных менеджеров.")

    elif text == '/remove':
        if chat_id in MANAGER_IDS:
            MANAGER_IDS.remove(chat_id)
            save_managers()
            bot.send_message(chat_id=chat_id, text="Вы удалены из списка менеджеров.")
        else:
            bot.send_message(chat_id=chat_id, text="Вас нет в списке менеджеров.")

def handle_callback(cb):
    chat_id = cb['message']['chat']['id']
    data = cb['data']
    message_id = cb['message']['message_id']

    parts = data.split('_', 1)
    if len(parts) < 2:
        return

    action, lead_id = parts[0], parts[1]
    lead = pending_leads.get(lead_id)

    if not lead:
        try:
            bot.answer_callback_query(cb['id'], "Заявка уже неактуальна")
        except:
            pass
        return

    if action == 'accept':
        lead['status'] = 'accepted'
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                f"✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
                f"👤 <b>Имя:</b> {lead['name']}\n"
                f"📞 <b>Телефон:</b> <code>{lead['phone']}</code>\n"
                f"🚗 <b>Модель:</b> {lead['model']}\n"
                f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n\n"
                f"<i>Свяжитесь с клиентом!</i>"
            ),
            parse_mode='HTML'
        )
        try:
            bot.answer_callback_query(cb['id'], "✅ Заявка принята!")
        except:
            pass
        pending_leads.pop(lead_id, None)

    elif action == 'reject':
        lead.setdefault('rejected_by', []).append(chat_id)
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=format_lead_message(lead) + "\n\n❌ <b>Вы отказались — передано другому менеджеру</b>",
                parse_mode='HTML'
            )
        except:
            pass
        try:
            bot.answer_callback_query(cb['id'], "Заявка передана другому менеджеру")
        except:
            pass
        send_to_random_manager(lead_id)

# ============================================================
# HEALTH / INFO
# ============================================================
@app.route('/health')
def health():
    return jsonify({
        'ok': True,
        'managers': len(MANAGER_IDS),
        'pending_leads': len(pending_leads),
        'rate_limited_ips': len(rate_limit)
    })

@app.route('/')
def index():
    return jsonify({'service': 'JAC MOTORS ANGREN Bot Backend', 'endpoints': ['/api/submit', '/webhook', '/health']})

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("🚀 Starting JAC MOTORS ANGREN backend...")
    print(f"   Bot token: {BOT_TOKEN[:10]}...")
    print(f"   Managers: {MANAGER_IDS}")
    print("   Register managers by sending /start to the bot on Telegram")
    app.run(host='0.0.0.0', port=5000, debug=True)
