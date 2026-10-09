"""Actual Canvas2D raster proof, cosmetic isolation, playback and review captures.

All animation keys here are synthetic engine fixtures. Production RO proof is
explicitly unavailable; these tests never certify Swordsman choreography/art.
"""
import argparse
import base64
import io
import json
import math
import os
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8011')
parser.add_argument('--output',type=Path,default=Path('/tmp/astraeon-assembly-browser'))
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']


def image(data):
    return Image.open(io.BytesIO(base64.b64decode(data.split(',',1)[1]))).convert('RGBA')


def sheet(items,destination,cols,heading,scale=1):
    tile=128*scale;height=tile+38
    out=Image.new('RGB',(tile*cols,height*math.ceil(len(items)/cols)+38),'#23303d');draw=ImageDraw.Draw(out)
    draw.text((7,7),heading,fill='#ffd282')
    for i,(label,im) in enumerate(items):
        x=i%cols*tile;y=i//cols*height+38
        draw.text((x+5,y+3),label,fill='white')
        im=im.resize((tile,tile),Image.Resampling.LANCZOS)
        out.paste(im,(x,y+32),im)
    out.save(destination)


errors=[];resources=[];report={'provenance':'SYNTHETIC_ENGINE_FIXTURE','roProductionProof':False,'ownerVisualApproval':False}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1360,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:resources.append(f'{r.status} {r.url}') if r.status>=400 else None)
    page.goto(args.url.rstrip('/')+'/character-engine-review.html',wait_until='networkidle')
    page.wait_for_function('window.AstraeonCharacterReview')
    page.evaluate('AstraeonCharacterReview.prepareVariants()')
    matrix=page.evaluate('''()=>{
      const R=AstraeonCharacterReview,c=R.loaded.compiled,M=AstraeonMotionTemplate;
      let frames=0,swaps=0,pixelComparisons=0;const strips=[];
      const changes=[['Hair','hair-b',['HairBack','HairFront']],['MainHand','weapon-b',['MainHand']],['OffHand',null,['OffHand']],['Headgear',null,['HeadgearTop']],['Headgear','headgear-b',['HeadgearTop']],['Garment',null,['GarmentBack','GarmentFront']]];
      for(const [action,a] of Object.entries(c.motion.template.actions))for(const direction of M.DIRECTIONS){
        const samples=[];
        for(let frameIndex=0;frameIndex<a.directions[direction].frames.length;frameIndex++){
          const pose={action,direction,frameIndex,cosmeticTimeMs:100},s=c.sample(action,direction,0,pose),data=R.renderPose(pose);
          if(JSON.stringify(s.frame.root)!==JSON.stringify(c.motion.template.registration.root))throw Error('Root drift');
          const nonchanging=R.renderPose({...pose,visibleLayers:['Body','HeadBase','CosmeticFX']});
          for(const [slot,id,layers] of changes){
            const appearance={...c.pack.defaultParts,[slot]:id},after=c.sample(action,direction,0,{...pose,appearance});
            if(after.frameIndex!==s.frameIndex||after.motionTemplateId!==s.motionTemplateId)throw Error('Clock/pose changed');
            const other=s.layers.filter(l=>!layers.includes(l.layer)),next=after.layers.filter(l=>!layers.includes(l.layer));
            if(JSON.stringify(other)!==JSON.stringify(next))throw Error('Unrelated raster references changed');
            const unaffected=s.drawOrder.filter(l=>!layers.includes(l));
            if(R.renderPose({...pose,appearance,visibleLayers:unaffected})!==R.renderPose({...pose,visibleLayers:unaffected}))throw Error('Unrelated pixels changed');
            if(R.renderPose({...pose,appearance,visibleLayers:['Body','HeadBase','CosmeticFX']})!==nonchanging)throw Error('Body pixels changed');
            if(R.renderPose({...pose,appearance})===data)throw Error('Cosmetic change not visible '+slot+'/'+direction+'/'+frameIndex);
            swaps++;pixelComparisons+=3;
          }
          samples.push({frameIndex,role:s.frame.role,phase:s.frame.referencePhase,root:s.frame.root,data});frames++;
        }
        strips.push({action,direction,samples});
      }
      return {frames,swaps,pixelComparisons,strips};
    }''')
    report.update({k:matrix[k] for k in ['frames','swaps','pixelComparisons']})
    cache={}
    for strip in matrix['strips']:
        action,direction=strip['action'],strip['direction'];tiles=[]
        for f in strip['samples']:
            im=image(f['data']);cache[action,direction,f['frameIndex']]=im
            role='KEY (fixture)' if f['role']=='referenceKey' else 'IN-BETWEEN'
            tiles.append((f"{direction} F{f['frameIndex']}\n{role}",im))
        if action in ['Walk','BasicAttack']:
            sheet(tiles,args.output/f'{action}-{direction}-strip.png',len(tiles),'DEV_ONLY synthetic '+action+' / '+direction)
    neutral=[(d,cache['Idle',d,0]) for d in DIRECTIONS]
    sheet(neutral,args.output/'neutral-eight-directions.png',4,'DEV_ONLY debug shape turnaround')
    idle=[(f'{d} F{i}',cache['Idle',d,i]) for d in DIRECTIONS for i in range(4)]
    sheet(idle,args.output/'Idle-eight-directions.png',4,'DEV_ONLY synthetic Idle / all eight directions')
    role_items=[]
    for strip in matrix['strips']:
        if strip['direction']!='S':continue
        for f in strip['samples']:
            role_items.append((f"{strip['action']} F{f['frameIndex']}\n"+('FIXTURE KEY' if f['role']=='referenceKey' else 'IN-BETWEEN'),cache[strip['action'],'S',f['frameIndex']]))
    sheet(role_items,args.output/'reference-key-vs-inbetween.png',5,'ENGINE FIXTURE CLASSIFICATION — zero RO keys')
    for name,slot,values in [('hair-A-B','Hair',['hair-a','hair-b']),('weapon-A-B','MainHand',['weapon-a','weapon-b']),('offhand-ordering','OffHand',['offhand',None]),('headgear-A-B','Headgear',['headgear-a','headgear-b']),('garment-on-off','Garment',['garment',None])]:
        tiles=[]
        for d in DIRECTIONS:
            for value in values:
                data=page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',{'action':'Walk','direction':d,'frameIndex':5,'appearance':{slot:value}})
                tiles.append((f'{d} / {value or "NONE"}',image(data)))
        sheet(tiles,args.output/(name+'.png'),4,'DEV_ONLY '+name+' / same Body frame')
    layers=page.evaluate('AstraeonCharacterReview.snapshot().drawOrder')
    tiles=[('COMPOSITE',image(page.evaluate('AstraeonCharacterReview.renderPose({action:"Walk",direction:"SW",frameIndex:5})')))]
    for layer in layers:
        data=page.evaluate('(layer)=>AstraeonCharacterReview.renderPose({action:"Walk",direction:"SW",frameIndex:5,visibleLayers:[layer]})',layer)
        tiles.append((layer,image(data)))
    sheet(tiles,args.output/'layer-decomposition.png',4,'DEV_ONLY semantic layer decomposition')
    page.select_option('#action','Walk');page.select_option('#direction','SW');page.locator('#frame').fill('5')
    before=page.evaluate('AstraeonCharacterReview.snapshot()')
    assert before['frameIndex']==5
    for control,value,slot in [('hair','hair-b','Hair'),('weapon','weapon-b','MainHand'),('offhand','','OffHand'),('headgear','headgear-b','Headgear'),('garment','','Garment')]:
        page.select_option('#'+control,value)
        page.wait_for_function('([slot,value])=>AstraeonCharacterReview.snapshot().appearance[slot]===value',arg=[slot,value or None])
        after=page.evaluate('AstraeonCharacterReview.snapshot()')
        assert (after['action'],after['direction'],after['frameIndex'],after['elapsedMs'])==(before['action'],before['direction'],5,before['elapsedMs'])
    report['uiSwapsPreserveWalkSWFrame5']=True
    page.select_option('#anchors','0');page.screenshot(path=str(args.output/'desktop-review.png'),full_page=True)
    initial=page.locator('#gameplay').evaluate('(c)=>c.toDataURL()')
    page.locator('[data-layer="Body"]').uncheck()
    assert page.locator('#gameplay').evaluate('(c)=>c.toDataURL()')!=initial
    page.locator('[data-layer="Body"]').check()
    page.select_option('#speed','0.25')
    page.wait_for_function('AstraeonCharacterReview.snapshot().frameIndex!==5')
    page.select_option('#speed','0');report['quarterSpeedPlayback']=True
    page.click('#rotate');assert page.locator('#direction').input_value()=='W'
    old=page.evaluate('AstraeonCharacterReview.snapshot()')
    page.select_option('#pack','debug-coral')
    page.wait_for_function('AstraeonCharacterReview.snapshot().packId==="debug-coral-v1"')
    new=page.evaluate('AstraeonCharacterReview.snapshot()')
    assert (new['motionTemplateId'],new['frameIndex'],new['elapsedMs'])==(old['motionTemplateId'],old['frameIndex'],old['elapsedMs'])
    page.evaluate('AstraeonCharacterReview.prepareVariants()')
    count=page.evaluate('''()=>{const c=AstraeonCharacterReview.loaded.compiled;let n=0;for(const [action,a] of Object.entries(c.motion.template.actions))for(const d of AstraeonMotionTemplate.DIRECTIONS)for(let i=0;i<a.directions[d].frames.length;i++){AstraeonCharacterReview.renderPose({action,direction:d,frameIndex:i});n++}return n}''')
    assert count==matrix['frames'];report['secondPackFrames']=count
    page.screenshot(path=str(args.output/'second-pack.png'),full_page=True)
    for width,height in [(390,844),(844,390)]:
        page.set_viewport_size({'width':width,'height':height})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.select_option('#hair','hair-a');page.wait_for_function('AstraeonCharacterReview.snapshot().appearance.Hair==="hair-a"')
        page.screenshot(path=str(args.output/f'mobile-{width}-{height}.png'),full_page=True)
    report['viewports']=[[1360,1000],[390,844],[844,390]]
    rejection=page.evaluate('''async()=>{try{await AstraeonCharacterAssembly.loadAssembly({motionUrl:'authoring/characters/motion-templates/assembly-debug/motion-template.json',appearanceUrl:'authoring/characters/appearance/debug-blue/appearance-pack.json'});return null}catch(e){return e.message}}''')
    assert 'DEV_ONLY' in rejection;report['unapprovedRuntimeRejected']=True
    # Failed preload retains complete old appearance; retry clears failed cache.
    page.evaluate('''async()=>{window.loaderTest=await AstraeonCharacterAssembly.loadAssembly({motionUrl:'authoring/characters/motion-templates/assembly-debug/motion-template.json',appearanceUrl:'authoring/characters/appearance/debug-blue/appearance-pack.json',allowDev:true})}''')
    page.route('**/hair-b-front.png*',lambda route:route.abort())
    failed=page.evaluate('''async()=>{try{await loaderTest.setAppearance({Hair:'hair-b'});return null}catch(e){return {error:e.message,hair:loaderTest.appearance.Hair,frame:loaderTest.sample('Walk','SW',430).frameIndex}}}''')
    assert failed['hair']=='hair-a' and failed['frame']==5
    page.unroute('**/hair-b-front.png*')
    page.evaluate('loaderTest.setAppearance({Hair:"hair-b"})')
    assert page.evaluate('loaderTest.appearance.Hair')=='hair-b';report['failedLoadAndRetry']=True
    # Delayed request gets superseded by newer complete appearance.
    page.evaluate('''async()=>{window.loaderRace=await AstraeonCharacterAssembly.loadAssembly({motionUrl:'authoring/characters/motion-templates/assembly-debug/motion-template.json',appearanceUrl:'authoring/characters/appearance/debug-blue/appearance-pack.json',allowDev:true})}''')
    delayed=[];page.route('**/hair-b-front.png*',lambda route:delayed.append(route))
    raced=page.evaluate('''async()=>{window.slowSwap=loaderRace.setAppearance({Hair:'hair-b'});await loaderRace.setAppearance({MainHand:'weapon-b'});return loaderRace.appearance}''')
    assert raced['Hair']=='hair-a' and raced['MainHand']=='weapon-b'
    assert delayed
    for route in delayed:route.continue_()
    assert page.evaluate('slowSwap') is False
    assert page.evaluate('loaderRace.appearance.Hair')=='hair-a';report['supersededPreloadSafe']=True
    assert not errors,errors
    assert not resources,resources
    report['errors']=errors;report['unexpectedHttpErrors']=resources;report['expectedFailure']='One intentionally aborted alternate-hair request'
    (args.output/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    browser.close()
print('PASS',report['frames'],'blue frames,',report['secondPackFrames'],'second-pack frames,',report['swaps'],'visible isolated swaps')
