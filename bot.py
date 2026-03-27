import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

user_links = {}

# 🔗 PUT YOUR CHANNEL LINK HERE
CHANNEL_LINK = "https://t.me/your_channel"

# =========================
# 🚀 START UI
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Download Video", callback_data="download")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
    ]

    await update.message.reply_text(
        "✨ *
