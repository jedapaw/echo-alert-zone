import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import { BroadcastProvider } from '@/lib/BroadcastProvider';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BroadcastProvider>
      <App />
    </BroadcastProvider>
  </React.StrictMode>,
);
