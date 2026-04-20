class AdminPanel {
    constructor() {
        this.feedbackData = [];
        this.ticketsData = [];
        this.filteredData = [];
        this.currentTab = 'feedback';
        this.init();
        this.loadData();
    }
    
    init() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Event listeners
        document.getElementById('refreshBtn').addEventListener('click', () => this.loadData());
        document.getElementById('searchInput').addEventListener('input', () => this.filterData());
        document.getElementById('ratingFilter').addEventListener('change', () => this.filterData());
        document.getElementById('dateFilter').addEventListener('change', () => this.filterData());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportCSV());
        document.getElementById('exportTicketsBtn').addEventListener('click', () => this.exportTicketsCSV());
        document.getElementById('closeDetailModal').addEventListener('click', () => this.closeModal());
        
        // Close modal when clicking outside
        document.getElementById('detailModal').addEventListener('click', (e) => {
            if (e.target.id === 'detailModal') {
                this.closeModal();
            }
        });
    }
    
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        
        // Show/hide sections
        document.getElementById('feedbackSection').style.display = tab === 'feedback' ? 'block' : 'none';
        document.getElementById('ticketsSection').style.display = tab === 'tickets' ? 'block' : 'none';
        
        // Update stats for the current tab
        this.updateStats();
        this.filterData();
    }
    
    async loadData() {
        try {
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            refreshBtn.disabled = true;
            
            // Load feedback
            const feedbackResponse = await fetch('/api/feedback');
            const feedbackData = await feedbackResponse.json();
            
            // Load tickets
            const ticketsResponse = await fetch('/api/tickets');
            const ticketsData = await ticketsResponse.json();
            
            if (feedbackData.success && ticketsData.success) {
                this.feedbackData = feedbackData.data;
                this.ticketsData = ticketsData.data;
                this.updateStats();
                this.filterData();
            } else {
                this.showError('Failed to load data');
            }
        } catch (error) {
            this.showError('Connection error: ' + error.message);
        } finally {
            const refreshBtn = document.getElementById('refreshBtn');
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            refreshBtn.disabled = false;
        }
    }
    
    updateStats() {
        const totalFeedback = this.feedbackData.length;
        const totalTickets = this.ticketsData.length;
        const avgRating = totalFeedback > 0 ? 
            (this.feedbackData.reduce((sum, item) => sum + item.satisfaction_rating, 0) / totalFeedback).toFixed(1) : 0;
        
        const today = new Date().toISOString().split('T')[0];
        const todayFeedback = this.feedbackData.filter(item => 
            item.created_at.startsWith(today)
        ).length;
        const todayTickets = this.ticketsData.filter(item => 
            item.created_at.startsWith(today)
        ).length;
        
        // Update stats based on current tab
        if (this.currentTab === 'feedback') {
            document.getElementById('totalFeedback').textContent = totalFeedback;
            document.getElementById('totalTickets').textContent = totalTickets;
            document.getElementById('avgRating').textContent = avgRating;
            document.getElementById('todayCount').textContent = todayFeedback;
            document.getElementById('todayLabel').textContent = "Today's Feedback";
            
            // Enable all stat cards for feedback
            document.querySelectorAll('.stat-card').forEach(card => {
                card.style.opacity = '1';
                card.style.pointerEvents = 'auto';
            });
        } else {
            // For tickets tab, disable feedback-specific stats
            document.getElementById('totalFeedback').textContent = totalFeedback;
            document.getElementById('totalTickets').textContent = totalTickets;
            document.getElementById('avgRating').textContent = 'N/A';
            document.getElementById('todayCount').textContent = todayTickets;
            document.getElementById('todayLabel').textContent = "Today's Tickets";
            
            // Disable feedback and rating cards for tickets
            const statCards = document.querySelectorAll('.stat-card');
            statCards[0].style.opacity = '0.5'; // Total Feedback
            statCards[0].style.pointerEvents = 'none';
            statCards[2].style.opacity = '0.5'; // Average Rating
            statCards[2].style.pointerEvents = 'none';
            
            // Keep tickets and today count enabled
            statCards[1].style.opacity = '1'; // Total Tickets
            statCards[1].style.pointerEvents = 'auto';
            statCards[3].style.opacity = '1'; // Today's Items
            statCards[3].style.pointerEvents = 'auto';
        }
    }
    
    filterData() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const ratingFilter = document.getElementById('ratingFilter').value;
        const dateFilter = document.getElementById('dateFilter').value;
        
        if (this.currentTab === 'feedback') {
            this.filteredData = this.feedbackData.filter(item => {
                const matchesSearch = !searchTerm || 
                    item.name.toLowerCase().includes(searchTerm) ||
                    item.email.toLowerCase().includes(searchTerm) ||
                    item.challenge.toLowerCase().includes(searchTerm);
                
                const matchesRating = !ratingFilter || 
                    item.satisfaction_rating.toString() === ratingFilter;
                
                let matchesDate = true;
                if (dateFilter) {
                    const itemDate = new Date(item.created_at);
                    const now = new Date();
                    
                    switch (dateFilter) {
                        case 'today':
                            matchesDate = itemDate.toDateString() === now.toDateString();
                            break;
                        case 'week':
                            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                            matchesDate = itemDate >= weekAgo;
                            break;
                        case 'month':
                            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                            matchesDate = itemDate >= monthAgo;
                            break;
                    }
                }
                
                return matchesSearch && matchesRating && matchesDate;
            });
        } else {
            this.filteredData = this.ticketsData.filter(item => {
                const matchesSearch = !searchTerm || 
                    item.name.toLowerCase().includes(searchTerm) ||
                    item.email.toLowerCase().includes(searchTerm) ||
                    item.reason.toLowerCase().includes(searchTerm) ||
                    item.id.toLowerCase().includes(searchTerm);
                
                let matchesDate = true;
                if (dateFilter) {
                    const itemDate = new Date(item.created_at);
                    const now = new Date();
                    
                    switch (dateFilter) {
                        case 'today':
                            matchesDate = itemDate.toDateString() === now.toDateString();
                            break;
                        case 'week':
                            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                            matchesDate = itemDate >= weekAgo;
                            break;
                        case 'month':
                            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                            matchesDate = itemDate >= monthAgo;
                            break;
                    }
                }
                
                return matchesSearch && matchesDate;
            });
        }
        
        this.renderTable();
    }
    
    renderTable() {
        if (this.currentTab === 'feedback') {
            this.renderFeedbackTable();
        } else {
            this.renderTicketsTable();
        }
    }
    
    renderFeedbackTable() {
        const tbody = document.getElementById('feedbackTableBody');
        
        if (this.filteredData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px; color: #666;">
                        <i class="fas fa-inbox" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                        No feedback data found
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredData.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.email}</td>
                <td>${this.truncateText(item.challenge, 50)}</td>
                <td>
                    <span class="rating-stars">
                        ${'★'.repeat(item.satisfaction_rating)}${'☆'.repeat(5 - item.satisfaction_rating)}
                    </span>
                    (${item.satisfaction_rating}/5)
                </td>
                <td>${this.truncateText(item.query || 'N/A', 30)}</td>
                <td>${this.truncateText(item.response || 'N/A', 30)}</td>
                <td>${this.formatDate(item.created_at)}</td>
                <td>
                    <button class="view-btn" onclick="adminPanel.viewFeedbackDetails('${item.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    renderTicketsTable() {
        const tbody = document.getElementById('ticketsTableBody');
        
        if (this.filteredData.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" style="text-align: center; padding: 40px; color: #666;">
                        <i class="fas fa-inbox" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                        No tickets found
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredData.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.email}</td>
                <td>${this.truncateText(item.reason, 50)}</td>
                <td><span class="priority-badge priority-${item.priority.toLowerCase()}">${item.priority}</span></td>
                <td><span class="status-badge status-${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></td>
                <td>
                    <select class="status-select" onchange="adminPanel.updateTicketAssignment('${item.id}', this.value)">
                        <option value="Unassigned" ${(item.assigned_to || 'Unassigned') === 'Unassigned' ? 'selected' : ''}>Unassigned</option>
                        <option value="Security Team" ${(item.assigned_to || '') === 'Security Team' ? 'selected' : ''}>Security Team</option>
                        <option value="Cloud Team" ${(item.assigned_to || '') === 'Cloud Team' ? 'selected' : ''}>Cloud Team</option>
                        <option value="SME Team" ${(item.assigned_to || '') === 'SME Team' ? 'selected' : ''}>SME Team</option>
                        <option value="Emergency Team" ${(item.assigned_to || '') === 'Emergency Team' ? 'selected' : ''}>Emergency Team</option>
                    </select>
                </td>
                <td>${this.formatDate(item.created_at)}</td>
                <td>${this.formatDate(item.updated_at)}</td>
                <td>
                    <select class="status-select" onchange="adminPanel.updateTicketStatus('${item.id}', this.value)">
                        <option value="Open" ${item.status === 'Open' ? 'selected' : ''}>Open</option>
                        <option value="In Progress" ${item.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Resolved" ${item.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                        <option value="Closed" ${item.status === 'Closed' ? 'selected' : ''}>Closed</option>
                    </select>
                    <button class="view-btn" onclick="adminPanel.viewTicketDetails('${item.id}')" style="margin-left: 5px;">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    async updateTicketStatus(ticketId, newStatus) {
        try {
            const response = await fetch(`/api/tickets/${ticketId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const ticket = this.ticketsData.find(t => t.id === ticketId);
                if (ticket) {
                    ticket.status = newStatus;
                    ticket.updated_at = new Date().toISOString();
                }
                this.filterData();
            } else {
                alert('Failed to update ticket status: ' + data.error);
            }
        } catch (error) {
            alert('Error updating ticket status: ' + error.message);
        }
    }
    
    async updateTicketAssignment(ticketId, assignedTo) {
        try {
            const response = await fetch(`/api/tickets/${ticketId}/assign`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ assigned_to: assignedTo })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const ticket = this.ticketsData.find(t => t.id === ticketId);
                if (ticket) {
                    ticket.assigned_to = assignedTo;
                    ticket.updated_at = new Date().toISOString();
                }
                this.filterData();
                
                // Show success message
                this.showSuccessMessage(`Ticket ${ticketId} assigned successfully to ${assignedTo}`);
            } else {
                alert('Failed to assign ticket: ' + data.error);
            }
        } catch (error) {
            alert('Error assigning ticket: ' + error.message);
        }
    }
    
    viewFeedbackDetails(id) {
        const item = this.feedbackData.find(feedback => feedback.id === id);
        if (!item) return;
        
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-comments"></i> Feedback Details';
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="detail-item">
                <div class="detail-label">Feedback ID</div>
                <div class="detail-value">${item.id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Name</div>
                <div class="detail-value">${item.name}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Email</div>
                <div class="detail-value">${item.email}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Challenge/Issue</div>
                <div class="detail-value">${item.challenge}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Satisfaction Rating</div>
                <div class="detail-value">
                    <span class="rating-stars">
                        ${'★'.repeat(item.satisfaction_rating)}${'☆'.repeat(5 - item.satisfaction_rating)}
                    </span>
                    (${item.satisfaction_rating}/5)
                </div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Original Query</div>
                <div class="detail-value">${item.query || 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">AI Response</div>
                <div class="detail-value">${item.response || 'N/A'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Submitted Date</div>
                <div class="detail-value">${this.formatDate(item.created_at)}</div>
            </div>
        `;
        
        document.getElementById('detailModal').classList.add('show');
    }
    
    viewTicketDetails(id) {
        const item = this.ticketsData.find(ticket => ticket.id === id);
        if (!item) return;
        
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-ticket-alt"></i> Ticket Details';
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="detail-item">
                <div class="detail-label">Ticket ID</div>
                <div class="detail-value">${item.id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Name</div>
                <div class="detail-value">${item.name}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Email</div>
                <div class="detail-value">${item.email}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Reason/Challenge</div>
                <div class="detail-value">${item.reason}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Priority Level</div>
                <div class="detail-value"><span class="priority-badge priority-${item.priority.toLowerCase()}">${item.priority}</span></div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Current Status</div>
                <div class="detail-value"><span class="status-badge status-${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Assigned To</div>
                <div class="detail-value">${item.assigned_to || 'Unassigned'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Created Date</div>
                <div class="detail-value">${this.formatDate(item.created_at)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Last Updated</div>
                <div class="detail-value">${this.formatDate(item.updated_at)}</div>
            </div>
        `;
        
        document.getElementById('detailModal').classList.add('show');
    }
    
    closeModal() {
        document.getElementById('detailModal').classList.remove('show');
    }
    
    exportCSV() {
        if (this.filteredData.length === 0) {
            alert('No data to export');
            return;
        }
        
        const headers = ['ID', 'Name', 'Email', 'Challenge', 'Rating', 'Query', 'Response', 'Date'];
        const csvContent = [
            headers.join(','),
            ...this.filteredData.map(item => [
                item.id,
                `"${item.name}"`,
                item.email,
                `"${item.challenge.replace(/"/g, '""')}"`,
                item.satisfaction_rating,
                `"${(item.query || '').replace(/"/g, '""')}"`,
                `"${(item.response || '').replace(/"/g, '""')}"`,
                item.created_at
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `feedback_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    exportTicketsCSV() {
        if (this.filteredData.length === 0) {
            alert('No data to export');
            return;
        }
        
        const headers = ['Ticket ID', 'Name', 'Email', 'Reason', 'Priority', 'Status', 'Assigned To', 'Created', 'Updated'];
        const csvContent = [
            headers.join(','),
            ...this.filteredData.map(item => [
                item.id,
                `"${item.name}"`,
                item.email,
                `"${item.reason.replace(/"/g, '""')}"`,
                item.priority,
                item.status,
                item.assigned_to || 'Unassigned',
                item.created_at,
                item.updated_at
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tickets_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    truncateText(text, maxLength) {
        if (!text) return 'N/A';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    showError(message) {
        const tbody = document.getElementById('feedbackTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align: center; padding: 40px; color: #ef4444;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                    ${message}
                </td>
            </tr>
        `;
    }
    
    showSuccessMessage(message) {
        // Create success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            z-index: 10001;
            font-weight: 500;
            animation: slideIn 0.3s ease;
        `;
        notification.innerHTML = `
            <i class="fas fa-check-circle" style="margin-right: 8px;"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Initialize admin panel when page loads
let adminPanel;
document.addEventListener('DOMContentLoaded', () => {
    adminPanel = new AdminPanel();
});