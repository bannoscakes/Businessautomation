# 🔌 API Setup Guide - Customer Communication Hub

This guide will help you connect your email and social media accounts to the Business Automation Platform's Customer Communication Hub.

## Table of Contents
- [Outlook Email (Microsoft 365)](#outlook-email-microsoft-365)
- [Gmail](#gmail)
- [Facebook Messenger](#facebook-messenger)
- [Instagram](#instagram)
- [WhatsApp Business](#whatsapp-business)
- [Twitter / X](#twitter--x)
- [Adding Custom Platforms](#adding-custom-platforms)

---

## 📧 Outlook Email (Microsoft 365)

### Prerequisites
- Active Microsoft 365 or Outlook.com account
- Azure AD admin access (for business accounts)

### Setup Steps

1. **Register an Application in Azure AD:**
   - Go to [Azure Portal](https://portal.azure.com/)
   - Navigate to **Azure Active Directory** → **App registrations**
   - Click **New registration**
   - Name: "Business Automation Platform"
   - Supported account types: Select appropriate option for your organization
   - Click **Register**

2. **Get Client ID and Tenant ID:**
   - After registration, you'll see the **Application (client) ID** - Copy this
   - You'll also see the **Directory (tenant) ID** - Copy this

3. **Create Client Secret:**
   - Go to **Certificates & secrets** in your app
   - Click **New client secret**
   - Add a description and select expiration
   - **IMPORTANT:** Copy the secret value immediately (you won't see it again)

4. **Set API Permissions:**
   - Go to **API permissions**
   - Click **Add a permission** → **Microsoft Graph**
   - Select **Delegated permissions**
   - Add these permissions:
     - `Mail.Read`
     - `Mail.ReadWrite`
     - `Mail.Send`
   - Click **Grant admin consent** (if you have admin access)

5. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **Email (Outlook)**, enter:
     - **Client ID**: From step 2
     - **Client Secret**: From step 3
     - **Tenant ID**: From step 2
   - Click **Save Outlook Config**

### Required API Endpoints
- Microsoft Graph API: `https://graph.microsoft.com/v1.0`

---

## 📬 Gmail

### Prerequisites
- Active Gmail or Google Workspace account
- Google Cloud Platform account

### Setup Steps

1. **Create a Project in Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click **Create Project**
   - Name: "Business Automation Platform"
   - Click **Create**

2. **Enable Gmail API:**
   - In your project, go to **APIs & Services** → **Library**
   - Search for "Gmail API"
   - Click **Enable**

3. **Create Credentials:**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Name: "Business Automation Gmail"
   - Authorized redirect URIs: `http://localhost:8501` (or your domain)
   - Click **Create**

4. **Download Credentials:**
   - After creating, click **Download JSON**
   - This downloads your `credentials.json` file

5. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **Gmail**, upload your `credentials.json` file
   - Click **Save Gmail Config**

### Required Scopes
- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.send`
- `https://www.googleapis.com/auth/gmail.modify`

---

## 📘 Facebook Messenger

### Prerequisites
- Facebook Page (not personal profile)
- Facebook Developer account

### Setup Steps

1. **Create a Facebook App:**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Click **My Apps** → **Create App**
   - Use case: **Business**
   - App name: "Business Automation Platform"
   - Click **Create App**

2. **Add Messenger Product:**
   - In your app dashboard, click **Add Product**
   - Find **Messenger** and click **Set Up**

3. **Generate Page Access Token:**
   - In Messenger settings, scroll to **Access Tokens**
   - Select your Facebook Page
   - Click **Generate Token**
   - **IMPORTANT:** Copy this token immediately

4. **Get Page ID:**
   - Go to your Facebook Page
   - Click **About**
   - Scroll down to find **Page ID** or use Graph API Explorer

5. **Set Up Webhooks (Optional - for receiving messages):**
   - In Messenger settings, scroll to **Webhooks**
   - Click **Add Callback URL**
   - Verify token: Create your own secure string
   - Subscribe to events: `messages`, `messaging_postbacks`

6. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **Facebook Messenger**, enter:
     - **Page Access Token**: From step 3
     - **Page ID**: From step 4
   - Click **Save Facebook Config**

### Required Permissions
- `pages_messaging`
- `pages_manage_metadata`
- `pages_read_engagement`

---

## 📷 Instagram

### Prerequisites
- Instagram Business or Creator account
- Facebook Page connected to your Instagram account
- Facebook Developer account

### Setup Steps

1. **Connect Instagram to Facebook Page:**
   - In Instagram app, go to **Settings** → **Account** → **Linked Accounts**
   - Link your Instagram to a Facebook Page

2. **Use Facebook App (from Facebook Messenger setup):**
   - If you haven't created a Facebook app yet, follow the Facebook Messenger steps above

3. **Add Instagram Product:**
   - In your Facebook app dashboard, click **Add Product**
   - Find **Instagram** and click **Set Up**

4. **Generate Instagram Access Token:**
   - Use [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your app
   - Add these permissions: `instagram_basic`, `instagram_manage_messages`
   - Generate Access Token

5. **Get Instagram Account ID:**
   - Use Graph API Explorer
   - Make a GET request to `/me/accounts`
   - Find your connected Instagram account ID

6. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **Instagram**, enter:
     - **Access Token**: From step 4
     - **Instagram Account ID**: From step 5
   - Click **Save Instagram Config**

### Required Permissions
- `instagram_basic`
- `instagram_manage_messages`
- `pages_show_list`

---

## 💬 WhatsApp Business

### Prerequisites
- WhatsApp Business Account
- Facebook Business Manager account
- Verified phone number

### Setup Steps

1. **Set Up WhatsApp Business API:**
   - Go to [Facebook Business Manager](https://business.facebook.com/)
   - Navigate to **Business Settings** → **WhatsApp Accounts**
   - Click **Add** → **Create a WhatsApp Business Account**

2. **Get Access to WhatsApp Business Platform:**
   - Choose between:
     - **Cloud API** (Hosted by Meta - Recommended)
     - **On-premises API** (Self-hosted)

3. **For Cloud API (Recommended):**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Select your app or create new one
   - Add **WhatsApp** product
   - Follow the setup wizard

4. **Get API Credentials:**
   - In WhatsApp setup, you'll receive:
     - **Phone Number ID**
     - **WhatsApp Business Account ID**
     - **Access Token** (temporary - generate a permanent one)

5. **Generate Permanent Access Token:**
   - In your app, go to **Settings** → **Basic**
   - Create a **System User** with appropriate permissions
   - Generate a permanent token for the system user

6. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **WhatsApp Business**, enter:
     - **API Key**: Your access token
     - **Phone Number ID**: From step 4
   - Click **Save WhatsApp Config**

### Required Permissions
- `whatsapp_business_messaging`
- `whatsapp_business_management`

### API Endpoint
- Cloud API: `https://graph.facebook.com/v18.0`

---

## 🐦 Twitter / X

### Prerequisites
- Twitter/X account
- Twitter Developer account

### Setup Steps

1. **Apply for Developer Account:**
   - Go to [Twitter Developer Portal](https://developer.twitter.com/)
   - Click **Sign up** or **Apply**
   - Fill out the application form
   - Wait for approval (usually instant to 24 hours)

2. **Create a Twitter App:**
   - In Developer Portal, go to **Projects & Apps**
   - Click **Create App**
   - Name: "Business Automation Platform"
   - Click **Create**

3. **Get API Keys:**
   - After creating the app, you'll see:
     - **API Key** (Consumer Key)
     - **API Secret Key** (Consumer Secret)
   - **IMPORTANT:** Copy these immediately

4. **Generate Access Token:**
   - In your app settings, go to **Keys and tokens**
   - Under **Access Token and Secret**, click **Generate**
   - Copy both:
     - **Access Token**
     - **Access Token Secret**

5. **Set Permissions:**
   - Go to **Settings** → **App permissions**
   - Select **Read and write and Direct message**
   - Click **Save**

6. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Under **Twitter / X**, enter:
     - **API Key**: From step 3
     - **API Secret**: From step 3
   - Click **Save Twitter Config**

### API Endpoints
- API v2: `https://api.twitter.com/2`
- API v1.1: `https://api.twitter.com/1.1`

---

## ➕ Adding Custom Platforms

The Communication Hub supports adding any platform with a REST API!

### General Steps

1. **Get API Documentation:**
   - Find the platform's developer documentation
   - Look for REST API or Messaging API

2. **Register Your Application:**
   - Most platforms require you to register an application
   - This usually gives you API keys/tokens

3. **Identify Required Information:**
   - API Key or Access Token
   - API Endpoint URL
   - Any additional IDs (account ID, bot ID, etc.)

4. **Configure in the App:**
   - Open your Business Automation Platform
   - Go to **Customer Communication Hub** → **API Configuration**
   - Scroll to **Add Custom Platform**
   - Enter:
     - **Platform Name**: e.g., "Telegram", "Discord", "LinkedIn"
     - **API Key/Token**: Your authentication token
     - **API Endpoint**: Base URL for API calls
   - Click **Add Platform**

### Supported Custom Platforms Examples

#### Telegram
- Get Bot Token from [@BotFather](https://t.me/botfather)
- API Endpoint: `https://api.telegram.org/bot{token}`

#### Discord
- Create app at [Discord Developer Portal](https://discord.com/developers/applications)
- Get Bot Token
- API Endpoint: `https://discord.com/api/v10`

#### LinkedIn
- Create app at [LinkedIn Developers](https://www.linkedin.com/developers/)
- Get Client ID and Secret
- API Endpoint: `https://api.linkedin.com/v2`

#### Slack
- Create app at [Slack API](https://api.slack.com/apps)
- Get Bot Token
- API Endpoint: `https://slack.com/api`

---

## 🔒 Security Best Practices

1. **Never Share Your API Keys:**
   - Keep all tokens and secrets confidential
   - Don't commit them to version control

2. **Use Environment Variables (Optional):**
   - For production, consider storing sensitive data in environment variables
   - The app stores them securely in `templates/api_config.json`

3. **Rotate Tokens Regularly:**
   - Change your API keys periodically
   - Revoke unused tokens

4. **Monitor API Usage:**
   - Check for unusual activity
   - Set up usage alerts in developer consoles

5. **Use HTTPS:**
   - Always use secure connections
   - Run the app with SSL in production

---

## 🆘 Troubleshooting

### Common Issues

**"API Key Invalid"**
- Double-check you copied the entire key/token
- Verify the key hasn't expired
- Ensure correct permissions are granted

**"Authentication Failed"**
- Check if you granted admin consent (for Microsoft)
- Verify OAuth redirect URIs are correct
- Ensure your app is approved (for Twitter)

**"Rate Limit Exceeded"**
- Most APIs have rate limits
- Wait before making more requests
- Consider implementing caching

**"Webhook Not Receiving Messages"**
- Verify webhook URL is publicly accessible
- Check webhook verification token matches
- Ensure correct events are subscribed

### Getting Help

- Check the platform's developer documentation
- Visit developer forums and communities
- Contact platform support if needed

---

## 📚 Additional Resources

### Microsoft Graph API
- [Documentation](https://learn.microsoft.com/en-us/graph/)
- [Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)

### Gmail API
- [Documentation](https://developers.google.com/gmail/api)
- [Quickstart Guide](https://developers.google.com/gmail/api/quickstart/python)

### Facebook/Instagram APIs
- [Messenger Platform](https://developers.facebook.com/docs/messenger-platform/)
- [Instagram Messaging](https://developers.facebook.com/docs/messenger-platform/instagram)

### WhatsApp Business API
- [Cloud API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Getting Started](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)

### Twitter API
- [API Documentation](https://developer.twitter.com/en/docs)
- [API Reference](https://developer.twitter.com/en/docs/api-reference-index)

---

## 🎉 You're All Set!

Once you've configured your platforms, head to the **Customer Communication Hub** in the app to:
- View all messages in one unified inbox
- Create and use message templates
- Reply to customers across all platforms
- Track conversation history

Happy communicating! 💬
