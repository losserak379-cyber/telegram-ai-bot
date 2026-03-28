import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🎬 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a video link\n\nI support YouTube, Instagram, Terabox & more!"
    )

# 🎯 HANDLE LINK
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data=f"360|{url}"),
            InlineKeyboardButton("720p", callback_data=f"720|{url}"),
        ],
        [InlineKeyboardButton("🔥 Best", callback_data=f"best|{url}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎛 Choose download quality:",
        reply_markup=reply_markup
    )

# 📥 DOWNLOAD FUNCTIONS 
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|")

    msg = await query.message.reply_text("⏳ Fetching video...")

    try:
        if quality == "360":
            format_code = "best[height<=360]"
        elif quality == "720":
            format_code = "best[height<=720]"
        else:
            format_code = "best"

        ydl_opts = {
            "format": format_code,
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": False,

            # 🔥 IMPORTANT FIXES
            "nocheckcertificate": True,
            "geo_bypass": True,
            "headers": {
                "User-Agent": "Mozilla/5.0",
                "Referer": url,
            },

            # try generic extractor
            "extractor_retries": 3,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading...")

        await query.message.reply_video(video=open(file_path, "rb"))

        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Failed:\n{str(e)}")

# 🚀 MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(download_video))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
