import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://api-inference.huggingface.co/models/sczhou/CodeFormer"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# ===== BUTTON MENU =====
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("🖼 Enhance Photo")
    btn2 = KeyboardButton("ℹ Help")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "✨ Send a photo to enhance", reply_markup=markup)

# ===== HANDLE PHOTO =====
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "✨ Enhancing... Please wait")

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    response = requests.post(API_URL, headers=headers, data=downloaded_file)

    if response.status_code == 200:
        bot.send_photo(message.chat.id, response.content)
    else:
        bot.reply_to(message, "❌ Enhancement failed. Try later.")

# ===== HELP BUTTON =====
@bot.message_handler(func=lambda m: m.text == "ℹ Help")
def help_btn(message):
    bot.reply_to(message, "Send a photo and I will enhance it using AI.")

print("Bot running...")
bot.infinity_polling()
