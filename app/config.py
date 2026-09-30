from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR=Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    app_name:str='ComicCraft'; debug:bool=True; host:str='127.0.0.1'; port:int=8000
    gemini_api_key:str=''; gemini_flash_model:str='gemini-2.5-flash'; gemini_pro_model:str='gemini-2.5-pro'
    image_backend:str='demo'; image_model_id:str='stable-diffusion-v1-5/stable-diffusion-v1-5'; hf_token:str=''
    image_device:str='auto'; image_steps:int=20; image_width:int=512; image_height:int=512; image_guidance:float=7.5
    model_config=SettingsConfigDict(env_file='.env',env_file_encoding='utf-8',case_sensitive=False,extra='ignore')
    @property
    def static_dir(self): return BASE_DIR/'static'
    @property
    def panels_dir(self): return self.static_dir/'panels'
    @property
    def exports_dir(self): return self.static_dir/'exports'
    @property
    def templates_dir(self): return BASE_DIR/'templates'
@lru_cache
def get_settings():
    s=Settings(); s.panels_dir.mkdir(parents=True,exist_ok=True); s.exports_dir.mkdir(parents=True,exist_ok=True); return s
