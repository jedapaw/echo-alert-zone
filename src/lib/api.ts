const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

export interface BroadcastPayload {
  message: string;
  sourceLanguage: string;
  location?: string;
  radius?: number;
  emergency?: boolean;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async createBroadcast(payload: BroadcastPayload) {
    const url = `${this.baseURL}/api/broadcasts`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Broadcast failed: ${error}`);
    }

    return await response.json();
  }

  async getAnalytics() {
    const response = await fetch(`${this.baseURL}/api/analytics`);
    if (!response.ok) throw new Error('Analytics fetch failed');
    return await response.json();
  }

  async sendChatMessage(payload: { message: string; language?: string; userId?: string }) {
    const response = await fetch(`${this.baseURL}/api/ai-chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Chat failed');
    return await response.json();
  }
}

export const apiClient = new APIClient(API_BASE_URL);
