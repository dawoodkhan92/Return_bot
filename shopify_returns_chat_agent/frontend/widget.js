// Shopify Returns Chat Widget - Integration Fixed Version
(function() {
    'use strict';

    // Configuration with dynamic API URL detection
    const CONFIG = {
        // Try to auto-detect the API URL, fallback to hardcoded
        apiUrl: window.RETURNS_API_URL || detectApiUrl() || 'https://returnbot-production.up.railway.app',
        debug: window.RETURNS_DEBUG || false,
        theme: {
            primaryColor: '#4a154b',
            backgroundColor: '#fff'
        },
        texts: {
            welcome: "👋 Hi! I'm your returns assistant. I can help you with order returns, exchanges, and refunds. What can I help you with today?",
            placeholder: "Ask about an order return, exchange, or refund...",
            buttonText: "Returns Help"
        }
    };

    let isOpen = false;
    let conversationId = null;
    let isInitialized = false;

    // Auto-detect API URL from current domain (for Railway deployments)
    function detectApiUrl() {
        // If we're on a Shopify store, try to detect the Railway URL
        const currentHost = window.location.hostname;
        
        // Common Railway URL patterns
        if (currentHost.includes('railway.app')) {
            return `https://${currentHost}`;
        }
        
        // For local development
        if (currentHost === 'localhost' || currentHost.includes('127.0.0.1')) {
            return 'http://localhost:8080';
        }
        
        // Try to get from meta tag if set by store owner
        const metaTag = document.querySelector('meta[name="returns-api-url"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        return null;
    }

    // Debug logging
    function debugLog(message, data = null) {
        if (CONFIG.debug) {
            console.log('[Returns Widget]', message, data);
        }
    }

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
                    <div class="returns-header-actions">
                        <span class="returns-status" id="connection-status">●</span>
                        <button class="returns-close" id="chat-close">×</button>
                    </div>
                </div>
                <div class="returns-messages" id="messages">
                    <div class="returns-message system">
                        ${CONFIG.texts.welcome}
                    </div>
                </div>
                <div class="returns-typing-indicator" id="typing-indicator" style="display: none;">
                    <div class="returns-typing-dot"></div>
                    <div class="returns-typing-dot"></div>
                    <div class="returns-typing-dot"></div>
                </div>
                <div class="returns-input">
                    <form id="chat-form">
                        <input type="text" id="chat-input" placeholder="${CONFIG.texts.placeholder}" maxlength="500" disabled />
                        <button type="submit" disabled>Send</button>
                    </form>
                </div>
                ${CONFIG.debug ? `<div class="returns-debug">API: ${CONFIG.apiUrl}</div>` : ''}
            </div>
        `;

        document.body.appendChild(widget);
        bindEvents();
        debugLog('Widget created', { apiUrl: CONFIG.apiUrl });
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
                
                /* Mobile responsive */
                @media screen and (max-width: 480px) {
                    .returns-chat-panel {
                        position: fixed;
                        bottom: 0;
                        right: 0;
                        left: 0;
                        width: 100%;
                        height: 70vh;
                        border-radius: 15px 15px 0 0;
                        max-height: 500px;
                    }
                    
                    #returns-widget {
                        bottom: 10px;
                        right: 10px;
                    }
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
                
                .returns-header-actions {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .returns-status {
                    font-size: 12px;
                    opacity: 0.8;
                }
                
                .returns-status.connected { color: #4CAF50; }
                .returns-status.connecting { color: #FF9800; }
                .returns-status.error { color: #F44336; }
                
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
                
                .returns-message.system {
                    align-self: flex-start;
                    background: #e3f2fd;
                    color: #1565c0;
                    border-bottom-left-radius: 4px;
                    font-style: italic;
                }
                
                .returns-message.error {
                    align-self: center;
                    background: #ffebee;
                    color: #c62828;
                    border: 1px solid #ffcdd2;
                    text-align: center;
                    font-size: 13px;
                }

                .returns-typing-indicator {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    padding: 8px 12px;
                    background: #f1f3f4;
                    border-radius: 15px;
                    border-bottom-left-radius: 4px;
                    align-self: flex-start;
                    margin: 0 15px 10px;
                }

                .returns-typing-dot {
                    width: 8px;
                    height: 8px;
                    background: #9ca3af;
                    border-radius: 50%;
                    animation: returns-typing-animation 1.4s infinite ease-in-out;
                }

                .returns-typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .returns-typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes returns-typing-animation {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
                    30% { transform: translateY(-4px); opacity: 1; }
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
                
                .returns-input input:disabled {
                    background-color: #f5f5f5;
                    cursor: not-allowed;
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
                
                .returns-input button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                
                .returns-debug {
                    padding: 8px 12px;
                    background: #fffde7;
                    border-top: 1px solid #f9fbe7;
                    font-size: 11px;
                    color: #827717;
                    font-family: monospace;
                }
            </style>
        `;

        // Remove existing styles
        const existingStyles = document.getElementById('returns-widget-styles');
        if (existingStyles) {
            existingStyles.remove();
        }

        // Inject new styles
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    // Bind events
    function bindEvents() {
        document.getElementById('chat-toggle').addEventListener('click', toggleChat);
        document.getElementById('chat-close').addEventListener('click', closeChat);
        document.getElementById('chat-form').addEventListener('submit', sendMessage);
    }

    // Initialize chat session
    async function initChat() {
        debugLog('Initializing chat...');
        setConnectionStatus('connecting');
        
        try {
            const response = await fetch(`${CONFIG.apiUrl}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_id: getCustomerId(),
                    shop_domain: getShopDomain()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            conversationId = data.conversation_id;
            
            debugLog('Chat initialized', { conversationId });
            setConnectionStatus('connected');
            enableInput();
            
            // Update welcome message if provided
            if (data.message) {
                const systemMessage = document.querySelector('.returns-message.system');
                if (systemMessage) {
                    systemMessage.textContent = data.message;
                }
            }
            
            isInitialized = true;
            
        } catch (error) {
            console.error('Failed to initialize chat:', error);
            debugLog('Chat initialization failed', error);
            setConnectionStatus('error');
            addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'error');
        }
    }

    // Toggle chat open/close
    function toggleChat() {
        if (isOpen) {
            closeChat();
        } else {
            const panel = document.getElementById('chat-panel');
            panel.style.display = 'flex';
            isOpen = true;
            
            // Initialize chat if not already done
            if (!isInitialized) {
                initChat();
            }
            
            // Focus input
            setTimeout(() => {
                const input = document.getElementById('chat-input');
                if (input && !input.disabled) {
                    input.focus();
                }
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
        const message = input.value.trim();
        
        if (!message || !conversationId) {
            return;
        }

        // Add user message to chat
        addMessage(message, 'user');
        input.value = '';
        
        // Disable input and show typing indicator
        disableInput();
        showTyping();
        
        try {
            debugLog('Sending message', { message, conversationId });
            
            const response = await fetch(`${CONFIG.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            debugLog('Received response', data);
            
            // Add assistant response
            if (data.response) {
                addMessage(data.response, 'assistant');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            debugLog('Message send failed', error);
            addMessage('Sorry, I encountered an error. Please try again.', 'error');
        } finally {
            hideTyping();
            enableInput();
        }
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `returns-message ${sender}`;
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Show/hide typing indicator
    function showTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }
        const messagesContainer = document.getElementById('messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    // Set connection status
    function setConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `returns-status ${status}`;
            const statusText = status === 'connecting' ? '◐' : '●';
            statusElement.textContent = statusText;
        }
    }

    // Enable input
    function enableInput() {
        const input = document.getElementById('chat-input');
        const button = document.querySelector('#chat-form button');
        
        if (input) {
            input.disabled = false;
            input.placeholder = CONFIG.texts.placeholder;
            input.focus();
        }
        if (button) {
            button.disabled = false;
        }
    }

    // Disable input
    function disableInput() {
        const input = document.getElementById('chat-input');
        const button = document.querySelector('#chat-form button');
        
        if (input) {
            input.disabled = true;
            input.placeholder = 'Sending...';
        }
        if (button) {
            button.disabled = true;
        }
    }

    // Get customer ID (if available from Shopify)
    function getCustomerId() {
        // Try to get from Shopify's customer object
        return window.ShopifyAnalytics?.meta?.page?.customerId || 
               window.meta?.page?.customerId || 
               null;
    }

    // Get shop domain
    function getShopDomain() {
        return window.Shopify?.shop || 
               window.ShopifyAnalytics?.meta?.page?.shop || 
               window.location.hostname;
    }

    // Initialize widget when DOM is ready
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createWidget);
        } else {
            createWidget();
        }
    }

    // Start initialization
    init();

})();
