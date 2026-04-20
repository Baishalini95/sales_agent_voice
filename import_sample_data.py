import csv
from database import DatabaseManager

def import_sample_data():
    db_manager = DatabaseManager()
    
    print("Importing sample feedback data...")
    
    # Import feedback data
    with open('sample_feedback.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                db_manager.save_feedback(
                    name=row['name'],
                    email=row['email'],
                    challenge=row['challenge'],
                    satisfaction_rating=int(row['satisfaction_rating']),
                    query=row['query'],
                    response=row['response']
                )
                print(f"Added feedback: {row['name']}")
            except Exception as e:
                print(f"Error adding feedback {row['name']}: {e}")
    
    print("\nImporting sample tickets data...")
    
    # Import tickets data
    with open('sample_tickets.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # First create the ticket
                ticket_id = db_manager.save_ticket(
                    name=row['name'],
                    email=row['email'],
                    reason=row['reason'],
                    priority=row['priority']
                )
                
                # Then update status and assignment if different from defaults
                if row['status'] != 'Open':
                    db_manager.update_ticket_status(ticket_id, row['status'])
                
                if row['assigned_to'] != 'Unassigned':
                    db_manager.update_ticket_assignment(ticket_id, row['assigned_to'])
                
                print(f"Added ticket: {ticket_id} - {row['name']}")
            except Exception as e:
                print(f"Error adding ticket {row['name']}: {e}")
    
    print("\nSample data import completed!")

if __name__ == "__main__":
    import_sample_data()