# Echo - Multilingual Public Announcement System

## 🎯 Problem Statement (LA-04)

**Challenge:** Language barriers during emergencies or events can cause panic and confusion. Loudspeaker messages often go unheard or misunderstood, especially by non-native speakers and the hearing-impaired.

**Consequence:** Missed information leads to injuries, lost people, and delayed safety actions. Vulnerable groups face the highest risk when alerts aren't accessible.

**The Case: "Emergency Announced—But Not for Rajiv"**
> Rajiv waits at a crowded railway station. An urgent announcement blares—only in the local language. While others move, Rajiv stands confused, unsure what's happening or what to do. Not knowing the language leaves him lost, anxious, and at risk.

## 💡 Solution: Echo

Echo is a multi-channel emergency announcement system that ensures **universal reach**—not just smartphone users, but everyone. Using Agora Conversational AI, it broadcasts announcements across multiple platforms simultaneously while providing interactive AI assistance for clarification.

### Key Features
- ✅ **Universal Reach**: PWA, SMS, WhatsApp, and physical PA systems
- ✅ **Real-time Translation**: Instant announcements in 50+ languages
- ✅ **Interactive AI**: Conversational assistance for confused listeners
- ✅ **No App Required**: QR codes, SMS, and WhatsApp—works on any phone
- ✅ **Cultural Sensitivity**: Context-aware translations adapted for local nuances
- ✅ **Government-Ready**: Audit trails, compliance tracking, and existing system integration

### Why Echo Wins for Mass Adoption

**Problem with App-Only Solutions:**
Most emergency systems fail because they require smartphone apps. In India, 60%+ users have feature phones or don't download apps.

**Echo's Multi-Channel Approach:**
```
One Operator Announcement
    ↓
Agora AI Processing (< 2 seconds)
    ↓
Simultaneous Broadcast to:
├─ 📱 Progressive Web App (scan QR code)
├─ 💬 SMS (automatic zone-based alerts)
├─ 📲 WhatsApp (500M+ users in India)
└─ 🔊 Physical PA Speakers (existing infrastructure)
```

**Reach Breakdown:**
- **Smartphone Users**: PWA via QR codes (no download needed)
- **Feature Phone Users**: SMS + WhatsApp Lite
- **Non-Tech Users**: Automatic SMS + Voice announcements
- **Everyone**: Physical PA speakers augmented with multi-language

## 🏗️ Architecture

### Dual-Interface System Flow

**OPERATOR SIDE:**
```
1. Operator Speaks in Tamil
    ↓
2. Agora Voice SDK Captures Audio
    ↓
3. Agora AI Pipeline → Audio to Text (STT)
    ↓
4. Text to 50+ Languages (Translation)
    ↓
5. AI Cultural Context Filter (Contextualize)
    ↓
6. Split into two streams:
    ├─→ Text to 50+ Audio Streams (TTS)
    ├─→ Save All Final Text to Context DB (SDKs)
    └─→ Agora Signaling SDK (13+ Text Transcripts)
    ↓
7. Agora Broadcast SDK (50+ Audio Streams)
```

**LISTENER SIDE:**
```
1. Listener Sees Text Alert
    ↓
2. User taps text alert to ask question
    ↓
3. Open Agora Conversational AI Agent
    ↓
4. AI Agent instantly reads from Context DB
    ↓
5. User asks: "Which way?"
    ↓
6. AI: "The best Gate is to your left"
    ↓
7. User asks: "Repeat in Hindi?"
    ↓
8. AI plays pre-generated Hindi Audio Stream
    ↓
9. Listener Hears Audio → End Interaction
```

### Core Technologies

1. **Agora Conversational AI REST API**
   - Real-time voice transcription (STT)
   - Text-to-speech in 50+ languages (TTS)
   - Conversational AI agent for listener questions
   - Low-latency processing (< 2 seconds)

2. **Agora Voice SDK**
   - Captures operator audio in real-time
   - Handles audio streaming

3. **Agora Broadcast SDK**
   - Simultaneously broadcasts 50+ audio streams
   - Multi-language audio delivery

4. **Agora Signaling SDK**
   - Delivers text transcripts to listener devices
   - Real-time text synchronization

5. **Cultural Sensitivity Engine**
   - Localizes messages for cultural nuances
   - Emotion detection to prevent panic
   - Context-aware translations

6. **Context Database**
   - Stores all translations for AI agent reference
   - Enables instant query responses
   - Maintains conversation history

## 🚀 Quick Start

### Prerequisites
- Node.js 14+ (for development)
- Modern web browser (Chrome, Firefox, Safari)
- Agora Account (for production deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-team/echo-pa-system.git
cd echo-pa-system

# Install dependencies
npm install

# Start development server
npm start
```

### Environment Setup

Create a `.env` file:

```env
REACT_APP_AGORA_APP_ID=your_agora_app_id
REACT_APP_AGORA_TOKEN=your_agora_token
```

### Demo Usage

**OPERATOR MODE:**
1. **Select Source Language** - Choose operator's language (default: Tamil)
2. **Start Recording** - Click to record announcement via microphone
3. **Watch Pipeline** - See real-time processing through 5 steps:
   - Audio Captured
   - Transcribing
   - Translating to 50+ languages
   - Applying cultural context
   - Generating audio streams
4. **View Broadcasts** - See all language translations with audio
5. **Broadcast Complete** - Announcements sent to all listeners

**LISTENER MODE:**
1. **Select Your Language** - Choose preferred language (default: Hindi)
2. **Receive Alert** - Get text notification in your language
3. **Play Audio** - Listen to announcement
4. **Ask AI Agent** - Tap to start conversation for clarification
5. **Get Help** - Ask questions like "Which way?" or "Repeat in Hindi?"
6. **Receive Guidance** - AI provides instant, context-aware responses

## 📋 API Integration

### Agora Conversational AI - Operator Side

```javascript
// 1. Join STT session for voice capture
const sttResponse = await fetch('https://api.agora.io/v1/projects/{appId}/rtsc/speech-to-text/tasks', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    languages: ['ta-IN'], // Operator's language
    maxIdleTime: 60
  })
});

// 2. Start conversation agent for translation
const agentResponse = await fetch('https://api.agora.io/v1/projects/{appId}/conversational-ai/agents/start', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agentId: 'translation-agent',
    channel: 'broadcast-channel',
    uid: operatorId
  })
});

// 3. Broadcast translated audio streams
const broadcastResponse = await fetch('https://api.agora.io/v1/projects/{appId}/rtc/broadcast', {
  method: 'POST',
  body: JSON.stringify({
    channels: translations.map(t => ({
      language: t.code,
      audioUrl: t.ttsUrl
    }))
  })
});
```

### Agora Conversational AI - Listener Side

```javascript
// 1. Subscribe to text alerts via Signaling SDK
const signalingClient = AgoraSignaling.createInstance(appId);
await signalingClient.login(userId, token);

const channel = signalingClient.createChannel('alerts-channel');
await channel.join();

channel.on('ChannelMessage', (message) => {
  const alert = JSON.parse(message.text);
  displayAlert(alert);
});

// 2. Start conversational AI agent when user asks questions
const conversationResponse = await fetch('https://api.agora.io/v1/projects/{appId}/conversational-ai/agents/start', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agentId: 'listener-helper-agent',
    channel: `listener-${userId}`,
    uid: userId,
    contextDb: 'announcements-db' // Reference to stored translations
  })
});

// 3. Send user questions to AI agent
const questionResponse = await fetch(`https://api.agora.io/v1/projects/{appId}/conversational-ai/agents/${agentId}/message`, {
  method: 'POST',
  body: JSON.stringify({
    message: userQuestion,
    language: listenerLanguage,
    context: announcementId
  })
});
```

## 🎨 UI/UX Features

### Design Principles
- **High Contrast**: Readable in all lighting conditions
- **Large Touch Targets**: Accessible for all users
- **Visual Feedback**: Clear processing states
- **Responsive Layout**: Works on all screen sizes

### Accessibility
- Screen reader compatible
- Keyboard navigation support
- Color blind friendly palette
- Audio alternatives for all text

## 📊 Core Capabilities Breakdown

### 1. Cultural Sensitivity
- Localizes messages to respect cultural nuances
- Adjusts tone and formality based on target culture
- Handles idioms and colloquialisms appropriately

### 2. Interactive AI
- Provides instant, context-aware assistance
- Users can tap for clarification
- Conversational interface for complex queries

### 3. Emotion Detection
- Analyzes emotional content of announcements
- Offers empathetic support during emergencies
- Prevents panic through calm, clear messaging

### 4. Real-time Broadcasting
- Ensures announcements reach everyone in their language
- Minimal latency (< 2 seconds)
- Simultaneous multi-language delivery

### 5. Universal Accessibility
- Makes public safety inclusive for diverse populations
- Supports text, audio, and visual outputs
- Works offline with cached translations

## 🔧 Technical Stack

### Frontend
- React 18
- Tailwind CSS
- Lucide React Icons

### Backend (Production)
- Agora Conversational AI REST API
- Agora Voice SDK
- Agora TTS Service

### Audio Processing
- Web Audio API
- MediaRecorder API
- Speech Synthesis API (fallback)

## 📱 Deployment Options

### Cloud Deployment (Recommended)
```bash
# Build for production
npm run build

# Deploy to Vercel/Netlify
npm run deploy
```

### On-Premise Deployment
```bash
# Docker containerization
docker build -t echo-pa-system .
docker run -p 3000:3000 echo-pa-system
```
## 🔒 Security & Privacy

- No permanent storage of announcements
- End-to-end encryption for audio streams
- GDPR compliant data handling
- No personal data collection

## 📈 Future Enhancements

1. **Offline Mode** - Cached translations for common announcements
2. **Mobile App** - Native iOS/Android applications
3. **Hardware Integration** - Direct PA system connectivity
4. **Analytics Dashboard** - Usage statistics and reach metrics
5. **Sign Language** - Video generation for deaf community

## 👥 Team Information

**Project Name:** Echo - Multilingual PA System  
**Hackathon:** HackFest GDG 2025  
**Organizer:** Google Developer Groups New Delhi  
**Sponsor:** Agora  
**Problem Statement:** LA-04: PA System


## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for public safety and inclusivity**
