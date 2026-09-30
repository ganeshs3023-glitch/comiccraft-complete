# ComicCraft

FastAPI + Gemini + Stable Diffusion comic generator based on the supplied project documentation.

## Setup (VS Code / Windows)

1. Install Python 3.11 or 3.12.
2. Open this folder in VS Code.
3. Terminal:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
5. Leave `IMAGE_BACKEND=demo` for the first run. This tests the complete UI, Gemini, layout and PDF flow without downloading Stable Diffusion.
6. Start:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## Real Stable Diffusion

Set `IMAGE_BACKEND=diffusers`. `IMAGE_MODEL_ID` is configurable and defaults to `stable-diffusion-v1-5/stable-diffusion-v1-5`. A compatible GPU is strongly recommended. The first generation downloads the model.

## API

`POST /generate-comic/json` accepts `story_prompt`, `character_name`, `setting`, `tone`, `art_style`.

`POST /test-image` accepts `{ "prompt": "..." }`.

`GET /health` reports configuration state.

## Tests

```powershell
pytest -q
```
