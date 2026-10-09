from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from flask import Flask
import asyncio
import os
import threading

# ==========================================
# ENVIRONMENT VARIABLES (Render me daalna)
# ==========================================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ==========================================
# ⚙️ APNI DETAILS YAHAN SET KARO
# ==========================================
CHANNEL_USERNAME = "rovixbyultimate"      # Bina @ ke
CHANNEL_LINK = "https://t.me/rovixbyultimate"
SECRET_PASSWORD = "WELCOME@TO@CLN"

# ==========================================
# 🌍 MULTI-LANGUAGE MESSAGES
# ==========================================
LANG_MENU = """╔══════════════════════╗
   🌐  LANGUAGE SELECTION
╚══════════════════════╝

Welcome! Please select your preferred language.

━━━━━━━━━━━━━━━━━━━━━━
👇 **Tap a button below to continue**
━━━━━━━━━━━━━━━━━━━━━━"""

# Har language ke liye 3 messages: prompt, not_joined, password
MESSAGES = {
    "en": {
        "prompt": f"""👋 **Hello!**

To get the secret password, you need to join our official channel first.

🔗 {CHANNEL_LINK}

After joining, click the button below 👇""",
        "not_joined": "❌ You haven't joined the channel yet! Please join first.",
        "password": f"""🎉 **Welcome!**

✅ You are now verified!

🔐 **Your Secret Password:**
`{SECRET_PASSWORD}`

⚠️ Keep it safe. Do not share."""
    },
    "hi": {
        "prompt": f"""👋 **नमस्ते!**

गुप्त पासवर्ड पाने के लिए आपको पहले हमारे आधिकारिक चैनल से जुड़ना होगा।

🔗 {CHANNEL_LINK}

जुड़ने के बाद नीचे वाले बटन पर क्लिक करें 👇""",
        "not_joined": "❌ आपने अभी तक चैनल जॉइन नहीं किया है! कृपया पहले जॉइन करें।",
        "password": f"""🎉 **स्वागत है!**

✅ आप वेरिफाइड हो गए हैं!

🔐 **आपका सीक्रेट पासवर्ड:**
`{SECRET_PASSWORD}`

⚠️ इसे संभाल कर रखें। किसी को न दें।"""
    },
    "my": {
        "prompt": f"""👋 **မင်္ဂလာပါ!**

လျှို့ဝှက်စကားဝှက် ရရှိရန် ကျွန်ုပ်တို့၏ တရားဝင်ချန်နယ်သို့ ဦးစွာဝင်ရောက်ရန် လိုအပ်ပါသည်။

🔗 {CHANNEL_LINK}

ဝင်ရောက်ပြီးပါက အောက်ရှိခလုတ်ကို နှိပ်ပါ 👇""",
        "not_joined": "❌ သင်သည် ချန်နယ်သို့ မဝင်ရောက်ရသေးပါ။ ဦးစွာဝင်ရောက်ပါ။",
        "password": f"""🎉 **ကြိုဆိုပါတယ်!**

✅ အတည်ပြုပြီးပါပြီ!

🔐 **သင့်လျှို့ဝှက်စကားဝှက်:**
`{SECRET_PASSWORD}`

⚠️ လုံခြုံစွာ သိမ်းထားပါ။ မမျှဝေပါနှင့်။"""
    },
    "ar": {
        "prompt": f"""👋 **مرحباً!**

للحصول على كلمة المرور السرية، عليك الانضمام إلى قناتنا الرسمية أولاً.

🔗 {CHANNEL_LINK}

بعد الانضمام، اضغط على الزر أدناه 👇""",
        "not_joined": "❌ لم تنضم إلى القناة بعد! يرجى الانضمام أولاً.",
        "password": f"""🎉 **أهلاً بك!**

✅ تم التحقق منك!

🔐 **كلمة المرور السرية الخاصة بك:**
`{SECRET_PASSWORD}`

⚠️ احتفظ بها بأمان. لا تشاركها."""
    },
    "ur": {
        "prompt": f"""👋 **السلام علیکم!**

خفیہ پاس ورڈ حاصل کرنے کے لیے آپ کو پہلے ہمارے آفیشل چینل میں شامل ہونا ہوگا۔

🔗 {CHANNEL_LINK}

شامل ہونے کے بعد نیچے والے بٹن پر کلک کریں 👇""",
        "not_joined": "❌ آپ نے ابھی تک چینل جوائن نہیں کیا! پہلے جوائن کریں۔",
        "password": f"""🎉 **خوش آمدید!**

✅ آپ کی تصدیق ہو گئی ہے!

🔐 **آپ کا خفیہ پاس ورڈ:**
`{SECRET_PASSWORD}`

⚠️ اسے محفوظ رکھیں۔ کسی کو نہ بتائیں۔"""
    }
}

user_langs = {} # Language save karne ke liye

# ==========================================
# TELEGRAM CLIENT
# ==========================================
bot = TelegramClient('bot_session', API_ID, API_HASH)

# ==========================================
# 🔍 CHECK USER JOINED HAI YA NAHI
# ==========================================
async def is_user_joined(user_id):
    try:
        await bot(GetParticipantRequest(
            channel=CHANNEL_USERNAME,
            participant=user_id
        ))
        return True
    except UserNotParticipantError:
        return False
    except ChatAdminRequiredError:
        print("⚠️ Bot ko channel ka admin banao!")
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

# ==========================================
# 🎯 START COMMAND HANDLER
# ==========================================
@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    try:
        if not event.is_private:
            return

        user_id = event.sender_id

        # Agar language pehle se select nahi ki → Language Menu bhejo
        if user_id not in user_langs:
            buttons = [
                [Button.inline("🇬🇧 English", b"lang_en")],
                [Button.inline("🇮🇳 हिन्दी (Hindi)", b"lang_hi")],
                [Button.inline("🇲🇲 မြန်မာ (Burmese)", b"lang_my")],
                [Button.inline("🇸🇦 العربية (Arabic)", b"lang_ar")],
                [Button.inline("🇵🇰 اردو (Urdu)", b"lang_ur")],
            ]
            await event.reply(LANG_MENU, buttons=buttons)
            return

        # Agar language select kar li → Channel check karo
        lang = user_langs[user_id]
        joined = await is_user_joined(user_id)

        if joined:
            await event.reply(MESSAGES[lang]["password"])
        else:
            verify_buttons = [
                [Button.url("🔗 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")]
            ]
            await event.reply(MESSAGES[lang]["prompt"], buttons=verify_buttons)
    except Exception as e:
        print(f"⚠️ Start Error: {e}")

# ==========================================
# 🎯 LANGUAGE SELECTION HANDLER
# ==========================================
@bot.on(events.CallbackQuery(data=lambda d: d.startswith(b"lang_")))
async def lang_callback(event):
    try:
        lang = event.data.decode().replace("lang_", "")
        user_id = event.sender_id

        if lang not in MESSAGES:
            return

        user_langs[user_id] = lang
        await event.delete()

        # Language select hone ke baad turant channel check karo
        joined = await is_user_joined(user_id)

        if joined:
            await bot.send_message(event.chat_id, MESSAGES[lang]["password"])
        else:
            verify_buttons = [
                [Button.url("🔗 Join Channel", CHANNEL_LINK)],
                [Button.inline("✅ I've Joined", b"verify_join")]
            ]
            await bot.send_message(event.chat_id, MESSAGES[lang]["prompt"], buttons=verify_buttons)
    except Exception as e:
        print(f"⚠️ Lang Error: {e}")

# ==========================================
# 🎯 VERIFY JOIN BUTTON HANDLER
# ==========================================
@bot.on(events.CallbackQuery(data=b"verify_join"))
async def verify_handler(event):
    try:
        user_id = event.sender_id
        lang = user_langs.get(user_id, "en") # Default English agar language nahi mili

        joined = await is_user_joined(user_id)

        if joined:
            # ✅ Joined hai → Password do
            await event.edit(MESSAGES[lang]["password"])
        else:
            # ❌ Nahi joined → Alert dikhao
            await event.answer(MESSAGES[lang]["not_joined"], alert=True)
    except Exception as e:
        print(f"⚠️ Verify Error: {e}")

# ==========================================
# 🌐 WEB SERVER (Render ke liye)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# MAIN
# ==========================================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    print("=" * 55)
    print("✅ BOT RUNNING!")
    print(f"🤖 Bot: @{me.username}")
    print(f"🔗 Channel: {CHANNEL_USERNAME}")
    print("=" * 55)
    await bot.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    asyncio.run(main())
