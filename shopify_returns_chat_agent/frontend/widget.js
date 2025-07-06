// Shopify Returns Chat Widget
(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        apiUrl: 'https://shopify-returns-chat-agent-production.up.railway.app',
        theme: {
            primaryColor: '#4a154b',
            backgroundColor: '#fff'
        },
        texts: {
            welcome: "👋 Hi! I'm your returns assistant. I can help you look up orders and process returns.",
            placeholder: "Ask about an order or return...",
            buttonText: "Returns Help"
        }
    };

    let isOpen = false;
    let conversationId = null;

    // Create the widget
    function createWidget() {
        // Inject CSS
        injectCSS();
        
        // Create HTML
        const widget = document.createElement('div');
        widget.id = 'returns-widget';
        widget.innerHTML = `
            <div class="returns-chat-button" id="chat-toggle">
                <span>🛍️ ${CONFIG.texts.buttonText}</span>
            </div>
            <div class="returns-chat-panel" id="chat-panel" style="display: none;">
                <div class="returns-header">
                    <h3>🛍️ Returns Assistant</h3>
                    <button class="returns-close" id="chat-close">×</button>
                </div>
                <div class="returns-messages" id="messages">
                    <div class="returns-message assistant">
                        ${CONFIG.texts.welcome}
                    </div>
                </div>
                <div class="returns-input">
                    <form id="chat-form">
                        <input type="text" id="chat-input" placeholder="${CONFIG.texts.placeholder}" maxlength="500" />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
        bindEvents();
        initChat();
    }

    // Inject CSS styles
    function injectCSS() {
        const styles = `
            <style id="returns-widget-styles">
                #returns-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 999999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .returns-chat-button {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 25px;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                    transition: transform 0.2s;
                    user-select: none;
                }
                
                .returns-chat-button:hover {
                    transform: translateY(-2px);
                }
                
                .returns-chat-panel {
                    position: absolute;
                    bottom: 60px;
                    right: 0;
                    width: 350px;
                    height: 450px;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideUp 0.3s ease;
                }
                
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .returns-header {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69);
                    color: white;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .returns-header h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                
                .returns-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                }
                
                .returns-close:hover {
                    background: rgba(255,255,255,0.1);
                }
                
                .returns-messages {
                    flex: 1;
                    padding: 15px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .returns-message {
                    padding: 8px 12px;
                    border-radius: 15px;
                    max-width: 85%;
                    word-wrap: break-word;
                    line-height: 1.4;
                    font-size: 14px;
                }
                
                .returns-message.user {
                    align-self: flex-end;
                    background: ${CONFIG.theme.primaryColor};
                    color: white;
                    border-bottom-right-radius: 4px;
                }
                
                .returns-message.assistant {
                    align-self: flex-start;
                    background: #f1f3f4;
                    color: #333;
                    border-bottom-left-radius: 4px;
                }
                
                .returns-input {
                    padding: 15px;
                    border-top: 1px solid #eee;
                }
                
                .returns-input form {
                    display: flex;
                    gap: 8px;
                }
                
                .returns-input input {
                    flex: 1;
                    padding: 10px 12px;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    outline: none;
                    font-size: 14px;
                }
                
                .returns-input input:focus {
                    border-color: ${CONFIG.theme.primaryColor};
                }
                
                .returns-input button {
                    background: ${CONFIG.theme.primaryColor};
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: opacity 0.2s;
                }
                
                .returns-input button:hover:not(:disabled) {
                    opacity: 0.9;
                }
                
                .returns-input button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                @media (max-width: 480px) {
                    #returns-widget {
                        bottom: 10px;
                        right: 10px;
                        left: 10px;
                    }
                    
                    .returns-chat-panel {
                        width: 100%;
                        height: 400px;
                    }
                    
                    .returns-chat-button {
                        width: 100%;
                        text-align: center;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    // Bind event listeners
    function bindEvents() {
        document.getElementById('chat-toggle').addEventListener('click', toggleChat);
        document.getElementById('chat-close').addEventListener('click', closeChat);
        document.getElementById('chat-form').addEventListener('submit', sendMessage);
    }

    // Initialize chat
    function initChat() {
        conversationId = 'conv_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    // Toggle chat panel
    function toggleChat() {
        const panel = document.getElementById('chat-panel');
        if (isOpen) {
            panel.style.display = 'none';
            isOpen = false;
        } else {
            panel.style.display = 'flex';
            isOpen = true;
            setTimeout(() => {
                document.getElementById('chat-input').focus();
            }, 100);
        }
    }

    // Close chat
    function closeChat() {
        document.getElementById('chat-panel').style.display = 'none';
        isOpen = false;
    }

    // Send message
    async function sendMessage(event) {
        event.preventDefault();
        
        const input = document.getElementById('chat-input');
        const button = event.target.querySelector('button');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        
        // Clear input and disable
        input.value = '';
        input.disabled = true;
        button.disabled = true;
        button.textContent = 'Sending...';

        try {
            // Call API
            const response = await fetch(`${CONFIG.apiUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) throw new Error('Network error');
            
            const data = await response.json();
            addMessage(data.response, 'assistant');
            
        } catch (error) {
            console.error('Chat error:', error);
            addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            // Re-enable input
            input.disabled = false;
            button.disabled = false;
            button.textContent = 'Send';
            input.focus();
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messages = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `returns-message ${sender}`;
        messageDiv.textContent = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    // Initialize widget
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createWidget);
        } else {
            createWidget();
        }
    }

    // Expose public API
    window.ReturnsWidget = {
        init: init,
        open: () => isOpen ? null : toggleChat(),
        close: () => isOpen ? toggleChat() : null
    };

    // Auto-initialize
    init();
})();
