"""Explicit candidate selection in the real player renderer; no visual approval."""
import argparse
import base64
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def capture_action(page, clip, key, state, column, output):
    page.evaluate('async clip=>{await AstraeonSwordsmanDevelopment.prepare(clip)}', clip)
    # Install the observer before input so a slow software renderer cannot
    # finish the short action before Playwright starts waiting for its frame.
    page.evaluate("""({clip,state,column})=>{window.swordsmanActionCapture=new Promise((resolve,reject)=>{
      const deadline=performance.now()+30000;
      function capture(){
        const s=AstraeonQA.snapshot(),a=s.renderer.actors.find(a=>a.id==='player');
        if(AstraeonSwordsmanDevelopment.snapshot().currentClip!==clip ||
           s.animation.state!==state || a?.motionSample.frame.column<column){
          if(performance.now()>deadline){reject(Error('No '+clip+' frame captured'));return}
          requestAnimationFrame(capture);return;
        }
        const v=AstraeonSpatialView,w=document.getElementById('world');
        v.renderer.render(v.scene,v.camera);
        const c=document.createElement('canvas');c.width=w.width;c.height=w.height;
        const ctx=c.getContext('2d');ctx.drawImage(v.canvas,0,0,c.width,c.height);ctx.drawImage(w,0,0);
        resolve({frame:a.motionSample.frame,time:s.time,image:c.toDataURL('image/png')});
      }requestAnimationFrame(capture);
    })}""", {'clip':clip,'state':state,'column':column})
    page.keyboard.press(key)
    capture = page.evaluate('()=>window.swordsmanActionCapture')
    output.write_bytes(base64.b64decode(capture.pop('image').split(',')[1]))
    page.wait_for_function('AstraeonSwordsmanDevelopment.snapshot().currentClip==="Idle"')
    return capture


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--body', default='male')
parser.add_argument('--output', type=Path, default=Path('/tmp/astraeon-swordsman-gameplay'))
args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
errors = []; samples = {}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
        args=['--no-sandbox', '--enable-gpu', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    context = browser.new_context(viewport={'width':1280, 'height':800})
    page = context.new_page(); page.set_default_timeout(120000)
    page.on('pageerror', lambda e: errors.append(str(e)))
    url = args.url.rstrip('/')+'/index.html?qa=1&swordsman='+args.body
    page.goto(url, wait_until='networkidle')
    page.locator('#newname').fill('Swordsman Development'); page.locator('#create').click()
    page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().sockets.spriteSockets')
    # Use the existing safe plaza spawn as a browser-save fixture. The default
    # gate spawn hides feet behind a parapet and cannot prove visual grounding.
    fixture = page.evaluate('''()=>{const save=AstraeonQA.snapshot().save,w=AstraeonContent.nativeWorld;
      return {...save,x:w.safeSpawn[0],y:w.safeSpawn[1],worldLayout:w.layoutId}}''')
    page.goto(args.url.rstrip('/')+'/icon.svg', wait_until='load')
    page.evaluate('save=>localStorage.setItem("astraeon-iso-v1",JSON.stringify(save))', fixture)
    page.goto(url, wait_until='networkidle'); page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().sockets.spriteSockets')
    idle = page.evaluate('AstraeonSwordsmanDevelopment.snapshot()')
    assert idle['classId']=='Swordsman' and idle['bodyVariant']==args.body
    assert idle['currentClip']=='Idle'
    page.screenshot(path=str(args.output/'Idle.png'))
    directions = [('S',['s']), ('SW',['s','a']), ('W',['a']), ('NW',['w','a']),
                  ('N',['w']), ('NE',['w','d']), ('E',['d']), ('SE',['s','d'])]
    for row, (direction, keys) in enumerate(directions):
        before = page.evaluate('AstraeonQA.snapshot().player.distance')
        page.keyboard.down('Alt')
        for key in keys: page.keyboard.down(key)
        page.wait_for_function('AstraeonSwordsmanDevelopment.snapshot().currentClip==="Walk"')
        page.wait_for_function('row=>{const a=AstraeonQA.snapshot().renderer.actors.find(a=>a.id==="player");return a?.motionSample.frame.row===row && a.motionSample.frame.clip.includes("swordsman-")}', arg=row)
        now = page.evaluate('AstraeonQA.snapshot().time')
        page.wait_for_function('start=>AstraeonQA.snapshot().time>start+.45', arg=now)
        frame = page.evaluate('AstraeonQA.snapshot()')
        assert frame['player']['distance']>before, direction
        assert frame['sockets']['spriteSockets']['root']=={'x':128,'y':224}
        samples[direction] = {'distance':frame['player']['distance'], 'state':frame['animation']['state'],
                              'development':page.evaluate('AstraeonSwordsmanDevelopment.snapshot()')}
        page.screenshot(path=str(args.output/(direction+'-Walk.png')))
        for key in keys: page.keyboard.up(key)
        page.keyboard.up('Alt')
        page.wait_for_function('AstraeonSwordsmanDevelopment.snapshot().currentClip==="Idle"')
    page.keyboard.down('d')
    page.wait_for_function('AstraeonSwordsmanDevelopment.snapshot().currentClip==="Run"')
    page.screenshot(path=str(args.output/'Run.png')); page.keyboard.up('d')
    page.wait_for_function('AstraeonSwordsmanDevelopment.snapshot().currentClip==="Idle"')
    attack_capture = capture_action(page, 'BasicAttack', 'f', 'attack', 6, args.output/'BasicAttack.png')
    skill_capture = capture_action(page, 'SkillAction', '4', 'cast', 6, args.output/'SkillAction.png')
    appearance = page.evaluate('AstraeonSwordsmanDevelopment.snapshot().appearance')
    # Leave the game first: its pagehide handler intentionally flushes the
    # live save. Writing a fixture immediately before reload would be replaced.
    page.goto(args.url.rstrip('/')+'/icon.svg', wait_until='load')
    page.evaluate('''()=>{const save=JSON.parse(localStorage.getItem('astraeon-iso-v1'));
      save.equipment.weapon='Legendary Fire Sword';save.equipment.armor='Ancient Plate';
      localStorage.setItem('astraeon-iso-v1',JSON.stringify(save))}''')
    page.goto(url, wait_until='networkidle'); page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().sockets.spriteSockets')
    assert page.evaluate('AstraeonSwordsmanDevelopment.snapshot().appearance')==appearance
    assert page.evaluate('AstraeonQA.snapshot().save.equipment.weapon')=='Legendary Fire Sword'
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(args.output/'mobile.png'))
    assert not errors, errors
    report = {'bodyVariant':args.body,'classId':'Swordsman','explicitDevelopmentFlag':True,
              'actualPlayerRenderer':True,'idle':idle,'walkDirections':samples,'run':True,'basicAttack':attack_capture,'skillAction':skill_capture,
              'gameplayEquipmentIndependent':True,'mobileViewport':[390,844],
              'ownerApproval':'NOT_APPROVED','errors':errors}
    (args.output/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    browser.close()
print('PASS explicit Swordsman player: Idle, eight Walk directions, Run, BasicAttack, SkillAction, equipment independence and mobile capture')
