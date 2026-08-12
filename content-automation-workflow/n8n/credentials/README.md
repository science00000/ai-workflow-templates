# n8n Credentials Setup Guide

## Required Credentials for Content Automation Workflow

### 1. WordPress (Blog Publishing)
**Type:** Basic Auth
- **Username:** Your WordPress admin username
- **Password:** Application password (not your login password)

To create an application password:
1. Go to WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Generate a new password and note it

### 2. Twitter/X (Social Media)
**Type:** OAuth2
- **Client ID:** From Twitter Developer Portal
- **Client Secret:** From Twitter Developer Portal
- **Callback URL:** `https://your-n8n-instance/rest/oauth2-credential/callback`
- **Scope:** `tweet.write tweet.read users.read`

Apply at: https://developer.twitter.com/

### 3. Facebook (Social Media)
**Type:** Generic Auth
- Set `FACEBOOK_ACCESS_TOKEN` in your n8n environment variables
- Get a Page Access Token from Facebook Developer Console
- Required permissions: `pages_manage_posts`, `pages_read_engagement`

### 4. Email / SMTP (Newsletter)
**Type:** SMTP
- **Host:** Your SMTP server (e.g., `smtp.gmail.com`)
- **Port:** 587 (TLS) or 465 (SSL)
- **Username:** Your email address
- **Password:** App-specific password (not your login password)

For Gmail: Generate an App Password at https://myaccount.google.com/apppasswords

### 5. Slack (Notifications — Optional)
**Type:** OAuth2
- Create a Slack app at https://api.slack.com/apps
- Add `chat:write` scope
- Set Bot Token in n8n credentials

### Environment Variables for n8n

Add these to your n8n `.env` or Docker environment:

```env
CONTENT_API_URL=http://content-api:8000
WORDPRESS_URL=https://your-site.wordpress.com
FACEBOOK_ACCESS_TOKEN=EAABxxx
EMAIL_RECIPIENT=newsletter@yourdomain.com
```
