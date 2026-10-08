"""Real browser proof matrix, shared-clock playback, part swaps and responsiveness."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8011')
parser.add_argument('--output',type=Path,default=Path('/tmp/astraeon-modular-browser'))
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
errors=[];bad_resources=[];cases=0;report=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1100,'height':850})
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('response',lambda r:bad_resources.append(f'{r.status} {r.url}') if r.status>=400 else None)
    page.goto(args.url.rstrip('/')+'/sprite-preview.html',wait_until='networkidle')
    page.wait_for_function('window.AstraeonSpritePreview && document.getElementById("status").textContent.includes("swordsman-proof / Idle")')
    for character in ['swordsman-proof','mage-proof']:
        page.select_option('#character',character)
        page.wait_for_function('(id)=>document.getElementById("status").textContent.includes(id+" / Idle")',arg=character)
        clips=page.locator('#animation option').evaluate_all('(options)=>options.map(o=>o.value)')
        for clip in clips:
            page.select_option('#animation',clip)
            page.wait_for_function('(clip)=>document.getElementById("status").textContent.includes(" / "+clip+" /")',arg=clip)
            count=int(page.locator('#frame').get_attribute('max'))+1
            directions=page.locator('#direction option').evaluate_all('(options)=>options.map(o=>o.value)')
            assert directions==['S','SW','W','NW','N','NE','E','SE']
            for direction in directions:
                page.select_option('#direction',direction)
                for frame in range(count):
                    page.locator('#frame').fill(str(frame))
                    snap=page.evaluate('AstraeonSpritePreview.snapshot()')
                    assert snap['frameIndex']==frame and snap['direction']==direction and snap['animationId']==clip
                    assert len(snap['layers'])==6 and snap['sockets']['root']==[160,264]
                    assert all(layer['rect'][2:]==[320,320] for layer in snap['layers'])
                    cases+=1
            report.append({'character':character,'clip':clip,'directions':8,'framesPerDirection':count})
        page.select_option('#animation','Walk')
        page.wait_for_function('document.getElementById("status").textContent.includes(" / Walk /")')
        page.select_option('#direction','SW');page.locator('#frame').fill('1')
        before=page.evaluate('AstraeonSpritePreview.snapshot()');pixels_before=page.locator('#sprite').evaluate('(c)=>c.toDataURL()')
        page.select_option('#weapon','weapon-alt')
        after=page.evaluate('AstraeonSpritePreview.snapshot()');pixels_after=page.locator('#sprite').evaluate('(c)=>c.toDataURL()')
        assert before['frameIndex']==after['frameIndex'] and before['sockets']==after['sockets']
        assert [l for l in before['layers'] if l['slot']!='Weapon']==[l for l in after['layers'] if l['slot']!='Weapon']
        assert pixels_before!=pixels_after,'Visible alternate marker did not change'
        page.screenshot(path=str(args.output/(character+'-SW.png')))
        page.select_option('#weapon','weapon')
        page.select_option('#playback','0.25')
        page.wait_for_function('AstraeonSpritePreview.snapshot().frameIndex!==1')
        page.select_option('#playback','0')
        initial=page.locator('#sprite').evaluate('(c)=>c.toDataURL()')
        page.locator('[data-layer="Hair"]').uncheck()
        assert page.locator('#sprite').evaluate('(c)=>c.toDataURL()')!=initial
        page.locator('[data-layer="Hair"]').check()
    for width,height in [(390,844),(844,390)]:
        page.set_viewport_size({'width':width,'height':height})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(args.output/f'preview-{width}-{height}.png'))
    # Reject placeholder use without an explicit development flag, before image loads.
    rejection=page.evaluate('''async()=>{try{await AstraeonModularSprites.load('./assets/characters/swordsman-proof/sprite.json');return null}catch(error){return error.message}}''')
    assert 'DEV_ONLY' in rejection
    # The registered player adapter can also assemble the exact current proof pose.
    adapter=page.evaluate('''async()=>{const loaded=await AstraeonModularSprites.load('./assets/characters/swordsman-proof/sprite.json',{allowDev:true});const c=document.createElement('canvas');c.width=c.height=400;const t={position:{x:0,y:0,z:0},facingDirection:{x:1,y:0},rotation:0,state:'idle',stateTime:0,speed:0};const iso=()=>({x:200,y:300});const sockets=AstraeonCharacters.humanoid(c.getContext('2d'),iso,t,{modular:loaded});const pixels=c.getContext('2d').getImageData(0,0,400,400).data;return {root:sockets.spriteSockets.root,painted:[...pixels].filter((n,i)=>i%4===3&&n>0).length}}''')
    assert adapter['root']=={'x':200,'y':300} and adapter['painted']>500,adapter
    assert not errors,errors
    assert not bad_resources,bad_resources
    (args.output/'report.json').write_text(json.dumps({'cases':cases,'clips':report,'partSwap':True,'quarterSpeed':True,'adapter':adapter,'viewports':[[390,844],[844,390]],'errors':errors,'resourceErrors':bad_resources},indent=2)+'\n')
    browser.close()
print('PASS',cases,'real-browser modular frames, swap, playback, player adapter and responsive preview')
