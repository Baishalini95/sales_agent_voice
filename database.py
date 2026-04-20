import sqlite3
import uuid
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="chatbot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                challenge TEXT NOT NULL,
                satisfaction_rating INTEGER NOT NULL,
                query TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                reason TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                assigned_to TEXT DEFAULT 'Unassigned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add assigned_to column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE tickets ADD COLUMN assigned_to TEXT DEFAULT "Unassigned"')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def save_feedback(self, name, email, challenge, satisfaction_rating, query="", response=""):
        feedback_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (id, name, email, challenge, satisfaction_rating, query, response)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (feedback_id, name, email, challenge, satisfaction_rating, query, response))
        
        conn.commit()
        conn.close()
        return feedback_id
    
    def get_all_feedback(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC')
        feedback = cursor.fetchall()
        conn.close()
        return feedback
    
    def save_ticket(self, name, email, reason, priority):
        ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (id, name, email, reason, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, name, email, reason, priority))
        
        conn.commit()
        conn.close()
        return ticket_id
    
    def get_all_tickets(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
        tickets = cursor.fetchall()
        conn.close()
        return tickets
    
    def update_ticket_status(self, ticket_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tickets 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, ticket_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def update_ticket_assignment(self, ticket_id, assigned_to):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tickets 
            SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (assigned_to, ticket_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0