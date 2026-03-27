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
        "✨ *MultiSaver Bot* ✨\n\n"
        "📥 Send any video link (YouTube, Instagram, Facebook)\n\n"
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
        await update.message.reply_text("❌ Send a valid video link")
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
# ⏳ DOWNLOAD FUNCTION
# =========================
async def process_download(query, url):
    msg = await query.edit_message_text("⏳ Downloading...")

    ydl_opts = {
    'format': 'best',
    'outtmpl': 'video.%(ext)s',
    'noplaylist': True,
    'quiet': False,

    # 🔥 FIXES
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'geo_bypass': True,

    # ✅ Add browser headers (VERY IMPORTANT)
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    },

    # ✅ Force Android client (fix YouTube)
    'extractor_args': {
        'youtube': {
            'player_client': ['android']
        }
    }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not info:
                await msg.edit_text("❌ Could not fetch video info")
                return

            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading...")

        await query.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"🎬 {info.get('title','Video')}\n\n✅ Done"
        )

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")

# =========================
# ⚙️ MAIN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link))

print("🚀 Bot Running...")
app.run_polling()
