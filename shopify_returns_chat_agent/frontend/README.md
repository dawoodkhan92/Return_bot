# 🛍️ Shopify Returns Chat Widget

This directory contains the frontend assets for a beautiful, responsive, and embeddable chat widget designed to provide instant customer support for e-commerce returns on any Shopify store.

## ✨ Features

-   🎨 **Modern Design**: A clean, modern interface that can be easily customized to match any theme.
-   📱 **Fully Responsive**: Optimized for a seamless experience on desktops, tablets, and mobile devices.
-   ⚡ **Lightweight & Fast**: Performance-optimized to ensure it doesn't slow down your store.
-   🔧 **Easy to Integrate**: Add to any Shopify theme by pasting a single script tag.
-   🔒 **Secure**: All communication with the backend is handled over HTTPS.
-   🤖 **AI-Powered**: Intelligent conversation handling with natural language processing.

## 📁 File Overview

-   **`widget.js`**: The core, production-ready JavaScript file that powers the chat widget.
-   **`styles.css`**: The CSS styles for the chat widget.
-   **`index.html`**: A standalone HTML file for testing and demonstrating the widget locally.
-   **`standalone-chat.html`**: A complete standalone implementation for testing.
-   **`assets/`**: Directory containing additional assets like icons and images.

---

## 🚀 Complete Implementation Guide

### Part 1: Backend Deployment

The backend is a FastAPI application that powers the chat logic. We recommend deploying it on Railway.

#### Step 1: Prepare Your Environment

1.  **GitHub Repository:** Ensure your project is pushed to a GitHub repository.

2.  **Environment Variables:** Set up your environment variables:
    ```env
    # Essential for the agent to work
    OPENAI_API_KEY="sk-..."
    SHOPIFY_ADMIN_TOKEN="shpua_..." # Your Shopify Admin API token
    SHOPIFY_STORE_DOMAIN="your-store.myshopify.com"

    # Optional, but recommended for production
    SENTRY_DSN="https://your-sentry-dsn"
    ENVIRONMENT="production"
    ```

#### Step 2: Deploy on Railway

1. Go to [Railway](https://railway.app) and connect your GitHub repository
2. Add the environment variables in the Railway dashboard
3. Deploy the application
4. Note your deployment URL (e.g., `https://your-app.railway.app`)

### Part 2: Widget Integration

#### Quick Installation (Recommended)

1.  From your Shopify Admin, go to **Online Store > Themes**.
2.  Find the theme you want to edit, click the **"..."** button, and select **"Edit code"**.
3.  In the code editor, open the `theme.liquid` file from the "Layout" directory.
4.  Before the closing `</body>` tag, add:

```html
<!-- Shopify Returns Chat Widget -->
<script>
  window.chatConfig = {
    apiUrl: 'https://your-app.railway.app', // Replace with your deployed backend URL
    position: 'bottom-right',
    theme: 'light',
    primaryColor: '#007cba',
    greeting: 'Hi! How can I help you with returns today?'
  };
</script>
<script src="https://your-app.railway.app/static/widget.js"></script>
```

5.  **Save** the file.

#### Advanced Configuration

The widget supports extensive customization options:

```javascript
window.chatConfig = {
  // Required
  apiUrl: 'https://your-app.railway.app',
  
  // Appearance
  position: 'bottom-right', // 'bottom-left', 'bottom-right', 'top-left', 'top-right'
  theme: 'light', // 'light', 'dark', 'auto'
  primaryColor: '#007cba',
  secondaryColor: '#f8f9fa',
  
  // Behavior
  autoOpen: false,
  greeting: 'Hi! How can I help you with returns today?',
  placeholder: 'Type your message...',
  
  // Advanced
  enableNotifications: true,
  maxMessages: 100,
  typingIndicator: true,
  
  // Branding
  companyName: 'Your Store Name',
  supportEmail: 'support@yourstore.com'
};
```

### Part 3: Testing & Validation

#### Local Testing

1. Open `index.html` in your browser
2. Update the `apiUrl` to point to your deployed backend
3. Test the chat functionality

#### Production Testing

1. Visit your Shopify store
2. Look for the chat widget in the bottom-right corner
3. Test a sample return request
4. Verify the widget integrates properly with your store's design

### Part 4: Customization

#### Styling

The widget can be customized to match your store's branding:

1. **Colors**: Modify the `primaryColor` and `secondaryColor` in the config
2. **Position**: Change the `position` setting
3. **Theme**: Use `theme: 'auto'` to automatically match your store's theme

#### Advanced Styling

For more advanced customization, you can override CSS classes:

```css
/* Custom styles for the chat widget */
.chat-widget {
  border-radius: 12px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}
```

## 🛠️ Development

### Running Locally

1. Start the backend server (see main README.md)
2. Open `index.html` in your browser
3. Update the `apiUrl` to `http://localhost:8000`

### Building for Production

The widget is already production-ready. Simply:

1. Deploy your backend
2. Update the `apiUrl` in your Shopify theme
3. Test thoroughly before going live

## 🔧 Troubleshooting

### Common Issues

1. **Widget doesn't appear**: Check that the script tag is properly placed before `</body>`
2. **CORS errors**: Ensure your backend is configured to allow requests from your Shopify domain
3. **API errors**: Verify your environment variables are set correctly
4. **Styling issues**: Check for CSS conflicts with your theme

### Support

For additional support, check:
- The main project documentation in `/docs`
- The backend API reference
- GitHub issues for known problems

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.