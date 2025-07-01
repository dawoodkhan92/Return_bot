// Simple Returns Chat Widget - Clean Version
(function() {
    'use strict';

    // Prevent multiple instances
    if (window.ReturnsWidgetLoaded) {
        return;
    }
    window.ReturnsWidgetLoaded = true;

    const API_URL = 'https://shopify-returns-chat-agent-production.up.railway.app';
    let isOpen = false;
    let conversationId = null;

    // Create widget
    function createWidget() {
        // Remove any existing widget
        const existing = document.getElementById('returns-widget-clean');
        if (existing) {
            existing.remove();
        }

        // Create container
        const widget = document.createElement('div');
        widget.id = 'returns-widget-clean';
        widget.innerHTML = `
            <style>
                #returns-widget-clean {
                    position: fixed !important;
                    bottom: 20px !important;
                    right: 20px !important;
                    z-index: 999999 !important;
                    font-family: Arial, sans-serif !important;
                }
                
                .rw-button {
                    background: #4a154b !important;
                    color: white !important;
                    padding: 12px 16px !important;
                    border-radius: 25px !important;
                    cursor: pointer !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
                    border: none !important;
                    font-size: 14px !important;
                    font-weight: 600 !important;
                    transition: transform 0.2s !important;
                    display: block !important;
                }
                
                .rw-button:hover {
                    transform: translateY(-2px) !important;
                }
                
                .rw-chat {
                    position: absolute !important;
                    bottom: 60px !important;
                    right: 0 !important;
                    width: 320px !important;
                    height: 400px !important;
                    background: white !important;
                    border-radius: 12px !important;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
                    display: none !important;
                    flex-direction: column !important;
                    overflow: hidden !important;
                    border: 1px solid #e0e0e0 !important;
                }
                
                .rw-header {
                    background: #4a154b !important;
                    color: white !important;
                    padding: 12px 16px !important;
                    display: flex !important;
                    justify-content: space-between !important;
                    align-items: center !important;
                }
                
                .rw-close {
                    background: none !important;
                    border: none !important;
                    color: white !important;
                    font-size: 18px !important;
                    cursor: pointer !important;
                    padding: 4px !important;
                    border-radius: 4px !important;
                }
                
                .rw-messages {
                    flex: 1 !important;
                    padding: 12px !important;
                    overflow-y: auto !important;
                    background: #f9f9f9 !important;
                }
                
                .rw-message {
                    margin-bottom: 8px !important;
                    padding: 8px 12px !important;
                    border-radius: 12px !important;
                    max-width: 80% !important;
                    word-wrap: break-word !important;
                    font-size: 13px !important;
                    line-height: 1.4 !important;
                }
                
                .rw-message.user {
                    background: #4a154b !important;
                    color: white !important;
                    margin-left: auto !important;
                    margin-right: 0 !important;
                }
                
                .rw-message.assistant {
                    background: white !important;
                    color: #333 !important;
                    border: 1px solid #e0e0e0 !important;
                }
                
                .rw-input {
                    padding: 12px !important;
                    border-top: 1px solid #e0e0e0 !important;
                    background: white !important;
                }
                
                .rw-form {
                    display: flex !important;
                    gap: 8px !important;
                }
                
                .rw-form input {
                    flex: 1 !important;
                    padding: 8px 12px !important;
                    border: 1px solid #ddd !important;
                    border-radius: 16px !important;
                    outline: none !important;
                    font-size: 13px !important;
                }
                
                .rw-form button {
                    background: #4a154b !important;
                    color: white !important;
                    border: none !important;
                    padding: 8px 12px !important;
                    border-radius: 16px !important;
                    cursor: pointer !important;
                    font-size: 13px !important;
                }
            </style>
            
            <button class="rw-button" onclick="window.toggleReturnsChat()">
                🛍️ Returns Help
            </button>
            
            <div class="rw-chat" id="rw-chat">
                <div class="rw-header">
                    <span>Returns Assistant</span>
                    <button class="rw-close" onclick="window.closeReturnsChat()">×</button>
                </div>
                <div class="rw-messages" id="rw-messages">
                    <div class="rw-message assistant">
                        Hi! I'm your returns assistant. I can help you look up orders and process returns.
                    </div>
                </div>
                <div class="rw-input">
                    <form class="rw-form" onsubmit="window.sendReturnsMessage(event)">
                        <input type="text" id="rw-input" placeholder="Ask about an order or return..." maxlength="300" />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
    }

    // Toggle chat open/close
    window.toggleReturnsChat = function() {
        const chat = document.getElementById('rw-chat');
        if (isOpen) {
            chat.style.display = 'none';
            isOpen = false;
        } else {
            chat.style.display = 'flex';
            isOpen = true;
        }
    };

    // Close chat
    window.closeReturnsChat = function() {
        document.getElementById('rw-chat').style.display = 'none';
        isOpen = false;
    };

    // Send message
    window.sendReturnsMessage = async function(event) {
        event.preventDefault();
        
        const input = document.getElementById('rw-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        input.value = '';
        
        // Show typing indicator
        addMessage('Typing...', 'assistant');
        
        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            const messages = document.getElementById('rw-messages');
            messages.removeChild(messages.lastChild);
            
            if (response.ok) {
                addMessage(data.response, 'assistant');
                conversationId = data.conversation_id;
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        } catch (error) {
            // Remove typing indicator
            const messages = document.getElementById('rw-messages');
            messages.removeChild(messages.lastChild);
            addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    };

    // Add message to chat
    function addMessage(text, sender) {
        const messages = document.getElementById('rw-messages');
        const message = document.createElement('div');
        message.className = `rw-message ${sender}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }

    // Initialize when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})(); 