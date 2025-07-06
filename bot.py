import logging
import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

if not BOT_TOKEN:
    raise RuntimeError("💥  BOT_TOKEN is missing in .env")
if not ADMIN_IDS:
    raise RuntimeError("💥  ADMIN_IDS is empty or invalid in .env")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋  *Anonymous Suggest Bot* ga xush kelibsiz.\n"
        "Har qanday fikr‑mulohazangizni yozib yuboring — u anonim tarzda administratorlarga yetkaziladi.",
        parse_mode="Markdown",
    )


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💡  Anonim taklif yuborish uchun shunchaki matn yozing va jo‘nating.\n"
        "•  `/start` – xush kelibsiz xabarini ko‘rish\n"
        "•  `/help` – yordam oynasi",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward user‑sent text to each admin anonymously."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    text = update.message.text

    if user_id in ADMIN_IDS:
        await update.message.reply_text("🛑  Adminlar anonim taklif yubora olmaydi.")
        return

    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin,
                f"📬  *Yangi anonim taklif*\n\n{text}",
                parse_mode="Markdown",
            )
        except Exception as exc:
            log.exception("Failed to DM admin %s: %s", admin, exc)

    await update.message.reply_text("✅  Yuborildi! Taklifingiz adminlarga yetib bordi.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Update %s caused error %s", update, context.error)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    log.info("🤖  Bot online. Waiting for spicy takes…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
