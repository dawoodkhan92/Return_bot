# 🛍️ Shopify Returns Chat Widget

A beautiful, responsive chat widget that can be embedded on any Shopify store to provide instant customer support for orders and returns.

## 📁 Files Overview

- **`widget.js`** - Main widget JavaScript file (production ready)
- **`demo.html`** - Interactive demo showing the widget in action
- **`INSTALLATION.md`** - Complete installation guide for Shopify stores
- **`styles.css`** - Standalone CSS (not needed if using widget.js)
- **`index.html`** - Standalone chat interface (alternative implementation)

## 🚀 Quick Start

### For Shopify Store Owners

1. **Download** the `widget.js` file
2. **Follow** the step-by-step instructions in `INSTALLATION.md`
3. **Test** the widget using the `demo.html` file first

### For Developers

1. **Demo the widget**: Open `demo.html` in your browser
2. **Customize**: Edit the configuration options in `widget.js`
3. **Deploy**: Follow the Shopify installation guide

## ✨ Features

- 🎨 **Beautiful Design** - Modern, clean interface that matches any theme
- 📱 **Mobile Responsive** - Optimized for all screen sizes
- ⚡ **Fast Loading** - Lightweight and performance optimized
- 🔧 **Highly Customizable** - Colors, text, positioning, and behavior
- 🌐 **Universal Compatibility** - Works with all Shopify themes
- 🔒 **Secure** - HTTPS communication with your backend
- 📊 **Analytics Ready** - Built-in tracking capabilities

## 🎯 Widget Capabilities

The widget connects to your FastAPI backend and can:

- **Look up orders** by order number or email
- **Check return policies** and eligibility  
- **Process return requests** with automated workflows
- **Provide instant answers** about shipping, exchanges, and refunds
- **Log conversations** for customer service review
- **Maintain conversation context** across multiple messages

## 🖥️ Demo

Open `demo.html` in your browser to see the widget in action on a simulated store page.

### Test Messages:
- "I need help with order #123456"
- "What's your return policy?"
- "I want to return an item" 
- "Track my order"

## ⚙️ Configuration

Basic configuration example:

```javascript
window.ReturnsWidgetConfig = {
  apiUrl: 'https://your-api-endpoint.com',
  theme: {
    primaryColor: '#4a154b',
    backgroundColor: '#fff'
  },
  texts: {
    welcome: "Hi! I'm your returns assistant.",
    buttonText: "Returns Help"
  }
};
```

See `INSTALLATION.md` for complete configuration options.

## 🔧 Customization

The widget is highly customizable:

- **Colors & Styling** - Match your brand perfectly
- **Text & Messages** - Customize all user-facing text
- **Position & Behavior** - Control where and how it appears
- **Mobile Experience** - Optimize for mobile users
- **Analytics** - Track usage and performance

## 📱 Mobile Experience

The widget includes:
- Touch-friendly interface
- Responsive design that adapts to screen size
- Mobile-optimized chat bubbles
- Keyboard-friendly input
- Gesture support

## 🔗 Integration

### Backend API
The widget communicates with your FastAPI backend at:
```
POST /chat
```

Expected request format:
```json
{
  "message": "Customer message",
  "conversation_id": "unique_conversation_id"
}
```

Expected response format:
```json
{
  "response": "Assistant response",
  "conversation_id": "same_conversation_id"
}
```

### Shopify Integration
- Works with all Shopify themes
- No app installation required
- Simple theme code modification
- Compatible with Online Store 2.0

## 🚦 Installation Status

✅ **Widget Created** - Ready for Shopify installation  
✅ **Demo Ready** - Test with demo.html  
✅ **Installation Guide** - Complete documentation  
✅ **Mobile Optimized** - Responsive design  
✅ **API Integration** - Connected to Railway backend  

## 📋 Installation Checklist

- [ ] Test widget with `demo.html`
- [ ] Upload `widget.js` to Shopify theme assets
- [ ] Add widget script to `theme.liquid`
- [ ] Configure widget settings
- [ ] Test on live store
- [ ] Verify mobile experience
- [ ] Set up analytics (optional)

## 🆘 Support

If you encounter issues:

1. **Check demo first** - Verify widget works in `demo.html`
2. **Review installation guide** - Follow `INSTALLATION.md` step by step
3. **Check browser console** - Look for JavaScript errors
4. **Test API connection** - Verify backend is accessible
5. **Check mobile** - Test on actual mobile devices

## 🔄 Updates

To update the widget:
1. Replace `widget.js` content with new version
2. Clear browser cache
3. Test functionality

The widget automatically handles API version compatibility.

---

**Ready to install? Start with `INSTALLATION.md` for complete instructions! 🚀** 