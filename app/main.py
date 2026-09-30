from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .routes import router
s=get_settings(); app=FastAPI(title='ComicCraft API',description='AI-powered five-panel comic story creator.',version='1.0.0')
app.mount('/static',StaticFiles(directory=str(s.static_dir)),name='static'); app.include_router(router)
