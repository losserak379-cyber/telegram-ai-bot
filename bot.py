import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("❌ Send a valid link")
        return

    await update.message.reply_video(
    video=open(file, 'rb'),
    caption="✅ Downloaded by MultiSaverBot"
    )

    ydl_opts = {
    'format': 'best[height<=720][filesize<50M]/best',
    'outtmpl': 'video.%(ext)s',
    'noplaylist': True,
    'merge_output_format': 'mp4',
    'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file, 'rb'))
        os.remove(file)

    except:
        await update.message.reply_text("❌ Failed to download")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, download))

app.run_polling()
