# n8n Credentials Setup
# These credentials need to be configured in your n8n instance before importing the workflow.

# ── Required Credentials ──────────────────────────────────
#
# 1. Support Bot API (HTTP Request nodes)
#    - Type: Generic Credential (Header Auth or no auth for local)
#    - URL: http://localhost:8000 (or your deployed endpoint)
#    - Set env var: SUPPORT_BOT_URL
#
# 2. Slack (optional — escalation notifications)
#    - Type: Slack OAuth or Webhook
#    - Channel: #support-notifications
#    - Token: xoxb-your-slack-token
#
# 3. Notion (optional — conversation logging)
#    - Type: Notion API Token
#    - Token: ntn-your-notion-token
#    - Database ID: your-conversations-db-id

# ── Environment Variables ─────────────────────────────────
# Add to your n8n .env:
# SUPPORT_BOT_URL=http://host.docker.internal:8000
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
# NOTION_API_KEY=ntn_...
# NOTION_DATABASE_ID=...
