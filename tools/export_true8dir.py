"""Export owner evidence through the shipping browser assembly, with continuity diagnostics."""
from pathlib import Path
import io,base64,json,math,hashlib
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/review/character-true8dir-weapon-repair-v1';O.mkdir(exist_ok=True);D=['S','SW','W','NW','N','NE','E','SE'];F=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def board(items,cols=4,size=320,title=''):
 im=Image.new('RGB',(cols*size,math.ceil(len(items)/cols)*(size+25)+35),'#243644');dr=ImageDraw.Draw(im);dr.text((10,8),title,font=F,fill='#efd5a6')
 for k,(label,img) in enumerate(items):
  x=k%cols*size;y=k//cols*(size+25)+35;dr.text((x+5,y+3),label,font=F,fill='white');tile=img.resize((size,size),Image.Resampling.LANCZOS);im.paste(tile,(x,y+25),tile if tile.mode=='RGBA' else None)
 return im
def animate(frames,durations,path):
 # One palette across the entire animation prevents per-frame color flicker.
 pool=Image.new('RGB',(512,256*len(frames)))
 for i,f in enumerate(frames):pool.paste(f.resize((512,256)),(0,i*256))
 pal=pool.quantize(colors=256);ims=[f.quantize(palette=pal,dither=Image.Dither.NONE) for f in frames];total=last=0;delays=[]
 for t in durations:total+=t;now=round(total/10)*10;delays.append(now-last);last=now
 ims[0].save(path,save_all=True,append_images=ims[1:],duration=delays,loop=0,disposal=2,optimize=False)
m=json.loads((R/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text());dur=[f['durationMs'] for f in m['actions']['BasicAttack']['directions']['S']['frames']];cache={};old={};diagnostics={};errors=[];clipped=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge',headless=True);p=b.new_page(viewport={'width':1440,'height':1050});prev=b.new_page()
 for page,url in [(p,''),(prev,'?anatomy=1')]:page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8022/character-review.html'+url);page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
 def capture(page,d,i,**kw):
  data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='BasicAttack',direction=d,frameIndex=i,canonical=True,**kw));return Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA')
 modes={'body-only':dict(visibleLayers=['Body']),'weapon-only':dict(visibleLayers=['MainHand']),'body-weapon':dict(visibleLayers=['Body','MainHand']),'grip-debug':dict(visibleLayers=['Body','MainHand'],overlay=['arm joints','equipment anchor','weapon anchor','grip contact','weapon tip']),'full-composite':{}}
 for d in D:
  for i in range(16):
   for mode,kw in modes.items():cache[mode,d,i]=capture(p,d,i,**kw)
   im=cache['full-composite',d,i];box=im.getbbox()
   if not box or min(box[:2])<=0 or max(box[2:])>=320:clipped.append([d,i,box])
   old[d,i]=capture(prev,d,i)
  board([(str(i),cache['full-composite',d,i]) for i in range(16)],cols=8,title=d+' / all frames / owner approval pending').save(O/(d+'-all-frames.png'))
 for mode in modes:
  films=[board([(d,cache[mode,d,i]) for d in D],title='BasicAttack / '+mode+' / frame '+str(i)+' / owner approval pending') for i in range(16)];animate(films,dur,O/('BasicAttack-'+mode+'.gif'))
 normal=[board([(d,cache['full-composite',d,i]) for d in D],title='BasicAttack / 450ms / frame '+str(i)+' / owner approval pending') for i in range(16)];animate(normal,dur,O/'BasicAttack-eight-directions-normal.gif');animate(normal,[t*2 for t in dur],O/'BasicAttack-eight-directions-half-speed.gif');normal[0].save(O/'BasicAttack-exact-timing.apng',save_all=True,append_images=normal[1:],duration=dur,loop=0,disposal=0,blend=0)
 owner=[];od=[]
 for d in D:
  for speed in [1,2]:
   for i in range(16):owner.append(board([(d+' / '+str(i)+' / '+('normal' if speed==1 else 'half speed'),cache['full-composite',d,i])],cols=1,size=640,title='ASTRAEON / owner visual approval pending'));od.append(dur[i]*speed)
 animate(owner,od,O/'swordsman-basicattack-true8dir-owner-preview.gif')
 phases=[(0,'Ready'),(4,'Anticipation'),(6,'Acceleration'),(7,'Contact'),(10,'Follow-through'),(14,'Recovery')];board([(d+' / '+name,cache['full-composite',d,i]) for d in D for i,name in phases],cols=6,title='Eight projections / VISUAL_DERIVED attack reconstruction; raw RO attack has four projection groups').save(O/'true8dir-pose-board.png')
 board([(d,cache['grip-debug',d,7]) for d in D],title='Joint / grip / separate attachment anchors / contact').save(O/'joint-grip-overlay.png')
 for name,layers,crop in [('arm-anatomy-before-after',['Body'],None),('direction-pose-before-after',None,None),('weapon-grip-before-after',None,(70,65,265,240)),('weapon-draw-order-before-after',None,None)]:
  pairs=[]
  for d in D:
   for i in [7,14]:
    for page,label in [(prev,'before'),(p,'after')]:
     im=capture(page,d,i,**({'visibleLayers':layers} if layers else {}));im=im.crop(crop) if crop else im;pairs.append((d+'/'+str(i)+' '+label,im))
  board(pairs,cols=4,title=name+' / identical frame and scale / owner approval pending').save(O/(name+'.png'))
 sworditems=[]
 for weapon in ['weapon-a','weapon-b']:
  atlas=Image.open(R/f'assets/characters/swordsman-true8dir-v1/{weapon}-poses.png').convert('RGBA')
  for i,n in enumerate(['face','edge','foreshortened','rear']):
   tile=Image.new('RGBA',(128,128));tile.paste(atlas.crop((64*i,0,64*(i+1),128)),(32,0));sworditems.append((weapon+' '+n,tile))
 board(sworditems,size=256,title='Two sword designs / four original perspective samples each').save(O/'weapon-pose-set-contact-sheet.png')
 # Test real asynchronous appearance swaps without advancing either clock.
 proof=[]
 for d in D:
  p.evaluate('(d)=>AstraeonCharacterReview.setReviewPose({action:"BasicAttack",direction:d,timeMs:182,play:false})',d);before=p.evaluate('AstraeonCharacterReview.snapshot()')
  for patch in [{'BodyWithOutfit':'swordsman-body-royal-proof'},{'MainHand':'weapon-b'},{'Head':'head-style-b'}]:
   p.evaluate('(p)=>AstraeonCharacterReview.setAppearance(p)',patch);after=p.evaluate('AstraeonCharacterReview.snapshot()');assert all(before[k]==after[k] for k in ['action','direction','frameIndex','time','cosmetic','frame']);proof.append([d,patch,after['frameIndex'],after['time']])
  p.evaluate('AstraeonCharacterReview.setAppearance({BodyWithOutfit:"swordsman-body-default",MainHand:"weapon-a",Head:"head-style-a"})')
 board([(d+' royal / Sword B / Head B',capture(p,d,7,appearance={'BodyWithOutfit':'swordsman-body-royal-proof','MainHand':'weapon-b','Head':'head-style-b','OffHand':'offhand','Headgear':'headgear'})) for d in D],title='Same contact frame / alternate equipment and costume').save(O/'alternate-compatibility.png')
 # Retain raw values and suspicious-jump diagnostics rather than silently adjusting art.
 allsamples=p.evaluate('''()=>{const R=AstraeonCharacterReview,A=AstraeonCharacterAssembly;return Object.fromEntries(AstraeonMotionTemplate.DIRECTIONS.map(d=>[d,Array.from({length:16},(_,i)=>{const s=R.loaded.compiled.sample('BasicAttack',d,0,{frameIndex:i}),w=s.layers.find(l=>l.layer==='MainHand'),f=w.weaponPoseFrame,world=p=>A.composeTransform(w.transform,{x:p[0]-w.pivot[0],y:p[1]-w.pivot[1],rotation:0,scale:1});return {frame:i,grip:world(f.gripContactPoint),tip:world(f.weaponTip),hand:f.handContactPoint,equipment:s.registeredAnchors.mainHand}})]))}''')
 joints=json.loads((R/'authoring/characters/builds/swordsman-true8dir-v1/joint-review.json').read_text())['frames']
 for d,frames in allsamples.items():
  points={k:[e['joints'][n] for e in joints[d]] for n,k in enumerate(['shoulder','elbow','wrist','handContact'])};points.update(weaponGrip=[[f['grip']['x'],f['grip']['y']] for f in frames],weaponTip=[[f['tip']['x'],f['tip']['y']] for f in frames]);metrics={}
  for key,pts in points.items():
   jumps=[math.dist(pts[i],pts[(i+1)%16]) for i in range(16)];metrics[key]=dict(points=pts,maxJump=round(max(jumps),3),suspiciousTransitions=[dict(fromFrame=i,toFrame=(i+1)%16,pixels=round(v,3)) for i,v in enumerate(jumps) if v>(90 if key=='weaponTip' else 45)])
  diagnostics[d]=metrics
 p.evaluate('AstraeonCharacterReview.setReviewPose({action:"BasicAttack",direction:"SW",frameIndex:7,play:false})');p.click('#next');assert p.evaluate('AstraeonCharacterReview.snapshot().frameIndex')==8;p.click('#previous');assert p.evaluate('AstraeonCharacterReview.snapshot().frameIndex')==7
 assert p.evaluate('[...document.querySelectorAll("#debug-toggles input")].every(e=>!e.checked)')
 for mode in ['Body only','Weapon only','Body + Weapon','Body + Weapon + Grip Debug','Full composite']:p.select_option('#solo',label=mode)
 p.select_option('#speed','0.5');p.click('#play');t=p.evaluate('AstraeonCharacterReview.snapshot().time');p.wait_for_function('(t)=>AstraeonCharacterReview.snapshot().time>t+40',arg=t);p.click('#play');t=p.evaluate('AstraeonCharacterReview.snapshot().time');p.wait_for_timeout(80);assert p.evaluate('AstraeonCharacterReview.snapshot().time')==t;p.select_option('#speed','1');p.screenshot(path=str(O/'review-desktop.png'))
 p.set_viewport_size({'width':390,'height':844});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(O/'review-mobile.png'));b.close()
(O/'continuity-diagnostics.json').write_text(json.dumps(dict(note='Review diagnostics only. Fast contact movement and occluded/interpolated joint annotations are not anatomy certification.',directions=diagnostics),indent=2));(O/'browser-validation.json').write_text(json.dumps(dict(errors=errors,clippedFrames=clipped,swaps=proof,modes=list(modes),frameStep=True,playPause=True,speedControls=True,debugDefaultOff=True,desktop=True,mobile=True,ownerApproval='PENDING'),indent=2));print('Exported evidence. Errors:',errors,'clipped:',clipped)
assert not errors and not clipped
