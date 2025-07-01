# 🛍️ Shopify Returns Chat Widget Installation Guide

This guide will help you install the Returns Chat Widget on any Shopify store in just a few minutes.

## 📋 Prerequisites

- Admin access to your Shopify store
- Basic knowledge of Shopify theme editing
- The widget files (`widget.js`)

## 🚀 Installation Methods

### Method 1: Theme Code Installation (Recommended)

#### Step 1: Access Your Theme Editor
1. Go to your Shopify admin panel
2. Navigate to **Online Store** → **Themes**
3. Find your current theme and click **Actions** → **Edit code**

#### Step 2: Upload the Widget File
1. In the theme editor, scroll down to **Assets** folder
2. Click **Add a new asset**
3. Choose **Create a blank file**
4. Name it `returns-widget.js`
5. Copy the entire content from `widget.js` and paste it into this file
6. Click **Save**

#### Step 3: Add Widget to Your Theme
1. In the theme editor, go to **Layout** → `theme.liquid`
2. Find the closing `</body>` tag (usually near the bottom)
3. Add this code just **before** the `</body>` tag:

```html
<!-- Returns Chat Widget -->
<script>
  // Widget configuration (customize as needed)
  window.ReturnsWidgetConfig = {
    apiUrl: 'https://shopify-returns-chat-agent-production.up.railway.app',
    position: 'bottom-right',
    theme: {
      primaryColor: '#4a154b',
      textColor: '#333',
      backgroundColor: '#fff'
    },
    texts: {
      welcome: "👋 Hi! I'm your returns assistant. I can help you look up orders and process returns.",
      placeholder: "Ask about an order or return...",
      buttonText: "Returns Help"
    }
  };
</script>
<script src="{{ 'returns-widget.js' | asset_url }}" defer></script>
```

4. Click **Save**

#### Step 4: Test the Widget
1. Visit your store's frontend
2. Look for the floating "Returns Help" button in the bottom-right corner
3. Click it to test the chat functionality

---

### Method 2: Using Custom HTML/JS (Alternative)

If you prefer not to upload files to your theme, you can embed the widget directly:

1. Go to **Online Store** → **Themes** → **Actions** → **Edit code**
2. Open **Layout** → `theme.liquid`
3. Add this code before the closing `</body>` tag:

```html
<!-- Returns Chat Widget - Inline Version -->
<script>
  // Widget configuration
  window.ReturnsWidgetConfig = {
    apiUrl: 'https://shopify-returns-chat-agent-production.up.railway.app',
    position: 'bottom-right'
  };
  
  // Load widget from external source
  (function() {
    const script = document.createElement('script');
    script.src = 'https://your-cdn-url.com/widget.js'; // Replace with your hosted widget URL
    script.defer = true;
    document.head.appendChild(script);
  })();
</script>
```

---

### Method 3: Shopify App Block (For Online Store 2.0 Themes)

For newer Shopify themes that support app blocks:

1. The widget can be converted to a Shopify app block
2. This requires creating a Shopify app (more advanced)
3. Contact us for the app block version if needed

---

## ⚙️ Configuration Options

You can customize the widget by modifying the `ReturnsWidgetConfig` object:

```javascript
window.ReturnsWidgetConfig = {
  // API endpoint (required)
  apiUrl: 'https://shopify-returns-chat-agent-production.up.railway.app',
  
  // Widget position
  position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
  
  // Theme customization
  theme: {
    primaryColor: '#4a154b',     // Main widget color
    textColor: '#333',           // Text color
    backgroundColor: '#fff',     // Background color
    borderRadius: '20px'         // Border radius
  },
  
  // Text customization
  texts: {
    welcome: "Custom welcome message",
    placeholder: "Type your message...",
    buttonText: "Custom Button Text",
    offline: "We're currently offline"
  },
  
  // Display options
  showOnPages: ['all'],          // ['all'] or ['product', 'collection', 'home']
  hideOnMobile: false,           // Hide on mobile devices
  autoOpen: false,               // Auto-open chat on page load
  
  // Shopify integration
  includeCustomerInfo: true,     // Include logged-in customer info
  includeCartInfo: false         // Include current cart information
};
```

---

## 🎨 Styling Customization

### Custom CSS
Add custom styles to your theme's CSS file (`assets/theme.css` or similar):

```css
/* Customize widget button */
#returns-widget-button {
  background: linear-gradient(45deg, #your-color1, #your-color2) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
}

/* Customize chat window */
#returns-widget-chat {
  font-family: your-font-family !important;
  border-radius: 15px !important;
}

/* Hide on specific pages */
.template-cart #returns-widget,
.template-checkout #returns-widget {
  display: none !important;
}
```

---

## 📱 Mobile Optimization

The widget is fully responsive and includes:
- Touch-friendly interface
- Mobile-optimized sizing
- Gesture support for opening/closing
- Keyboard-friendly on mobile

To test mobile experience:
1. Use browser dev tools to simulate mobile
2. Test on actual mobile devices
3. Verify touch interactions work properly

---

## 🔧 Troubleshooting

### Widget Not Showing
1. **Check console for errors**: Open browser dev tools → Console tab
2. **Verify script loading**: Ensure `returns-widget.js` is loaded in Network tab
3. **Check theme compatibility**: Some themes may have conflicting CSS
4. **Clear cache**: Clear browser cache and Shopify theme cache

### Widget Not Responding
1. **Check API connectivity**: Verify the Railway deployment is running
2. **CORS issues**: Ensure your domain is allowed in the API
3. **Network blocking**: Check if firewall/ad blocker is interfering

### Styling Issues
1. **CSS conflicts**: Your theme CSS might override widget styles
2. **Z-index problems**: Adjust z-index in widget CSS if it appears behind elements
3. **Mobile display**: Test responsive behavior on different screen sizes

### Common Error Messages
- `"Failed to load widget"` → Script loading issue
- `"API connection failed"` → Backend service unavailable
- `"CORS error"` → Domain not allowed by API

---

## 🔒 Security Considerations

- The widget only communicates with your designated API endpoint
- No sensitive customer data is stored in the widget
- All conversations are handled through secure HTTPS connections
- Customer authentication is handled server-side

---

## 📊 Analytics Integration

Track widget usage by adding to your `ReturnsWidgetConfig`:

```javascript
window.ReturnsWidgetConfig = {
  // ... other config
  analytics: {
    enabled: true,
    trackEvents: ['widget_opened', 'message_sent', 'chat_completed'],
    gtag: true,          // Google Analytics 4
    fbPixel: false,      // Facebook Pixel
    customEvents: true   // Custom event tracking
  }
};
```

---

## 🆘 Support

If you need help with installation:

1. **Check the demo**: Open `demo.html` to see how it should work
2. **Test locally**: Use the demo file to verify widget functionality
3. **Contact support**: Reach out with specific error messages
4. **Theme compatibility**: Some themes may need custom adjustments

---

## 🔄 Updates

To update the widget:
1. Replace the content in `assets/returns-widget.js` with the new version
2. Clear your browser cache
3. Test functionality after update

The widget will automatically handle API updates and new features.

---

**Installation Complete! 🎉**

Your customers can now get instant help with returns and order inquiries directly on your store pages. 