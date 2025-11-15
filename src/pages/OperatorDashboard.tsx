import { useState } from 'react';
import Navigation from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Slider } from '@/components/ui/slider';
import { Mic, Upload, Send, MapPin, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const OperatorDashboard = () => {
  const [language, setLanguage] = useState('english');
  const [message, setMessage] = useState('');
  const [radius, setRadius] = useState([5]);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const { toast } = useToast();

  const [broadcastStatus, setBroadcastStatus] = useState({
    listenersReached: 0,
    languagesDeployed: 0,
    deliveryConfirmation: 0
  });

  const predefinedMessages = {
    evacuation: 'Emergency evacuation order: Please proceed to the nearest exit in an orderly manner. Follow safety personnel instructions.',
    maintenance: 'Scheduled maintenance alert: Certain facilities will be unavailable from 2 PM to 4 PM today. We apologize for any inconvenience.',
    lostFound: 'Lost and found announcement: A child has been separated from their parents. Please report to the information desk if you can help.',
    safety: 'Safety instructions: In case of emergency, remain calm and follow the illuminated exit signs. Do not use elevators.'
  };

  const emergencyTemplates = {
    fire: 'FIRE EMERGENCY: Please evacuate the building immediately. Use the nearest stairwell. Do not use elevators. Proceed to the designated assembly point.',
    security: 'SECURITY ALERT: A security situation is in progress. Please remain calm and follow instructions from security personnel. Stay in your current location until further notice.',
    medical: 'MEDICAL EMERGENCY: Medical assistance is required. Please clear the area and allow emergency personnel to access. If you have medical training, please report to the information desk.'
  };

  const handleDeploy = () => {
    if (!message.trim()) {
      toast({
        title: "Error",
        description: "Please enter an announcement message",
        variant: "destructive",
      });
      return;
    }
    
    // Simulate broadcast with Agora
    const simulatedListeners = Math.floor(Math.random() * 500) + 100;
    const simulatedLanguages = Math.floor(Math.random() * 6) + 3;
    const simulatedConfirmation = Math.floor(Math.random() * 15) + 85;
    
    setBroadcastStatus({
      listenersReached: simulatedListeners,
      languagesDeployed: simulatedLanguages,
      deliveryConfirmation: simulatedConfirmation
    });
    
    setShowConfirmation(true);
    
    // Store announcement for listener dashboard
    localStorage.setItem('latestAnnouncement', JSON.stringify({
      message,
      timestamp: new Date().toISOString(),
      language
    }));
  };

  const handlePredefinedSelect = (value: string) => {
    setMessage(predefinedMessages[value as keyof typeof predefinedMessages] || '');
  };

  const handleEmergencyTemplate = (value: string) => {
    setMessage(emergencyTemplates[value as keyof typeof emergencyTemplates] || '');
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Operator Dashboard</h1>
          <p className="text-muted-foreground">Create and broadcast announcements to listeners</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Select Announcement Language</CardTitle>
                <CardDescription>Choose the language you'll speak or type in</CardDescription>
              </CardHeader>
              <CardContent>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="w-full">
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
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Emergency Templates</CardTitle>
                <CardDescription>Quick access to critical emergency messages</CardDescription>
              </CardHeader>
              <CardContent>
                <Select onValueChange={handleEmergencyTemplate}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select emergency template..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fire">Fire Emergency</SelectItem>
                    <SelectItem value="security">Security Threat</SelectItem>
                    <SelectItem value="medical">Medical Emergency</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Choose Announcement Mode</CardTitle>
                <CardDescription>Select how you want to create your announcement</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="text" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="text">Text Input</TabsTrigger>
                    <TabsTrigger value="audio">Audio Input</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="text" className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Enter your announcement</label>
                      <Textarea
                        placeholder="Type your announcement message here..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        className="min-h-32"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Or choose a pre-defined message</label>
                      <Select onValueChange={handlePredefinedSelect}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a template..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="evacuation">Emergency Evacuation</SelectItem>
                          <SelectItem value="maintenance">Maintenance Alert</SelectItem>
                          <SelectItem value="lostFound">Lost & Found</SelectItem>
                          <SelectItem value="safety">Safety Instructions</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <Button className="w-full">
                      <Mic className="mr-2 h-4 w-4" />
                      Generate Speech with Agora AI
                    </Button>
                  </TabsContent>
                  
                  <TabsContent value="audio" className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Select speaking language</label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose language..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="en">English</SelectItem>
                          <SelectItem value="hi">Hindi</SelectItem>
                          <SelectItem value="ta">Tamil</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="flex gap-3">
                      <Button className="flex-1">
                        <Mic className="mr-2 h-4 w-4" />
                        Record Audio
                      </Button>
                      <Button variant="secondary" className="flex-1">
                        <Upload className="mr-2 h-4 w-4" />
                        Upload File
                      </Button>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Broadcast Status</CardTitle>
                <CardDescription>Live deployment statistics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3">
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-sm text-muted-foreground">Listeners Reached</p>
                    <p className="text-2xl font-bold text-foreground">{broadcastStatus.listenersReached}</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-sm text-muted-foreground">Languages Deployed</p>
                    <p className="text-2xl font-bold text-foreground">{broadcastStatus.languagesDeployed}</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-sm text-muted-foreground">Delivery Confirmation</p>
                    <p className="text-2xl font-bold text-foreground">{broadcastStatus.deliveryConfirmation}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Deployment Zone</CardTitle>
                <CardDescription>Select target area for announcement</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="aspect-square bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-border relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-accent/10" />
                  <div className="relative text-center space-y-2">
                    <MapPin className="h-12 w-12 text-primary mx-auto" />
                    <p className="text-sm font-medium">Interactive Map</p>
                    <p className="text-xs text-muted-foreground">Click to select location</p>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Broadcast Radius: {radius[0]} km</label>
                  <Slider
                    value={radius}
                    onValueChange={setRadius}
                    min={1}
                    max={20}
                    step={1}
                    className="w-full"
                  />
                </div>

                <Button 
                  className="w-full bg-primary hover:bg-primary/90" 
                  size="lg"
                  onClick={handleDeploy}
                >
                  <Send className="mr-2 h-4 w-4" />
                  Broadcast with Agora AI
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <Dialog open={showConfirmation} onOpenChange={setShowConfirmation}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex justify-center mb-4">
              <div className="rounded-full bg-success/10 p-3">
                <CheckCircle className="h-12 w-12 text-success" />
              </div>
            </div>
            <DialogTitle className="text-center text-2xl">Announcement Deployed Successfully!</DialogTitle>
            <DialogDescription className="text-center space-y-2">
              <p>Your announcement has been processed by Agora Conversational AI</p>
              <p className="font-medium">✓ Reached {broadcastStatus.listenersReached} listeners</p>
              <p className="font-medium">✓ Translated into {broadcastStatus.languagesDeployed} languages</p>
              <p className="font-medium">✓ {broadcastStatus.deliveryConfirmation}% delivery confirmation</p>
            </DialogDescription>
          </DialogHeader>
          <Button onClick={() => setShowConfirmation(false)}>
            Close
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OperatorDashboard;
