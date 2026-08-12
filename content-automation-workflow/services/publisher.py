"""
Publishing service

Handles publishing content to WordPress, social media, and email
platforms. Each method checks for configured credentials first.
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config.settings import settings
import httpx


class PublishResult:
    def __init__(self, platform: str, success: bool, message: str, url: str = ""):
        self.platform = platform
        self.success = success
        self.message = message
        self.url = url

    def __dict__(self):
        return {
            "platform": self.platform,
            "success": self.success,
            "message": self.message,
            "url": self.url,
        }


async def publish_to_wordpress(title: str, content: str, categories: list = None) -> PublishResult:
    """Publish a blog post to WordPress via REST API."""
    if not settings.wordpress_url or not settings.wordpress_user:
        return PublishResult("wordpress", False, "WordPress not configured")

    # WordPress REST API uses Basic Auth
    import base64
    auth = base64.b64encode(f"{settings.wordpress_user}:{settings.wordpress_password}".encode()).decode()

    payload = {
        "title": title,
        "content": content,
        "status": "publish",
        "categories": categories or [1],
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.wordpress_url}/wp-json/wp/v2/posts",
                json=payload,
                headers={"Authorization": f"Basic {auth}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return PublishResult("wordpress", True, "Published", data.get("link", ""))
    except Exception as e:
        return PublishResult("wordpress", False, str(e))


async def publish_to_twitter(content: str) -> PublishResult:
    """Post to Twitter/X."""
    if not settings.twitter_bearer_token:
        return PublishResult("twitter", False, "Twitter not configured")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.twitter.com/2/tweets",
                json={"text": content[:280]},
                headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
            )
            resp.raise_for_status()
            return PublishResult("twitter", True, "Posted")
    except Exception as e:
        return PublishResult("twitter", False, str(e))


async def publish_to_facebook(content: str) -> PublishResult:
    """Post to Facebook page."""
    if not settings.facebook_access_token:
        return PublishResult("facebook", False, "Facebook not configured")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://graph.facebook.com/me/feed",
                params={"message": content, "access_token": settings.facebook_access_token},
            )
            resp.raise_for_status()
            return PublishResult("facebook", True, "Posted")
    except Exception as e:
        return PublishResult("facebook", False, str(e))


async def send_email(to_email: str, subject: str, body_html: str, body_text: str) -> PublishResult:
    """Send an email via SMTP."""
    if not settings.mail_host:
        return PublishResult("email", False, "SMTP not configured")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.mail_from
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.mail_host, settings.mail_port) as server:
            server.starttls()
            server.login(settings.mail_user, settings.mail_password)
            server.send_message(msg)
        return PublishResult("email", True, f"Sent to {to_email}")
    except Exception as e:
        return PublishResult("email", False, str(e))


async def publish_all(results: list[PublishResult]) -> dict:
    """Collect and return all publish results."""
    return {
        "published": [r.__dict__() for r in results if r.success],
        "failed": [r.__dict__() for r in results if not r.success],
        "total": len(results),
        "success_count": sum(1 for r in results if r.success),
    }
