import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
from dotenv import load_dotenv
import requests
import asyncio

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3001')

# Store user languages (as a local cache)
user_languages = {}

# Emergency context responses
EMERGENCY_RESPONSES = {
    'en': {
        'welcome': """👋 Welcome to Emergency Alert System!

You are now subscribed to emergency broadcasts.

🚨 You'll receive instant alerts during emergencies
💬 Ask me questions anytime
🌍 Choose your preferred language

Type /help to see available commands.""",
        'help': """📋 Available Commands:

/start - Subscribe to alerts
/help - Show this help message
/language - Change language
/status - Check system status
/location - Find safe zones & exits

💬 Just send a message to ask:
• "Where is the exit?"
• "Safe zone location?"
• "I need water"
• "Medical emergency"

You can also just type in your own language (like Bengali, Marathi, etc.) and I will do my best to understand!

🚨 You'll automatically receive all emergency broadcasts!""",
        'subscribed': "✅ You're subscribed! You'll receive emergency alerts instantly.",
        'status_checking': "Checking system status...",
        'language_prompt': "🌍 Select your preferred language:"
    },
    'hi': {
        'welcome': """👋 आपातकालीन अलर्ट सिस्टम में आपका स्वागत है!

आप अब आपातकालीन प्रसारण के लिए सदस्यता ले चुके हैं।

🚨 आपातकाल के दौरान आपको तुरंत अलर्ट मिलेंगे
💬 कभी भी मुझसे सवाल पूछें
🌍 अपनी पसंदीदा भाषा चुनें

उपलब्ध कमांड देखने के लिए /help टाइप करें।""",
        'help': """📋 उपलब्ध कमांड:

/start - अलर्ट के लिए सदस्यता लें
/help - यह मदद संदेश दिखाएं
/language - भाषा बदलें
/status - सिस्टम स्थिति जांचें
/location - सुरक्षित क्षेत्र और निकास खोजें

💬 बस एक संदेश भेजें:
• "निकास कहाँ है?"
• "सुरक्षित क्षेत्र का स्थान?"
• "मुझे पानी चाहिए"
• "चिकित्सा आपातकाल"

आप अपनी भाषा (जैसे बंगाली, मराठी, आदि) में भी टाइप कर सकते हैं और मैं समझने की पूरी कोशिश करूँगा!

🚨 आपको सभी आपातकालीन प्रसारण स्वचालित रूप से मिलेंगे!""",
        'subscribed': "✅ आप सब्सक्राइब हो गए हैं! आपको आपातकालीन अलर्ट तुरंत मिलेंगे।",
        'status_checking': "सिस्टम स्थिति जांच रहे हैं...",
        'language_prompt': "🌍 अपनी पसंदीदा भाषा चुनें:"
    }
}

def get_text(user_id: int, key: str) -> str:
    """Get text in user's preferred language"""
    lang = user_languages.get(user_id, 'en')
    return EMERGENCY_RESPONSES.get(lang, EMERGENCY_RESPONSES['en']).get(key, '')

# --- UPDATED FUNCTION (from previous fix) ---
async def subscribe_user(user_id: int, username: str, first_name: str, language: str = 'en'):
    """Subscribe user to backend by calling the API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/telegram/subscribe",
            json={
                "userId": user_id,
                "username": username or "",
                "firstName": first_name or "",
                "language": language
            },
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"User subscribed/updated: {user_id} - {first_name} ({language})")
            return True
        else:
            logger.error(f"Failed to subscribe user {user_id}. Status: {response.status_code}, Body: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to subscribe user {user_id}: {e}")
        return False

async def get_ai_response(message: str, user_id: int) -> str:
    """Get AI response from backend"""
    try:
        lang = user_languages.get(user_id, 'en')
        response = requests.post(
            f"{BACKEND_URL}/api/ai-chat",
            json={
                "message": message,
                "language": lang,
                "userId": str(user_id)
            },
            timeout=10 # Increased timeout for Gemini
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'Sorry, I could not process that.')
        else:
            logger.error(f"AI response error, status {response.status_code}: {response.text}")
            return get_fallback_response(message, lang)
    
    except Exception as e:
        logger.error(f"AI response error: {e}")
        return get_fallback_response(message, user_languages.get(user_id, 'en'))

def get_fallback_response(message: str, language: str = 'en') -> str:
    """Fallback responses when backend is unavailable"""
    message_lower = message.lower()
    
    fallbacks = {
        'en': {
            'exit': "🚪 Nearest exit: Gate 2 (50m to your right). Follow GREEN emergency signs.",
            'safe': "🛡️ Safe zone: Main courtyard (100m north). Gather there for instructions.",
            'water': "💧 Water stations: South entrance, Medical station, Main gate.",
            'medical': "🏥 First aid at Gate 2. Emergency: Dial 112",
            'help': "🆘 Emergency services notified. Stay calm. Share your location if urgent.",
            'default': "I'm here to help! Ask about: exits, safe zones, water, medical help."
        },
        'hi': {
            'exit': "🚪 निकटतम निकास: गेट 2 (आपके दाईं ओर 50 मीटर)। हरे आपातकालीन संकेतों का पालन करें।",
            'safe': "🛡️ सुरक्षित क्षेत्र: मुख्य प्रांगण (100 मीटर उत्तर)। निर्देशों के लिए वहां इकट्ठा हों।",
            'water': "💧 जल केंद्र: दक्षिण प्रवेश द्वार, चिकित्सा केंद्र, मुख्य द्वार।",
            'medical': "🏥 गेट 2 पर प्राथमिक चिकित्सा। आपातकाल: 112 डायल करें",
            'help': "🆘 आपातकालीन सेवाओं को सूचित किया गया। शांत रहें। यदि जरूरी हो तो अपना स्थान साझा करें।",
            'default': "मैं मदद के लिए हूं! पूछें: निकास, सुरक्षित क्षेत्र, पानी, चिकित्सा सहायता।"
        }
    }
    
    lang_fallbacks = fallbacks.get(language, fallbacks['en'])
    
    for keyword in ['exit', 'safe', 'water', 'medical', 'help']:
        if keyword in message_lower:
            return lang_fallbacks.get(keyword, lang_fallbacks['default'])
    
    return lang_fallbacks['default']

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    lang = user_languages.get(user_id, 'en')
    
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
        lang = 'en'
    
    await subscribe_user(user_id, user.username, user.first_name, lang)
    await update.message.reply_text(get_text(user_id, 'welcome'))
    
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data='lang_hi')
        ],
        [
            InlineKeyboardButton("🇮🇳 தமிழ் (Tamil)", callback_data='lang_ta'),
            InlineKeyboardButton("🇮🇳 తెలుగు (Telugu)", callback_data='lang_te')
        ],
        [
            InlineKeyboardButton("🇮🇳 বাংলা (Bengali)", callback_data='lang_bn'),
            InlineKeyboardButton("🇮🇳 मराठी (Marathi)", callback_data='lang_mr')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(user_id, 'language_prompt'), reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    await update.message.reply_text(get_text(user_id, 'help'))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data='lang_hi')
        ],
        [
            InlineKeyboardButton("🇮🇳 தமிழ் (Tamil)", callback_data='lang_ta'),
            InlineKeyboardButton("🇮🇳 తెలుగు (Telugu)", callback_data='lang_te')
        ],
        [
            InlineKeyboardButton("🇮🇳 বাংলা (Bengali)", callback_data='lang_bn'),
            InlineKeyboardButton("🇮🇳 मराठी (Marathi)", callback_data='lang_mr')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 Select your preferred language:", reply_markup=reply_markup)

# --- UPDATED: /status command ---
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check system status"""
    user_id = update.effective_user.id
    status_msg = await update.message.reply_text(get_text(user_id, 'status_checking'))
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Updated status text to remove listener/operator counts
            status_text = f"""✅ **System Status: Online**

💬 Telegram Subscribers: {data.get('telegram_subscribers', 0)}
📡 Agora RTM: Enabled

🟢 All systems operational"""
            await status_msg.edit_text(status_text, parse_mode='Markdown')
        else:
            await status_msg.edit_text("⚠️ System status unknown")
    except:
        await status_msg.edit_text("❌ Cannot reach backend server. Emergency protocols active.")

async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show location info"""
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, 'en')
    
    if lang == 'hi':
        location_info = """📍 **स्थान की जानकारी**

🚪 **निकास:**
• गेट 2 - मुख्य निकास (पूर्व)
• गेट 1 - उत्तरी निकास
• दक्षिणी आपातकालीन निकास

🛡️ **सुरक्षित क्षेत्र:**
• मुख्य प्रांगण (100 मीटर उत्तर)
• खेल का मैदान (पश्चिम)

🏥 **चिकित्सा सहायता:**
• गेट 2 चिकित्सा केंद्र
• आपातकाल: 112 या 102

💧 **पानी/सुविधाएं:**
• दक्षिण प्रवेश द्वार
• मुख्य द्वार रिसेप्शन"""
    else:
        location_info = """📍 **Location Information**

🚪 **Exits:**
• Gate 2 - Main exit (East side)
• Gate 1 - North exit
• South emergency exit

🛡️ **Safe Zones:**
• Main courtyard (100m north)
• Sports field (West side)

🏥 **Medical Help:**
• Gate 2 Medical Station
• Emergency: 112 or 102

💧 **Water/Facilities:**
• South entrance
• Main gate reception"""
    
    await update.message.reply_text(location_info, parse_mode='Markdown')

# --- UPDATED FUNCTION (from previous fix) ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    if query.data.startswith('lang_'):
        lang_code = query.data.split('_')[1]
        user_languages[user_id] = lang_code
        
        # --- ADDED: Save language preference to DB ---
        await subscribe_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            language=lang_code
        )
        
        lang_names = {
            'en': 'English 🇬🇧',
            'hi': 'हिन्दी 🇮🇳',
            'ta': 'தமிழ் 🇮🇳',
            'te': 'తెలుగు 🇮🇳',
            'bn': 'বাংলা 🇮🇳',
            'mr': 'मराठी 🇮🇳'
        }
        
        await query.edit_message_text(
            f"✅ Language set to {lang_names.get(lang_code, lang_code)}\n\n"
            f"You'll receive alerts in this language."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Message from {user_id}: {user_message}")
    
    await update.message.chat.send_action("typing")
    ai_response = await get_ai_response(user_message, user_id)
    await update.message.reply_text(ai_response)

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("\n❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("📝 Steps to fix:")
        print("   1. Open Telegram and search for @BotFather")
        print("   2. Send: /newbot")
        print("   3. Follow instructions to create your bot")
        print("   4. Copy the token to your .env file\n")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("location", location_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("\n" + "="*60)
    print("🤖 TELEGRAM BOT STARTED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📱 Bot is running and ready to receive messages")
    print(f"🔍 Search for your bot on Telegram and send /start")
    print(f"\n💡 Features enabled:")
    print(f"   ✅ Emergency broadcasts (via server)")
    print(f"   ✅ Real AI-powered responses (via Gemini on server)")
    print(f"   ✅ Multi-language support")
    print(f"   ✅ Location information")
    print(f"\n⏹️  Press Ctrl+C to stop the bot")
    print("="*60 + "\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
