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

# Store user links temporarily
user_links = {}

# =========================
# 🚀 START UI
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Download", callback_data="download")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"),
         InlineKeyboardButton("👨‍💻 About", callback_data="about")]
    ]

    await update.message.reply_text(
        "✨ *MultiSaver Pro Bot* ✨\n\n"
        "📥 Send any video link to begin\n\n"
        "Supports YouTube, Instagram, Facebook & more 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================
# 🔘 BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download":
        await query.edit_message_text("📥 Send your video link now!")

    elif query.data == "help":
        await query.edit_message_text(
            "📌 Send link → Choose format → Download 🎉",
            parse_mode="Markdown"
        )

    elif query.data == "about":
        await query.edit_message_text(
            "🤖 MultiSaver Pro\n⚡ Fast Downloader\nMade with ❤️",
            parse_mode="Markdown"
        )

    # Handle format selection
    elif query.data.startswith("type_"):
        choice = query.data.split("_")[1]
        url = user_links.get(query.from_user.id)

        if not url:
            await query.edit_message_text("❌ Link expired. Send again.")
            return

        await process_download(query, url, choice)

# =========================
# 📩 RECEIVE LINK
# =========================
async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("❌ Send valid link")
        return

    user_links[update.message.from_user.id] = url

    keyboard = [
        [InlineKeyboardButton("🎥 Video", callback_data="type_video"),
         InlineKeyboardButton("🎧 Audio (MP3)", callback_data="type_audio")]
    ]

    await update.message.reply_text(
        "🎯 Choose format:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# ⏳ DOWNLOAD PROCESS
# =========================
async def process_download(query, url, choice):
    msg = await query.edit_message_text("⏳ Processing...")

    try:
        if choice == "video":
            ydl_opts = {
                'format': 'best[height<=720][filesize<50M]/best',
                'outtmpl': f'{DOWNLOAD_FOLDER}/video.%(ext)s',
                'merge_output_format': 'mp4',
                'quiet': True
            }

        else:  # AUDIO
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': f'{DOWNLOAD_FOLDER}/audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }

        await msg.edit_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading...")

        if choice == "video":
            await query.message.reply_video(open(file_path, "rb"))
        else:
            mp3_file = file_path.rsplit(".", 1)[0] + ".mp3"
            await query.message.reply_audio(open(mp3_file, "rb"))

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text("❌ Failed to download")

# =========================
# ⚙️ MAIN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))

print("🚀 Pro Bot Running...")
app.run_polling()
