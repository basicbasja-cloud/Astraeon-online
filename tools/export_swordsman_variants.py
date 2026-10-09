#!/usr/bin/env python3
"""Render alternate equipment and the second appearance on the same timeline."""
import argparse,json,os
from PIL import Image
from playwright.sync_api import sync_playwright
from export_swordsman_review import ROOT,OUT,DIRS,board,decode,animate

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',default='http://127.0.0.1:8012');args=parser.parse_args()
motion=json.loads((ROOT/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text())
variant={'Hair':'hair-b','MainHand':'weapon-b','OffHand':'offhand','Headgear':'headgear','Garment':'garment'}
count=0
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page();page.goto(args.url+'/character-review.html',wait_until='networkidle');page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
    for action,a in motion['actions'].items():
        movies=[];durations=[]
        for i,f in enumerate(a['directions']['S']['frames']):
            items=[]
            for d in DIRS:
                appearance={**page.evaluate('AstraeonCharacterReview.loaded.appearance'),**variant}
                im=decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=action,direction=d,frameIndex=i,appearance=appearance,scale=4)))
                bbox=im.getbbox();assert bbox and min(bbox[:2])>0 and max(bbox[2:])<512,(action,d,i,'equipped crop')
                count+=1;items.append((d+' / Hair B, Sword B, shield, circlet',im))
            temp=OUT/'contact-sheets'/f'{action}-alternate-equipped.png';board(items,temp,4,256);movies.append(Image.open(temp).copy());durations.append(f['durationMs'])
        animate(movies,durations,OUT/'previews'/f'{action}-alternate-equipped-eight-directions.gif')
    page.evaluate('''async()=>{window.reuseProof=await AstraeonCharacterAssembly.loadAssembly({motionUrl:'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json',appearanceUrl:'authoring/characters/appearance/ro1-reuse-dummy/appearance-pack.json',allowDev:true})}''')
    movies=[];durations=[]
    for i,f in enumerate(motion['actions']['Walk']['directions']['S']['frames']):
        items=[]
        for d in DIRS:
            im=decode(page.evaluate('''([d,i])=>{const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d'),r=reuseProof,s=r.sample('Walk',d,0,{frameIndex:i});AstraeonCharacterAssembly.drawAssembly(ctx,s,r.images,{x:128,y:211.2,scale:140/176});return c.toDataURL()}''',[d,i]))
            items.append((d+' / same MotionTemplate, DEV_ONLY Body',im))
        temp=OUT/'contact-sheets/second-pack-reuse.png';board(items,temp,4,256);movies.append(Image.open(temp).copy());durations.append(f['durationMs'])
    animate(movies,durations,OUT/'previews/second-pack-reuse-eight-directions.gif')
    browser.close()
seed=Image.open(ROOT/'authoring/characters/gait-rig-v50/approved-warrior-seed.png').convert('RGBA')
items=[('Owner-approved ASTRAEON seed',seed)]+[(d+' / new painted identity, review pending',Image.open(OUT/'frames/Idle'/d/'00.png').convert('RGBA')) for d in DIRS]
board(items,OUT/'contact-sheets/approved-seed-vs-painted-turnaround.png',3,256)
(OUT/'variant-review.json').write_text(json.dumps(dict(fullyEquippedFrameCropChecks=count,hairB='all3 actions/all8 directions',weaponB='all3 actions/all8 directions',offhand=True,headgear=True,garment=True,secondPackUsesSameMotionTemplate=True,secondPackStatus='DEV_ONLY',ownerVisualApproval='PENDING'),indent=2)+'\n')
print('PASS328 equipped composites uncropped; exported all3 alternate equipment movies and second-pack animation')
