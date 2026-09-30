import json
from google import genai
from google.genai import types
from .config import get_settings
from .models import ComicStory,PromptRequest
def _client():
    s=get_settings()
    if not s.gemini_api_key: raise RuntimeError('GEMINI_API_KEY is not configured. Add it to .env.')
    return genai.Client(api_key=s.gemini_api_key)
def generate_story(request:PromptRequest,outline:list[dict]):
    s=get_settings(); c=_client(); outline_json=json.dumps(outline,ensure_ascii=False)
    prompt=f'''Write the full five-panel comic story from this outline: {outline_json}. Character: {request.character_name}; setting: {request.setting}; tone: {request.tone}. For every panel produce caption, narration and natural dialogue. Keep continuity. Return only JSON.'''
    schema={'type':'OBJECT','properties':{'panels':{'type':'ARRAY','minItems':5,'maxItems':5,'items':{'type':'OBJECT','properties':{'panel_number':{'type':'INTEGER'},'caption':{'type':'STRING'},'narration':{'type':'STRING'},'dialogue':{'type':'STRING'}},'required':['panel_number','caption','narration','dialogue']}}},'required':['panels']}
    r=c.models.generate_content(model=s.gemini_pro_model,contents=prompt,config=types.GenerateContentConfig(temperature=.9,max_output_tokens=6000,response_mime_type='application/json',response_schema=schema))
    try: out=ComicStory.model_validate_json(r.text or '')
    except Exception:
        try: out=ComicStory.model_validate(json.loads(r.text or '{}'))
        except Exception as e: raise RuntimeError(f'Gemini story response could not be validated: {e}')
    out.panels.sort(key=lambda x:x.panel_number)
    if [p.panel_number for p in out.panels]!=[1,2,3,4,5]: raise RuntimeError('Gemini returned invalid story panel numbering.')
    return [p.model_dump() for p in out.panels]
