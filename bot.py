import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ===== START MENU =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("🖼 Enhance Photo")
    btn2 = KeyboardButton("🎭 Remove Background")
    btn3 = KeyboardButton("💎 My Credits")
    btn4 = KeyboardButton("📣 Admin Panel")
    btn5 = KeyboardButton("ℹ Help")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)

    bot.send_message(message.chat.id, "✨ Welcome! Choose an option:", reply_markup=markup)

# ===== BUTTON HANDLER =====
@bot.message_handler(func=lambda m: True)
def buttons(m):
    if m.text == "🖼 Enhance Photo":
        bot.reply_to(m, "📷 Send photo to enhance.")
    elif m.text == "🎭 Remove Background":
        bot.reply_to(m, "🖼 Send photo to remove background.")
    elif m.text == "💎 My Credits":
        bot.reply_to(m, "⭐ You have 10 free credits.")
    elif m.text == "📣 Admin Panel":
        bot.reply_to(m, "🔐 Admin feature coming soon.")
    elif m.text == "ℹ Help":
        bot.reply_to(m, "Send a photo and choose what you want to do.")

print("Bot running...")
bot.infinity_polling()
