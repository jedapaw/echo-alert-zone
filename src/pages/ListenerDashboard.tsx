import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { AlertCircle, Volume2, MessageSquare, Send } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const ListenerDashboard = () => {
  const [language, setLanguage] = useState('english');
  const [announcement, setAnnouncement] = useState<any>(null);
  const [translatedText, setTranslatedText] = useState('');
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);

  useEffect(() => {
    // Load latest announcement from localStorage
    const stored = localStorage.getItem('latestAnnouncement');
    if (stored) {
      const announcementData = JSON.parse(stored);
      setAnnouncement(announcementData);
      
      // Simulate auto-play audio
      setTimeout(() => {
        console.log('Auto-playing announcement audio...');
      }, 500);
    }
  }, []);

  const handleTranslate = () => {
    // Simulate translation
    const translations: Record<string, string> = {
      english: announcement?.message || 'No announcement available',
      hindi: 'आपातकालीन घोषणा: कृपया निकटतम बाहर निकलने की ओर व्यवस्थित तरीके से आगे बढ़ें।',
      tamil: 'அவசர அறிவிப்பு: தயவுசெய்து அருகிலுள்ள வெளியேறும் இடத்திற்கு ஒழுங்காக செல்லவும்.',
      bengali: 'জরুরী ঘোষণা: অনুগ্রহ করে নিকটতম প্রস্থান পথে শৃঙ্খলিতভাবে এগিয়ে যান।',
      telugu: 'అత్యవసర ప్రకటన: దయచేసి సమీపంలోని నిష్క్రమణకు క్రమంగా వెళ్లండి.',
      marathi: 'आपत्कालीन घोषणा: कृपया जवळच्या बाहेर पडण्याच्या दिशेने व्यवस्थितपणे जा.',
    };
    
    setTranslatedText(translations[language] || announcement?.message);
  };

  const handleAskQuestion = () => {
    if (!question.trim()) return;

    // Add user question to chat
    setChatHistory([...chatHistory, { role: 'user', content: question }]);

    // Simulate AI response
    const responses: Record<string, string> = {
      'repeat in hindi': 'आपातकालीन घोषणा: कृपया निकटतम बाहर निकलने की ओर व्यवस्थित तरीके से आगे बढ़ें।',
      'where do i go': 'Please proceed to the nearest exit. Follow the illuminated green exit signs. Emergency personnel are stationed at all exits to assist you.',
      'what should i do': 'Remain calm and follow these steps: 1) Gather your belongings, 2) Proceed to the nearest exit, 3) Follow instructions from safety personnel, 4) Do not use elevators.',
      default: 'I understand your concern. The announcement indicates you should proceed to the nearest exit in an orderly manner. Emergency personnel are available to assist you. Is there anything specific you need help with?'
    };

    const responseKey = question.toLowerCase();
    const response = responses[responseKey] || responses.default;

    setTimeout(() => {
      setChatHistory(prev => [...prev, { role: 'assistant', content: response }]);
    }, 500);

    setQuestion('');
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto px-6 py-8">
        {announcement && (
          <div className="mb-6 bg-emergency text-emergency-foreground rounded-lg p-4 shadow-lg animate-in slide-in-from-top duration-500">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-6 w-6 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-bold text-sm">NEW ANNOUNCEMENT</p>
                <p className="text-sm opacity-90">Tap to view details and translate to your language</p>
              </div>
              <Badge variant="secondary" className="bg-emergency-foreground text-emergency">LIVE</Badge>
            </div>
          </div>
        )}

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Listener Dashboard</h1>
          <p className="text-muted-foreground">Receive and interact with announcements</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-emergency border-2 shadow-lg">
              <CardHeader className="bg-emergency text-emergency-foreground">
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-8 w-8" />
                  <div>
                    <CardTitle className="text-2xl">IMPORTANT ANNOUNCEMENT</CardTitle>
                    <CardDescription className="text-emergency-foreground/80">
                      {announcement && new Date(announcement.timestamp).toLocaleString()}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Badge variant="destructive" className="mt-1 bg-emergency text-emergency-foreground">NEW</Badge>
                    <p className="text-lg leading-relaxed">{announcement?.message}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Translation & Audio</CardTitle>
                <CardDescription>Translate and listen to the announcement in your preferred language</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Select your language</label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="hindi">Hindi (हिन्दी)</SelectItem>
                      <SelectItem value="tamil">Tamil (தமிழ்)</SelectItem>
                      <SelectItem value="bengali">Bengali (বাংলা)</SelectItem>
                      <SelectItem value="telugu">Telugu (తెలుగు)</SelectItem>
                      <SelectItem value="marathi">Marathi (मराठी)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  className="w-full" 
                  onClick={handleTranslate}
                  disabled={!announcement}
                >
                  <Volume2 className="mr-2 h-4 w-4" />
                  Translate & Play with Agora AI
                </Button>

                {translatedText && (
                  <Card className="bg-muted">
                    <CardContent className="pt-6">
                      <p className="text-base">{translatedText}</p>
                      <div className="mt-4 flex items-center gap-2">
                        <div className="flex-1 h-2 bg-background rounded-full overflow-hidden">
                          <div className="h-full w-1/3 bg-primary animate-pulse" />
                        </div>
                        <Volume2 className="h-4 w-4 text-primary" />
                      </div>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="h-full border-primary shadow-lg">
              <CardHeader className="bg-primary/5">
                <CardTitle className="flex items-center gap-2 text-primary">
                  <MessageSquare className="h-5 w-5" />
                  Interactive AI Assistant
                </CardTitle>
                <CardDescription>Ask questions about the announcement - powered by Agora AI</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-accent/20 border border-accent rounded-lg p-4 space-y-2">
                  <p className="text-sm font-medium text-foreground">Try asking:</p>
                  <div className="space-y-1">
                    <button 
                      onClick={() => setQuestion("Repeat in Hindi")}
                      className="block w-full text-left text-xs text-primary hover:underline"
                    >
                      💬 "Repeat in Hindi"
                    </button>
                    <button 
                      onClick={() => setQuestion("Where do I go?")}
                      className="block w-full text-left text-xs text-primary hover:underline"
                    >
                      📍 "Where do I go?"
                    </button>
                    <button 
                      onClick={() => setQuestion("What should I do?")}
                      className="block w-full text-left text-xs text-primary hover:underline"
                    >
                      ❓ "What should I do?"
                    </button>
                  </div>
                </div>

                <div className="space-y-3 min-h-64 max-h-96 overflow-y-auto">
                  {chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`rounded-lg px-4 py-2 max-w-[85%] ${
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <Input
                    placeholder="Ask a question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
                    disabled={!announcement}
                  />
                  <Button 
                    size="icon" 
                    onClick={handleAskQuestion}
                    disabled={!announcement || !question.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListenerDashboard;
