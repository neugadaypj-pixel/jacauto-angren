"""Telegram bot and form API for JAC MOTORS ANGREN."""

import asyncio
import csv
import html
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

from flask import Flask, jsonify, request
from flask_cors import CORS
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
MANAGERS_FILE = Path(os.environ.get("MANAGERS_FILE", "managers.json"))
MANAGERS_SHEET = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vSgam8czC85ktRCxfKNpyL_eV2E0rA96xSvYDNrcXD0CNJk-3X7qP0ISNQr0qRmPx5CctG0d6qeHaEN/"
    "pub?output=csv"
)
AUTO_REJECT_SECONDS = 60
RATE_LIMIT_MAX = 3
RATE_LIMIT_SECONDS = 20 * 60
MAX_FIELD_LENGTHS = {"name": 100, "phone": 40, "model": 120, "comment": 1000}

app = Flask(__name__)
CORS(app, origins=[
    "https://jac-motors.uz",
    "https://www.jac-motors.uz",
    "https://neugadaypj-pixel.github.io",
])

manager_ids = []
pending = {}
rate_limits = {}
state_lock = threading.Lock()
manager_lock = threading.Lock()
bot_application = None
bot_loop = None


def save_managers():
    MANAGERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with manager_lock:
        MANAGERS_FILE.write_text(
            json.dumps({"manager_ids": manager_ids}),
            encoding="utf-8",
        )


def load_managers():
    """Load authorized manager IDs from configuration or the published sheet."""
    global manager_ids
    configured_ids = os.environ.get("MANAGER_IDS", "").strip()
    if configured_ids:
        manager_ids = [int(value.strip()) for value in configured_ids.split(",") if value.strip().isdigit()]

    try:
        data = json.loads(MANAGERS_FILE.read_text(encoding="utf-8"))
        saved_ids = [int(value) for value in data.get("manager_ids", [])]
        manager_ids = list(dict.fromkeys(manager_ids + saved_ids))
        return
    except (OSError, ValueError, TypeError):
        if manager_ids:
            return

    try:
        with urlopen(MANAGERS_SHEET, timeout=8) as response:
            rows = csv.reader(response.read().decode("utf-8-sig").splitlines())
            next(rows, None)
            manager_ids = [int(row[0].strip()) for row in rows if row and row[0].strip().isdigit()]
    except Exception:
        logger.exception("Could not load manager IDs from the published sheet")
        manager_ids = []


def escaped(value):
    return html.escape(str(value or "—"), quote=False)


def lead_message(lead, accepted=False):
    if accepted:
        return (
            "✅ <b>ЗАЯВКА ПРИНЯТА</b>\n\n"
            f"👤 <b>Имя:</b> {escaped(lead['name'])}\n"
            f"📞 <b>Телефон:</b> <code>{escaped(lead['phone'])}</code>\n"
            f"🚗 <b>Модель:</b> {escaped(lead['model'])}\n"
            f"💬 <b>Комментарий:</b> {escaped(lead['comment'])}\n"
            f"⏰ <b>Время:</b> {escaped(lead['time'])}\n\n"
            "<i>Свяжитесь с клиентом.</i>"
        )
    return (
        "🚘 <b>НОВАЯ ЗАЯВКА JAC MOTORS ANGREN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚗 <b>Модель:</b> {escaped(lead['model'])}\n"
        f"⏰ <b>Время:</b> {escaped(lead['time'])}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Нажмите «Принять», чтобы увидеть контакты клиента.\n"
        "Если не ответить за минуту, заявка перейдёт следующему менеджеру."
    )


def lead_keyboard(lead_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Принять заявку", callback_data=f"accept:{lead_id}"),
        InlineKeyboardButton("↪️ Передать дальше", callback_data=f"reject:{lead_id}"),
    ]])


async def send_to_next(lead_id, context):
    lead = pending.get(lead_id)
    if not lead or lead["status"] != "pending":
        return False

    rejected = set(lead["rejected_by"])
    with manager_lock:
        available = [manager_id for manager_id in manager_ids if manager_id not in rejected]
    while available:
        manager_id = available.pop(0)
        try:
            message = await context.bot.send_message(
                chat_id=manager_id,
                text=lead_message(lead),
                reply_markup=lead_keyboard(lead_id),
                parse_mode="HTML",
            )
        except Exception:
            logger.exception("Failed to deliver lead %s to a manager", lead_id)
            lead["rejected_by"].append(manager_id)
            continue

        lead["current_manager"] = manager_id
        lead["message_id"] = message.message_id
        lead["timer"] = asyncio.create_task(expire_lead(lead_id, context))
        return True

    lead["status"] = "undelivered"
    return False


async def expire_lead(lead_id, context):
    await asyncio.sleep(AUTO_REJECT_SECONDS)
    lead = pending.get(lead_id)
    if not lead or lead["status"] != "pending":
        return

    manager_id = lead.get("current_manager")
    if manager_id is not None:
        lead["rejected_by"].append(manager_id)
        try:
            await context.bot.edit_message_text(
                chat_id=manager_id,
                message_id=lead["message_id"],
                text=lead_message(lead) + "\n\n⌛ Время ответа истекло. Заявка передана дальше.",
                parse_mode="HTML",
            )
        except Exception:
            logger.info("Could not update expired lead message %s", lead_id, exc_info=True)

    if not await send_to_next(lead_id, context):
        logger.error("No manager could receive lead %s", lead_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("Для подключения к заявкам откройте со мной личный чат и отправьте /start.")
        return
    user_id = update.effective_user.id
    with manager_lock:
        is_new_manager = user_id not in manager_ids
        if is_new_manager:
            manager_ids.append(user_id)
    if is_new_manager:
        try:
            save_managers()
        except OSError:
            with manager_lock:
                manager_ids.remove(user_id)
            logger.exception("Could not save newly registered manager %s", user_id)
            await update.message.reply_text("Не удалось подключить вас к заявкам. Попробуйте позже.")
            return
    await update.message.reply_text(
        "👋 <b>JAC MOTORS ANGREN</b>\n\n"
        "Вы подключены к заявкам как менеджер.\n"
        "Уведомления будут приходить сюда. Нажмите «Принять», чтобы увидеть имя и телефон клиента.\n"
        "Данные заявок предназначены только для связи с клиентом.",
        parse_mode="HTML",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, _, lead_id = (query.data or "").partition(":")
    lead = pending.get(lead_id)
    if action not in {"accept", "reject"} or not lead or lead["status"] != "pending":
        await query.answer("Заявка уже неактуальна.")
        return
    if query.from_user.id != lead.get("current_manager") or query.from_user.id not in manager_ids:
        await query.answer("Эта заявка назначена другому менеджеру.")
        return

    timer = lead.get("timer")
    if timer:
        timer.cancel()

    if action == "accept":
        lead["status"] = "accepted"
        await query.edit_message_text(lead_message(lead, accepted=True), parse_mode="HTML")
        await query.answer("Заявка принята.")
        pending.pop(lead_id, None)
        return

    lead["rejected_by"].append(query.from_user.id)
    await query.edit_message_text("↪️ Вы передали заявку следующему менеджеру.")
    await query.answer("Передаём заявку.")
    if not await send_to_next(lead_id, context):
        pending.pop(lead_id, None)
        try:
            await query.message.reply_text(
                "Не удалось передать заявку: нет доступных менеджеров. "
                "Свяжитесь с клиентом по телефону, если заявка у вас уже открыта."
            )
        except Exception:
            logger.exception("Could not notify manager that lead %s was undelivered", lead_id)


async def managers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in manager_ids:
        await update.message.reply_text("Сначала отправьте /start, чтобы подключиться к заявкам.")
        return
    await update.message.reply_text(f"В списке менеджеров: {len(manager_ids)}.")

async def remove_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with manager_lock:
        is_manager = user_id in manager_ids
        if is_manager:
            manager_ids.remove(user_id)
    if not is_manager:
        await update.message.reply_text("Вы не подключены к заявкам.")
        return
    try:
        save_managers()
    except OSError:
        with manager_lock:
            manager_ids.append(user_id)
        logger.exception("Could not save manager removal for %s", user_id)
        await update.message.reply_text("Не удалось отключить уведомления. Попробуйте позже.")
        return
    await update.message.reply_text("Вы отключены от заявок. Чтобы подключиться снова, отправьте /start.")


async def create_lead(payload, context):
    lead_id = uuid.uuid4().hex[:16]
    lead = {
        **payload,
        "id": lead_id,
        "time": datetime.now().astimezone().strftime("%d.%m.%Y %H:%M"),
        "status": "pending",
        "rejected_by": [],
        "current_manager": None,
        "message_id": None,
        "timer": None,
    }
    pending[lead_id] = lead
    if not await send_to_next(lead_id, context):
        pending.pop(lead_id, None)
        return False
    return True


def rate_limited(client_ip):
    now = time.time()
    attempts = [stamp for stamp in rate_limits.get(client_ip, []) if now - stamp < RATE_LIMIT_SECONDS]
    if len(attempts) >= RATE_LIMIT_MAX:
        rate_limits[client_ip] = attempts
        return True
    attempts.append(now)
    rate_limits[client_ip] = attempts
    return False


@app.post("/api/submit")
def submit_lead():
    if not request.is_json:
        return jsonify({"ok": False, "error": "Некорректный формат заявки."}), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"ok": False, "error": "Некорректный формат заявки."}), 400

    payload = {}
    for field in ("name", "phone", "model", "comment"):
        value = data.get(field, "")
        if not isinstance(value, str):
            return jsonify({"ok": False, "error": "Проверьте заполненные поля."}), 400
        value = value.strip()
        if len(value) > MAX_FIELD_LENGTHS[field]:
            return jsonify({"ok": False, "error": "Некоторые поля слишком длинные."}), 400
        payload[field] = value
    if not payload["name"] or not payload["phone"]:
        return jsonify({"ok": False, "error": "Укажите имя и номер телефона."}), 400
    if not manager_ids:
        logger.error("Lead rejected because no manager IDs are configured")
        return jsonify({"ok": False, "error": "Приём заявок временно недоступен. Позвоните нам: 71 200 77 11"}), 503

    with state_lock:
        if rate_limited(request.remote_addr or "unknown"):
            return jsonify({"ok": False, "error": "Слишком много заявок. Попробуйте позже."}), 429

    if bot_loop is None or bot_application is None:
        logger.error("Lead rejected because the Telegram bot is not ready")
        return jsonify({"ok": False, "error": "Сервис временно недоступен. Позвоните нам: 71 200 77 11"}), 503

    future = asyncio.run_coroutine_threadsafe(
        create_lead(payload, bot_application),
        bot_loop,
    )
    try:
        delivered = future.result(timeout=20)
    except Exception:
        logger.exception("Could not route a new customer lead")
        return jsonify({"ok": False, "error": "Не удалось отправить заявку. Позвоните нам: 71 200 77 11"}), 503
    if not delivered:
        logger.error("No manager accepted delivery of a new lead")
        return jsonify({"ok": False, "error": "Не удалось отправить заявку. Позвоните нам: 71 200 77 11"}), 503
    return jsonify({"ok": True, "message": "Заявка отправлена менеджеру."})


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "bot_ready": bot_application is not None,
        "managers": len(manager_ids),
        "pending": len(pending),
    })


async def run():
    global bot_application, bot_loop
    if not BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in the hosting provider's environment settings.")

    load_managers()
    if not manager_ids:
        logger.warning("No managers are configured; form submissions will be rejected until configured.")

    bot_application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    bot_application.add_handler(CommandHandler("start", start))
    bot_application.add_handler(CommandHandler("managers", managers_command))
    bot_application.add_handler(CommandHandler("remove", remove_manager))
    bot_application.add_handler(CallbackQueryHandler(handle_callback))

    await bot_application.initialize()
    await bot_application.start()
    await bot_application.updater.start_polling()
    bot_loop = asyncio.get_running_loop()

    port = int(os.environ.get("PORT", "5000"))
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
        daemon=True,
    ).start()
    logger.info("Telegram bot and form API are running; loaded %d managers.", len(manager_ids))

    try:
        await asyncio.Event().wait()
    finally:
        await bot_application.updater.stop()
        await bot_application.stop()
        await bot_application.shutdown()


if __name__ == "__main__":
    asyncio.run(run())
