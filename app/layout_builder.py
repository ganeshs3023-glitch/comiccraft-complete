def build_comic_layout(outline,stories,image_paths):
    by={x['panel_number']:x for x in stories}; out=[]
    for i,p in enumerate(outline):
        st=by.get(p['panel_number'],{}); out.append({'panel_number':p['panel_number'],'title':p['title'],'scene_description':p['scene_description'],'image_prompt':p['image_prompt'],'image_path':image_paths[i],'caption':st.get('caption',''),'narration':st.get('narration',''),'dialogue':st.get('dialogue','')})
    return out
