// Shopify Returns Chat Widget - Integration Fixed Version
(function() {
    'use strict';

    // Configuration with dynamic API URL detection
    const CONFIG = {
        // Try to auto-detect the API URL, fallback to hardcoded
        apiUrl: window.RETURNS_API_URL || detectApiUrl() || 'https://returnbot-production.up.railway.app',
        debug: window.RETURNS_DEBUG || false,
        theme: {
            primaryColor: '#667eea',
            secondaryColor: '#764ba2',
            backgroundColor: '#fff',
            textColor: '#333',
            successColor: '#10b981',
            errorColor: '#ef4444'
        },
        texts: {
            welcome: "✨ Hi there! I'm your AI returns assistant. I'm here to make returns and exchanges super easy for you. What can I help you with today?",
            placeholder: "Ask me anything about returns, exchanges, or refunds...",
            buttonText: "💬 Returns Help",
            thinking: "Let me think about that...",
            typing: "AI is typing"
        },
        animations: {
            messageDuration: 300,
            typingDelay: 1000,
            buttonPulse: true
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
            <div class="returns-chat-button ${CONFIG.animations.buttonPulse ? 'pulse' : ''}" id="chat-toggle">
                <span>` + CONFIG.texts.buttonText + `</span>
            </div>
            <div class="returns-chat-panel" id="chat-panel" style="display: none;">
                <div class="returns-header">
                    <h3>AI Returns Assistant</h3>
                    <div class="returns-header-actions">
                        <span class="returns-status" id="connection-status">●</span>
                        <button class="returns-close" id="chat-close">×</button>
                    </div>
                </div>
                <div class="quick-actions" id="quick-actions" style="display: none;">
                    <button class="quick-action-btn" data-action="check-order">📦 Check Order Status</button>
                    <button class="quick-action-btn" data-action="start-return">🔄 Start Return</button>
                    <button class="quick-action-btn" data-action="exchange-item">🔄 Exchange Item</button>
                </div>
                <div class="returns-messages" id="messages">
                    <div class="returns-message system">
                        ` + CONFIG.texts.welcome + `
                    </div>
                </div>
                <div class="returns-typing-indicator" id="typing-indicator" style="display: none;">
                    <span class="typing-text">` + CONFIG.texts.thinking + `</span>
                    <div class="returns-typing-dot"></div>
                    <div class="returns-typing-dot"></div>
                    <div class="returns-typing-dot"></div>
                </div>
                <div class="returns-input">
                    <form id="chat-form">
                        <input type="text" id="chat-input" placeholder="` + CONFIG.texts.placeholder + `" maxlength="500" disabled />
                        <button type="submit" disabled>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9"></polygon>
                            </svg>
                        </button>
                    </form>
                </div>
                ` + (CONFIG.debug ? `<div class="returns-debug">API: ` + CONFIG.apiUrl + `</div>` : '') + `
            </div>
        `;

        document.body.appendChild(widget);
        bindEvents();
        debugLog('Widget created', { apiUrl: CONFIG.apiUrl });
    }

    // Inject CSS styles
    function injectCSS() {
        const primaryColor = CONFIG.theme.primaryColor;
        const secondaryColor = CONFIG.theme.secondaryColor;
        const messageDuration = CONFIG.animations.messageDuration;
        
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
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    color: white;
                    padding: 14px 24px;
                    border-radius: 30px;
                    cursor: pointer;
                    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    user-select: none;
                    font-weight: 500;
                    font-size: 15px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    position: relative;
                    overflow: hidden;
                }
                
                .returns-chat-button::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    transition: left 0.5s;
                }
                
                .returns-chat-button:hover::before {
                    left: 100%;
                }
                
                .returns-chat-button:hover {
                    transform: translateY(-4px) scale(1.02);
                    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
                }
                
                .returns-chat-button:active {
                    transform: translateY(-2px) scale(1.01);
                }
                
                .returns-chat-button.pulse {
                    animation: gentle-pulse 3s ease-in-out infinite;
                }
                
                @keyframes gentle-pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
                
                .returns-chat-panel {
                    position: absolute;
                    bottom: 70px;
                    right: 0;
                    width: 380px;
                    height: 500px;
                    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.15), 0 0 0 1px rgba(255,255,255,0.8);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: slideUpScale 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
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
                
                @keyframes slideUpScale {
                    from { 
                        opacity: 0; 
                        transform: translateY(30px) scale(0.9); 
                        filter: blur(5px);
                    }
                    to { 
                        opacity: 1; 
                        transform: translateY(0) scale(1); 
                        filter: blur(0px);
                    }
                }
                
                @keyframes messageSlideIn {
                    from {
                        opacity: 0;
                        transform: translateY(15px) scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }
                
                @keyframes shimmer {
                    0% { background-position: -200px 0; }
                    100% { background-position: calc(200px + 100%) 0; }
                }
                
                .returns-header {
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    color: white;
                    padding: 20px 24px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    position: relative;
                    overflow: hidden;
                }
                
                .returns-header::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(255,255,255,0.1) 100%);
                    background-size: 200% 200%;
                    animation: headerShine 3s ease-in-out infinite;
                }
                
                @keyframes headerShine {
                    0%, 100% { background-position: 0% 0%; }
                    50% { background-position: 100% 100%; }
                }
                
                .returns-header h3 {
                    margin: 0;
                    font-size: 18px;
                    font-weight: 600;
                    z-index: 1;
                    position: relative;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .returns-header h3::before {
                    content: '🤖';
                    animation: bounce 2s ease-in-out infinite;
                }
                
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                    40% { transform: translateY(-3px); }
                    60% { transform: translateY(-2px); }
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
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 85%;
                    word-wrap: break-word;
                    line-height: 1.5;
                    font-size: 14px;
                    animation: messageSlideIn ` + messageDuration + `ms cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                    margin: 4px 0;
                }
                
                .returns-message.user {
                    align-self: flex-end;
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    color: white;
                    border-bottom-right-radius: 6px;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                    position: relative;
                }
                
                .returns-message.user::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    right: -8px;
                    width: 0;
                    height: 0;
                    border: 8px solid transparent;
                    border-left-color: ` + secondaryColor + `;
                    border-bottom: 0;
                    border-right: 0;
                }
                
                .returns-message.assistant {
                    align-self: flex-start;
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    color: #1e293b;
                    border-bottom-left-radius: 6px;
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
                    position: relative;
                }
                
                .returns-message.assistant::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: -8px;
                    width: 0;
                    height: 0;
                    border: 8px solid transparent;
                    border-right-color: #e2e8f0;
                    border-bottom: 0;
                    border-left: 0;
                }
                
                .returns-message.system {
                    align-self: center;
                    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                    color: #1e40af;
                    border-radius: 18px;
                    font-style: normal;
                    font-weight: 500;
                    border: 1px solid rgba(59, 130, 246, 0.2);
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
                    text-align: center;
                    max-width: 90%;
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
                    gap: 8px;
                    padding: 12px 16px;
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    border-radius: 18px;
                    border-bottom-left-radius: 6px;
                    align-self: flex-start;
                    margin: 4px 15px 10px;
                    animation: messageSlideIn 0.3s ease;
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    position: relative;
                }
                
                .returns-typing-indicator::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: -8px;
                    width: 0;
                    height: 0;
                    border: 8px solid transparent;
                    border-right-color: #e2e8f0;
                    border-bottom: 0;
                    border-left: 0;
                }
                
                .typing-text {
                    font-size: 13px;
                    color: #64748b;
                    font-style: italic;
                }

                .returns-typing-dot {
                    width: 10px;
                    height: 10px;
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    border-radius: 50%;
                    animation: returns-typing-animation 1.4s infinite ease-in-out;
                    box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
                }

                .returns-typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .returns-typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes returns-typing-animation {
                    0%, 60%, 100% { 
                        transform: translateY(0) scale(1); 
                        opacity: 0.5; 
                    }
                    30% { 
                        transform: translateY(-6px) scale(1.2); 
                        opacity: 1; 
                    }
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
                    padding: 12px 18px;
                    border: 2px solid #e2e8f0;
                    border-radius: 25px;
                    outline: none;
                    font-size: 14px;
                    background: #ffffff;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
                }
                
                .returns-input input:focus {
                    border-color: ` + primaryColor + `;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.05);
                    transform: translateY(-1px);
                }
                
                .returns-input input:disabled {
                    background-color: #f5f5f5;
                    cursor: not-allowed;
                }
                
                .returns-input button {
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    color: white;
                    border: none;
                    padding: 12px 18px;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                    position: relative;
                    overflow: hidden;
                }
                
                .returns-input button::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    transition: left 0.5s;
                }
                
                .returns-input button:hover::before {
                    left: 100%;
                }
                
                .returns-input button:hover:not(:disabled) {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                }
                
                .returns-input button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
                
                .quick-actions {
                    padding: 15px 20px;
                    background: #f8fafc;
                    border-bottom: 1px solid #e2e8f0;
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                    animation: slideDown 0.3s ease;
                }
                
                @keyframes slideDown {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .quick-action-btn {
                    background: linear-gradient(135deg, #ffffff, #f1f5f9);
                    border: 1px solid #e2e8f0;
                    border-radius: 20px;
                    padding: 8px 12px;
                    font-size: 13px;
                    color: #475569;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-weight: 500;
                }
                
                .quick-action-btn:hover {
                    background: linear-gradient(135deg, ` + primaryColor + `, ` + secondaryColor + `);
                    color: white;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
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
        
        // Bind quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', handleQuickAction);
        });
        
        // Add input focus events for better UX
        const input = document.getElementById('chat-input');
        input.addEventListener('focus', () => {
            document.getElementById('quick-actions').style.display = 'none';
        });
        
        input.addEventListener('blur', () => {
            if (!input.value.trim()) {
                setTimeout(() => {
                    document.getElementById('quick-actions').style.display = 'flex';
                }, 100);
            }
        });
    }
    
    // Handle quick action button clicks
    function handleQuickAction(event) {
        const action = event.target.getAttribute('data-action');
        const input = document.getElementById('chat-input');
        
        let message = '';
        switch(action) {
            case 'check-order':
                message = 'I\'d like to check my order status';
                break;
            case 'start-return':
                message = 'I need to return an item';
                break;
            case 'exchange-item':
                message = 'I\'d like to exchange an item for a different size';
                break;
        }
        
        if (message) {
            input.value = message;
            document.getElementById('quick-actions').style.display = 'none';
            input.focus();
            
            // Auto-submit after a brief delay
            setTimeout(() => {
                const form = document.getElementById('chat-form');
                const submitEvent = new Event('submit');
                form.dispatchEvent(submitEvent);
            }, 500);
        }
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
                    systemMessage.innerHTML = formatMessage(data.message);
                }
            }
            
            // Show quick actions after connection
            setTimeout(() => {
                const quickActions = document.getElementById('quick-actions');
                if (quickActions) {
                    quickActions.style.display = 'flex';
                }
            }, 1500);
            
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
            
            // Show quick actions initially
            setTimeout(() => {
                const quickActions = document.getElementById('quick-actions');
                if (quickActions && !document.getElementById('chat-input').value.trim()) {
                    quickActions.style.display = 'flex';
                }
            }, 1000);
            
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
        
        // Disable input and show typing indicator with delay for realism
        disableInput();
        
        // Add realistic delay before showing typing indicator
        setTimeout(() => {
            showTyping();
        }, 300);
        
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
            
            // Add assistant response with realistic delay
            if (data.response) {
                // Hide typing first
                hideTyping();
                
                // Add realistic delay before showing response
                setTimeout(() => {
                    addMessage(data.response, 'assistant');
                    enableInput();
                }, 500);
            } else {
                enableInput();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            debugLog('Message send failed', error);
            addMessage('Sorry, I encountered an error. Please try again.', 'error');
        } catch (error) {
            console.error('Error sending message:', error);
            debugLog('Message send failed', error);
            hideTyping();
            addMessage('Sorry, I encountered an error. Please try again.', 'error');
            enableInput();
        }
    }

    // Add message to chat with enhanced animations
    function addMessage(text, sender) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `returns-message ${sender}`;
        
        // Enhanced text processing for better display
        if (sender === 'assistant') {
            // Process emojis and formatting
            messageDiv.innerHTML = formatMessage(text);
        } else {
            messageDiv.textContent = text;
        }
        
        // Add with animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(15px) scale(0.95)';
        messagesContainer.appendChild(messageDiv);
        
        // Trigger animation
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0) scale(1)';
        }, 50);
        
        // Smooth scroll to bottom
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Format assistant messages for better display
    function formatMessage(text) {
        // Simple formatting - replace line breaks and enhance emojis
        return text
            .replace(/\n/g, '<br>')
            .replace(/✨/g, '<span style="color: #fbbf24;">✨</span>')
            .replace(/🎯/g, '<span style="color: #ef4444;">🎯</span>')
            .replace(/💝/g, '<span style="color: #ec4899;">💝</span>')
            .replace(/👍/g, '<span style="color: #10b981;">👍</span>')
            .replace(/📦/g, '<span style="color: #8b5cf6;">📦</span>');
    }

    // Show/hide typing indicator with smooth animation
    function showTyping() {
        const indicator = document.getElementById('typing-indicator');
        const messagesContainer = document.getElementById('messages');
        
        if (indicator) {
            indicator.style.display = 'flex';
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                indicator.style.transition = 'all 0.3s ease';
                indicator.style.opacity = '1';
                indicator.style.transform = 'translateY(0)';
            }, 50);
            
            // Smooth scroll to show typing indicator
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }

    function hideTyping() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.transition = 'all 0.2s ease';
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-5px)';
            
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 200);
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

    // Enable input with enhanced UX
    function enableInput() {
        const input = document.getElementById('chat-input');
        const button = document.querySelector('#chat-form button');
        
        if (input) {
            input.disabled = false;
            input.placeholder = CONFIG.texts.placeholder;
            
            // Add subtle animation when enabled
            input.style.transition = 'all 0.3s ease';
            input.style.transform = 'scale(1)';
            
            // Focus with slight delay to ensure it's ready
            setTimeout(() => {
                if (!document.activeElement || document.activeElement === document.body) {
                    input.focus();
                }
            }, 100);
        }
        if (button) {
            button.disabled = false;
            button.style.opacity = '1';
        }
    }

    // Disable input with visual feedback
    function disableInput() {
        const input = document.getElementById('chat-input');
        const button = document.querySelector('#chat-form button');
        
        if (input) {
            input.disabled = true;
            input.placeholder = 'AI is thinking...';
            input.style.transform = 'scale(0.98)';
        }
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
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
