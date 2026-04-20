from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rag_engine import RAGEngine
from database import DatabaseManager
import json

app = Flask(__name__)
CORS(app)

# Initialize components
rag_engine = RAGEngine()
db_manager = DatabaseManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Generate response using RAG
        response = rag_engine.generate_response(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        print("Feedback endpoint called")
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        challenge = data.get('challenge', '').strip()
        satisfaction = data.get('satisfaction', 0)
        query = data.get('query', '')
        response = data.get('response', '')
        
        print(f"Parsed data - Name: {name}, Email: {email}, Challenge: {challenge}, Satisfaction: {satisfaction}")
        
        if not all([name, email, challenge]) or satisfaction == 0:
            return jsonify({'error': 'Missing required fields'}), 400
        
        feedback_id = db_manager.save_feedback(name, email, challenge, satisfaction, query, response)
        print(f"Feedback saved with ID: {feedback_id}")
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your feedback!'
        })
    
    except Exception as e:
        print(f"Error in feedback endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    try:
        feedback_list = db_manager.get_all_feedback()
        
        # Convert to list of dictionaries for JSON response
        feedback_data = []
        for feedback in feedback_list:
            feedback_data.append({
                'id': feedback[0],
                'name': feedback[1],
                'email': feedback[2],
                'challenge': feedback[3],
                'satisfaction_rating': feedback[4],
                'query': feedback[5],
                'response': feedback[6],
                'created_at': feedback[7]
            })
        
        return jsonify({
            'success': True,
            'data': feedback_data,
            'count': len(feedback_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ticket', methods=['POST'])
def create_ticket():
    try:
        print("Ticket endpoint called")
        data = request.get_json()
        print(f"Received ticket data: {data}")
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        reason = data.get('reason', '').strip()
        priority = data.get('priority', '').strip()
        
        print(f"Parsed ticket data - Name: {name}, Email: {email}, Reason: {reason}, Priority: {priority}")
        
        if not all([name, email, reason, priority]):
            return jsonify({'error': 'All fields are required'}), 400
        
        ticket_id = db_manager.save_ticket(name, email, reason, priority)
        print(f"Ticket saved with ID: {ticket_id}")
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'message': f'Ticket {ticket_id} created successfully! We will get back to you soon.'
        })
    
    except Exception as e:
        print(f"Error in ticket endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    try:
        tickets = db_manager.get_all_tickets()
        
        ticket_data = []
        for ticket in tickets:
            # Handle both old and new ticket formats
            if len(ticket) >= 9:  # New format with assigned_to
                ticket_data.append({
                    'id': ticket[0],
                    'name': ticket[1],
                    'email': ticket[2],
                    'reason': ticket[3],
                    'priority': ticket[4],
                    'status': ticket[5],
                    'assigned_to': ticket[6],
                    'created_at': ticket[7],
                    'updated_at': ticket[8]
                })
            else:  # Old format without assigned_to
                ticket_data.append({
                    'id': ticket[0],
                    'name': ticket[1],
                    'email': ticket[2],
                    'reason': ticket[3],
                    'priority': ticket[4],
                    'status': ticket[5],
                    'assigned_to': 'Unassigned',
                    'created_at': ticket[6],
                    'updated_at': ticket[7] if len(ticket) > 7 else ticket[6]
                })
        
        return jsonify({
            'success': True,
            'data': ticket_data,
            'count': len(ticket_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    try:
        data = request.get_json()
        status = data.get('status', '').strip()
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = db_manager.update_ticket_status(ticket_id, status)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Ticket {ticket_id} status updated to {status}'
            })
        else:
            return jsonify({'error': 'Ticket not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<ticket_id>/assign', methods=['PUT'])
def update_ticket_assignment(ticket_id):
    try:
        data = request.get_json()
        assigned_to = data.get('assigned_to', '').strip()
        
        if not assigned_to:
            return jsonify({'error': 'Assignment is required'}), 400
        
        success = db_manager.update_ticket_assignment(ticket_id, assigned_to)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Ticket {ticket_id} assigned to {assigned_to}'
            })
        else:
            return jsonify({'error': 'Ticket not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/<analysis_type>', methods=['GET'])
def get_analytics(analysis_type):
    try:
        if analysis_type == 'satisfaction':
            feedback_list = db_manager.get_all_feedback()
            ratings = [item[4] for item in feedback_list]  # satisfaction_rating column
            
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in ratings:
                rating_counts[rating] += 1
            
            return jsonify({
                'success': True,
                'chartType': 'bar',
                'title': 'Customer Satisfaction Distribution',
                'chartData': {
                    'labels': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
                    'datasets': [{
                        'label': 'Number of Responses',
                        'data': list(rating_counts.values()),
                        'backgroundColor': ['#ef4444', '#f97316', '#eab308', '#22c55e', '#10b981']
                    }]
                }
            })
        
        elif analysis_type == 'priority':
            tickets = db_manager.get_all_tickets()
            priorities = [item[4] for item in tickets]  # priority column
            
            priority_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
            for priority in priorities:
                if priority in priority_counts:
                    priority_counts[priority] += 1
            
            return jsonify({
                'success': True,
                'chartType': 'doughnut',
                'title': 'Ticket Priority Distribution',
                'chartData': {
                    'labels': list(priority_counts.keys()),
                    'datasets': [{
                        'data': list(priority_counts.values()),
                        'backgroundColor': ['#10b981', '#eab308', '#f97316', '#ef4444']
                    }]
                }
            })
        
        elif analysis_type == 'status':
            tickets = db_manager.get_all_tickets()
            statuses = [item[5] for item in tickets]  # status column
            
            status_counts = {'Open': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0}
            for status in statuses:
                if status in status_counts:
                    status_counts[status] += 1
            
            return jsonify({
                'success': True,
                'chartType': 'pie',
                'title': 'Ticket Status Overview',
                'chartData': {
                    'labels': list(status_counts.keys()),
                    'datasets': [{
                        'data': list(status_counts.values()),
                        'backgroundColor': ['#eab308', '#3b82f6', '#10b981', '#6b7280']
                    }]
                }
            })
        
        elif analysis_type == 'timeline':
            from datetime import datetime, timedelta
            
            feedback_list = db_manager.get_all_feedback()
            tickets = db_manager.get_all_tickets()
            
            # Get last 7 days
            dates = []
            feedback_counts = []
            ticket_counts = []
            
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                dates.append(date)
                
                feedback_count = len([f for f in feedback_list if f[7].startswith(date)])
                ticket_count = len([t for t in tickets if t[6].startswith(date)])
                
                feedback_counts.append(feedback_count)
                ticket_counts.append(ticket_count)
            
            dates.reverse()
            feedback_counts.reverse()
            ticket_counts.reverse()
            
            return jsonify({
                'success': True,
                'chartType': 'line',
                'title': 'Activity Timeline (Last 7 Days)',
                'chartData': {
                    'labels': dates,
                    'datasets': [
                        {
                            'label': 'Feedback',
                            'data': feedback_counts,
                            'borderColor': '#10b981',
                            'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                            'tension': 0.4
                        },
                        {
                            'label': 'Tickets',
                            'data': ticket_counts,
                            'borderColor': '#3b82f6',
                            'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                            'tension': 0.4
                        }
                    ]
                }
            })
        
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})

if __name__ == '__main__':
    print("Starting RAG Chatbot Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)