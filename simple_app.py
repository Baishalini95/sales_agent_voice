from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    # Simple response without RAG for now
    response = f"I received your message: {message}. The full AI system will be available once all components are loaded."
    
    return jsonify({
        'response': response,
        'status': 'success'
    })

@app.route('/ticket', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        reason = data.get('reason', '').strip()
        priority = data.get('priority', '').strip()
        
        if not all([name, email, reason, priority]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Generate ticket ID
        ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'message': f'✅ Ticket {ticket_id} created successfully! We will get back to you soon.',
            'actions': [
                {
                    'label': '📋 View in ServiceNow',
                    'url': f'https://dev123456.service-now.com/nav_to.do?uri=incident.do?sys_id={ticket_id}',
                    'type': 'external'
                },
                {
                    'label': '🔗 Open in Salesforce',
                    'url': f'https://yourorg.lightning.force.com/lightning/r/Case/{ticket_id}/view',
                    'type': 'external'
                },
                {
                    'label': '📊 Track Progress',
                    'url': f'/track/{ticket_id}',
                    'type': 'internal'
                }
            ]
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        challenge = data.get('challenge', '').strip()
        satisfaction = data.get('satisfaction', 0)
        
        if not all([name, email, challenge]) or satisfaction == 0:
            return jsonify({'error': 'Missing required fields'}), 400
        
        feedback_id = str(uuid.uuid4())[:8]
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your feedback!'
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/track/<ticket_id>')
def track_ticket(ticket_id):
    return f'''
    <html>
    <head><title>Track Ticket {ticket_id}</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>🎫 Ticket Tracking: {ticket_id}</h2>
        <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <p><strong>Status:</strong> <span style="color: #ff6b35;">🔄 In Progress</span></p>
            <p><strong>Priority:</strong> <span style="color: #e74c3c;">🔥 High</span></p>
            <p><strong>Assigned to:</strong> Support Team</p>
            <p><strong>Created:</strong> {ticket_id[:3]}-{ticket_id[3:6]}-{ticket_id[6:]}</p>
        </div>
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h3>📈 Progress Timeline</h3>
            <ul>
                <li>✅ Ticket Created</li>
                <li>🔄 Under Review (Current)</li>
                <li>⏳ Pending Resolution</li>
                <li>⏳ Closed</li>
            </ul>
        </div>
        <button onclick="window.close()" style="background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Close</button>
    </body>
    </html>
    '''

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    # Sample feedback data for demo
    sample_feedback = [
        {
            'id': 'FB001',
            'name': 'John Smith',
            'email': 'john@example.com',
            'challenge': 'Login issues with the system',
            'satisfaction_rating': 4,
            'query': 'How to reset password?',
            'response': 'You can reset your password from the login page.',
            'created_at': '2024-01-15 10:30:00'
        },
        {
            'id': 'FB002',
            'name': 'Sarah Johnson',
            'email': 'sarah@example.com',
            'challenge': 'Slow performance during peak hours',
            'satisfaction_rating': 3,
            'query': 'Why is the system slow?',
            'response': 'We are working on performance improvements.',
            'created_at': '2024-01-15 14:20:00'
        },
        {
            'id': 'FB003',
            'name': 'Mike Davis',
            'email': 'mike@example.com',
            'challenge': 'Feature request for mobile app',
            'satisfaction_rating': 5,
            'query': 'When will mobile app be available?',
            'response': 'Mobile app is planned for Q2 2024.',
            'created_at': '2024-01-15 16:45:00'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': sample_feedback,
        'count': len(sample_feedback)
    })

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    # Sample ticket data for demo
    sample_tickets = [
        {
            'id': 'TKT-A1B2C3D4',
            'name': 'Alice Brown',
            'email': 'alice@example.com',
            'reason': 'Cannot access dashboard after update',
            'priority': 'High',
            'status': 'Open',
            'assigned_to': 'Support Team',
            'created_at': '2024-01-15 09:15:00',
            'updated_at': '2024-01-15 09:15:00'
        },
        {
            'id': 'TKT-E5F6G7H8',
            'name': 'Bob Wilson',
            'email': 'bob@example.com',
            'reason': 'Data export functionality not working',
            'priority': 'Medium',
            'status': 'In Progress',
            'assigned_to': 'Tech Team',
            'created_at': '2024-01-15 11:30:00',
            'updated_at': '2024-01-15 13:20:00'
        },
        {
            'id': 'TKT-I9J0K1L2',
            'name': 'Carol Martinez',
            'email': 'carol@example.com',
            'reason': 'Request for additional user permissions',
            'priority': 'Low',
            'status': 'Resolved',
            'assigned_to': 'Admin Team',
            'created_at': '2024-01-14 15:45:00',
            'updated_at': '2024-01-15 10:30:00'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': sample_tickets,
        'count': len(sample_tickets)
    })

@app.route('/api/analytics/<analysis_type>', methods=['GET'])
def get_analytics(analysis_type):
    if analysis_type == 'satisfaction':
        return jsonify({
            'success': True,
            'chartType': 'bar',
            'title': 'Customer Satisfaction Distribution',
            'chartData': {
                'labels': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
                'datasets': [{
                    'label': 'Number of Responses',
                    'data': [1, 2, 5, 8, 12],
                    'backgroundColor': ['#ef4444', '#f97316', '#eab308', '#22c55e', '#10b981']
                }]
            }
        })
    elif analysis_type == 'priority':
        return jsonify({
            'success': True,
            'chartType': 'doughnut',
            'title': 'Ticket Priority Distribution',
            'chartData': {
                'labels': ['Low', 'Medium', 'High', 'Critical'],
                'datasets': [{
                    'data': [5, 8, 4, 2],
                    'backgroundColor': ['#10b981', '#eab308', '#f97316', '#ef4444']
                }]
            }
        })
    elif analysis_type == 'status':
        return jsonify({
            'success': True,
            'chartType': 'pie',
            'title': 'Ticket Status Overview',
            'chartData': {
                'labels': ['Open', 'In Progress', 'Resolved', 'Closed'],
                'datasets': [{
                    'data': [6, 4, 7, 2],
                    'backgroundColor': ['#eab308', '#3b82f6', '#10b981', '#6b7280']
                }]
            }
        })
    else:
        return jsonify({'error': 'Invalid analysis type'}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting Simple Chatbot Server on port 8080...")
    print("Access at: http://localhost:8080")
    app.run(debug=True, host='127.0.0.1', port=8080)