import { Link } from 'react-router-dom';
import Navigation from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Radio, 
  Globe, 
  MessageSquare, 
  Mic, 
  Languages, 
  AlertCircle,
  Users,
  User,
  Sparkles,
  CheckCircle,
  Headphones
} from 'lucide-react';
import heroImage from '@/assets/hero-communication.jpg';

const Index = () => {
  const features = [
    {
      icon: Globe,
      title: 'Inclusive Communication',
      description: 'Reach everyone regardless of language barriers with real-time translation'
    },
    {
      icon: Headphones,
      title: 'Accessibility First',
      description: 'Support for hearing-impaired users with visual alerts and text display'
    },
    {
      icon: Languages,
      title: 'Multi-Language Support',
      description: 'Automatic translation to Hindi, Tamil, Bengali, Telugu, Marathi and more'
    },
    {
      icon: AlertCircle,
      title: 'Emergency Ready',
      description: 'Critical alerts delivered instantly with prioritized broadcasting'
    }
  ];

  const howItWorks = [
    {
      step: 1,
      icon: Mic,
      title: 'Operator Broadcasts',
      description: 'Operator speaks or types a message in any supported language'
    },
    {
      step: 2,
      icon: Sparkles,
      title: 'AI Multilingual Delivery',
      description: 'Agora Conversational AI transcribes, translates, and generates TTS audio instantly'
    },
    {
      step: 3,
      icon: MessageSquare,
      title: 'Interactive Assistant',
      description: 'Listeners receive alerts and can ask follow-up questions in their preferred language'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${heroImage})` }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20" />
        
        <div className="relative container mx-auto px-6 py-24 text-center">
          <div className="flex justify-center mb-6">
            <div className="rounded-full bg-primary/10 p-4">
              <Radio className="h-16 w-16 text-primary" />
            </div>
          </div>
          
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Echo
          </h1>
          <p className="text-2xl font-semibold text-foreground mb-4">
            The Interactive Public Announcement System
          </p>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            A real-time, multi-language, AI-powered platform that converts announcements into multiple languages, 
            delivers text and audio simultaneously, and enables interactive follow-up questions
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/operator">
              <Button size="lg" className="gap-2">
                <Users className="h-5 w-5" />
                Open Operator Dashboard
              </Button>
            </Link>
            <Link to="/listener">
              <Button size="lg" variant="secondary" className="gap-2">
                <User className="h-5 w-5" />
                Open Listener View
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How Echo Works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Three simple steps to broadcast multilingual announcements powered by Agora Conversational AI
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {howItWorks.map((item) => (
              <Card key={item.step} className="relative overflow-hidden">
                <div className="absolute top-0 right-0 text-9xl font-bold text-primary/5 -mr-4 -mt-4">
                  {item.step}
                </div>
                <CardHeader>
                  <div className="rounded-full bg-primary/10 w-14 h-14 flex items-center justify-center mb-4">
                    <item.icon className="h-7 w-7 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{item.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{item.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Why Echo Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Why Echo is Needed</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Breaking barriers and ensuring everyone receives critical information
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <Card key={idx} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="rounded-full bg-primary/10 w-14 h-14 flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="h-7 w-7 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Key Benefits Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6">One Message → Many Languages</h2>
              <p className="text-lg text-muted-foreground mb-8">
                Echo automatically translates and broadcasts announcements in multiple Indian languages, 
                ensuring no one is left behind in critical situations.
              </p>
              
              <div className="space-y-4">
                {[
                  'Real-time speech-to-text transcription',
                  'Instant translation to 6+ languages',
                  'Natural TTS audio generation',
                  'Context-aware interactive Q&A',
                  'Emergency alert prioritization'
                ].map((benefit, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle className="h-6 w-6 text-success flex-shrink-0 mt-0.5" />
                    <span className="text-foreground">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            <Card className="bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-6 w-6 text-primary" />
                  Powered by Agora Conversational AI
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  Echo leverages Agora's cutting-edge AI technology for:
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Speech-to-Text (STT) for real-time transcription</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Neural machine translation for accuracy</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Text-to-Speech (TTS) with natural voices</span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Conversational AI for interactive assistance</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary to-accent text-primary-foreground">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Experience Echo?</h2>
          <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
            Try the platform now and see how Echo can revolutionize public communication
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/operator">
              <Button size="lg" variant="secondary" className="gap-2">
                <Users className="h-5 w-5" />
                Try Operator Dashboard
              </Button>
            </Link>
            <Link to="/listener">
              <Button size="lg" variant="secondary" className="gap-2">
                <User className="h-5 w-5" />
                Try Listener Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
