import telebot
from telebot import types
import random
import database as db

# ----------------- تنظیمات -----------------
BOT_TOKEN = '9295424680:AAFxP-EV5lokJM7HCHOalFTFGlLiPN1_xCY'
ADMIN_ID = 123456789  # ⚠️ خپل ټیلیګرام ID دلته ولیکئ (د @userinfobot څخه یې واخلئ)
OTP_GROUP = '@freecash1F' # ⚠️ ډاډه اوسئ چې روباټ دلته اډمین دی
CHANNELS = ['@investmentpnl', '@pay_star1', '@Ahmadullah_Tech', '@Airdrops_io_3']

bot = telebot.TeleBot(BOT_TOKEN)
db.init_db()

# د هیوادونو لیست او د هغوی د شمېرو اصلي فارمټ
COUNTRIES = {
    "af": {"name": "افغانستان 🇦🇫", "code": "+93", "prefixes": ["70", "72", "74", "76", "77", "78", "79"], "length": 9},
    "pk": {"name": "پاکستان 🇵🇰", "code": "+92", "prefixes": ["300", "301", "321", "333", "345"], "length": 10},
    "eg": {"name": "مصر 🇪🇬", "code": "+20", "prefixes": ["10", "11", "12", "15"], "length": 10},
    "us": {"name": "امریکا 🇺🇸", "code": "+1", "prefixes": ["212", "310", "415", "786"], "length": 10},
    "uk": {"name": "برتانیه 🇬🇧", "code": "+44", "prefixes": ["74", "75", "77", "79"], "length": 10},
    "in": {"name": "هند 🇮🇳", "code": "+91", "prefixes": ["98", "99", "70", "88"], "length": 10}
}

# د ریښتینو شمېرو جوړول (د هیواد د اصلي فارمټ سره سم)
def generate_fake_numbers(country_code):
    nums = []
    country_data = COUNTRIES.get(country_code)
    if not country_data:
        return nums

    for _ in range(4):
        prefix = random.choice(country_data["prefixes"])
        # د پاتې عددونو شمېر محاسبه کول
        remaining_length = country_data["length"] - len(prefix)
        # تصادفي عددونه جوړول
        random_digits = ''.join(random.choices("0123456789", k=remaining_length))
        
        # بشپړه شمېره جوړول
        full_number = f"{country_data['code']} {prefix}{random_digits}"
        nums.append(full_number)
        
    return nums

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

def get_join_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, channel in enumerate(CHANNELS, 1):
        markup.add(types.InlineKeyboardButton(f"📢 کانال {i} ته ننوځه", url=f"https://t.me/{channel.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("✅ ما جوین کړل (چک کړه)", callback_data="check_join"))
    return markup

# ----------------- اصلي مینو -----------------
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('📱 Get Number'),
        types.KeyboardButton('🔗 Referral'),
        types.KeyboardButton('💰 My Balance'),
        types.KeyboardButton('💸 Withdraw')
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # د ریفرال لینک چک کول
    referrer_id = None
    if len(args) > 1 and args[1].startswith('ref'):
        referrer_id = int(args[1].replace('ref', ''))
        if referrer_id == user_id:
            referrer_id = None 
    
    db.add_user(user_id, referrer_id)

    if not check_membership(user_id):
        bot.send_message(message.chat.id, "⚠️ لومړی لاندې کانالونه جوین کړئ:", reply_markup=get_join_keyboard())
        return

    bot.send_message(message.chat.id, "👋 خوش آمدید! یو انتخاب وکړئ:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def cb_check_join(call):
    if check_membership(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ مننه! یو انتخاب وکړئ:", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ لا هم ټول کانالونه نه دي جوین شوي.", show_alert=True)

# ----------------- Get Number -----------------
@bot.message_handler(func=lambda m: m.text == '📱 Get Number')
def get_number_service(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 WhatsApp", callback_data="service_whatsapp"))
    bot.send_message(message.chat.id, "یو خدمت انتخاب کړئ:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "service_whatsapp")
def show_countries(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(data["name"], callback_data=f"country_{code}") for code, data in COUNTRIES.items()]
    markup.add(*btns)
    bot.edit_message_text("یو هیواد انتخاب کړئ:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def show_numbers(call):
    country_code = call.data.split("_")[1]
    country_name = COUNTRIES[country_code]["name"]
    numbers = generate_fake_numbers(country_code)
    
    text = f"📱 ستاسو لپاره د {country_name} شمېرې:\n\n"
    for i, num in enumerate(numbers, 1):
        text += f"{i}. `{num}`\n"
    
    text += "\n👇 یو شمېره کاپي کړئ او د WhatsApp لپاره یې وکاروئ، بیا لاندې تڼۍ کېکاږئ:"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔄 Change Number", callback_data=f"changenum_{country_code}"),
        types.InlineKeyboardButton("🌍 Change Country", callback_data="service_whatsapp"),
        types.InlineKeyboardButton("📢 OTP Group (Send to Group)", callback_data=f"otpgroup_{country_code}")
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("changenum_"))
def change_number(call):
    country_code = call.data.split("_")[1]
    country_name = COUNTRIES[country_code]["name"]
    numbers = generate_fake_numbers(country_code)
    
    text = f"📱 نوي شمېرې د {country_name}:\n\n"
    for i, num in enumerate(numbers, 1):
        text += f"{i}. `{num}`\n"
    text += "\n👇 یو شمېره کاپي کړئ:"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔄 Change Number", callback_data=f"changenum_{country_code}"),
        types.InlineKeyboardButton("🌍 Change Country", callback_data="service_whatsapp"),
        types.InlineKeyboardButton("📢 OTP Group (Send to Group)", callback_data=f"otpgroup_{country_code}")
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("otpgroup_"))
def send_to_otp_group(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    country_code = call.data.split("_")[1]
    country_name = COUNTRIES[country_code]["name"]
    
    # ۱. لیږل ګروپ ته
    try:
        bot.send_message(OTP_GROUP, f"🔔 نوی غوښتنه!\nکارونکی: {user_name} (ID: `{user_id}`)\nغواړي د {country_name} لپاره شمېره واخلي.", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ په ګروپ کې خطا: ډاډه اوسئ روباټ اډمین دی.\n{e}")

    # ۲. د بیلانس ورکول (د ازموینې لپاره فرض کوو چې کوډ راغی)
    if db.check_bonus_status(user_id) == 0:
        db.update_balance(user_id, 0.001) # خپله یې فعاله کړه
        db.mark_bonus_received(user_id)
        
        # د ریفرال انعام
        referrer_id = db.get_referrer(user_id)
        if referrer_id:
            db.update_balance(referrer_id, 0.0001)
            try:
                bot.send_message(referrer_id, f"🎉 یو ملګري ستاسو په لینک شمېره فعاله کړه! تاسو ته $0.0001 ورزیات شول.")
            except: pass

        bot.edit_message_text("✅ شمېره ګروپ ته ولېږل شوه!\nستاسو بیلانس ته $0.001 ورزیات شو.", call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text("✅ شمېره ګروپ ته ولېږل شوه!\n(تاسو دمخه خپل یو ځل انعام اخیستی دی)", call.message.chat.id, call.message.message_id)


# ----------------- نور بټنونه -----------------
@bot.message_handler(func=lambda m: m.text == '💰 My Balance')
def my_balance(message):
    bal = db.get_balance(message.from_user.id)
    bot.reply_to(message, f"💰 ستاسو بیلانس: **${bal:.4f}**", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '🔗 Referral')
def referral(message):
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref{message.from_user.id}"
    text = f"🔗 ستاسو د ریفرال لینک:\n\n`{link}`\n\nهر کله چې یو څوک ستاسو په لینک راشي او شمېره فعاله کړي، تاسو ته $0.0001 ورکول کیږي."
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == '💸 Withdraw')
def withdraw(message):
    user_id = message.from_user.id
    bal = db.get_balance(user_id)
    
    if bal >= 0.5:
        db.reset_balance(user_id) # بیلانس زیرو کول
        bot.reply_to(message, "✅ ستاسو د ایستلو غوښتنه ومنل شوه! کله چې تادیه وشوه تاسو ته به خبر درکړل شي.")
        bot.send_message(ADMIN_ID, f"🚨 د پیسو ایستلو غوښتنه!\nکارونکی: {message.from_user.first_name}\nID: `{user_id}`\nمقدار: $0.5", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"❌ ستاسو بیلانس ${bal:.4f} دی.\nد پیسو ایستلو لپاره باید لږ تر لږه **$0.5** ولرئ.")

# =======================================================
# د Render Web Service لپاره (که په Render کې یې چلوئ)
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), BaseHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()
# =======================================================

print("Bot is running...")
bot.infinity_polling()
