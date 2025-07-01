// Shopify Returns Chat Widget - CSS Conflict Fixed Version
(function() {
    'use strict';

    const CONFIG = {
        apiUrl: 'https://shopify-returns-chat-agent-production.up.railway.app',
        theme: { primaryColor: '#4a154b' },
        texts: {
            welcome: "👋 Hi! I'm your returns assistant. I can help you look up orders and process returns.",
            placeholder: "Ask about an order or return...",
            buttonText: "Returns Help"
        }
    };

    let isOpen = false;
    let conversationId = null;

    function createWidget() {
        injectCSS();
        const widget = document.createElement('div');
        widget.id = 'rw-widget';
        widget.innerHTML = `
            <div class="rw-btn" id="rw-toggle">
                <span>🛍️ ${CONFIG.texts.buttonText}</span>
            </div>
            <div class="rw-panel" id="rw-panel" style="display: none;">
                <div class="rw-head">
                    <h3>🛍️ Returns Assistant</h3>
                    <button class="rw-x" id="rw-close">×</button>
                </div>
                <div class="rw-msgs" id="rw-msgs">
                    <div class="rw-msg rw-bot">${CONFIG.texts.welcome}</div>
                </div>
                <div class="rw-form-wrap">
                    <form id="rw-form">
                        <input type="text" id="rw-input" placeholder="${CONFIG.texts.placeholder}" maxlength="500" />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
        bindEvents();
        initChat();
    }

    function injectCSS() {
        const styles = `
            <style id="rw-styles">
                #rw-widget, #rw-widget * {
                    box-sizing: border-box !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                }
                
                #rw-widget {
                    position: fixed !important;
                    bottom: 20px !important;
                    right: 20px !important;
                    z-index: 999999 !important;
                    font-size: 14px !important;
                }
                
                .rw-btn {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69) !important;
                    color: white !important;
                    padding: 12px 20px !important;
                    border-radius: 25px !important;
                    cursor: pointer !important;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
                    transition: transform 0.2s !important;
                    user-select: none !important;
                    font-weight: 500 !important;
                }
                
                .rw-btn:hover {
                    transform: translateY(-2px) !important;
                }
                
                .rw-panel {
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
                    border: 1px solid #e0e0e0 !important;
                }
                
                .rw-head {
                    background: linear-gradient(135deg, ${CONFIG.theme.primaryColor}, #611f69) !important;
                    color: white !important;
                    padding: 15px 20px !important;
                    display: flex !important;
                    justify-content: space-between !important;
                    align-items: center !important;
                }
                
                .rw-head h3 {
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    color: white !important;
                }
                
                .rw-x {
                    background: none !important;
                    border: none !important;
                    color: white !important;
                    font-size: 18px !important;
                    cursor: pointer !important;
                    width: 24px !important;
                    height: 24px !important;
                    border-radius: 4px !important;
                }
                
                .rw-x:hover {
                    background: rgba(255,255,255,0.1) !important;
                }
                
                .rw-msgs {
                    flex: 1 !important;
                    padding: 15px !important;
                    overflow-y: auto !important;
                    display: flex !important;
                    flex-direction: column !important;
                    gap: 10px !important;
                }
                
                .rw-msg {
                    padding: 8px 12px !important;
                    border-radius: 15px !important;
                    max-width: 85% !important;
                    word-wrap: break-word !important;
                    line-height: 1.4 !important;
                    font-size: 14px !important;
                }
                
                .rw-msg.rw-user {
                    align-self: flex-end !important;
                    background: ${CONFIG.theme.primaryColor} !important;
                    color: white !important;
                    border-bottom-right-radius: 4px !important;
                }
                
                .rw-msg.rw-bot {
                    align-self: flex-start !important;
                    background: #f1f3f4 !important;
                    color: #333 !important;
                    border-bottom-left-radius: 4px !important;
                }
                
                .rw-form-wrap {
                    padding: 15px !important;
                    border-top: 1px solid #eee !important;
                }
                
                .rw-form-wrap form {
                    display: flex !important;
                    gap: 8px !important;
                }
                
                .rw-form-wrap input {
                    flex: 1 !important;
                    padding: 10px 12px !important;
                    border: 1px solid #ddd !important;
                    border-radius: 20px !important;
                    outline: none !important;
                    font-size: 14px !important;
                    background: white !important;
                    color: #333 !important;
                }
                
                .rw-form-wrap input:focus {
                    border-color: ${CONFIG.theme.primaryColor} !important;
                }
                
                .rw-form-wrap button {
                    background: ${CONFIG.theme.primaryColor} !important;
                    color: white !important;
                    border: none !important;
                    padding: 10px 16px !important;
                    border-radius: 20px !important;
                    cursor: pointer !important;
                    font-size: 14px !important;
                }
                
                .rw-form-wrap button:disabled {
                    opacity: 0.6 !important;
                    cursor: not-allowed !important;
                }

                @media (max-width: 480px) {
                    #rw-widget {
                        left: 10px !important;
                        right: 10px !important;
                    }
                    .rw-panel {
                        width: calc(100vw - 20px) !important;
                        height: 400px !important;
                    }
                    .rw-btn {
                        width: 100% !important;
                        text-align: center !important;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    function bindEvents() {
        document.getElementById('rw-toggle').addEventListener('click', toggleChat);
        document.getElementById('rw-close').addEventListener('click', closeChat);
        document.getElementById('rw-form').addEventListener('submit', sendMessage);
    }

    function initChat() {
        conversationId = 'conv_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    function toggleChat() {
        const panel = document.getElementById('rw-panel');
        if (isOpen) {
            panel.style.display = 'none';
            isOpen = false;
        } else {
            panel.style.display = 'flex';
            isOpen = true;
            setTimeout(() => document.getElementById('rw-input').focus(), 100);
        }
    }

    function closeChat() {
        document.getElementById('rw-panel').style.display = 'none';
        isOpen = false;
    }

    async function sendMessage(event) {
        event.preventDefault();
        
        const input = document.getElementById('rw-input');
        const button = event.target.querySelector('button');
        const message = input.value.trim();
        
        if (!message) return;

        addMessage(message, 'rw-user');
        input.value = '';
        input.disabled = true;
        button.disabled = true;
        button.textContent = 'Sending...';

        try {
            const response = await fetch(`${CONFIG.apiUrl}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            addMessage(data.response || data.message || 'Thanks for your message!', 'rw-bot');
            
        } catch (error) {
            console.error('Chat error:', error);
            addMessage('Sorry, I\'m having connection issues. Please try again or contact support.', 'rw-bot');
        } finally {
            input.disabled = false;
            button.disabled = false;
            button.textContent = 'Send';
            input.focus();
        }
    }

    function addMessage(text, className) {
        const messages = document.getElementById('rw-msgs');
        const messageDiv = document.createElement('div');
        messageDiv.className = `rw-msg ${className}`;
        messageDiv.textContent = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    function init() {
        const existing = document.getElementById('rw-widget');
        if (existing) existing.remove();
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createWidget);
        } else {
            createWidget();
        }
    }

    window.ReturnsWidget = { init, open: () => !isOpen && toggleChat(), close: () => isOpen && toggleChat() };
    init();
})(); 