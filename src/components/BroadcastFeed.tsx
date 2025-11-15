import React from 'react';
import { useBroadcasts } from '@/lib/BroadcastProvider';

export const BroadcastFeed: React.FC = () => {
  // 1. Get data from the context
  const { messages, isConnected } = useBroadcasts();

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">Live Broadcasts</h2>
      <p>
        Connection Status: 
        <span className={isConnected ? 'text-green-500' : 'text-red-500'}>
          {isConnected ? ' Connected' : ' Disconnected'}
        </span>
      </p>

      {/* 2. Render the messages */}
      <div className="mt-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-gray-500">Waiting for broadcasts...</p>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className="p-3 border rounded-lg shadow">
            {msg.emergency && (
              <p className="font-bold text-red-600">🚨 EMERGENCY 🚨</p>
            )}
            <p className="text-lg">{msg.message}</p>
            {/* Example: Show a specific translation */}
            <p className="text-sm text-gray-500">
              Hindi: {msg.translations.hi || '...'}
            </p>
            <p className="text-xs text-gray-400">
              {new Date(msg.timestamp).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
