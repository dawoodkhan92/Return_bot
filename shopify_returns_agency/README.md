# Shopify Returns Agency

An automated system for processing Shopify return requests according to configurable policies using the Agency Swarm framework.

## Overview

This application automates the approval/denial of Shopify refund webhooks for apparel brands by checking return policy rules, logging all actions, and reducing manual workload and errors. It's designed for mid-market Shopify stores needing efficiency and auditability.

## Features

- **Automated Return Processing**: Receives and processes Shopify refund webhooks automatically
- **Policy-Based Decisions**: Validates return requests against configurable policies (return window, valid reasons, item eligibility)
- **Comprehensive Logging**: Logs all decisions and actions with rotating file handlers for audit purposes
- **Secure Webhook Validation**: HMAC signature validation to ensure webhook authenticity
- **Multiple Environments**: Support for development, testing, and production configurations
- **Agency Swarm Architecture**: Built using the Agency Swarm framework with dedicated agents and tools

## Architecture

The system consists of:

- **ReturnsAgent**: Main agent that coordinates the return processing workflow
- **PolicyChecker Tool**: Validates returns against business rules
- **ActionLogger Tool**: Provides comprehensive logging with rotating files
- **RefundProcessor Tool**: Handles the refund processing logic
- **Flask Webhook Endpoint**: Secure endpoint for receiving Shopify webhooks

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd shopify_returns_agency
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment configuration:**
   ```bash
   cp .env.example .env
   ```

5. **Configure your `.env` file:**
   ```env
   # Flask Configuration
   FLASK_ENV=development
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   SECRET_KEY=your-secret-key-here
   
   # Shopify Configuration
   SHOPIFY_WEBHOOK_SECRET=your_shopify_webhook_secret
   
   # Policy Configuration
   RETURN_WINDOW_DAYS=30
   
   # Logging Configuration
   LOG_LEVEL=INFO
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment (development/testing/production) | development | No |
| `FLASK_HOST` | Host to bind the Flask server | 0.0.0.0 | No |
| `FLASK_PORT` | Port for the Flask server | 5000 | No |
| `SECRET_KEY` | Flask secret key for sessions | auto-generated | No |
| `SHOPIFY_WEBHOOK_SECRET` | Secret for webhook validation | None | Yes* |
| `RETURN_WINDOW_DAYS` | Days after purchase for valid returns | 30 | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |

*Required for production use with webhook validation

### Policy Configuration

The system validates returns based on:

- **Return Window**: Configurable number of days after purchase
- **Valid Reasons**: Predefined list of acceptable return reasons
  - `defective` - Item is defective or damaged
  - `wrong_item` - Wrong item was sent
  - `not_as_described` - Item doesn't match description
  - `changed_mind` - Customer changed their mind
- **Item Categories**: Supports different rules for different product types

## Running the Application

### Development Mode

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

### Production Mode

```bash
FLASK_ENV=production python app.py
```

## Setting Up Shopify Webhooks

1. **In your Shopify admin:**
   - Go to Settings → Notifications → Webhooks
   - Click "Create webhook"

2. **Configure the webhook:**
   - Event: `Refund creation`
   - Format: `JSON`
   - URL: `https://your-domain.com/shopify/returns-webhook`
   - API Version: Latest stable version

3. **Security:**
   - Copy the webhook secret from Shopify
   - Add it to your `.env` file as `SHOPIFY_WEBHOOK_SECRET`

4. **Test the webhook:**
   - Use the test functionality in Shopify admin
   - Check your application logs for successful processing

## API Endpoints

### Webhook Endpoint

```
POST /shopify/returns-webhook
```

Receives Shopify refund webhooks and processes them according to configured policies.

**Headers:**
- `X-Shopify-Hmac-SHA256`: HMAC signature for verification
- `Content-Type: application/json`

**Response:**
```json
{
  "status": "success",
  "decision": "approve|deny|flag",
  "reason": "Human readable reason",
  "event_id": "unique_event_identifier",
  "message": "Webhook processed successfully"
}
```

### Health Check

```
GET /health
```

Returns application health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "shopify-returns-agency",
  "version": "1.0.0"
}
```

## Testing

### Run All Tests

```bash
# Basic functionality tests
python run_tests.py

# Webhook integration tests
python test_webhook.py

# Webhook validation tests
python test_webhook_validation.py

# Enhanced logging tests
python test_enhanced_logging.py
```

### Test Individual Components

```bash
# Test PolicyChecker
python -m pytest tests/test_policy_checker.py

# Test ActionLogger
python -m pytest tests/test_action_logger.py

# Test RefundProcessor
python -m pytest tests/test_refund_processor.py

# Test ReturnsAgent
python -m pytest tests/test_returns_agent.py
```

## Logging

The application provides comprehensive logging with rotating file handlers:

### Log Files

- **`logs/returns_agent.log`**: Main application logs (10MB max, 5 backups)
- **`logs/actions.log`**: Structured action logs (5MB max, 10 backups)

### Log Levels

- **INFO**: Normal operation events
- **WARNING**: Potential issues that don't stop operation
- **ERROR**: Error conditions that need attention
- **DEBUG**: Detailed information for troubleshooting

### Structured Action Logs

All decisions are logged in JSON format for easy parsing:

```json
{
  "timestamp": "2025-06-28T21:46:28.161000",
  "event_id": "refund_order_12345_20250628_214628",
  "decision": "approve",
  "reason": "Return request meets all policy requirements",
  "additional_data": {
    "policy_check_details": {...},
    "order_info": {...}
  }
}
```

## Deployment

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t shopify-returns-agency .
   ```

2. **Run the container:**
   ```bash
   docker run -p 5000:5000 --env-file .env shopify-returns-agency
   ```

### Server Deployment

#### Using systemd (Linux)

1. **Create a service file** (`/etc/systemd/system/shopify-returns.service`):
   ```ini
   [Unit]
   Description=Shopify Returns Agency
   After=network.target
   
   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/shopify_returns_agency
   Environment=PATH=/path/to/shopify_returns_agency/venv/bin
   ExecStart=/path/to/shopify_returns_agency/venv/bin/python app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start the service:**
   ```bash
   sudo systemctl enable shopify-returns
   sudo systemctl start shopify-returns
   ```

#### Using Nginx (Reverse Proxy)

1. **Configure Nginx** (`/etc/nginx/sites-available/shopify-returns`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. **Enable the site:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/shopify-returns /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Environment-Specific Configuration

#### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use a strong `SECRET_KEY`
- [ ] Configure `SHOPIFY_WEBHOOK_SECRET`
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure log rotation
- [ ] Set up monitoring and alerting
- [ ] Configure backup for log files
- [ ] Test webhook endpoint accessibility

## Monitoring

### Health Checks

Monitor the `/health` endpoint for application availability:

```bash
curl http://your-domain.com/health
```

### Log Monitoring

Monitor log files for errors and unusual patterns:

```bash
# Monitor main application logs
tail -f logs/returns_agent.log

# Monitor action logs
tail -f logs/actions.log | grep "ACTION_LOG"
```

### Webhook Testing

Test webhook processing with sample data:

```bash
curl -X POST http://your-domain.com/shopify/returns-webhook \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Hmac-SHA256: valid_hmac_signature" \
  -d @sample_webhook.json
```

## Troubleshooting

### Common Issues

#### Webhook Verification Failures

**Problem**: Getting 401 errors on webhook endpoint

**Solution**:
1. Verify `SHOPIFY_WEBHOOK_SECRET` is correctly set
2. Check that the webhook secret in Shopify matches your configuration
3. Ensure the HMAC signature is being sent correctly

#### Log File Permissions

**Problem**: Cannot write to log files

**Solution**:
1. Check directory permissions: `chmod 755 logs/`
2. Check file permissions: `chmod 644 logs/*.log`
3. Ensure the application user has write access

#### Import Errors

**Problem**: Module import errors when running the application

**Solution**:
1. Activate your virtual environment
2. Install missing dependencies: `pip install -r requirements.txt`
3. Check Python path configuration

### Debug Mode

Enable debug mode for detailed error information:

```bash
FLASK_ENV=development FLASK_DEBUG=True python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `python run_tests.py`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Check the troubleshooting section above
- Review the application logs
- Create an issue in the repository
- Contact the development team

## Version History

- **v1.0.0**: Initial release with core functionality
  - Webhook processing
  - Policy validation
  - Comprehensive logging
  - HMAC verification
  - Multi-environment support 