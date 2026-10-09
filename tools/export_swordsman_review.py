#!/usr/bin/env python3
"""Export the actual browser raster composer, animated previews and QA captures."""
import argparse,base64,io,json,math,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/review/character-ro1-animated-v1'
DIRS=['S','SW','W','NW','N','NE','E','SE']
def decode(data):return Image.open(io.BytesIO(base64.b64decode(data.split(',',1)[1]))).convert('RGBA')
def board(items,path,columns=4,size=256):
    im=Image.new('RGB',(columns*size,math.ceil(len(items)/columns)*(size+30)),'#243644');dr=ImageDraw.Draw(im)
    for i,(label,tile) in enumerate(items):
        x=i%columns*size;y=i//columns*(size+30);dr.text((x+8,y+8),label,fill='#edf3ff');tile=tile.resize((size,size),Image.Resampling.LANCZOS);im.paste(tile,(x,y+30),tile)
    im.save(path)
def labeled(tile,label,details='',size=512):
    out=Image.new('RGB',(size,size+56),'#243644');tile=tile.resize((size,size),Image.Resampling.LANCZOS);out.paste(tile,(0,40),tile);dr=ImageDraw.Draw(out)
    dr.text((18,10),label,fill='#f4e2b9');dr.text((18,size+40),details,fill='#b8d0df');return out
def animate(images,durations,path):
    # GIF centiseconds cannot encode the exact37/38ms walk subdivisions.
    # APNG below preserves milliseconds; GIF preview rounds cumulative time.
    cumulative=0;previous=0;gifdelays=[]
    for ms in durations:
        cumulative+=ms;rounded=round(cumulative/10)*10;gifdelays.append(max(10,rounded-previous));previous=rounded
    montage=Image.new('RGB',(1024,64*math.ceil(len(images)/16)),'#243644')
    for i,im in enumerate(images):montage.paste(im.resize((64,64)),(i%16*64,i//16*64))
    palette=montage.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    frames=[im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE) for im in images]
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=gifdelays,loop=0,optimize=True,disposal=2)

def run(url):
    for p in ['previews','strips','contact-sheets','screenshots','frames']:(OUT/p).mkdir(parents=True,exist_ok=True)
    template=json.loads((ROOT/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text());cache={};errors=[];http=[];playback={}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:http.append(str(r.status)+' '+r.url) if r.status>=400 else None)
        page.goto(url+'/character-review.html',wait_until='networkidle');page.wait_for_function('window.AstraeonCharacterReview');page.evaluate('AstraeonCharacterReview.prepareVariants()')
        assert page.evaluate('AstraeonCharacterReview.snapshot().playing && AstraeonCharacterReview.snapshot().action==="Walk"')
        page.screenshot(path=str(OUT/'screenshots/desktop-autoplay-walk.png'))
        for action,a in template['actions'].items():
            page.evaluate('(action)=>AstraeonCharacterReview.setReviewPose({action,direction:"S",play:true})',action)
            before=page.evaluate('document.querySelector("#hero").toDataURL()');start=page.evaluate('AstraeonCharacterReview.snapshot().time')
            page.wait_for_function('(start)=>AstraeonCharacterReview.snapshot().time>start+450',arg=start)
            after=page.evaluate('document.querySelector("#hero").toDataURL()');assert before!=after,action+' does not visibly animate'
            playback[action]=True
            for d in DIRS:
                seq=a['directions'][d];items=[];movie=[];delays=[]
                for i,f in enumerate(seq['frames']):
                    opts=dict(action=action,direction=d,frameIndex=i,scale=4)
                    im=decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',opts));cache[action,d,i]=im
                    assert im.getbbox() and im.getbbox()[0]>0 and im.getbbox()[1]>0 and im.getbbox()[2]<512 and im.getbbox()[3]<512,(action,d,i,'crop')
                    framepath=OUT/'frames'/action/d;framepath.mkdir(parents=True,exist_ok=True);im.save(framepath/f'{i:02}.png')
                    label=f'{i:02} '+('RO key: '+f['referencePhase'] if f['role']=='referenceKey' else 'ASTRAEON in-between')
                    items.append((label,im));movie.append(labeled(im,action+' / '+d,f['role']));delays.append(f['durationMs'])
                board(items,OUT/'strips'/f'{action}-{d}.png',len(items),256)
                animate(movie,delays,OUT/'previews'/f'{action}-{d}.gif')
                images=[cache[action,d,i] for i in range(len(seq['frames']))]
                images[0].save(OUT/'previews'/f'{action}-{d}.apng',format='PNG',save_all=True,append_images=images[1:],duration=delays,loop=0,disposal=0,blend=0)
            # Eight-direction animated contact board sampled at exact timeline times.
            duration=a['directions']['S']['totalDurationMs'];times=sorted({0,*[sum(f['durationMs'] for f in a['directions']['S']['frames'][:i]) for i in range(len(a['directions']['S']['frames']))]})
            animation=[];durations=[]
            for k,t in enumerate(times):
                tiles=[]
                for d in DIRS:
                    cursor=0;index=0
                    for i,f in enumerate(a['directions'][d]['frames']):
                        if t<cursor+f['durationMs']:index=i;break
                        cursor+=f['durationMs']
                    tiles.append((d,cache[action,d,index]))
                tmp=OUT/'contact-sheets'/f'{action}-eight-directions.png';board(tiles,tmp,4,256);animation.append(Image.open(tmp).copy());durations.append((times[k+1] if k+1<len(times) else duration)-t)
            animate(animation,durations,OUT/'previews'/f'{action}-eight-directions.gif')
            board([(d,cache[action,d,0]) for d in DIRS],OUT/'contact-sheets'/f'{action}-eight-directions.png',4,256)
            page.evaluate('(a)=>AstraeonCharacterReview.setReviewPose({action:a,direction:"SE",play:false,frameIndex:7})',action)
            page.screenshot(path=str(OUT/'screenshots'/f'desktop-{action}-SE.png'))
        board([(d,cache['Idle',d,0]) for d in DIRS],OUT/'contact-sheets/neutral-turnaround.png',4,256)
        board([(a+'/'+d,cache[a,d,7 if a!='Idle' else 4]) for a in template['actions'] for d in DIRS],OUT/'contact-sheets/gameplay-1x.png',8,128)
        for action,a in template['actions'].items():
            board([(str(i)+' '+f['role'],cache[action,'S',i]) for i,f in enumerate(a['directions']['S']['frames'])],OUT/'contact-sheets'/f'{action}-keys-vs-inbetweens.png',4,256)
        for name,slot,values in [('hair','Hair',['hair-a','hair-b']),('weapons','MainHand',['weapon-a','weapon-b']),('offhand-ordering','OffHand',[None,'offhand']),('headgear','Headgear',[None,'headgear']),('garment','Garment',[None,'garment'])]:
            items=[]
            for d in DIRS:
                for value in values:
                    appearance={**page.evaluate('AstraeonCharacterReview.loaded.appearance'),slot:value}
                    im=decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='Walk',direction=d,frameIndex=5,appearance=appearance,scale=4)));items.append((d+' / '+str(value),im))
            board(items,OUT/'contact-sheets'/f'{name}-comparison.png',4,256)
        layeritems=[]
        for layer in ['Shadow','GarmentBack','Body','HairFront','MainHand','OffHand','HeadgearTop']:
            appearance={**page.evaluate('AstraeonCharacterReview.loaded.appearance'),'OffHand':'offhand','Headgear':'headgear'}
            im=decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='Walk',direction='SE',frameIndex=5,visibleLayers=[layer],appearance=appearance,scale=4)));layeritems.append((layer,im))
        layeritems.append(('Composite',decode(page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)',dict(action='Walk',direction='SE',frameIndex=5,appearance=appearance,scale=4)))))
        board(layeritems,OUT/'contact-sheets/layer-decomposition.png',4,256)
        # Cosmetic isolation across every production frame: compare unrelated
        # layer references and actual raster pixels, never body re-painting.
        isolation=page.evaluate('''()=>{const R=AstraeonCharacterReview,c=R.loaded.compiled;let swaps=0;for(const [action,a]of Object.entries(c.motion.template.actions))for(const direction of AstraeonMotionTemplate.DIRECTIONS)for(let frameIndex=0;frameIndex<a.directions[direction].frames.length;frameIndex++){const o={action,direction,frameIndex},s=c.sample(action,direction,0,{frameIndex});for(const [slot,id]of [['Hair','hair-b'],['MainHand','weapon-b'],['OffHand','offhand'],['Headgear','headgear'],['Garment',null]]){const appearance={...c.pack.defaultParts,[slot]:id},after=c.sample(action,direction,0,{frameIndex,appearance});const keep=s.drawOrder.filter(l=>!c.pack.slots[slot].layers.includes(l));if(JSON.stringify(s.layers.filter(l=>l.slot!==slot))!==JSON.stringify(after.layers.filter(l=>l.slot!==slot)))throw Error('unrelated references changed');if(R.renderPose({...o,visibleLayers:keep})!==R.renderPose({...o,appearance,visibleLayers:keep}))throw Error('unrelated pixels changed');swaps++}}return {swaps,unchangedRasterPixels:true}}''')
        mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=1,has_touch=True);mobile.goto(url+'/character-review.html',wait_until='networkidle');mobile.wait_for_function('window.AstraeonCharacterReview');mobile.screenshot(path=str(OUT/'screenshots/mobile-autoplay-walk.png'));assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth');mobile.close();browser.close()
    owner=[];delays=[]
    sequence=[('Idle','S')]+[('Walk',d) for d in DIRS]+[('BasicAttack',d) for d in DIRS]
    for action,d in sequence:
        seq=template['actions'][action]['directions'][d]
        for repeat in range(1 if action=='Idle' else 2):
            for i,f in enumerate(seq['frames']):owner.append(labeled(cache[action,d,i],'ASTRAEON SWORDSMAN / '+action+' / '+d,'Painted modular proof · owner review pending'));delays.append(f['durationMs'])
    animate(owner,delays,OUT/'swordsman-owner-preview.gif')
    assert not errors and not http,(errors,http)
    (OUT/'browser-review.json').write_text(json.dumps(dict(autoplayDefault='Walk/S',visiblyAnimated=playback,isolation=isolation,desktopCapture=True,mobileCapture=True,canvasCropChecks='PASS',errors=errors,unexpectedHTTP=http,ownerVisualApproval='PENDING'),indent=2)+'\n')
    print('Exported animated owner GIF, all24 direction GIF/APNGs,3animated boards, contact sheets and browser captures')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8012');run(ap.parse_args().url.rstrip('/'))
