import time

from google import genai
from google.genai import types

from .config import get_settings
from .models import ComicOutline, PromptRequest


def _client():
    s = get_settings()

    if not s.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env."
        )

    return genai.Client(api_key=s.gemini_api_key)


def generate_outline(request: PromptRequest):
    s = get_settings()

    prompt = f"""
Create a cohesive five-panel comic outline.

Story:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Return exactly 5 panels.

For EVERY panel, provide exactly these fields:
- panel_number: integer from 1 to 5
- title: short panel title
- scene_description: detailed description of what happens in the panel
- image_prompt: detailed visual prompt for generating the comic panel image

Make the story flow naturally from panel 1 through panel 5.
Keep the main character visually consistent across all panels.
"""

    schema = {
        "type": "OBJECT",
        "properties": {
            "panels": {
                "type": "ARRAY",
                "minItems": 5,
                "maxItems": 5,
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "panel_number": {
                            "type": "INTEGER"
                        },
                        "title": {
                            "type": "STRING"
                        },
                        "scene_description": {
                            "type": "STRING"
                        },
                        "image_prompt": {
                            "type": "STRING"
                        },
                    },
                    "required": [
                        "panel_number",
                        "title",
                        "scene_description",
                        "image_prompt",
                    ],
                },
            }
        },
        "required": ["panels"],
    }

    max_retries = 4
    delays = [3, 7, 15, 30]

    for attempt in range(max_retries + 1):
        try:
            client = _client()

            response = client.models.generate_content(
                model=s.gemini_flash_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=5000,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )

            text = response.text or "{}"

            try:
                outline = ComicOutline.model_validate_json(text)
            except Exception as e:
                raise RuntimeError(
                    f"Gemini returned an invalid JSON response: {e}"
                )

            outline.panels.sort(
                key=lambda panel: panel.panel_number
            )

            numbers = [
                panel.panel_number
                for panel in outline.panels
            ]

            if numbers != [1, 2, 3, 4, 5]:
                raise RuntimeError(
                    "Gemini returned invalid panel numbering."
                )

            return [
                panel.model_dump()
                for panel in outline.panels
            ]

        except Exception as e:
            error_text = str(e)

            retryable = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "500" in error_text
                or "INTERNAL" in error_text
                or "502" in error_text
                or "504" in error_text
                or "DEADLINE" in error_text
            )

            if not retryable or attempt >= max_retries:
                raise

            delay = delays[attempt]

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {delay} seconds "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            time.sleep(delay)