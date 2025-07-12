
# Shopify Chat Widget: Implementation Guide

This guide provides a step-by-step tutorial for deploying the backend and embedding the returns chat widget into your Shopify store.

---

## 🚀 Part 1: Deploying the Backend

The backend is a FastAPI application that powers the chat logic. We recommend deploying it on a platform like Railway, which is already configured in this repository.

### Step 1: Prepare Your Environment

1.  **GitHub Repository:** Ensure your project is pushed to a GitHub repository. Railway will deploy directly from it.

2.  **Environment Variables:** In the root of your project, copy the `.env.example` file to a new file named `.env`. Fill in the required values:
    ```env
    # Essential for the agent to work
    OPENAI_API_KEY="sk-..."
    SHOPIFY_ADMIN_TOKEN="shpua_..." # Your Shopify Admin API token
    SHOPIFY_STORE_DOMAIN="your-store.myshopify.com"

    # Optional, but recommended for production
    SENTRY_DSN="https://your-sentry-dsn"
    ENVIRONMENT="production"
    ```
    **Note:** These variables will be added to your deployment platform, not committed to Git.

### Step 2: Deploy on Railway

1.  **Sign Up:** Create an account on [Railway.app](https://railway.app) and log in.

2.  **Create a New Project:** From your dashboard, click "New Project" and select "Deploy from GitHub repo".

3.  **Select Your Repo:** Choose the GitHub repository containing this project. Railway will automatically detect the `Procfile` and `railway.json` to configure the deployment.

4.  **Add Environment Variables:** In your Railway project dashboard, go to the "Variables" tab. Add the key-value pairs from your `.env` file.

5.  **Get Your Public URL:** Once deployed, Railway will provide a public URL for your application (e.g., `https://returnbot-production.up.railway.app`). **Copy this URL**, as you will need it for the next part.

---

## 🛍️ Part 2: Integrating the Widget into Shopify

Now, you will add the widget to your Shopify theme so it appears on your storefront.

### Step 1: Navigate to Your Shopify Theme

1.  From your Shopify Admin, go to **Online Store > Themes**.
2.  Find the theme you want to edit, click the **"..."** button, and select **"Edit code"**.

### Step 2: Add the Widget Script

1.  In the code editor, open the `theme.liquid` file from the "Layout" directory.

2.  Scroll to the very bottom of the file. Just before the closing `</body>` tag, paste the following code snippet:

    ```html
    <!-- Returns Chat Widget -->
    <script>
      // This setting tells the widget where your backend is hosted.
      window.RETURNS_API_URL = "YOUR_RAILWAY_APP_URL";
    </script>
    <script src="YOUR_RAILWAY_APP_URL/widget.js" async></script>
    <!-- End Returns Chat Widget -->
    ```

3.  **Crucially, replace `YOUR_RAILWAY_APP_URL` in both places with the public URL you copied from Railway.**

    For example:
    ```html
    <!-- Returns Chat Widget -->
    <script>
      window.RETURNS_API_URL = "https://returnbot-production.up.railway.app";
    </script>
    <script src="https://returnbot-production.up.railway.app/widget.js" async></script>
    <!-- End Returns Chat Widget -->
    ```

4.  Click **"Save"**.

### Step 3: Verify the Installation

That's it! The returns chat widget should now appear on your storefront, typically in the bottom-right corner. Click the "Returns Help" button to open the chat and test the connection.

---

### Optional Configuration

You can add other settings to the `window` object to customize the widget's behavior.

-   **Enable Debug Mode:** To see detailed logs in the browser console, add `window.RETURNS_DEBUG = true;`.

    ```html
    <script>
      window.RETURNS_API_URL = "YOUR_RAILWAY_APP_URL";
      window.RETURNS_DEBUG = true; // Enable debug logs
    </script>
    ```

This provides a clear path for anyone to get the widget running.
