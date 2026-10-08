"""Default gameplay, real WebGL sprite assembly and preview/offline cache isolation."""
import argparse
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url',default='http://127.0.0.1:8011')
parser.add_argument('--output',type=Path,default=Path('/tmp/astraeon-modular-runtime'))
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
errors=[];resources=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--enable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    context=browser.new_context(viewport={'width':1280,'height':800});page=context.new_page();page.set_default_timeout(120000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:resources.append(f'{r.status} {r.url}') if r.status>=400 else None)
    page.goto(args.url.rstrip('/')+'/index.html?qa=1',wait_until='networkidle')
    page.locator('#newname').fill('Modular Regression');page.locator('#create').click();page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    assert page.evaluate('!!window.AstraeonModularSprites')
    before=page.evaluate('AstraeonQA.snapshot()')
    page.keyboard.down('d');page.wait_for_function('(start)=>AstraeonQA.snapshot().time>start+.4',arg=before['time']);page.keyboard.up('d')
    moved=page.evaluate('AstraeonQA.snapshot()')
    assert moved['player']['distance']>before['player']['distance']
    page.keyboard.press('f');page.wait_for_function('AstraeonQA.snapshot().animation.state==="attack"')
    page.wait_for_function('AstraeonQA.snapshot().animation.state!=="attack"')
    ordinary=page.evaluate('AstraeonQA.snapshot()')
    assert 'spriteSockets' not in ordinary['sockets'],'Placeholder replaced the default character'
    assert any(a['motionSample'].get('frame',{}).get('clip','').startswith('warrior') for a in ordinary['renderer']['actors'] if a['id']=='player'),ordinary['renderer']['actors']
    page.screenshot(path=str(args.output/'default-gameplay.png'))
    # Compose a separate temporary actor through the existing WebGL Canvas path.
    # No gameplay player, combat, equipment or save state is replaced.
    assembly=page.evaluate('''async()=>{
      const visual=await AstraeonModularSprites.load('./assets/characters/swordsman-proof/sprite.json',{allowDev:true,animationIds:['Walk']});
      const p=AstraeonQA.snapshot().player.position,t=new AstraeonMotion.CharacterTransform(p.x,p.y,0);t.position.z=p.z;t.state='walk';t.speed=1;t.gait=.5;
      const sockets=AstraeonSpatialView.actor('modular-proof-test',t,(ctx,iso)=>AstraeonCharacters.humanoid(ctx,iso,t,{modular:visual}));
      const actor=AstraeonSpatialView.actors.get('modular-proof-test'),pixels=actor.ctx.getImageData(0,0,256,256).data;
      const painted=[...pixels].filter((n,i)=>i%4===3&&n>0).length;
      return {sockets:sockets.spriteSockets,painted,directFrame:actor.directFrame,usesCanvasTexture:actor.mesh.material.map===actor.tex,pose:actor.motionSample.frame,root:actor.motionSample.root};
    }''')
    assert assembly['sockets']['root']=={'x':128,'y':224} and assembly['painted']>500,assembly
    assert not assembly['directFrame'] and assembly['usesCanvasTexture']
    assert assembly['pose']['clip']=='modular/swordsman-proof'
    # Navigate to the preview under the same service worker, then reload the
    # game offline. Its entry HTML and registered original player must survive.
    page.goto(args.url.rstrip('/')+'/sprite-preview.html',wait_until='networkidle')
    page.wait_for_function('window.AstraeonSpritePreview')
    cached=page.evaluate('''async()=>{const key=(await caches.keys()).find(k=>k.startsWith('astraeon-static-v'));const cache=await caches.open(key);return (await cache.match('./index.html')).text()}''')
    assert 'id="app"' in cached and 'Modular sprite alignment proof' not in cached
    context.set_offline(True)
    page.goto(args.url.rstrip('/')+'/index.html?qa=1',wait_until='networkidle')
    page.wait_for_selector('#world');page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    assert page.evaluate('AstraeonQA.snapshot().save.name')=='Modular Regression'
    assert page.evaluate('!!window.AstraeonModularSprites')
    assert not errors,errors
    assert not resources,resources
    page.screenshot(path=str(args.output/'offline-after-preview.png'))
    (args.output/'report.json').write_text(json.dumps({'ordinaryMovement':True,'ordinaryAttack':True,'originalPlayerRetained':True,'assembly':assembly,'previewDoesNotReplaceOfflineGame':True,'errors':errors,'resourceErrors':resources},indent=2)+'\n')
    browser.close()
print('PASS ordinary gameplay, modular WebGL 2D assembly and preview/offline cache isolation')
