// Shopify Returns Chat Widget - Fixed CSS Version
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
        // Inject CSS with better isolation
        injectCSS();
        
        // Create HTML
        const widget = document.createElement('div');
        widget.id = 'returns-widget-container';
        widget.innerHTML = `
            <div class="rw-chat-button" id="rw-chat-toggle">
                <span>🛍️ ${CONFIG.texts.buttonText}</span>
            </div>
            <div class="rw-chat-panel" id="rw-chat-panel" style="display: none;">
                <div class="rw-header">
                    <h3>🛍️ Returns Assistant</h3>
                    <button class="rw-close" id="rw-chat-close">×</button>
                </div>
                <div class="rw-messages" id="rw-messages">
                    <div class="rw-message rw-assistant">
                        ${CONFIG.texts.welcome}
                    </div>
                </div>
                <div class="rw-input">
                    <form id="rw-chat-form">
                        <input type="text" id="rw-chat-input" placeholder="${CONFIG.texts.placeholder}" maxlength="500" />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
        bindEvents();
        initChat();
    }

    // Inject CSS styles with better isolation
    function injectCSS() {
        const styles = `
            <style id="returns-widget-fixed-styles">
                /* Reset and isolate widget styles */
                #returns-widget-container,
                #returns-widget-container * {
                    box-sizing: border-box !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                    line-height: normal !important;
                    text-decoration: none !important;
                    border: none !important;
                    outline: none !important;
                    background: transparent !important;
                    color: inherit !important;
                }
                
                #returns-widget-container {
                    position: fixed !important;
                    bottom: 20px !important;
                    right: 20px !important;
                    z-index: 999999 !important;
                    font-size: 14px !important;
                    font-weight: normal !important;
                    text-align: left !important;
                    direction: ltr !important;
                    width: auto !important;
                    height: auto !important;
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                    transform: none !important;
                    pointer-events: auto !important;
                }
                
                #returns-widget-container .rw-chat-button {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69) !important;
                    color: white !important;
                    padding: 12px 20px !important;
                    border-radius: 25px !important;
                    cursor: pointer !important;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
                    transition: transform 0.2s ease !important;
                    user-select: none !important;
                    display: block !important;
                    text-align: center !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    border: none !important;
                    margin: 0 !important;
                }
                
                #returns-widget-container .rw-chat-button:hover {
                    transform: translateY(-2px) !important;
                }
                
                #returns-widget-container .rw-chat-panel {
                    position: absolute !important;
                    bottom: 60px !important;
                    right: 0 !important;
                    width: 350px !important;
                    height: 450px !important;
                    background: white !important;
                    border-radius: 15px !important;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.15) !important;
                    display: flex !important;
                    flex-direction: column !important;
                    overflow: hidden !important;
                    animation: rw-slideUp 0.3s ease !important;
                    border: 1px solid #e0e0e0 !important;
                }
                
                @keyframes rw-slideUp {
                    from { 
                        opacity: 0 !important; 
                        transform: translateY(20px) !important; 
                    }
                    to { 
                        opacity: 1 !important; 
                        transform: translateY(0) !important; 
                    }
                }
                
                #returns-widget-container .rw-header {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69) !important;
                    color: white !important;
                    padding: 15px 20px !important;
                    display: flex !important;
                    justify-content: space-between !important;
                    align-items: center !important;
                }
                
                #returns-widget-container .rw-header h3 {
                    margin: 0 !important;
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    color: white !important;
                }
                
                #returns-widget-container .rw-close {
                    background: none !important;
                    border: none !important;
                    color: white !important;
                    font-size: 20px !important;
                    cursor: pointer !important;
                    padding: 0 !important;
                    width: 24px !important;
                    height: 24px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    border-radius: 4px !important;
                }
                
                #returns-widget-container .rw-close:hover {
                    background: rgba(255,255,255,0.1) !important;
                }
                
                #returns-widget-container .rw-messages {
                    flex: 1 !important;
                    padding: 15px !important;
                    overflow-y: auto !important;
                    display: flex !important;
                    flex-direction: column !important;
                    gap: 10px !important;
                    background: white !important;
                }
                
                #returns-widget-container .rw-message {
                    padding: 8px 12px !important;
                    border-radius: 15px !important;
                    max-width: 85% !important;
                    word-wrap: break-word !important;
                    line-height: 1.4 !important;
                    font-size: 14px !important;
                    margin: 0 !important;
                    display: block !important;
                }
                
                #returns-widget-container .rw-message.rw-user {
                    align-self: flex-end !important;
                    background: ${CONFIG.theme.primaryColor} !important;
                    color: white !important;
                    border-bottom-right-radius: 4px !important;
                    margin-left: auto !important;
                }
                
                #returns-widget-container .rw-message.rw-assistant {
                    align-self: flex-start !important;
                    background: #f1f3f4 !important;
                    color: #333 !important;
                    border-bottom-left-radius: 4px !important;
                    margin-right: auto !important;
                }
                
                #returns-widget-container .rw-input {
                    padding: 15px !important;
                    border-top: 1px solid #eee !important;
                    background: white !important;
                }
                
                #returns-widget-container .rw-input form {
                    display: flex !important;
                    gap: 8px !important;
                    align-items: center !important;
                }
                
                #returns-widget-container .rw-input input {
                    flex: 1 !important;
                    padding: 10px 12px !important;
                    border: 1px solid #ddd !important;
                    border-radius: 20px !important;
                    outline: none !important;
                    font-size: 14px !important;
                    color: #333 !important;
                    background: white !important;
                }
                
                #returns-widget-container .rw-input input:focus {
                    border-color: ${CONFIG.theme.primaryColor} !important;
                }
                
                #returns-widget-container .rw-input button {
                    background: ${CONFIG.theme.primaryColor} !important;
                    color: white !important;
                    border: none !important;
                    padding: 10px 16px !important;
                    border-radius: 20px !important;
                    cursor: pointer !important;
                    font-size: 14px !important;
                    transition: opacity 0.2s ease !important;
                }
                
                #returns-widget-container .rw-input button:hover:not(:disabled) {
                    opacity: 0.9 !important;
                }
                
                #returns-widget-container .rw-input button:disabled {
                    opacity: 0.6 !important;
                    cursor: not-allowed !important;
                }

                /* Mobile responsive */
                @media (max-width: 480px) {
                    #returns-widget-container {
                        bottom: 10px !important;
                        right: 10px !important;
                        left: 10px !important;
                    }
                    
                    #returns-widget-container .rw-chat-panel {
                        width: calc(100vw - 20px) !important;
                        height: 400px !important;
                        right: 0 !important;
                        left: 0 !important;
                    }
                    
                    #returns-widget-container .rw-chat-button {
                        width: 100% !important;
                        text-align: center !important;
                    }
                }

                /* Override any theme conflicts */
                #returns-widget-container .rw-messages::-webkit-scrollbar {
                    width: 4px !important;
                }
                
                #returns-widget-container .rw-messages::-webkit-scrollbar-thumb {
                    background: #ddd !important;
                    border-radius: 2px !important;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    // Bind event listeners
    function bindEvents() {
        document.getElementById('rw-chat-toggle').addEventListener('click', toggleChat);
        document.getElementById('rw-chat-close').addEventListener('click', closeChat);
        document.getElementById('rw-chat-form').addEventListener('submit', sendMessage);
    }

    // Initialize chat
    function initChat() {
        conversationId = 'conv_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    // Toggle chat panel
    function toggleChat() {
        const panel = document.getElementById('rw-chat-panel');
        if (isOpen) {
            panel.style.display = 'none';
            isOpen = false;
        } else {
            panel.style.display = 'flex';
            isOpen = true;
            setTimeout(() => {
                document.getElementById('rw-chat-input').focus();
            }, 100);
        }
    }

    // Close chat
    function closeChat() {
        document.getElementById('rw-chat-panel').style.display = 'none';
        isOpen = false;
    }

    // Send message
    async function sendMessage(event) {
        event.preventDefault();
        
        const input = document.getElementById('rw-chat-input');
        const button = event.target.querySelector('button');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message
        addMessage(message, 'rw-user');
        
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

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            addMessage(data.response || data.message || 'I received your message!', 'rw-assistant');
            
        } catch (error) {
            console.error('Chat error:', error);
            addMessage('I apologize, but I\'m having trouble connecting right now. Please try again in a moment, or contact support if the issue persists.', 'rw-assistant');
        } finally {
            // Re-enable input
            input.disabled = false;
            button.disabled = false;
            button.textContent = 'Send';
            input.focus();
        }
    }

    // Add message to chat
    function addMessage(text, className) {
        const messages = document.getElementById('rw-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `rw-message ${className}`;
        messageDiv.textContent = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    // Initialize widget
    function init() {
        // Remove any existing widget
        const existing = document.getElementById('returns-widget-container');
        if (existing) {
            existing.remove();
        }
        
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