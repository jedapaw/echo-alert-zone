import { useState, useEffect, useRef } from 'react';
import AgoraRTM from 'agora-rtm-sdk';

export interface BroadcastMessage {
  id: number;
  message: string;
  translations: Record<string, string>;
  location: string;
  emergency: boolean;
  timestamp: string;
}

const APP_ID = import.meta.env.VITE_AGORA_APP_ID;
const CHANNEL_NAME = 'EMERGENCY_ALERTS';
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export const useAgoraRTM = () => {
  const [messages, setMessages] = useState<BroadcastMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef<any>(null);
  const channelRef = useRef<any>(null);
  const isInitializing = useRef(false);
  const isInitialized = useRef(false);

  useEffect(() => {
    if (!APP_ID) {
      console.error('VITE_AGORA_APP_ID is not set in .env file');
      return;
    }

    // Prevent double initialization in React strict mode
    if (isInitializing.current || isInitialized.current) {
      console.log('Already initializing or initialized, skipping...');
      return;
    }

    isInitializing.current = true;

    const initializeRTM = async () => {
      try {
        console.log('🔄 Initializing Agora RTM...');
        
        // Create RTM client
        clientRef.current = AgoraRTM.createInstance(APP_ID);
        console.log('✅ Agora RTM Client created');

        // Generate random user ID
        const userId = `web-listener-${Math.floor(Math.random() * 100000)}`;
        console.log(`👤 User ID: ${userId}`);

        // Fetch token from backend
        console.log('🔑 Fetching RTM token from backend...');
        const response = await fetch(`${BACKEND_URL}/api/token/rtm/${userId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch RTM token: ${response.status} ${response.statusText}`);
        }
        
        const { token } = await response.json();
        console.log('✅ Token received from backend');

        // Login to Agora RTM with token
        await clientRef.current.login({ uid: userId, token: token });
        console.log('✅ Logged in to Agora RTM');

        // Create and join channel
        channelRef.current = clientRef.current.createChannel(CHANNEL_NAME);
        await channelRef.current.join();
        console.log(`✅ Joined channel: ${CHANNEL_NAME}`);

        setIsConnected(true);
        isInitialized.current = true;

        // Set up message listener
        channelRef.current.on('ChannelMessage', (message: any, memberId: string) => {
          console.log(`📨 Message received from ${memberId}:`, message);
          
          if (message.text) {
            try {
              const payload = JSON.parse(message.text);
              if (payload.type === 'broadcast') {
                const broadcastData: BroadcastMessage = payload.data;
                console.log('📢 Broadcast received:', broadcastData);
                setMessages((prev) => [broadcastData, ...prev]);
              }
            } catch (e) {
              console.error('Failed to parse broadcast message:', e);
            }
          }
        });

        // Connection state listener
        clientRef.current.on('ConnectionStateChanged', (newState: string, reason: string) => {
          console.log('🔌 Connection state changed:', newState, reason);
          setIsConnected(newState === 'CONNECTED');
        });

      } catch (error) {
        console.error('❌ Agora RTM initialization failed:', error);
        setIsConnected(false);
        isInitializing.current = false;
        isInitialized.current = false;
      }
    };

    initializeRTM();

    // Cleanup
    return () => {
      const cleanup = async () => {
        if (!isInitialized.current) {
          return; // Don't cleanup if never initialized
        }
        
        try {
          if (channelRef.current) {
            await channelRef.current.leave();
            console.log('👋 Left channel');
          }
          if (clientRef.current) {
            await clientRef.current.logout();
            console.log('👋 Logged out from Agora RTM');
          }
        } catch (error) {
          // Ignore cleanup errors
          console.log('Cleanup completed (with minor errors, which is normal)');
        }
        
        isInitialized.current = false;
        isInitializing.current = false;
      };
      cleanup();
    };
  }, []); // Empty dependency array - run once

  return { messages, isConnected };
};
