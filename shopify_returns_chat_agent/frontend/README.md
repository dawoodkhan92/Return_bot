# 🛍️ Shopify Returns Chat Widget

This directory contains the frontend assets for a beautiful, responsive, and embeddable chat widget designed to provide instant customer support for e-commerce returns on any Shopify store.

## ✨ Features

-   🎨 **Modern Design**: A clean, modern interface that can be easily customized to match any theme.
-   📱 **Fully Responsive**: Optimized for a seamless experience on desktops, tablets, and mobile devices.
-   ⚡ **Lightweight & Fast**: Performance-optimized to ensure it doesn't slow down your store.
-   🔧 **Easy to Integrate**: Add to any Shopify theme by pasting a single script tag.
-   🔒 **Secure**: All communication with the backend is handled over HTTPS.

## 📁 File Overview

-   **`widget.js`**: The core, production-ready JavaScript file that powers the chat widget.
-   **`styles.css`**: The CSS styles for the chat widget.
-   **`index.html`**: A standalone HTML file for testing and demonstrating the widget locally.

---

## 🚀 Quick Installation Guide

You can add the chat widget to your Shopify store in just a few minutes.

### Step 1: Add the Widget to Your Theme

1.  From your Shopify Admin, go to **Online Store > Themes**.
2.  Find the theme you want to edit, click the **"..."** button, and select **"Edit code"**.
3.  In the code editor, open the `theme.liquid` file from the "Layout" directory.

### Step 2: Paste the Script Tag

Scroll to the bottom of the `theme.liquid` file. Just before the closing `</body>` tag, paste the following code snippet:

```html
<!-- Returns Chat Widget -->
<script>
  // This setting tells the widget where your backend is hosted.
  // Replace this with the public URL of your deployed application (e.g., from Railway).
  window.RETURNS_API_URL = "YOUR_BACKEND_API_URL";

  // Optional: Set to true to see detailed logs in the browser console for debugging.
  window.RETURNS_DEBUG = false;
</script>
<script src="YOUR_BACKEND_API_URL/widget.js" async></script>
<!-- End Returns Chat Widget -->
```

**Important:** Replace `YOUR_BACKEND_API_URL` in **both** places with the actual public URL of your deployed backend.

### Step 3: Save and Verify

Click **"Save"**. The returns chat widget should now appear on your storefront, typically in the bottom-right corner.

---

## 🧪 Local Testing

To test the widget locally, you can open the `index.html` file in your browser. By default, it will try to connect to a backend running on `http://localhost:8000`. You can modify the `apiBaseUrl` in the `widget.js` initialization script within `index.html` to point to your desired backend.

## 🎨 Customization

You can customize the widget's appearance by overriding the CSS styles in your theme's main stylesheet.

**Example:**

```css
/* Customize the widget's floating button */
#returns-widget-button {
  background: linear-gradient(45deg, #5e3a8c, #8a5fb9) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
}

/* Customize the chat window's header */
#returns-widget-chat .chat-header {
  background: linear-gradient(45deg, #5e3a8c, #8a5fb9) !important;
}
```