from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import aiohttp
from database import Database
from telegram import Bot
from telegram.error import TelegramError
import time

# --- API Imports ---
import google.generativeai as genai
import base64
from agora_token_builder import RtmTokenBuilder, RtcTokenBuilder

load_dotenv()

app = FastAPI(title="Emergency Broadcast System")

# --- Configure Gemini API ---
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=gemini_api_key)
    print("✅ Gemini AI initialized (for AI chat and Translation)")
except Exception as e:
    print(f"⚠️  Gemini AI not initialized: {e}")

# --- All Indian Languages (ISO 639-1 codes) ---
ALL_INDIAN_LANGUAGES = [
    'en', 'hi', 'bn', 'te', 'mr', 'ta', 'ur', 'gu', 'kn', 'or', 'pa', 
    'ml', 'as', 'mai', 'sa', 'ne', 'ks', 'sd', 'kok', 'mni', 'brx', 'doi', 'sat'
]

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

# Telegram bot instance
telegram_bot = None
try:
    telegram_bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    print("✅ Telegram bot initialized")
except Exception as e:
    print(f"⚠️  Telegram bot not initialized: {e}")

# --- AGORA CREDENTIALS & TOKEN SERVER ---
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")
AGORA_SERVER_USER_ID = os.getenv("AGORA_SERVER_USER_ID", "emergency_server")

@app.get("/api/token/rtm/{user_id}")
async def get_rtm_token(user_id: str):
    """Generates an RTM token for a user to log in."""
    if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
        raise HTTPException(status_code=500, detail="Agora RTM credentials not configured")
    
    try:
        expiration_time_in_seconds = 3600 * 24  # 24 hours
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expiration_time_in_seconds
        
        # Correct method signature for RTM token
        token = RtmTokenBuilder.buildToken(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            user_id,
            1,  # Role.Rtm_User
            privilege_expired_ts
        )
        
        return {"token": token, "user_id": user_id, "appId": AGORA_APP_ID}
    except Exception as e:
        print(f"❌ Error generating RTM token: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/token/rtc/{channel_name}/{user_id}")
async def get_rtc_token(channel_name: str, user_id: str):
    """Generates an RTC (voice/video) token for a user to join a channel."""
    if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE:
        raise HTTPException(status_code=500, detail="Agora RTC credentials not configured")
    
    try:
        expiration_time_in_seconds = 3600 * 24  # 24 hours
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expiration_time_in_seconds
        
        # Convert uid to integer
        try:
            uid_int = int(user_id)
        except ValueError:
            uid_int = 0  # Use 0 for string UIDs
        
        token = RtcTokenBuilder.buildTokenWithUid(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            channel_name,
            uid_int,
            1,  # Role.PUBLISHER
            privilege_expired_ts
        )
        
        return {"token": token, "user_id": user_id, "channel": channel_name, "appId": AGORA_APP_ID}
    except Exception as e:
        print(f"❌ Error generating RTC token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic models
class BroadcastMessage(BaseModel):
    message: str
    sourceLanguage: str
    location: Optional[str] = ""
    radius: Optional[int] = 5000
    emergency: Optional[bool] = False

class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"
    userId: Optional[str] = "anonymous"

class TelegramBroadcast(BaseModel):
    message: str
    emergency: Optional[bool] = False
    location: Optional[str] = ""

class TelegramSubscriber(BaseModel):
    userId: int
    username: Optional[str] = ""
    firstName: Optional[str] = ""
    language: Optional[str] = "en"

# --- Translation function using Gemini ---
async def translate_message_gemini(text: str, target_languages: List[str]) -> Dict[str, str]:
    """Translates text into multiple languages using Gemini in a single call."""
    translations = {}
    
    # Language name mapping for better translation accuracy
    lang_names = {
        'en': 'English', 'hi': 'Hindi', 'bn': 'Bengali', 'te': 'Telugu',
        'mr': 'Marathi', 'ta': 'Tamil', 'ur': 'Urdu', 'gu': 'Gujarati',
        'kn': 'Kannada', 'or': 'Odia', 'pa': 'Punjabi', 'ml': 'Malayalam',
        'as': 'Assamese', 'mai': 'Maithili', 'sa': 'Sanskrit', 'ne': 'Nepali',
        'ks': 'Kashmiri', 'sd': 'Sindhi', 'kok': 'Konkani', 'mni': 'Manipuri',
        'brx': 'Bodo', 'doi': 'Dogri', 'sat': 'Santali'
    }
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create a clear list of language requests
        lang_requests = []
        for code in target_languages:
            name = lang_names.get(code, code.upper())
            lang_requests.append(f'"{code}": "{name}"')
        
        lang_list = "{\n  " + ",\n  ".join(lang_requests) + "\n}"
        
        prompt = f"""You are a professional translation service. Translate this emergency message into multiple Indian languages.

**Original Message (English):**
{text}

**Required Translations:**
Translate the above message into the following languages. Provide ONLY valid JSON output with no additional text, explanations, or markdown formatting.

{lang_list}

**Output Format (JSON only):**
{{
  "en": "Test emergency announcement - please evacuate calmly",
  "hi": "परीक्षण आपातकालीन घोषणा - कृपया शांति से निकासी करें",
  "ta": "சோதனை அவசர அறிவிப்பு - தயவு செய்து அமைதியாக வெளியேறவும்"
}}

**Important Rules:**
1. Return ONLY the JSON object
2. No markdown code blocks
3. No explanations before or after
4. Translate accurately while preserving the urgent tone
5. Use native scripts for each language

JSON Output:"""
        
        response = await model.generate_content_async(prompt)
        json_text = response.text.strip()
        
        # Clean up any markdown formatting
        json_text = json_text.replace("```json", "").replace("```", "").strip()
        
        # Try to extract JSON if there's extra text
        if "{" in json_text and "}" in json_text:
            start = json_text.index("{")
            end = json_text.rindex("}") + 1
            json_text = json_text[start:end]
        
        print(f"🔍 Gemini response: {json_text[:200]}...")  # Debug log
        
        translations = json.loads(json_text)
        print(f"✅ Parsed {len(translations)} translations")
        
        # Fill in any missing languages with original text
        for lang in target_languages:
            if lang not in translations:
                print(f"⚠️  Missing translation for {lang}, using original")
                translations[lang] = text
                
        return translations
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"📄 Raw response: {json_text[:500]}")
        # Return original text for all languages as fallback
        return {lang: text for lang in target_languages}
    except Exception as e:
        print(f"❌ Gemini translation error: {e}")
        import traceback
        traceback.print_exc()
        return {lang: text for lang in target_languages}

# --- AI Response function ---
async def get_ai_response(message: str, language: str = 'en') -> str:
    """Get contextual AI response from Gemini"""
    message_lower = message.lower()
    
    # Check for fallback responses first
    EMERGENCY_RESPONSES = {
        'exit': {
            'en': "🚪 Nearest exit: Gate 2 (50m to your right). Follow the GREEN emergency signs.",
            'hi': "🚪 निकटतम निकास: गेट 2 (आपके दाईं ओर 50 मीटर)। हरे आपातकालीन संकेतों का पालन करें।"
        },
        'safe': {
            'en': "🛡️ Safe zone: Main courtyard (100m north). Gather there and await instructions.",
            'hi': "🛡️ सुरक्षित क्षेत्र: मुख्य प्रांगण (100 मीटर उत्तर)। वहां इकट्ठा हों और निर्देशों का इंतजार करें।"
        },
        'help': {
            'en': "🆘 Emergency services notified. Stay calm. Share your location if you need immediate help.",
            'hi': "🆘 आपातकालीन सेवाओं को सूचित कर दिया गया है। शांत रहें।"
        },
        'water': {
            'en': "💧 Water stations: South entrance, Medical station (Gate 2), Main gate reception.",
            'hi': "💧 जल केंद्र: दक्षिण प्रवेश द्वार, चिकित्सा केंद्र (गेट 2), मुख्य द्वार।"
        },
        'medical': {
            'en': "🏥 First aid: Gate 2 medical station. For emergencies: Dial 112",
            'hi': "🏥 प्राथमिक चिकित्सा: गेट 2। आपात स्थिति: 112 डायल करें।"
        },
        'fire': {
            'en': "🔥 FIRE: Use North & South exits. Stay LOW, cover mouth, NO elevators!",
            'hi': "🔥 आग: उत्तर और दक्षिण गेट से बाहर निकलें। नीचे रहें, मुंह ढकें!"
        }
    }
    
    for keyword, responses in EMERGENCY_RESPONSES.items():
        if keyword in message_lower:
            return responses.get(language, responses['en'])

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are an emergency response assistant for a large public event.
A user, whose preferred language is {language}, has sent: "{message}"
Provide a clear, concise response in {language}.
Keep it short like a text message.

Context:
- Exits: Gate 1 (North), Gate 2 (Main, East), South Emergency Exit
- Safe Zones: Main Courtyard (North), Sports Field (West)
- Medical: Gate 2 Medical Station
- Water: South Entrance, Main Gate
- Emergency Number: 112
Response:"""
        
        response = await model.generate_content_async(prompt)
        ai_text = response.text.strip()
        
        if not ai_text or "I am not able" in ai_text:
            return EMERGENCY_RESPONSES['help'].get(language, EMERGENCY_RESPONSES['help']['en'])
            
        return ai_text

    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        return EMERGENCY_RESPONSES['help'].get(language, EMERGENCY_RESPONSES['help']['en'])

# API Routes
@app.get("/")
async def root():
    subscriber_count = db.get_subscriber_count()
    return {
        "service": "Emergency Broadcast System",
        "status": "running",
        "version": "1.0.0",
        "telegram_subscribers": subscriber_count,
        "agora_configured": bool(AGORA_APP_ID and AGORA_APP_CERTIFICATE),
        "endpoints": {
            "agora_rtm_token": "/api/token/rtm/{user_id}",
            "agora_rtc_token": "/api/token/rtc/{channel_name}/{user_id}",
            "broadcast": "POST /api/broadcasts",
            "ai_chat": "POST /api/ai-chat"
        }
    }

@app.get("/api/health")
async def health_check():
    analytics = db.get_analytics()
    return {
        "status": "healthy",
        "telegram_subscribers": analytics.get('telegramSubscribers', 0),
        "agora_configured": bool(AGORA_APP_ID and AGORA_APP_CERTIFICATE)
    }

@app.post("/api/broadcasts")
async def create_broadcast(broadcast: BroadcastMessage):
    """Create and send a broadcast via Agora RTM REST API"""
    if not AGORA_APP_ID or not AGORA_APP_CERTIFICATE or not AGORA_SERVER_USER_ID:
        raise HTTPException(status_code=500, detail="Agora RTM credentials not configured")
        
    try:
        # 1. Translate message using Gemini
        print(f"📝 Translating message: {broadcast.message}")
        translations = await translate_message_gemini(broadcast.message, ALL_INDIAN_LANGUAGES)
        print(f"✅ Translated to {len(translations)} languages")
        
        # 2. Save to database
        broadcast_data = {**broadcast.dict(), 'translations': translations}
        broadcast_id = db.add_broadcast(broadcast_data)
        print(f"💾 Saved to database with ID: {broadcast_id}")
        
        # 3. Generate RTM token for server - FIXED VERSION
        current_timestamp = int(time.time())
        expiration_time_in_seconds = 3600
        privilege_expired_ts = current_timestamp + expiration_time_in_seconds
        
        # Use the correct method signature with all required parameters
        rtm_token = RtmTokenBuilder.buildToken(
            AGORA_APP_ID,
            AGORA_APP_CERTIFICATE,
            AGORA_SERVER_USER_ID,
            1,  # Role.Rtm_User
            privilege_expired_ts
        )
        print(f"🔑 Generated RTM token for server")

        # 4. Prepare broadcast
        broadcast_channel = "EMERGENCY_ALERTS"
        url = f"https://api.agora.io/dev/v2/project/{AGORA_APP_ID}/rtm/users/{AGORA_SERVER_USER_ID}/channel_messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-agora-token": rtm_token,
            "x-agora-uid": AGORA_SERVER_USER_ID
        }
        
        payload = {
            "channel_name": broadcast_channel,
            "payload": json.dumps({ 
                'type': 'broadcast',
                'data': {
                    'id': broadcast_id,
                    'message': broadcast.message,
                    'translations': translations,
                    'location': broadcast.location,
                    'emergency': broadcast.emergency,
                    'timestamp': datetime.now().isoformat()
                }
            }),
            "enable_historical_messaging": True
        }

        print(f"📡 Sending to Agora RTM channel: {broadcast_channel}")

        # 5. Send to Agora
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    response_text = await response.text()
                    print(f"❌ Agora RTM broadcast failed: {response.status} {response_text}")
                    raise HTTPException(status_code=500, detail=f"Agora RTM failed: {response_text}")
        
        print(f"📢 Broadcast sent successfully to Agora RTM!")
        db.update_broadcast_delivery(broadcast_id, 1)

        return {
            'success': True,
            'broadcastId': broadcast_id,
            'deliveredCount': 1, 
            'translations': translations,
            'platform': 'agora_rtm'
        }
    
    except Exception as e:
        print(f"❌ Broadcast error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/telegram/broadcast")
async def telegram_broadcast(broadcast: TelegramBroadcast):
    """Send broadcast via Telegram"""
    if not telegram_bot:
        raise HTTPException(status_code=503, detail="Telegram bot not configured")
    
    try:
        subscribers = db.get_telegram_subscribers()
        if not subscribers:
            return {'success': False, 'message': 'No subscribers', 'deliveredCount': 0}
        
        emoji = "🚨" if broadcast.emergency else "📢"
        title = "EMERGENCY ALERT" if broadcast.emergency else "Broadcast Message"
        message = f"{emoji} **{title}**\n\n{broadcast.message}"
        if broadcast.location:
            message += f"\n\n📍 {broadcast.location}"
        message += f"\n\n⏰ {datetime.now().strftime('%I:%M %p, %d %b %Y')}"
        
        success_count = 0
        failed_count = 0
        
        for user_id in subscribers:
            try:
                await telegram_bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
                success_count += 1
                await asyncio.sleep(0.05)
            except TelegramError as e:
                failed_count += 1
                print(f"Failed to send to {user_id}: {e}")
        
        broadcast_data = {
            'message': broadcast.message,
            'sourceLanguage': 'en',
            'location': broadcast.location,
            'emergency': broadcast.emergency
        }
        broadcast_id = db.add_broadcast(broadcast_data)
        db.update_broadcast_delivery(broadcast_id, success_count)
        
        print(f"📱 Telegram: {success_count} sent, {failed_count} failed")
        
        return {
            'success': True,
            'broadcastId': broadcast_id,
            'deliveredCount': success_count,
            'failedCount': failed_count,
            'platform': 'telegram'
        }
    except Exception as e:
        print(f"❌ Telegram broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/telegram/subscribe")
async def subscribe_telegram_user(subscriber: TelegramSubscriber):
    """Add Telegram subscriber"""
    try:
        db.add_telegram_subscriber(
            user_id=subscriber.userId,
            username=subscriber.username,
            first_name=subscriber.firstName,
            language=subscriber.language
        )
        print(f"✅ Subscribed: {subscriber.userId}")
        return {'success': True, 'userId': subscriber.userId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-chat")
async def ai_chat(chat: ChatMessage):
    """AI-powered chat endpoint"""
    try:
        response = await get_ai_response(chat.message, chat.language)
        db.add_message(chat.userId, chat.message, response, chat.language)
        return {'success': True, 'response': response, 'language': chat.language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/broadcasts")
async def get_broadcasts(limit: int = 50):
    broadcasts = db.get_broadcasts(limit)
    return {'success': True, 'broadcasts': broadcasts}

@app.get("/api/analytics")
async def get_analytics():
    analytics = db.get_analytics()
    return {'success': True, 'data': analytics}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    print(f"\n🚀 Starting Emergency Broadcast System on port {port}")
    print(f"📊 API Docs: http://localhost:{port}/docs")
    print(f"💬 Telegram subscribers: {db.get_subscriber_count()}")
    print(f"📡 Agora RTM: {'✅ Enabled' if AGORA_APP_ID else '⚠️  Not configured'}")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
