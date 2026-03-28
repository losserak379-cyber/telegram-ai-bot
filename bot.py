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

# 🔗 YOUR CHANNEL
CHANNEL_USERNAME = "@Multisaverbot_for_all"
CHANNEL_LINK = "https://t.me/Multisaverbot_for_all"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

user_links = {}

# =========================
# 🔒 FORCE JOIN CHECK
# =========================
async def check_join(update, context):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# =========================
# 🚀 START UI
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await check_join(update, context)

    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "🚫 You must join our channel to use this bot!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("📥 Download Video", callback_data="download")]
    ]

    await update.message.reply_text(
        "✨ *MultiSaver Bot* ✨\n\n"
        "📥 Send any video link (YouTube, Instagram, Facebook)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================
# 📩 RECEIVE LINK
# =========================
async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await check_join(update, context)

    if not joined:
        await update.message.reply_text("🚫 Join channel first using /start")
        return

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

    elif query.data == "check_join":
        joined = await check_join(update, context)

        if joined:
            await query.edit_message_text("✅ You can now use the bot! Send link 🎉")
        else:
            await query.answer("❌ Join channel first!", show_alert=True)

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

    'nocheckcertificate': True,
    'ignoreerrors': False,
    'geo_bypass': True,

    'http_headers': {
        'User-Agent': 'Mozilla/5.0',
    },

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
            caption=f"🎬 {info.get('title','Video')}\n\n✅ Done",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]
            ])
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
