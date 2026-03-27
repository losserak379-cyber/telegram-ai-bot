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

# 🔗 CHANGE THIS TO YOUR CHANNEL
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
        "✨ *MultiSaver Bot* ✨\n\n"
        "📥 Download videos from:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• Facebook\n\n"
        "👇 Click below to start:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================
# 📩 RECEIVE LINK
# =========================
async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("❌ Send valid video link")
        return

    user_links[update.message.from_user.id] = url

    keyboard = [
        [InlineKeyboardButton("⬇️ Download Now", callback_data="download_now")]
    ]

    await update.message.reply_text(
        "🎯 Ready to download?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔘 BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download":
        await query.edit_message_text("📥 Send your video link!")

    elif query.data == "download_now":
        url = user_links.get(query.from_user.id)

        if not url:
            await query.edit_message_text("❌ Link expired. Send again.")
            return

        await process_download(query, url)

# =========================
# ⏳ DOWNLOAD PROCESS
# =========================
async def process_download(query, url):
    msg = await query.edit_message_text("⏳ Processing...")

    ydl_opts = {
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        title = info.get("title", "Downloaded Video")
        thumbnail = info.get("thumbnail", None)

        caption = f"🎬 *{title}*\n\n✅ Downloaded by MultiSaver Bot"

        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]
        ]

        await msg.edit_text("📤 Uploading video...")

        await query.message.reply_video(
            video=open(file_path, "rb"),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")

# =========================
# ⚙️ MAIN APP
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))

print("🚀 Bot Running...")
app.run_polling()
