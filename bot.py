import telebot
import requests
from telebot import types
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ستاسو بوټ ټوکن
BOT_TOKEN = '9295424680:AAFxP-EV5lokJM7HCHOalFTFGlLiPN1_xCY'
bot = telebot.TeleBot(BOT_TOKEN)

# ----------------- د چینلونو تنظیمات -----------------
CHANNELS = [
    '@investmentpnl', 
    '@pay_star1', 
    '@Ahmadullah_Tech', 
    '@Airdrops_io_3'
]

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            return False
    return True

def get_join_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, channel in enumerate(CHANNELS, 1):
        url = f"https://t.me/{channel.replace('@', '')}"
        btn = types.InlineKeyboardButton(f"📢 کانال {i} ته ننوځه", url=url)
        markup.add(btn)
    
    check_btn = types.InlineKeyboardButton("✅ ما ټول کانالونه جوین کړل (چک کړه)", callback_data="check_join")
    markup.add(check_btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_membership(user_id):
        bot.reply_to(
            message, 
            "⚠️ **تاسو باید لومړی لاندې ۴ کانالونه جوین کړئ، بیا کولی شئ روباټ وکاروئ:**",
            reply_markup=get_join_keyboard(),
            parse_mode='Markdown'
        )
        return

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📱 Get Number (Afghanistan)')
    btn2 = types.KeyboardButton('🇪🇬 Get Number (Egypt)')
    btn3 = types.KeyboardButton('📞 My Numbers')
    btn4 = types.KeyboardButton('💳 My Balance')
    markup.add(btn1, btn2, btn3, btn4)
    bot.reply_to(message, "خوش آمدید! یو انتخاب وکړئ:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "✅ مننه! تاسو ټول کانالونه جوین کړل.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ تاسو لا هم ټول کانالونه نه دي جوین کړي.", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_membership(user_id):
        bot.reply_to(
            message, 
            "⚠️ **تاسو باید لومړی لاندې ۴ کانالونه جوین کړئ:**",
            reply_markup=get_join_keyboard(),
            parse_mode='Markdown'
        )
        return

    if 'Get Number' in message.text:
        bot.reply_to(message, "⏳ د مجازي شمېرې په لټه کې...")
        try:
            response = requests.get("https://onlinesim.io/api/getFreeList?country=7&lang=en")
            data = response.json()
            if data and 'numbers' in data:
                number = data['numbers'][0]['number']
                bot.reply_to(message, f"✅ ستاسو مجازي شمېره: `{number}`\n\nدا شمېره د OTP کوډ ترلاسه کولو لپاره وکاروئ.", parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ اوس مهال شمېره پیدا نشوه.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ خطا: {str(e)}")

    elif 'My Balance' in message.text:
        bot.reply_to(message, "💰 ستاسو بیلانس: $0.00")

# =======================================================
# د Render Web Service لپاره د پورټ غوښتنې پوره کولو فنکشن
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), BaseHTTPRequestHandler)
    server.serve_forever()

# دا فنکشن باید د bot.polling() څخه مخکې چل شي
threading.Thread(target=run_dummy_server, daemon=True).start()
# =======================================================

print("🤖 روباټ پیل شو...")
bot.infinity_polling()
