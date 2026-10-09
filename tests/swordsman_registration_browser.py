"""Real browser regression for the owner's undersized hair rejection.

This checks sampled crown coverage, not art perspective or visual approval.
"""
import base64,io,json
from pathlib import Path
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];p=json.loads((R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text());s=json.loads((R/'authoring/characters/builds/swordsman-registration-v1/measured-sockets.json').read_text());D=p['bodyContract']['directions'];rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();page.goto('http://127.0.0.1:8022/character-review.html',wait_until='networkidle');page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
 for action in p['bodyContract']['actions']:
  original=Image.open(R/f'assets/characters/swordsman-ro1-painted-v1/body-{action.lower()}.png').convert('RGBA')
  for j,d in enumerate(D):
   for i in range(len(p['parts']['swordsman-head']['timelines'][action][d]['frames'])):
    a=np.asarray(original.crop((i*320,j*320,(i+1)*320,(j+1)*320)));l,t,r,bot=s[f'{action}/{d}/{i}']['headBox'];mask=np.zeros((320,320),bool);mask[t:t+16,l:r]=True;mask&=(a[:,:,0]>130)&(a[:,:,1]>85)&(a[:,:,2]>55)&(a[:,:,0]>a[:,:,1]*1.13)&(a[:,:,1]>a[:,:,2]*1.10)&(a[:,:,2]>a[:,:,0]*.50)&(a[:,:,3]>200)
    for hair in ['hair-a','hair-b']:
     data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=action,direction=d,frameIndex=i,appearance={'Hair':hair},scale=1,canonical=True,visibleLayers=['HairFront']));ha=np.asarray(Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA'))[:,:,3];coverage=float((ha[mask]>220).mean());rows.append(dict(action=action,direction=d,frame=i,hair=hair,crownCoverage=coverage))
 b.close()
minimum=min(r['crownCoverage'] for r in rows)
assert len(rows)==656 and minimum>.97,(len(rows),minimum)
receipt={'scope':'Opaque Hair coverage of existing painted skin in the upper sixteen skull rows; excludes face and nape; does not certify projected angle or visual approval','poses':328,'hairVariants':2,'minimumCrownCoverage':minimum,'threshold':.97,'ownerVisualApproval':'PENDING','rows':rows}
(R/'docs/review/character-bodywithoutfit-registration-v1/hair-crown-raster-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'PASS 656 actual-browser Hair/Head crown raster comparisons; minimum {minimum:.4%}')
