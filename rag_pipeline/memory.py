import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manage conversation memory with SQLite backend"""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.db_path = "./conversations.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    title TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
            raise e
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation"""
        if not self.user_id:
            return None
        
        try:
            conversation_id = f"conv_{datetime.now().timestamp()}_{self.user_id}"
            title = title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (conversation_id, self.user_id, title, datetime.now(), datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created conversation: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"❌ Error creating conversation: {e}")
            return None
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add message
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, role, content, datetime.now()))
            
            # Update conversation timestamp
            cursor.execute('''
                UPDATE conversations 
                SET updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), conversation_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error adding message: {e}")
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get all messages in a conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, timestamp 
                FROM messages 
                WHERE conversation_id = ?
                ORDER BY timestamp
            ''', (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2]
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation: {e}")
            return []
    
    def get_user_conversations(self) -> List[Dict]:
        """Get all conversations for current user"""
        if not self.user_id:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, created_at, updated_at 
                FROM conversations 
                WHERE user_id = ?
                ORDER BY updated_at DESC
            ''', (self.user_id,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error getting user conversations: {e}")
            return []
    
    def clear_conversation(self, conversation_id: str):
        """Clear all messages in a conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cleared conversation: {conversation_id}")
            
        except Exception as e:
            logger.error(f"❌ Error clearing conversation: {e}")