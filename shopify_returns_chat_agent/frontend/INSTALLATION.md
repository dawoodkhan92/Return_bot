# 🛍️ Shopify Returns Chat Widget Installation Guide

This guide will help you install the Returns Chat Widget on any Shopify store in just a few minutes.

## 📋 Prerequisites

- Admin access to your Shopify store
- Basic knowledge of Shopify theme editing
- The production widget file (`widget.js`) - **Now consolidated into a single, feature-complete version**

## 🎉 Widget Consolidation Complete

We've consolidated **5 different widget versions** into one production-ready solution:

### ✅ **Single Production Widget: `widget.js`**
- **Dynamic API URL Detection** - Auto-detects Railway, localhost, or custom URLs
- **Enhanced Integration** - Two-step API flow (/start + /chat endpoints)
- **Connection Status Indicators** - Visual feedback for connection state  
- **Debug Mode Support** - Configurable debugging with `window.RETURNS_DEBUG`
- **CSS Isolation** - Prevents conflicts with existing store styles
- **Shopify Integration** - Built-in customer and shop domain detection
- **Mobile Optimized** - Responsive design for all devices
- **Error Handling** - Comprehensive error management and retry logic

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
<!-- Returns Chat Widget - Production Version -->
<script>
  // Optional configuration (widget auto-detects API URL)
  window.RETURNS_API_URL = 'https://returnbot-production.up.railway.app'; // Optional override
  window.RETURNS_DEBUG = false; // Set to true for debugging
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
    apiUrl: 'https://returnbot-production.up.railway.app',
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

The consolidated widget uses simplified configuration with smart defaults:

### 🔧 **Basic Configuration:**
```javascript
// Optional: Override API URL (auto-detected by default)
window.RETURNS_API_URL = 'https://your-custom-api.com';

// Optional: Enable debug mode
window.RETURNS_DEBUG = true;

// Optional: Set custom meta tag for API URL
<meta name="returns-api-url" content="https://your-api.com">
```

### 🎯 **Smart Auto-Detection:**
The widget automatically detects:
- **Railway deployments** - Uses current domain if hosted on Railway  
- **Local development** - Uses `http://localhost:8080` for testing
- **Custom domains** - Reads from meta tag or window variables
- **Shopify customer data** - Includes logged-in customer information
- **Shop domain** - Automatically detects current Shopify store

### 🎨 **Styling:**
The widget includes built-in responsive design and CSS isolation. All styling is self-contained to prevent conflicts with your theme.

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

1. **Test on development store**: Install on a development store first to verify functionality
2. **Check console**: Use browser developer tools to check for errors
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