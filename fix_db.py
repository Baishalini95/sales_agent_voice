import sqlite3

def fix_database():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    # Check if assigned_to column exists
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'assigned_to' not in columns:
        print("Adding assigned_to column...")
        cursor.execute('ALTER TABLE tickets ADD COLUMN assigned_to TEXT DEFAULT "Unassigned"')
        conn.commit()
        print("Column added successfully!")
    else:
        print("assigned_to column already exists")
    
    # Show current table structure
    cursor.execute("PRAGMA table_info(tickets)")
    print("\nCurrent table structure:")
    for column in cursor.fetchall():
        print(f"  {column[1]} ({column[2]})")
    
    conn.close()

if __name__ == "__main__":
    fix_database()