from app.models import PromptRequest
from app.layout_builder import build_comic_layout
def test_validation():
    x=PromptRequest(story_prompt='A fox finds a door.',character_name='Ravi',setting='Forest',tone='Dramatic',art_style='Comic book'); assert x.character_name=='Ravi'
def test_layout():
    o=[{'panel_number':i,'title':f'P{i}','scene_description':'S','image_prompt':'I'} for i in range(1,6)]; s=[{'panel_number':i,'caption':'C','narration':'N','dialogue':'D'} for i in range(1,6)]; imgs=[f'/static/panels/{i}.png' for i in range(1,6)]; x=build_comic_layout(o,s,imgs); assert len(x)==5 and x[4]['dialogue']=='D'
