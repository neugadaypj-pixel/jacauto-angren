"""
JAC MOTORS ANGREN — Telegram Bot (Standalone)
================================================
Запусти этот скрипт на своём компьютере.
Форма на сайте будет отправлять заявки через Telegram Bot напрямую.

Требования:
    pip install python-telegram-bot flask flask-cors gunicorn

Запуск:
    python bot.py

Оставь работающим в фоне — и всё будет работать.
"""

import json
import time
import random
import threading
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# ============================================================
# КОНФИГ
# ============================================================
BOT_TOKEN = "8854046020:AAHtK4ZTZLDt5_TowHAUIXFVBmcuYNxZdE8"
MANAGERS_FILE = "managers.json"
AUTO_REJECT_TIMEOUT = 60  # секунд до авто-отклонения
RATE_LIMIT_MAX = 2
RATE_LIMIT_WINDOW = 20 * 60  # 20 минут

# ============================================================
# ХРАНИЛИЩЕ
# ============================================================
pending_leads = {}   # {lead_id: {...}}
rate_limit = {}      # {ip: [timestamp, ...]}
manager_ids = []

def load_managers():
    global manager_ids
    try:
        with open(MANAGERS_FILE, 'r') as f:
            data = json.load(f)
            manager_ids = data.get('manager_ids', [])
        print(f"📋 Загружено менеджеров: {len(manager_ids)}")
    except:
        save_managers()

def save_managers():
    with open(MANAGERS_FILE, 'w') as f:
        json.dump({'manager_ids': manager_ids}, f, indent=2)

load_managers()

# ============================================================
# ТЕЛЕГРАМ БОТ
# ============================================================
app_telegram = Application.builder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)

def accept_reject_keyboard(lead_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Принять", callback_data=f"accept_{lead_id}"),
         InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{lead_id}")]
    ])

def format_lead(lead):
    return (
        f"🆕 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"👤 <b>Имя:</b> {lead['name']}\n"
        f"📞 <b>Телефон:</b> {lead['phone']}\n"
        f"🚗 <b>Модель:</b> {lead['model']}\n"
        f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n"
        f"⏰ <b>Время:</b> {lead['time']}\n\n"
        f"<i>У вас есть 1 минута чтобы ответить</i>"
    )

async def start_cmd(update, context):
    uid = update.effective_user.id
    if uid not in manager_ids:
        manager_ids.append(uid)
        save_managers()
    await update.message.reply_text(
        f"👋 <b>Вы зарегистрированы как менеджер JAC MOTORS ANGREN!</b>\n\n"
        f"Когда клиент оставит заявку, вы получите уведомление с кнопками:\n"
        f"✅ Принять — увидите контакты клиента\n"
        f"❌ Отказать — заявка уйдёт другому менеджеру\n\n"
        f"Ваш ID: <code>{uid}</code>\n"
        f"/managers — список менеджеров\n/remove — удалить себя",
        parse_mode='HTML'
    )

async def managers_cmd(update, context):
    if manager_ids:
        ids = '\n'.join([f"• <code>{m}</code>" for m in manager_ids])
        await update.message.reply_text(f"📋 Менеджеры:\n\n{ids}", parse_mode='HTML')
    else:
        await update.message.reply_text("Пока нет менеджеров. Отправьте /start чтобы зарегистрироваться.")

async def remove_cmd(update, context):
    uid = update.effective_user.id
    if uid in manager_ids:
        manager_ids.remove(uid)
        save_managers()
        await update.message.reply_text("Вы удалены из списка менеджеров.")
    else:
        await update.message.reply_text("Вас нет в списке.")

async def callback_handler(update, context):
    cb = update.callback_query
    data = cb.data
    mid = update.effective_user.id
    msg_id = cb.message.message_id

    parts = data.split('_', 1)
    if len(parts) < 2:
        await cb.answer()
        return

    action, lead_id = parts[0], parts[1]
    lead = pending_leads.get(lead_id)

    if not lead:
        await cb.answer("Заявка уже неактивна")
        return

    if action == 'accept':
        lead['status'] = 'accepted'
        await cb.edit_message_text(
            f"✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
            f"👤 <b>Имя:</b> {lead['name']}\n"
            f"📞 <b>Телефон:</b> <code>{lead['phone']}</code>\n"
            f"🚗 <b>Модель:</b> {lead['model']}\n"
            f"💬 <b>Комментарий:</b> {lead.get('comment', '—')}\n\n"
            f"<i>Свяжитесь с клиентом!</i>",
            parse_mode='HTML'
        )
        await cb.answer("✅ Заявка принята!")
        pending_leads.pop(lead_id, None)

    elif action == 'reject':
        lead.setdefault('rejected_by', []).append(mid)
        try:
            await cb.edit_message_text(
                format_lead(lead) + "\n\n❌ <b>Вы отказались — передано другому</b>",
                parse_mode='HTML'
            )
        except:
            pass
        await cb.answer("Заявка передана другому менеджеру")
        send_to_random_manager(lead_id)

app_telegram.add_handler(CommandHandler('start', start_cmd))
app_telegram.add_handler(CommandHandler('managers', managers_cmd))
app_telegram.add_handler(CommandHandler('remove', remove_cmd))
app_telegram.add_handler(CallbackQueryHandler(callback_handler))

# ============================================================
# ЛОГИКА РАСПРЕДЕЛЕНИЯ ЗАЯВОК
# ============================================================
def send_to_random_manager(lead_id):
    lead = pending_leads.get(lead_id)
    if not lead or not manager_ids:
        return

    available = [m for m in manager_ids if m not in lead.get('rejected_by', [])]
    if not available:
        pending_leads.pop(lead_id, None)
        return

    manager = random.choice(available)
    lead['current_manager'] = manager
    lead['sent_at'] = time.time()

    try:
        # Send synchronously via bot (we're in Flask thread)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        msg = loop.run_until_complete(
            bot.send_message(
                chat_id=manager,
                text=format_lead(lead),
                reply_markup=accept_reject_keyboard(lead_id),
                parse_mode='HTML'
            )
        )
        loop.close()
        lead['message_id'] = msg.message_id
    except Exception as e:
        print(f"❌ Ошибка отправки менеджеру {manager}: {e}")
        lead.setdefault('rejected_by', []).append(manager)
        send_to_random_manager(lead_id)

def auto_reject_timer(lead_id):
    time.sleep(AUTO_REJECT_TIMEOUT)
    lead = pending_leads.get(lead_id)
    if not lead or lead.get('status') != 'pending':
        return
    mid = lead.get('current_manager')
    if mid:
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                bot.edit_message_text(
                    chat_id=mid,
                    message_id=lead['message_id'],
                    text=format_lead(lead) + "\n\n⏰ <b>Время истекло — передано другому</b>",
                    parse_mode='HTML'
                )
            )
            loop.close()
        except:
            pass
        lead.setdefault('rejected_by', []).append(mid)
    send_to_random_manager(lead_id)
    threading.Thread(target=auto_reject_timer, args=(lead_id,), daemon=True).start()

# ============================================================
# АНТИ-СПАМ
# ============================================================
def check_rate(ip):
    now = time.time()
    rate_limit.setdefault(ip, [])
    rate_limit[ip] = [t for t in rate_limit[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(rate_limit[ip]) >= RATE_LIMIT_MAX:
        return False
    rate_limit[ip].append(now)
    return True

# ============================================================
# FLASK API (для приёма заявок с сайта)
# ============================================================
flask_app = Flask(__name__)
CORS(flask_app)

@flask_app.route('/api/submit', methods=['POST'])
def submit_lead():
    data = request.get_json(force=True) if request.is_json else {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    model = data.get('model', '') or 'Не указана'
    comment = data.get('comment', '').strip()

    if not name or not phone:
        return jsonify({'ok': False, 'error': 'Имя и телефон обязательны'}), 400

    ip = request.remote_addr or '0.0.0.0'
    if not check_rate(ip):
        return jsonify({'ok': False, 'error': 'Лимит: 2 заявки за 20 минут'}), 429

    lid = f"lead_{int(time.time())}_{random.randint(1000,9999)}"
    lead = {
        'id': lid, 'name': name, 'phone': phone, 'model': model,
        'comment': comment, 'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'status': 'pending', 'rejected_by': [], 'current_manager': None,
        'message_id': None, 'sent_at': None
    }
    pending_leads[lid] = lead
    send_to_random_manager(lid)
    threading.Thread(target=auto_reject_timer, args=(lid,), daemon=True).start()

    return jsonify({'ok': True, 'message': 'Заявка отправлена! Менеджер свяжется с вами.'})

@flask_app.route('/health')
def health():
    return jsonify({'ok': True, 'managers': len(manager_ids), 'pending': len(pending_leads)})

@flask_app.route('/')
def index():
    return jsonify({'service': 'JAC MOTORS ANGREN Bot API', 'endpoints': ['/api/submit', '/health']})

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 JAC MOTORS ANGREN — Telegram Bot + API")
    print("=" * 60)
    print(f"🤖 Бот запущен")
    print(f"📋 Менеджеров: {len(manager_ids)}")
    print(f"🌐 API: http://localhost:5000/api/submit")
    print(f"💚 Health: http://localhost:5000/health")
    print()
    print("Отправь /start боту в Telegram чтобы зарегистрироваться как менеджер!")
    print("Нажми Ctrl+C чтобы остановить")
    print("=" * 60)

    # Запускаем Flask API в отдельном потоке
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=5000, use_reloader=False), daemon=True).start()
    time.sleep(1)

    # Запускаем Telegram polling в главном потоке
    print("🤖 Telegram polling запущен...")
    app_telegram.run_polling()
