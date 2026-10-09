#!/usr/bin/env python3
"""Export repaired review evidence from the actual browser assembly renderer."""
import argparse,base64,hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];OUT=R/'docs/review/character-bodywithoutfit-registration-v1';D=['S','SW','W','NW','N','NE','E','SE']
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
PALETTE=None
def authored_palette():
 # Sample visible painted pixels, with independent Head samples retained at
 # full weight. Thumbnail montages underrepresent faces and flatten skin gold.
 p=json.loads((R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text());pool=[]
 for id,a in p['atlases'].items():
  pixels=np.asarray(Image.open(R/a['file']).convert('RGBA')).reshape(-1,4);visible=pixels[pixels[:,3]>200,:3]
  if len(visible):pool.append(visible[::max(1,len(visible)//20000)][:20000])
  if id.startswith('body-'):
   # Small jade insignia must survive alongside the much larger bronze and
   # proof-costume blue areas. Retain actual source colours, not invented ones.
   jade=visible[(visible[:,1]>visible[:,0]*1.18)&(visible[:,1]>visible[:,2]*1.08)]
   if len(jade):pool.append(jade[::max(1,len(jade)//6000)][:6000])
 for col,count in [((36,54,68),5000),((237,243,255),1000),((239,213,166),1000),((185,210,226),1000)]:pool.append(np.tile(np.array(col,dtype='uint8'),(count,1)))
 pixels=np.concatenate(pool);height=math.ceil(len(pixels)/512);pad=np.tile(np.array([36,54,68],dtype='uint8'),(height*512-len(pixels),1));return Image.fromarray(np.concatenate([pixels,pad]).reshape(height,512,3)).quantize(colors=256,method=Image.Quantize.MEDIANCUT)
def animate(images,durations,path):
 global PALETTE
 if PALETTE is None:PALETTE=authored_palette()
 cumulative=previous=0;delays=[]
 for ms in durations:
  cumulative+=ms;rounded=round(cumulative/10)*10;delays.append(max(10,rounded-previous));previous=rounded
 frames=[im.convert('RGB').quantize(palette=PALETTE,dither=Image.Dither.NONE) for im in images]
 frames[0].save(path,save_all=True,append_images=frames[1:],duration=delays,loop=0,optimize=True,disposal=2)
def decode(data):return Image.open(io.BytesIO(base64.b64decode(data.split(',',1)[1]))).convert('RGBA')
def board(items,size=320,columns=4,title=''):
 im=Image.new('RGB',(size*columns,math.ceil(len(items)/columns)*(size+30)+32),'#243644');dr=ImageDraw.Draw(im);dr.text((12,7),title,fill='#efd5a6',font=FONT)
 for i,(label,tile) in enumerate(items):
  x=i%columns*size;y=i//columns*(size+30)+32;dr.text((x+8,y+5),label,fill='#edf3ff',font=FONT);tile=tile.resize((size,size),Image.Resampling.LANCZOS);im.paste(tile,(x,y+30),tile)
 return im
def labeled(tile,title):
 im=Image.new('RGB',(640,704),'#243644');im.paste(tile,(0,32),tile);dr=ImageDraw.Draw(im);dr.text((14,8),title,fill='#efd5a6',font=FONT);dr.text((14,679),'Repaired painted assembly — owner approval pending',fill='#b9d2e2',font=FONT);return im
def run(url):
 OUT.mkdir(parents=True,exist_ok=True)
 for sub in ['frames','strips','screenshots']:(OUT/sub).mkdir(exist_ok=True)
 t=json.loads((R/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text());cache={};errors=[];badhttp=[];proof={}
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1420,'height':1080})
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:badhttp.append(f'{r.status} {r.url}') if r.status>=400 else None)
  page.goto(url+'/character-review.html',wait_until='networkidle');page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
  defaults=page.evaluate('AstraeonCharacterReview.loaded.appearance')
  page.screenshot(path=str(OUT/'screenshots/repaired-desktop.png'))
  legacy=b.new_page();legacy.goto(url+'/character-review.html?legacy=1',wait_until='networkidle');legacy.wait_for_function('window.AstraeonCharacterReview')
  def capture(a,d,i,**kw):return decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=a,direction=d,frameIndex=i,scale=2,canonical=True,**kw)))
  for a,action in t['actions'].items():
   print('Capturing '+a,flush=True)
   page.evaluate('(action)=>AstraeonCharacterReview.setReviewPose({action,play:true})',a);initial=page.evaluate('AstraeonCharacterReview.snapshot().time');first=page.evaluate('document.querySelector("#hero").toDataURL()');page.wait_for_function('(t)=>AstraeonCharacterReview.snapshot().time>t+360',arg=initial);assert page.evaluate('document.querySelector("#hero").toDataURL()')!=first
   for d in D:
    tiles=[]
    for i,f in enumerate(action['directions'][d]['frames']):
     tile=capture(a,d,i);bbox=tile.getbbox();assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<640 and bbox[3]<640,(a,d,i,bbox)
     cache[a,d,i]=tile;folder=OUT/'frames'/a/d;folder.mkdir(parents=True,exist_ok=True);tile.save(folder/f'{i:02}.png');tiles.append((str(i)+' '+(f['referencePhase'] or 'in-between'),tile))
    board(tiles,size=256,columns=8,title=a+' '+d+' — all authored frames').save(OUT/'strips'/f'{a}-{d}.png')
   films=[];delays=[];equipped=[]
   for i,f in enumerate(action['directions']['S']['frames']):
    films.append(board([(d,cache[a,d,i]) for d in D],size=384,title=a+' — all eight directions / frame '+str(i)));delays.append(f['durationMs'])
    variant={**defaults,'Hair':'hair-b','MainHand':'weapon-b','OffHand':'offhand','Headgear':'headgear'}
    equipped.append(board([(d,capture(a,d,i,appearance=variant)) for d in D],size=320,title=a+' — Hair B / Sword B / shield / circlet'))
   animate(films,delays,OUT/f'{a}-fixed-eight-directions.gif');animate(equipped,delays,OUT/f'{a}-alternate-equipped-eight-directions.gif')
   # APNG retains exact milliseconds; GIF centisecond rounding is only preview.
   films[0].save(OUT/f'{a}-fixed-eight-directions.apng',format='PNG',save_all=True,append_images=films[1:],duration=delays,loop=0,disposal=0,blend=0)
   contact=0 if a=='Idle' else 7
   overlay=['root','body anchors','head pivot','hair pivot','mainHand anchor','weapon grip pivot','back anchor','cape pivot','action phase']
   board([(d,capture(a,d,contact,overlay=overlay)) for d in D],size=384,title=a+' — authored anchors and local pivots').save(OUT/f'{a}-anchor-debug.png')
  board([(d,capture('BasicAttack',d,7,overlay=['mainHand anchor','weapon grip pivot','action phase','sampling mode'])) for d in D],size=384,title='BasicAttack contact — actual grip / shared body hand anchor').save(OUT/'BasicAttack-grip-contact-debug.png')
  # Exact paired before/after captures use identical action/direction/frame.
  for name,indices in [('Head-neck',[('Idle',0),('BasicAttack',7)]),('Hair',[('Idle',0),('BasicAttack',6)]),('Weapon-grip',[('Idle',0),('BasicAttack',7)]),('Cape',[('Idle',0),('BasicAttack',9)])]:
   items=[]
   for a,i in indices:
    for d in D:
     before=decode(legacy.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=a,direction=d,frameIndex=i,scale=2,canonical=True)))
     items.extend([(a+'/'+d+' before',before),(a+'/'+d+' repaired',cache[a,d,i])])
   board(items,size=320,title=name+' — rejected baseline / repaired assembly').save(OUT/f'{name}-before-after.png')
  # Close registration views respond directly to the owner's size/angle
  # rejection. Preserve the previous candidate beside the original baseline.
  closeups=[];closeupDurations=[]
  for a,action in t['actions'].items():
   for i,f in enumerate(action['directions']['S']['frames']):
    closeups.append(board([(d,cache[a,d,i].crop((220,170,430,390))) for d in D],size=384,title=a+' — skull, hair angle and shoulder/cape attachment'))
    closeupDurations.append(f['durationMs'])
  animate(closeups,closeupDurations,OUT/'Hair-cape-closeup-eight-directions.gif')
  # The owner's W rejection needs a readable hand/handle view, with the
  # camera following the authored grip only in this development export.
  pack=json.loads((R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text());gripFilm=[];gripDelays=[]
  for i,f in enumerate(t['actions']['BasicAttack']['directions']['S']['frames']):
   items=[]
   for d in D:
    poly=pack['parts']['swordsman-body-default']['timelines']['BasicAttack'][d]['frames'][i]['layers']['Body']['foregroundPasses'][0]['polygon'];gx=sum(p[0] for p in poly)/len(poly)*2;gy=sum(p[1] for p in poly)/len(poly)*2
    items.append((d,cache['BasicAttack',d,i].crop((round(gx-100),round(gy-100),round(gx+100),round(gy+100)))))
   gripFilm.append(board(items,size=384,title='BasicAttack frame '+str(i)+' — glove/handle close-up, playback at half speed'));gripDelays.append(f['durationMs']*2)
  animate(gripFilm,gripDelays,OUT/'BasicAttack-hand-grip-closeup.gif')
  wframes=[labeled(cache['BasicAttack','W',i],f'Sword alignment / W / frame {i+1} / slow inspection') for i in range(16)]
  animate(wframes,[max(80,f['durationMs']*2) for f in t['actions']['BasicAttack']['directions']['W']['frames']],OUT/'Sword-alignment-W-review.gif')
  latest=json.loads((OUT/'rejected-sword-candidate-31bb1a8/appearance-pack.json').read_text());items=[]
  # The latest rejection predates the phase-view and projected-arc changes.
  # Its retained all-direction GIF contains the actual rejected contact.
  rejected=Image.open(OUT/'rejected-sword-candidate-31bb1a8/BasicAttack-fixed-eight-directions.gif');rejected.seek(7);rejected=rejected.convert('RGBA')
  for j,d in enumerate(D):
   x=j%4*384;y=j//4*414+62
   old=rejected.crop((x,y,x+384,y+384));items.extend([(d+' rejected sword alignment',old),(d+' revised contact',cache['BasicAttack',d,7])])
  board(items,size=384,title='Latest sword rejection / revised held blade, wrist arc and contact phase').save(OUT/'Sword-alignment-latest-rejection-before-after.png')
  pairs=[]
  for i in range(16):
   old=Image.open(OUT/'rejected-grip-candidate-4c0f0e2/W'/f'{i:02}.png').convert('RGBA');pairs.extend([('W frame '+str(i)+' owner-rejected',old),('W frame '+str(i)+' revised',cache['BasicAttack','W',i])])
  board(pairs,size=384,title='W hand/sword coordination — original rejection / glove occlusion and palm/pose repair').save(OUT/'Weapon-W-latest-rejection-before-after.png')
  pairs=[]
  for a,i in [('Idle',0),('BasicAttack',7)]:
   for d in D:
    old=Image.open(OUT/'rejected-registration-candidate-220d535/frames'/a/d/f'{i:02}.png').convert('RGBA')
    pairs.extend([(a+'/'+d+' owner-rejected',old.crop((220,170,430,390))),(a+'/'+d+' revised',cache[a,d,i].crop((220,170,430,390)))])
  board(pairs,size=384,title='Latest owner rejection — hair size/angle and cape neckline source correction').save(OUT/'Hair-cape-latest-rejection-before-after.png')
  # Runtime swap freezes playback only for the exact before/after assertion.
  # Body selection changes via the real async loader, with no clock mutation.
  page.evaluate('AstraeonCharacterReview.setReviewPose({action:"Walk",direction:"SW",timeMs:277,play:false})');before=page.evaluate('AstraeonCharacterReview.snapshot()');beforePixels=page.evaluate('AstraeonCharacterReview.renderPose({action:"Walk",direction:"SW",timeMs:277,visibleLayers:["HeadBase","HairFront","MainHand","OffHand","HeadgearTop","GarmentBack","GarmentFront"]})')
  page.evaluate('AstraeonCharacterReview.setAppearance({BodyWithOutfit:"swordsman-body-royal-proof"})');after=page.evaluate('AstraeonCharacterReview.snapshot()');afterPixels=page.evaluate('AstraeonCharacterReview.renderPose({action:"Walk",direction:"SW",timeMs:277,visibleLayers:["HeadBase","HairFront","MainHand","OffHand","HeadgearTop","GarmentBack","GarmentFront"]})');assert beforePixels==afterPixels
  for key in ['action','direction','frameIndex','time','cosmetic','frame','registeredAnchors']:assert before[key]==after[key],key
  assert before['appearance']['BodyWithOutfit']!=after['appearance']['BodyWithOutfit'];assert {k:v for k,v in before['appearance'].items() if k!='BodyWithOutfit'}=={k:v for k,v in after['appearance'].items() if k!='BodyWithOutfit'}
  proof['costumeSwap']={'action':after['action'],'direction':after['direction'],'frameIndex':after['frameIndex'],'elapsedMs':after['time'],'cosmeticClockUnchanged':True,'otherLayersPixelIdentical':True,'registeredAnchorsUnchanged':True,'appearanceBefore':before['appearance'],'appearanceAfter':after['appearance']}
  page.evaluate('AstraeonCharacterReview.setAppearance({BodyWithOutfit:"swordsman-body-default"})')
  proof['allFrameRasterIsolation']=page.evaluate('''()=>{const R=AstraeonCharacterReview,c=R.loaded.compiled;let count=0;for(const [action,a]of Object.entries(c.motion.template.actions))for(const direction of AstraeonMotionTemplate.DIRECTIONS)for(let frameIndex=0;frameIndex<a.directions[direction].frames.length;frameIndex++){const o={action,direction,frameIndex,visibleLayers:["HeadBase","HairFront","MainHand","OffHand","HeadgearTop","GarmentBack","GarmentFront"]},appearance={...c.pack.defaultParts,OffHand:'offhand',Headgear:'headgear'};const before=R.renderPose({...o,appearance}),after=R.renderPose({...o,appearance:{...appearance,BodyWithOutfit:'swordsman-body-royal-proof'}});if(before!==after)throw Error('costume changed non-body raster');count++}return {count,unchangedNonBodyRaster:true}}''')
  # Animated swaps use one continuous time variable, not per-costume resets.
  swaps=[];delays=[];clock=0
  for n in range(48):
   costume='swordsman-body-default' if n<7 or n>=23 else 'swordsman-body-royal-proof';appearance={**defaults,'BodyWithOutfit':costume,'OffHand':'offhand','Headgear':'headgear'}
   if n in [7,23]:
    prior='swordsman-body-default' if n==7 else 'swordsman-body-royal-proof'
    data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='Walk',direction='SW',timeMs=clock,appearance={**appearance,'BodyWithOutfit':prior},scale=2,canonical=True));swaps.append(labeled(decode(data),f'Walk / SW / same time {clock}ms / BEFORE costume swap'));delays.append(220)
   data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='Walk',direction='SW',timeMs=clock,appearance=appearance,scale=2,canonical=True));tile=decode(data);swaps.append(labeled(tile,f'Walk / SW / time {clock}ms / costume '+('A' if costume.endswith('default') else 'B')));delays.append(220 if n in [7,23] else 38);clock+=38
  animate(swaps,delays,OUT/'costume-swap-proof.gif')
  # Boundary evidence includes frame16->frame1 without changing phase sockets.
  board([(d+' frame16',cache['Walk',d,15]) for d in D]+[(d+' frame1',cache['Walk',d,0]) for d in D],size=320,title='Walk loop boundary — frame16 to frame1').save(OUT/'Walk-loop-boundary.png')
  board([(a+'/'+d,decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action=a,direction=d,frameIndex=0 if a=='Idle' else 7,scale=1)))) for a in t['actions'] for d in D],size=128,columns=8,title='Gameplay scale — 70px reference height').save(OUT/'gameplay-scale-review.png')
  # Development overlays are opt-in. Verify every requested solo control works.
  for solo in ['BodyWithOutfit','Head','Hair','MainHand','OffHand','Headgear','Garment','Composite']:page.select_option('#solo',solo)
  page.select_option('#solo','Composite');assert page.evaluate('[...document.querySelectorAll("#debug-toggles input")].every(c=>!c.checked)');assert page.input_value('#anchors')=='0'
  mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);mobile.goto(url+'/character-review.html',wait_until='networkidle');mobile.wait_for_function('window.AstraeonCharacterReview');assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth');mobile.screenshot(path=str(OUT/'screenshots/repaired-mobile.png'));mobile.close()
  b.close()
 # Owner gets a large, sequential view of EVERY action and direction.
 films=[];delays=[]
 for a,action in t['actions'].items():
  for d in D:
   for repeat in range(1 if a=='Idle' else 2):
    for i,f in enumerate(action['directions'][d]['frames']):films.append(labeled(cache[a,d,i],f'ASTRAEON / {a} / {d} / frame {i+1}'));delays.append(f['durationMs'])
 animate(films,delays,OUT/'swordsman-repaired-owner-preview.gif')
 assert not errors and not badhttp,(errors,badhttp)
 proof.update(renderedFrames=328,allActions=list(t['actions']),directions=D,canvasCropChecks='PASS',desktop=True,mobile=True,debugOffByDefault=True,oldRejectedProofPreserved=True,errors=errors,unexpectedHTTP=badhttp,ownerVisualApproval='PENDING')
 (OUT/'browser-review.json').write_text(json.dumps(proof,indent=2)+'\n')
 artifacts={path.name:{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size} for path in OUT.iterdir() if path.suffix in ['.gif','.png','.apng']};(OUT/'artifact-receipt.json').write_text(json.dumps(artifacts,indent=2)+'\n')
 print('Exported repaired owner GIF, three action GIFs/APNGs, equipped variants, before/after and anchor diagnostics, costume swap and gameplay scale',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8022');run(ap.parse_args().url.rstrip('/'))
