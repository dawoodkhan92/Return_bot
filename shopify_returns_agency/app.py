from flask import Flask, request, jsonify
import os
import logging
import sys
import hmac
import hashlib
import base64
from config import config

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from agents.returns_agent import ReturnsAgent

def verify_shopify_webhook(data, hmac_header, secret):
    """
    Verify that the webhook came from Shopify using HMAC signature.
    
    Args:
        data (bytes): The raw request body
        hmac_header (str): The X-Shopify-Hmac-SHA256 header value
        secret (str): The Shopify webhook secret
        
    Returns:
        bool: True if the webhook is verified, False otherwise
    """
    if not secret or not hmac_header:
        return False
        
    calculated_hmac = base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(calculated_hmac, hmac_header)

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    
    # Get configuration instance
    config_instance = config[config_name]()
    app.config.from_object(config_instance)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config_instance.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config_instance.LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Initialize the ReturnsAgent
    agent_config = {
        'return_window_days': config_instance.RETURN_WINDOW_DAYS,
        'log_dir': log_dir
    }
    
    returns_agent = ReturnsAgent(agent_config)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring and Docker health checks"""
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'service': 'shopify-returns-agency',
                'version': '1.0.0',
                'environment': config_name,
                'checks': {
                    'config_loaded': True,
                    'agent_initialized': returns_agent is not None,
                    'log_directory': os.path.exists(log_dir)
                }
            }
            
            # Check if all health checks pass
            all_healthy = all(health_status['checks'].values())
            
            if all_healthy:
                return jsonify(health_status), 200
            else:
                health_status['status'] = 'unhealthy'
                return jsonify(health_status), 503
                
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'service': 'shopify-returns-agency',
                'error': str(e)
            }), 503
    
    @app.route('/shopify/returns-webhook', methods=['POST'])
    def shopify_webhook():
        """Handle Shopify refund webhooks"""
        try:
            # Get raw request data for HMAC verification
            raw_data = request.get_data()
            hmac_header = request.headers.get('X-Shopify-Hmac-SHA256')
            
            # Verify webhook if secret is configured
            webhook_secret = config_instance.SHOPIFY_WEBHOOK_SECRET
            if webhook_secret:
                if not verify_shopify_webhook(raw_data, hmac_header, webhook_secret):
                    app.logger.warning(f"Webhook verification failed. HMAC header: {hmac_header}")
                    return jsonify({'error': 'Webhook verification failed'}), 401
            else:
                app.logger.warning("SHOPIFY_WEBHOOK_SECRET not configured - webhook verification skipped")
            
            # Parse JSON data
            webhook_data = request.get_json()
            if not webhook_data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Log webhook receipt
            order_id = webhook_data.get('order_id', 'unknown')
            app.logger.info(f"Received verified webhook for order: {order_id}")
            
            # Process the webhook using ReturnsAgent
            result = returns_agent.process_webhook(webhook_data)
            
            # Log the result
            app.logger.info(f"Webhook processed successfully - Decision: {result.get('decision', 'unknown')}")
            
            return jsonify({
                'status': 'success',
                'decision': result.get('decision'),
                'reason': result.get('reason'),
                'event_id': result.get('event_id'),
                'message': 'Webhook processed successfully'
            }), 200
            
        except Exception as e:
            app.logger.error(f"Error processing webhook: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration for running the app
    config_name = os.environ.get('FLASK_ENV', 'development')
    config_instance = config[config_name]()
    
    app.run(
        host=config_instance.FLASK_HOST,
        port=config_instance.FLASK_PORT,
        debug=(config_name == 'development')
    ) 