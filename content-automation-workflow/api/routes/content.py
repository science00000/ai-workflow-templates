"""
Content Generation API Routes

Endpoints for generating blog posts, social media posts,
email newsletters, and full multi-channel content.
"""

import json
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.content_generator import (
    generate_blog,
    generate_social_posts,
    generate_email,
    generate_full_content,
)
from services.publisher import publish_all, publish_to_wordpress, send_email
from config.settings import settings

router = APIRouter()

# ── Request/Response Models ─────────────────────────────────


class ContentRequest(BaseModel):
    """Base request for content generation."""
    topic: str = Field(..., min_length=5, max_length=500, description="The topic/subject for content")
    tone: str = Field(default="professional", description="Writing tone: professional, casual, humorous, academic, persuasive")
    language: str = Field(default="en", description="Output language code")


class BlogRequest(ContentRequest):
    min_words: int = Field(default=800, ge=300, le=5000)
    max_words: int = Field(default=2000, ge=500, le=10000)


class SocialRequest(ContentRequest):
    count: int = Field(default=3, ge=1, le=10)


class PublishBlogRequest(BlogRequest):
    categories: list[int] = Field(default=[1], description="WordPress category IDs")


class SendEmailRequest(ContentRequest):
    to_email: str = Field(..., description="Recipient email address")


# ── Endpoints ───────────────────────────────────────────────


@router.post("/generate", summary="Generate all content from one prompt")
async def generate_all(request: ContentRequest):
    """
    Generate blog post + social media posts + email newsletter from a single topic.

    This is the main endpoint — one input, multi-channel output.
    """
    try:
        content = await generate_full_content(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
        )
        return {
            "status": "success",
            "content": content,
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/blog", summary="Generate blog post only")
async def gen_blog(request: BlogRequest):
    """Generate a single blog post in Markdown."""
    try:
        blog = await generate_blog(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
            min_words=request.min_words,
            max_words=request.max_words,
        )
        return {"status": "success", "blog_post": blog}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/social", summary="Generate social media posts")
async def gen_social(request: SocialRequest):
    """Generate social media posts for multiple platforms."""
    try:
        posts = await generate_social_posts(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
            count=request.count,
        )
        return {"status": "success", "social_posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email", summary="Generate email newsletter")
async def gen_email(request: ContentRequest):
    """Generate a newsletter email with subject, HTML body, and plain text."""
    try:
        email = await generate_email(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
        )
        return {"status": "success", "email_newsletter": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/blog", summary="Generate and publish blog to WordPress")
async def publish_blog(request: PublishBlogRequest):
    """Generate a blog post and publish it directly to WordPress."""
    try:
        blog = await generate_blog(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
            min_words=request.min_words,
            max_words=request.max_words,
        )
        # Extract title from the first line of markdown
        title = blog.split("\n")[0].replace("# ", "").strip() or request.topic
        result = await publish_to_wordpress(title, blog, request.categories)
        results = await publish_all([result])
        return {"status": "success", "blog_post": blog, "publish": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/email", summary="Generate and send email newsletter")
async def publish_email(request: SendEmailRequest):
    """Generate a newsletter and send it via SMTP."""
    try:
        email = await generate_email(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
        )
        result = await send_email(
            to_email=request.to_email,
            subject=email.get("subject", ""),
            body_html=email.get("body_html", ""),
            body_text=email.get("body_text", ""),
        )
        results = await publish_all([result])
        return {"status": "success", "email": email, "publish": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save", summary="Save generated content to disk")
async def save_content(request: ContentRequest):
    """Generate all content and save to data/exports/ directory."""
    try:
        content = await generate_full_content(
            topic=request.topic,
            tone=request.tone,
            language=request.language,
        )
        export_dir = "data/exports"
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "saved_to": filepath,
            "filename": filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
