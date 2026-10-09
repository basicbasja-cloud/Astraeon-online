"""Real browser regression for the owner's undersized hair rejection.

This checks sampled crown coverage, not art perspective or visual approval.
"""
import base64,io,json
from pathlib import Path
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];p=json.loads((R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text());s=json.loads((R/'authoring/characters/builds/swordsman-registration-v1/measured-sockets.json').read_text());D=p['bodyContract']['directions'];rows=[];grips=[];sources={f['action']+'/'+f['direction']+'/'+str(f['frame']):f for f in json.loads((R/'authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json').read_text())['frames']};bodyImages={id:Image.open(R/v['file']).convert('RGBA') for id,v in p['atlases'].items() if id.startswith('body-') or id.startswith('royal-')}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();page.goto('http://127.0.0.1:8022/character-review.html',wait_until='networkidle');page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
 for action in p['bodyContract']['actions']:
  original=Image.open(R/f'assets/characters/swordsman-ro1-painted-v1/body-{action.lower()}.png').convert('RGBA')
  for j,d in enumerate(D):
   for i in range(len(p['parts']['swordsman-head']['timelines'][action][d]['frames'])):
    source=sources[f'{action}/{d}/{i}']['sourceFrame'];a=np.asarray(original.crop((source*320,j*320,(source+1)*320,(j+1)*320)));l,t,r,bot=s[f'{action}/{d}/{i}']['headBox'];mask=np.zeros((320,320),bool);mask[t:t+16,l:r]=True;mask&=(a[:,:,0]>130)&(a[:,:,1]>85)&(a[:,:,2]>55)&(a[:,:,0]>a[:,:,1]*1.13)&(a[:,:,1]>a[:,:,2]*1.10)&(a[:,:,2]>a[:,:,0]*.50)&(a[:,:,3]>200)
    for hair in ['hair-a','hair-b']:
     data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=action,direction=d,frameIndex=i,appearance={'Hair':hair},scale=1,canonical=True,visibleLayers=['HairFront']));ha=np.asarray(Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA'))[:,:,3];coverage=float((ha[mask]>220).mean());rows.append(dict(action=action,direction=d,frame=i,hair=hair,crownCoverage=coverage))
 # Real composite glove pixels must cover the weapon handle in strike and
 # recovery. Restrict the comparison to opaque authored palm centres.
 for d in D:
  for i in range(7,16):
   for body in ['swordsman-body-default','swordsman-body-royal-proof']:
    ref=p['parts'][body]['timelines']['BasicAttack'][d]['frames'][i]['layers']['Body'];poly=ref['foregroundPasses'][0]['polygon'];gx=round(sum(q[0] for q in poly)/len(poly));gy=round(sum(q[1] for q in poly)/len(poly));source=bodyImages[ref['atlasId']].getpixel((ref['rect'][0]+gx,ref['rect'][1]+gy));assert source[3]>200,(d,i,source)
    for weapon in ['weapon-a','weapon-b']:
     data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='BasicAttack',direction=d,frameIndex=i,appearance={'BodyWithOutfit':body,'MainHand':weapon},scale=1,canonical=True));actual=Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA').getpixel((gx,gy));error=max(abs(actual[k]-source[k]) for k in range(3));assert error<=8,(d,i,body,weapon,actual,source,error);grips.append(dict(direction=d,frame=i,body=body,weapon=weapon,palmPixelError=error))
 b.close()
minimum=min(r['crownCoverage'] for r in rows)
assert len(rows)==656 and minimum>.97,(len(rows),minimum)
receipt={'scope':'Opaque Hair coverage of existing painted skin in the upper sixteen skull rows; excludes face and nape; does not certify projected angle or visual approval','poses':328,'hairVariants':2,'minimumCrownCoverage':minimum,'threshold':.97,'ownerVisualApproval':'PENDING','rows':rows,'gloveForegroundComparisons':len(grips),'maximumPalmPixelError':max(g['palmPixelError'] for g in grips),'gloves':grips}
(R/'docs/review/character-bodywithoutfit-registration-v1/hair-crown-raster-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(f'PASS 656 actual-browser Hair/Head crown raster comparisons; minimum {minimum:.4%}; {len(grips)} actual-composite glove comparisons')
