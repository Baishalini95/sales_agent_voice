import csv
from database import DatabaseManager
from datetime import datetime

def export_to_csv():
    db_manager = DatabaseManager()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export feedback data
    print("Exporting feedback data...")
    feedback_data = db_manager.get_all_feedback()
    
    with open(f'feedback_export_{timestamp}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Email', 'Challenge', 'Rating', 'Query', 'Response', 'Date'])
        
        for feedback in feedback_data:
            writer.writerow([
                feedback[0],  # id
                feedback[1],  # name
                feedback[2],  # email
                feedback[3],  # challenge
                feedback[4],  # satisfaction_rating
                feedback[5] or '',  # query
                feedback[6] or '',  # response
                feedback[7]   # created_at
            ])
    
    print(f"Feedback exported to: feedback_export_{timestamp}.csv")
    
    # Export tickets data
    print("Exporting tickets data...")
    tickets_data = db_manager.get_all_tickets()
    
    with open(f'tickets_export_{timestamp}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticket ID', 'Name', 'Email', 'Reason', 'Priority', 'Status', 'Assigned To', 'Created', 'Updated'])
        
        for ticket in tickets_data:
            if len(ticket) >= 9:
                writer.writerow([
                    ticket[0],  # id
                    ticket[1],  # name
                    ticket[2],  # email
                    ticket[3],  # reason
                    ticket[4],  # priority
                    ticket[5],  # status
                    ticket[6],  # assigned_to
                    ticket[7],  # created_at
                    ticket[8]   # updated_at
                ])
            else:
                writer.writerow([
                    ticket[0],  # id
                    ticket[1],  # name
                    ticket[2],  # email
                    ticket[3],  # reason
                    ticket[4],  # priority
                    ticket[5],  # status
                    'Unassigned',  # assigned_to
                    ticket[6],  # created_at
                    ticket[7] if len(ticket) > 7 else ticket[6]  # updated_at
                ])
    
    print(f"Tickets exported to: tickets_export_{timestamp}.csv")
    print("\nExport completed successfully!")

if __name__ == "__main__":
    export_to_csv()