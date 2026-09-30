from fastapi import APIRouter,Form,HTTPException,Request
from fastapi.templating import Jinja2Templates
from .config import get_settings
from .models import PromptRequest,ImageTestRequest
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf
router=APIRouter(); settings=get_settings(); templates=Jinja2Templates(directory=str(settings.templates_dir))
def _all(data):
    outline=generate_outline(data); stories=generate_story(data,outline); images=[]
    for p in outline:
        q=f"{p['image_prompt']}. Consistent comic character: {data.character_name}. Setting: {data.setting}. Tone: {data.tone}. Art style: {data.art_style}. No text, no watermark."
        images.append(generate_image(q,p['panel_number']))
    layout=build_comic_layout(outline,stories,images); return layout,save_pdf(layout,settings.exports_dir)
@router.get('/')
async def home(request:Request): return templates.TemplateResponse(request=request,name='index.html',context={'app_name':settings.app_name,'image_backend':settings.image_backend})
@router.post('/generate')
async def generate(request:Request,story_prompt:str=Form(...),character_name:str=Form(...),setting:str=Form(...),tone:str=Form(...),art_style:str=Form(...)):
    try:
        data=PromptRequest(story_prompt=story_prompt,character_name=character_name,setting=setting,tone=tone,art_style=art_style); layout,pdf=_all(data)
        return templates.TemplateResponse(request=request,name='comic_preview.html',context={'app_name':settings.app_name,'layout':layout,'pdf_url':pdf})
    except Exception as e: return templates.TemplateResponse(request=request,name='error.html',context={'app_name':settings.app_name,'error':str(e)},status_code=500)
@router.post('/generate-comic/json')
async def generate_json(data:PromptRequest):
    try:
        layout,pdf=_all(data); return {'success':True,'message':'Comic generated successfully.','layout':layout,'pdf_url':pdf}
    except Exception as e: raise HTTPException(status_code=500,detail=str(e))
@router.post('/test-image')
async def test_image(data:ImageTestRequest):
    try: return {'success':True,'image_url':generate_image(data.prompt,0)}
    except Exception as e: raise HTTPException(status_code=500,detail=str(e))
@router.get('/export-success')
async def export_success(request:Request,pdf_url:str=''): return templates.TemplateResponse(request=request,name='export_success.html',context={'app_name':settings.app_name,'pdf_url':pdf_url})
@router.get('/health')
async def health(): return {'status':'ok','app':settings.app_name,'gemini_configured':bool(settings.gemini_api_key),'image_backend':settings.image_backend,'image_model':settings.image_model_id}
