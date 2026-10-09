"""Bake existing original Head+Hair appearance into independent RO-style head sets."""
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import json,base64,io
R=Path(__file__).resolve().parents[1];B=R/'authoring/characters/builds/swordsman-true8dir-v1';O=R/'assets/characters/swordsman-true8dir-v1';motion=json.loads((R/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text());records={}
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge',headless=True);p=b.new_page();p.goto('http://127.0.0.1:8022/character-review.html?anatomy=1');p.wait_for_function('window.AstraeonCharacterReview');p.evaluate('AstraeonCharacterReview.prepareVariants()')
 for style in ['a','b']:
  records[style]={}
  for action,a in motion['actions'].items():
   n=len(a['directions']['S']['frames']);atlas=Image.new('RGBA',(n*320,8*320));records[style][action]={}
   for row,d in enumerate(a['directions']):
    frames=[]
    for i in range(n):
     o=dict(action=action,direction=d,frameIndex=i,canonical=True,visibleLayers=['HeadBase','HairFront','HairBack'],appearance={'Hair':'hair-'+style})
     data=p.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',o);im=Image.open(io.BytesIO(base64.b64decode(data.split(',')[1])));atlas.paste(im,(i*320,row*320))
     sock=p.evaluate('''(o)=>{const A=AstraeonCharacterAssembly,s=AstraeonCharacterReview.loaded.compiled.sample(o.action,o.direction,0,{frameIndex:o.frameIndex});const h=s.layers.find(l=>l.layer==='HeadBase');return Object.fromEntries(Object.entries(h.sockets).map(([k,v])=>[k,A.composeTransform(h.transform,v)]))}''',o)
     frames.append(dict(rect=[i*320,row*320,320,320],sockets=sock))
    records[style][action][d]=frames
   atlas.save(O/f'head-{style}-{action.lower()}.png')
 b.close()
(B/'head-sets.json').write_text(json.dumps(records,indent=2))
