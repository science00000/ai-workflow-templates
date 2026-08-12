"""
Content generator service

Orchestrates blog post, social media, and email generation
from a single topic/prompt input.
"""

from datetime import datetime
from typing import Optional
from services.ollama_client import generate, generate_json
from config.settings import settings

# ── System Prompts ──────────────────────────────────────────

SYSTEM_BLOG = """You are an expert content writer. Write a well-structured blog post
with H2/H3 headings, paragraphs, bullet points where appropriate, and a compelling
conclusion. Use the specified tone and language. Output MUST be valid Markdown.
Include a title, meta description (50-160 chars), and 3-5 keywords."""

SYSTEM_SOCIAL = """You are a social media strategist. Create engaging social media posts
for the given topic. Output MUST be a JSON array of posts with fields:
platform (twitter|facebook|linkedin|instagram), content (the post text),
hashtags (array of 3-5 hashtags), and character_count.
Each platform post should be tailored to its style and limits."""

SYSTEM_EMAIL = """You are an email marketing expert. Create a compelling newsletter email
for the given topic. Output MUST be a JSON object with fields:
subject (catchy subject line, <60 chars),
preheader (preview text, <100 chars),
body_html (HTML email body, inline styles, responsive),
body_text (plain text version),
cta_text (call-to-action button text),
cta_link (placeholder URL)."""


async def generate_blog(
    topic: str,
    tone: str = "professional",
    language: str = "en",
    min_words: int = 800,
    max_words: int = 2000,
) -> str:
    """Generate a complete blog post in Markdown."""
    prompt = (
        f"Write a comprehensive blog post about: {topic}\n\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n"
        f"Word count: {min_words}-{max_words} words\n\n"
        f"Include:\n"
        f"- A compelling title\n"
        f"- Meta description\n"
        f"- 3-5 SEO keywords\n"
        f"- Well-structured sections with H2/H3 headings\n"
        f"- Bullet points and lists where appropriate\n"
        f"- A strong conclusion with a call-to-action\n"
        f"- Published date: {datetime.now().strftime('%B %d, %Y')}"
    )
    return await generate(prompt, SYSTEM_BLOG)


async def generate_social_posts(
    topic: str,
    tone: str = "professional",
    language: str = "en",
    count: int = 3,
) -> list:
    """Generate social media posts for multiple platforms."""
    prompt = (
        f"Create {count} engaging social media posts about: {topic}\n\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n\n"
        f"Requirements:\n"
        f"- Twitter: <280 chars, punchy, with hashtags\n"
        f"- Facebook: conversational, 100-300 chars\n"
        f"- LinkedIn: professional, thought-leadership style\n"
        f"- Instagram: visual, emoji-friendly, storytelling\n\n"
        f"Return as a JSON array with: platform, content, hashtags, character_count"
    )
    return await generate_json(prompt, SYSTEM_SOCIAL)


async def generate_email(
    topic: str,
    tone: str = "professional",
    language: str = "en",
) -> dict:
    """Generate a newsletter email."""
    prompt = (
        f"Create a newsletter email about: {topic}\n\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n\n"
        f"Requirements:\n"
        f"- Subject line: catchy, <60 chars\n"
        f"- Preheader: preview text, <100 chars\n"
        f"- Body: engaging, scannable, with a clear CTA\n"
        f"- Include both HTML and plain text versions\n"
        f"- Responsive HTML with inline styles\n\n"
        f"Return as JSON with: subject, preheader, body_html, body_text, cta_text, cta_link"
    )
    return await generate_json(prompt, SYSTEM_EMAIL)


async def generate_full_content(
    topic: str,
    tone: str = "professional",
    language: str = "en",
) -> dict:
    """Generate ALL content types at once (blog + social + email)."""
    blog = await generate_blog(topic, tone, language)
    social = await generate_social_posts(topic, tone, language)
    email = await generate_email(topic, tone, language)

    return {
        "topic": topic,
        "tone": tone,
        "language": language,
        "generated_at": datetime.now().isoformat(),
        "blog_post": blog,
        "social_media_posts": social if isinstance(social, list) else [social],
        "email_newsletter": email,
    }
