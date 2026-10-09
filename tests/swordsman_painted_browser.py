"""Capture the painted proof in the real world; keep all save writes in memory."""
import argparse,json,os
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8012')
parser.add_argument('--output',type=Path,default=Path('docs/review/character-ro1-animated-v1/gameplay'))
parser.add_argument('--contact-only',action='store_true',help='Capture exact presentation contact keys without executing Combat')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
directions=['S','SW','W','NW','N','NE','E','SE'];errors=[];bad_http=[];samples=[];tiles=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--enable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1360,'height':1000});page.set_default_timeout(60000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:bad_http.append(str(r.status)+' '+r.url) if r.status>=400 else None)
    page.goto(args.url+'/character-gameplay-review.html',wait_until='networkidle')
    page.wait_for_function('window.AstraeonGameplayReview?.snapshot().drawCount>3')
    storage_before=page.evaluate('JSON.stringify({...localStorage})')
    for action in (['BasicAttack'] if args.contact_only else ['Idle','Walk','BasicAttack']):
        for direction in directions:
            page.evaluate('([a,d])=>AstraeonGameplayReview.setPose(a,d)',[action,direction])
            if args.contact_only:page.evaluate('(d)=>AstraeonGameplayReview.inspectFrame("BasicAttack",d,7)',direction)
            page.wait_for_function('([a,d])=>{const s=AstraeonGameplayReview.snapshot().lastSample;return s.action===a&&s.direction===d&&s.frameIndex>=4}',arg=[action,direction])
            snap=page.evaluate('AstraeonGameplayReview.snapshot()');samples.append(snap)
            assert snap['memoryOnly'] and snap['combatAuthority'].startswith('existing game')
            if args.contact_only:assert snap['lastSample']['frameIndex']==7
            filename=args.output/f'{action}{"-contact" if args.contact_only else ""}-{direction}.png';page.screenshot(path=str(filename))
            frame=page.frame_locator('#game');bounds=frame.locator('#world').bounding_box()
            foot=snap['lastSample']['worldFoot'];x=bounds['x']+foot['x'];y=bounds['y']+foot['y']
            tile=Image.open(filename).crop((round(x-96),round(y-144),round(x+96),round(y+48)))
            tiles.append((action+'/'+direction,tile))
    if args.contact_only:
        assert not errors and not bad_http,(errors,bad_http)
        board=Image.new('RGB',(8*192,220),'#243644');draw=ImageDraw.Draw(board)
        for i,(label,tile) in enumerate(tiles):draw.text((i*192+8,5),label+' / contact key',fill='#edf3ff');board.paste(tile,(i*192,28))
        board.save(args.output/'BasicAttack-contact-eight-directions.png')
        (args.output/'contact-review.json').write_text(json.dumps(dict(exactContactFrameIndex=7,actualWorldStates=8,samples=samples,combatTriggered=False,errors=errors,unexpectedHTTP=bad_http),indent=2)+'\n')
        browser.close();print('PASS8 exact-contact world screenshots; visual frame inspection never executes Combat');raise SystemExit(0)
    # Swap at a running Walk frame: no action/time reset, no mechanics mutation.
    page.evaluate('AstraeonGameplayReview.setPose("Walk","SW")')
    page.wait_for_function('AstraeonGameplayReview.snapshot().lastSample.direction==="SW"')
    swap_before=page.evaluate('AstraeonGameplayReview.snapshot()')
    page.evaluate('AstraeonGameplayReview.loaded.setAppearance({Hair:"hair-b",MainHand:"weapon-b",OffHand:"offhand",Headgear:"headgear",Garment:null})')
    swap_after=page.evaluate('AstraeonGameplayReview.snapshot()')
    assert swap_after['lastSample']['action']=='Walk' and swap_after['lastSample']['direction']=='SW'
    assert swap_before['lastTransform']['position']==swap_after['lastTransform']['position']
    assert swap_before['lastTransform']['distance']==swap_after['lastTransform']['distance']
    page.screenshot(path=str(args.output/'appearance-swaps-in-world.png'))
    # Focus the actual canvas before keyboard input. Ordinary transform remains
    # the game's movement authority, while the review pose is independent.
    game=page.frames[1];game.evaluate('document.querySelector("#world").tabIndex=0;document.querySelector("#world").focus()')
    before=page.evaluate('AstraeonGameplayReview.snapshot()');page.keyboard.down('w')
    page.wait_for_function('(distance)=>AstraeonGameplayReview.snapshot().lastTransform.distance>distance+1',arg=before['lastTransform']['distance'])
    page.keyboard.up('w');after=page.evaluate('AstraeonGameplayReview.snapshot()')
    assert after['lastTransform']['distance']>before['lastTransform']['distance']
    assert storage_before==page.evaluate('JSON.stringify({...localStorage})')
    page.screenshot(path=str(args.output/'ordinary-movement-with-painted-proof.png'))
    page.close()
    mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile.set_default_timeout(90000)
    mobile.on('pageerror',lambda e:errors.append(str(e)))
    mobile.goto(args.url+'/character-gameplay-review.html',wait_until='networkidle')
    mobile.wait_for_function('window.AstraeonGameplayReview?.snapshot().drawCount>3')
    mobile.screenshot(path=str(args.output/'mobile-in-world.png'))
    assert not errors and not bad_http,(errors,bad_http)
    browser.close()
board=Image.new('RGB',(8*192,3*220),'#243644');draw=ImageDraw.Draw(board)
for i,(label,tile) in enumerate(tiles):
    x=i%8*192;y=i//8*220;draw.text((x+8,y+5),label,fill='#edf3ff');board.paste(tile,(x,y+28))
board.save(args.output/'all-actions-eight-directions-gameplay.png')
report=dict(realWorldRasterCapture=True,desktopStates=24,mobileCapture=True,allDirections=directions,actions=['Idle','Walk','BasicAttack'],samples=samples,appearanceSwapMechanicsUnchanged=True,movementDistanceBefore=before['lastTransform']['distance'],movementDistanceAfter=after['lastTransform']['distance'],ownerStorageUnchanged=True,memoryOnly=True,gameplayFixture='existing Mage; painted Swordsman presentation only',combatAuthorityUnchanged=True,errors=errors,unexpectedHTTP=bad_http,ownerVisualApproval='PENDING')
(args.output/'browser-review.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS24 actual world captures, mobile, cosmetic swap isolation, normal movement and private save storage')
