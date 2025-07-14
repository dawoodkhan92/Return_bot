# 🔧 Shopify Returns Chat Agent - Integration Fix Guide

This guide helps you fix the frontend-backend integration issues identified in Task 34.

## 🚨 Key Issues Fixed

1. **Backend not using LLM Agent** - Fixed ✅
2. **Missing conversation state management** - Fixed ✅  
3. **Incorrect API endpoints structure** - Fixed ✅
4. **Multiple widget versions causing confusion** - Fixed ✅
5. **Poor error handling and debugging** - Fixed ✅

## 📋 Quick Fix Checklist

### Step 1: Update Backend (✅ COMPLETED)
- [x] `app.py` now properly integrates with `LLMReturnsChatAgent`
- [x] Added `/start` endpoint for conversation initialization
- [x] Added proper conversation state management
- [x] Enhanced error handling and logging
- [x] Added configuration validation

### Step 2: Use the Fixed Widget
Replace your current widget with the new integration-fixed version:

```html
<!-- Add to your Shopify theme's theme.liquid file, before </body> -->

<!-- Optional: Enable debug mode -->
<script>
  window.RETURNS_DEBUG = true; // Remove in production
  window.RETURNS_API_URL = "YOUR_RAILWAY_URL_HERE"; // Optional: Override API URL
</script>

<!-- Load the fixed widget -->
<script src="https://your-cdn.com/widget-integration-fixed.js"></script>

<!-- Optional: Manual initialization -->
<script>
  // Widget auto-initializes, but you can also control it manually:
  // ReturnsWidget.open();  // Open widget programmatically
  // ReturnsWidget.debug(); // Show debug information
</script>
```

### Step 3: Environment Configuration

Ensure these environment variables are set in Railway:

**Required Variables:**
```bash
OPENAI_API_KEY=your_openai_key_here
SHOPIFY_ADMIN_TOKEN=your_shopify_admin_token
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
```

**Optional Variables:**
```bash
OPENAI_MODEL=gpt-4o
ALLOWED_ORIGINS=https://your-store.myshopify.com,https://your-domain.com
SENTRY_DSN=your_sentry_dsn_here
ENVIRONMENT=production
PORT=8080
```

### Step 4: Test the Integration

Test the API endpoints manually to verify everything works:

```bash
# Test health endpoint
curl https://your-railway-url.railway.app/health

# Test start conversation
curl -X POST https://your-railway-url.railway.app/start \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test123", "shop_domain": "test.myshopify.com"}'
```

## 🔍 Debugging Tools

### 1. Backend Debug Endpoints

Test your Railway deployment:
- `GET /health` - Check service health
- `GET /debug/railway` - Railway-specific debug info
- `GET /` - Basic service info

### 2. Widget Debug Mode

Enable debug mode in your widget:
```javascript
window.RETURNS_DEBUG = true;
```

Then use the debug console:
```javascript
ReturnsWidget.debug(); // Shows configuration and state
```

### 3. Manual Integration Testing

You can manually test the following components:
- ✅ Environment variables (check Railway dashboard)
- ✅ API endpoint connectivity (use curl commands)
- ✅ Conversation flow (test widget end-to-end)
- ✅ Error handling (test invalid inputs)
- ✅ Configuration validation (check console logs)

## 🛠️ Manual Testing Steps

### Test 1: Backend API
```bash
# Test health endpoint
curl https://your-railway-url.railway.app/health

# Test start conversation
curl -X POST https://your-railway-url.railway.app/start \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test123", "shop_domain": "test.myshopify.com"}'

# Test chat (use conversation_id from previous response)
curl -X POST https://your-railway-url.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I want to return an item", "conversation_id": "conv_xxx"}'
```

### Test 2: Widget Integration
1. Open your Shopify store
2. Open browser developer tools (F12)
3. Look for the Returns widget button (bottom right)
4. Click to open widget
5. Check console for any errors
6. Try sending a test message

### Test 3: End-to-End Flow
1. Open widget on store
2. Widget should show "Starting your returns assistant..."
3. After initialization, should show AI greeting
4. Type "I want to return order #1001"
5. Should get intelligent response from LLM agent

## 🔧 Common Issues & Solutions

### Issue: "Configuration error: Missing required environment variables"
**Solution:** Set the required environment variables in Railway:
- OPENAI_API_KEY
- SHOPIFY_ADMIN_TOKEN  
- SHOPIFY_STORE_DOMAIN

### Issue: "Conversation not found"
**Solution:** The widget needs to call `/start` before `/chat`. Use the new `widget-integration-fixed.js`.

### Issue: "CORS error" 
**Solution:** Set `ALLOWED_ORIGINS` environment variable with your store domain:
```bash
ALLOWED_ORIGINS=https://your-store.myshopify.com
```

### Issue: Widget shows "Connection failed"
**Solution:** 
1. Check if Railway service is running
2. Verify the API URL in widget configuration
3. Check browser network tab for HTTP errors
4. Enable debug mode to see detailed logs

### Issue: Widget appears but LLM doesn't respond intelligently
**Solution:**
1. Verify OPENAI_API_KEY is valid
2. Check Railway logs for OpenAI API errors
3. Ensure SHOPIFY_ADMIN_TOKEN has proper permissions

## 📊 Monitoring & Logs

### Railway Logs
```bash
# View logs in Railway dashboard or CLI
railway logs
```

### Sentry Error Tracking
If Sentry is configured, errors will appear in your Sentry dashboard with detailed context.

### Widget Console Logs
With debug mode enabled, check browser console for widget logs:
```
[Returns Widget] Widget created {apiUrl: "https://..."}
[Returns Widget] Initializing chat conversation
[Returns Widget] Chat initialized successfully {conversationId: "conv_xxx"}
```

## 🚀 Deployment Recommendations

### Production Checklist
- [ ] Environment variables properly set
- [ ] CORS origins restricted to your domain
- [ ] Debug mode disabled (`RETURNS_DEBUG = false`)
- [ ] Sentry error tracking enabled
- [ ] Health check endpoint responding
- [ ] Widget using production API URL

### Performance Optimization
- [ ] Enable Railway auto-scaling
- [ ] Configure proper health check intervals
- [ ] Monitor conversation memory usage
- [ ] Set up log rotation

### Security Considerations
- [ ] Restrict CORS to specific domains
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Secure environment variables
- [ ] Use HTTPS only

## 📞 Support & Troubleshooting

If you encounter issues:

1. **Test API endpoints manually** using curl commands above
2. **Check Railway logs** for backend errors
3. **Check browser console** for frontend errors  
4. **Verify environment variables** are properly set
5. **Test widget functionality** on your Shopify store

### Debug Information to Collect
When reporting issues, include:
- API endpoint test results (curl responses)
- Railway deployment logs
- Browser console errors
- Network requests (from browser dev tools)
- Environment variable names (not values!)

## 🎯 Next Steps After Integration

1. **Test with real customers** in a staging environment
2. **Monitor error rates** and response times
3. **Gather customer feedback** on the chat experience
4. **Optimize prompts** based on common customer queries
5. **Scale infrastructure** based on usage patterns

---

**✅ Integration Status**: Fixed and ready for testing
**🔄 Last Updated**: Task 34 completion
**📋 Next Task**: Deploy and monitor in production environment 