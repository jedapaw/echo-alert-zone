import React, { createContext, useContext } from 'react';
import { useAgoraRTM, BroadcastMessage } from '@/hooks/useAgoraRTM';

interface BroadcastContextType {
  messages: BroadcastMessage[];
  isConnected: boolean;
}

// 1. Create the context
const BroadcastContext = createContext<BroadcastContextType | undefined>(undefined);

// 2. Create the provider component
export const BroadcastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { messages, isConnected } = useAgoraRTM();

  return (
    <BroadcastContext.Provider value={{ messages, isConnected }}>
      {children}
    </BroadcastContext.Provider>
  );
};

// 3. Create a custom hook to easily use the context
export const useBroadcasts = () => {
  const context = useContext(BroadcastContext);
  if (!context) {
    throw new Error('useBroadcasts must be used within a BroadcastProvider');
  }
  return context;
};
