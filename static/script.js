class CornerChatBot {
    constructor() {
        this.chatToggle = document.getElementById('chatToggle');
        this.chatWindow = document.getElementById('chatWindow');
        this.minimizeBtn = document.getElementById('minimizeBtn');
        this.maximizeBtn = document.getElementById('maximizeBtn');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.charCount = document.getElementById('charCount');
        this.notificationBadge = document.getElementById('notificationBadge');
        this.feedbackModal = document.getElementById('feedbackModal');
        this.ticketModal = document.getElementById('ticketModal');
        
        this.isOpen = false;
        this.isFullscreen = false;
        this.currentQuery = '';
        this.currentResponse = '';
        this.init();
        this.checkHealth();
    }
    
    init() {
        // Toggle chat window
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        this.minimizeBtn.addEventListener('click', () => this.toggleChat());
        this.maximizeBtn.addEventListener('click', () => this.toggleMaximize());
        
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Character count
        this.messageInput.addEventListener('input', () => this.updateCharCount());
        
        // ESC key to exit fullscreen
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isFullscreen) {
                this.toggleMaximize();
            }
        });
        
        // Hide notification badge initially
        this.hideNotification();
        
        // Modal events
        this.initFeedbackModal();
        this.initTicketModal();
    }
    
    initFeedbackModal() {
        const closeModal = document.getElementById('closeModal');
        const cancelFeedback = document.getElementById('cancelFeedback');
        const feedbackForm = document.getElementById('feedbackForm');
        
        closeModal.addEventListener('click', () => this.closeFeedbackModal());
        cancelFeedback.addEventListener('click', () => this.closeFeedbackModal());
        feedbackForm.addEventListener('submit', (e) => this.submitFeedback(e));
        
        // Close modal when clicking outside
        this.feedbackModal.addEventListener('click', (e) => {
            if (e.target === this.feedbackModal) {
                this.closeFeedbackModal();
            }
        });
    }
    
    initTicketModal() {
        const closeTicketModal = document.getElementById('closeTicketModal');
        const cancelTicket = document.getElementById('cancelTicket');
        const ticketForm = document.getElementById('ticketForm');
        
        closeTicketModal.addEventListener('click', () => this.closeTicketModal());
        cancelTicket.addEventListener('click', () => this.closeTicketModal());
        ticketForm.addEventListener('submit', (e) => this.submitTicket(e));
        
        // Close modal when clicking outside
        this.ticketModal.addEventListener('click', (e) => {
            if (e.target === this.ticketModal) {
                this.closeTicketModal();
            }
        });
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            this.chatWindow.classList.add('open');
            this.chatToggle.innerHTML = '<i class="fas fa-times"></i>';
            this.messageInput.focus();
            this.hideNotification();
        } else {
            this.chatWindow.classList.remove('open');
            this.chatWindow.classList.remove('fullscreen');
            this.chatToggle.innerHTML = '<i class="fas fa-comments"></i>';
            this.isFullscreen = false;
            this.updateMaximizeButton();
        }
    }
    
    toggleMaximize() {
        this.isFullscreen = !this.isFullscreen;
        
        if (this.isFullscreen) {
            this.chatWindow.classList.add('fullscreen');
        } else {
            this.chatWindow.classList.remove('fullscreen');
        }
        
        this.updateMaximizeButton();
        
        // Scroll to bottom after animation
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 300);
    }
    
    updateMaximizeButton() {
        if (this.isFullscreen) {
            this.maximizeBtn.innerHTML = '<i class="fas fa-compress"></i>';
            this.maximizeBtn.title = 'Restore';
        } else {
            this.maximizeBtn.innerHTML = '<i class="fas fa-expand"></i>';
            this.maximizeBtn.title = 'Maximize';
        }
    }
    
    hideNotification() {
        this.notificationBadge.style.display = 'none';
    }
    
    showNotification() {
        this.notificationBadge.style.display = 'flex';
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const statusDot = document.querySelector('.status-dot');
            if (data.status === 'healthy') {
                statusDot.className = 'status-dot online';
            } else {
                statusDot.className = 'status-dot offline';
            }
        } catch (error) {
            const statusDot = document.querySelector('.status-dot');
            statusDot.className = 'status-dot offline';
        }
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/300`;
        this.charCount.style.color = count > 250 ? '#ef4444' : '#64748b';
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.currentQuery = message;
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateCharCount();
        this.showTyping();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            this.hideTyping();
            
            if (data.response) {
                this.currentResponse = data.response;
                this.addMessage(data.response, 'bot', true);
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage('Connection error. Please check your internet connection.', 'bot');
        }
    }
    
    addMessage(content, sender, showCloseTicket = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Format the content with line breaks
        const formattedContent = content.replace(/\n/g, '<br>');
        let messageHTML = `<p>${formattedContent}</p>`;
        
        // Add ticket buttons for bot responses
        if (showCloseTicket && sender === 'bot') {
            messageHTML += `
                <div class="ticket-buttons">
                    <button class="raise-ticket-btn" onclick="window.chatbotInstance.openTicketModal()">
                        <i class="fas fa-plus-circle"></i> Raise Ticket
                    </button>
                    <button class="close-ticket-btn" onclick="window.chatbotInstance.openFeedbackModal()">
                        <i class="fas fa-ticket-alt"></i> Close Ticket
                    </button>
                </div>
            `;
        }
        
        messageContent.innerHTML = messageHTML;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Show notification if chat is closed and it's a bot message
        if (!this.isOpen && sender === 'bot') {
            this.showNotification();
        }
    }
    
    openTicketModal() {
        this.ticketModal.classList.add('show');
        document.getElementById('ticketName').focus();
    }
    
    closeTicketModal() {
        this.ticketModal.classList.remove('show');
        document.getElementById('ticketForm').reset();
    }
    
    openFeedbackModal() {
        this.feedbackModal.classList.add('show');
        document.getElementById('feedbackName').focus();
    }
    
    closeFeedbackModal() {
        this.feedbackModal.classList.remove('show');
        document.getElementById('feedbackForm').reset();
    }
    
    async submitFeedback(e) {
        e.preventDefault();
        
        const name = document.getElementById('feedbackName').value.trim();
        const email = document.getElementById('feedbackEmail').value.trim();
        const challenge = document.getElementById('feedbackChallenge').value.trim();
        const satisfaction = document.querySelector('input[name="satisfaction"]:checked')?.value;
        
        console.log('Form data:', { name, email, challenge, satisfaction });
        
        if (!name || !email || !challenge) {
            alert('Please fill in all required fields.');
            return;
        }
        
        if (!satisfaction) {
            alert('Please select a satisfaction rating.');
            return;
        }
        
        const submitBtn = e.target.querySelector('.btn-submit');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        try {
            console.log('Sending feedback request...');
            
            const requestData = {
                name,
                email,
                challenge,
                satisfaction: parseInt(satisfaction),
                query: this.currentQuery || '',
                response: this.currentResponse || ''
            };
            
            console.log('Request data:', requestData);
            
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                this.closeFeedbackModal();
                this.addMessage('✅ Thank you for your feedback! Your ticket has been closed successfully.', 'bot');
            } else {
                alert(`Error: ${data.error || 'Unknown error occurred'}`);
            }
        } catch (error) {
            console.error('Feedback submission error:', error);
            alert(`Connection error: ${error.message}. Please check if the server is running.`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Feedback';
        }
    }
    
    async submitTicket(e) {
        e.preventDefault();
        
        const name = document.getElementById('ticketName').value.trim();
        const email = document.getElementById('ticketEmail').value.trim();
        const reason = document.getElementById('ticketReason').value.trim();
        const priority = document.getElementById('ticketPriority').value;
        
        if (!name || !email || !reason || !priority) {
            alert('Please fill in all required fields.');
            return;
        }
        
        const submitBtn = e.target.querySelector('.btn-submit');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating Ticket...';
        
        try {
            const response = await fetch('/ticket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name,
                    email,
                    reason,
                    priority
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.closeTicketModal();
                
                // Create message with action buttons
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.innerHTML = '<i class="fas fa-robot"></i>';
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                
                let messageHTML = `<p>${data.message}</p>`;
                
                // Add action buttons if provided
                if (data.actions && data.actions.length > 0) {
                    messageHTML += '<div class="action-buttons" style="margin-top: 15px;">';
                    data.actions.forEach(action => {
                        if (action.type === 'external') {
                            messageHTML += `<a href="${action.url}" target="_blank" class="action-btn external-btn" style="display: inline-block; margin: 5px; padding: 8px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 12px;">${action.label}</a>`;
                        } else {
                            messageHTML += `<a href="${action.url}" target="_blank" class="action-btn internal-btn" style="display: inline-block; margin: 5px; padding: 8px 15px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-size: 12px;">${action.label}</a>`;
                        }
                    });
                    messageHTML += '</div>';
                }
                
                messageContent.innerHTML = messageHTML;
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(messageContent);
                
                this.chatMessages.appendChild(messageDiv);
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert(`Connection error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Ticket';
        }
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span>AI is thinking</span>
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    hideTyping() {
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }
}

// Quick message function
function sendQuickMessage(message) {
    const chatbot = window.chatbotInstance;
    if (chatbot) {
        chatbot.messageInput.value = message;
        chatbot.sendMessage();
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotInstance = new CornerChatBot();
});