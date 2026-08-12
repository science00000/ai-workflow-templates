"""
Test content generation service
"""

import pytest
from unittest.mock import AsyncMock, patch
from services.content_generator import (
    generate_blog,
    generate_social_posts,
    generate_email,
    generate_full_content,
)


@pytest.mark.asyncio
async def test_generate_blog_returns_markdown():
    with patch("services.content_generator.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "# Test Post\n\nThis is a test blog post."
        result = await generate_blog("Test topic")
        assert "# Test Post" in result


@pytest.mark.asyncio
async def test_generate_social_returns_list():
    with patch("services.content_generator.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = [{"platform": "twitter", "content": "Test post"}]
        result = await generate_social_posts("Test topic")
        assert isinstance(result, list)
        assert len(result) == 1


@pytest.mark.asyncio
async def test_generate_email_returns_dict():
    with patch("services.content_generator.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {"subject": "Test Subject", "body_html": "<p>Test</p>"}
        result = await generate_email("Test topic")
        assert "subject" in result


@pytest.mark.asyncio
async def test_generate_full_content_returns_all():
    with patch("services.content_generator.generate_blog", new_callable=AsyncMock) as mock_blog, \
         patch("services.content_generator.generate_social_posts", new_callable=AsyncMock) as mock_social, \
         patch("services.content_generator.generate_email", new_callable=AsyncMock) as mock_email:
        mock_blog.return_value = "# Blog\n\nContent"
        mock_social.return_value = [{"platform": "twitter", "content": "Post"}]
        mock_email.return_value = {"subject": "Subject"}

        result = await generate_full_content("Test topic")
        assert "blog_post" in result
        assert "social_media_posts" in result
        assert "email_newsletter" in result
        assert result["topic"] == "Test topic"
