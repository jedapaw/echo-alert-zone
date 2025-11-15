import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "emergency.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Broadcasts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                source_language TEXT NOT NULL,
                location TEXT,
                radius INTEGER,
                emergency BOOLEAN,
                timestamp TEXT NOT NULL,
                delivered_count INTEGER DEFAULT 0,
                translations TEXT
            )
        ''')
        
        # Messages table (chat history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                language TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Telegram subscribers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT,
                subscribed_at TEXT,
                last_seen TEXT
            )
        ''')
        
        # --- The 'listeners' table has been removed ---
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def add_broadcast(self, broadcast_data: Dict) -> int:
        """Add new broadcast"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO broadcasts 
            (message, source_language, location, radius, emergency, timestamp, translations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            broadcast_data['message'],
            broadcast_data['sourceLanguage'],
            broadcast_data.get('location', ''),
            broadcast_data.get('radius', 5000),
            broadcast_data.get('emergency', False),
            datetime.now().isoformat(),
            json.dumps(broadcast_data.get('translations', {}))
        ))
        
        broadcast_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return broadcast_id
    
    def update_broadcast_delivery(self, broadcast_id: int, count: int):
        """Update delivery count for broadcast"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE broadcasts SET delivered_count = ? WHERE id = ?
        ''', (count, broadcast_id))
        
        conn.commit()
        conn.close()
    
    def get_broadcasts(self, limit: int = 50) -> List[Dict]:
        """Get recent broadcasts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, message, source_language, location, radius, 
                   emergency, timestamp, delivered_count, translations
            FROM broadcasts
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        broadcasts = []
        for row in rows:
            broadcasts.append({
                'id': row[0],
                'message': row[1],
                'sourceLanguage': row[2],
                'location': row[3],
                'radius': row[4],
                'emergency': bool(row[5]),
                'timestamp': row[6],
                'deliveredCount': row[7],
                'translations': json.loads(row[8]) if row[8] else {}
            })
        
        return broadcasts
    
    def add_message(self, user_id: str, message: str, response: str, language: str):
        """Add chat message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (user_id, message, response, language, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, message, response, language, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

    # --- add_listener() and remove_listener() are removed ---

    def add_telegram_subscriber(self, user_id: int, username: str, first_name: str, language: str = 'en'):
        """Add or update Telegram subscriber"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO telegram_subscribers 
            (user_id, username, first_name, language, subscribed_at, last_seen)
            VALUES (?, ?, ?, ?, 
                COALESCE((SELECT subscribed_at FROM telegram_subscribers WHERE user_id = ?), ?),
                ?)
        ''', (
            user_id, username, first_name, language, 
            user_id, datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_telegram_subscribers(self) -> List[int]:
        """Get all Telegram subscriber IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM telegram_subscribers')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_subscriber_count(self) -> int:
        """Get total subscriber count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM telegram_subscribers')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_analytics(self) -> Dict:
        """Get analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total broadcasts
        cursor.execute('SELECT COUNT(*) FROM broadcasts')
        total_broadcasts = cursor.fetchone()[0]
        
        # Total delivered
        cursor.execute('SELECT SUM(delivered_count) FROM broadcasts')
        total_delivered = cursor.fetchone()[0] or 0
        
        # --- 'activeListeners' is no longer tracked by this DB ---
        
        # Telegram subscribers
        cursor.execute('SELECT COUNT(*) FROM telegram_subscribers')
        telegram_subscribers = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'totalBroadcasts': total_broadcasts,
            'totalDelivered': total_delivered,
            # 'activeListeners': active_listeners, # This key is now removed
            'telegramSubscribers': telegram_subscribers,
            'averageDeliveryTime': 450  # Mock for now
        }
