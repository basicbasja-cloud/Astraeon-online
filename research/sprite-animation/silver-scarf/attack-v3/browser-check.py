"""Actual Chromium playback and effect-interruption review, outside the game."""
import hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT=Path(__file__).parent
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1050,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8770/attack-v3/preview.html')
    page.wait_for_function('window.study && !document.querySelector("#attack").disabled')
    def pixels(): return page.evaluate('document.querySelector("canvas").toDataURL()')
    ready=pixels()
    page.click('#attack')
    page.wait_for_function('window.study.state.index >= 3 && window.study.state.index <= 5')
    active=page.evaluate('window.study.state')
    active_pixels=pixels()
    page.click('#stop')
    assert pixels()==ready,'Interrupt did not clear trail and return to ready'
    page.click('#attack')
    page.wait_for_function('!window.study.state.playing',timeout=3000)
    assert pixels()==ready,'One-shot completion changed ready image'
    page.evaluate('window.study.seek(4)')
    trail_on=pixels()
    page.locator('canvas').screenshot(path=str(OUT/'browser-cut-trail.png'))
    page.uncheck('#trail')
    trail_off=pixels()
    assert trail_on!=trail_off,'Trail toggle did not change strike'
    page.locator('canvas').screenshot(path=str(OUT/'browser-cut-body.png'))
    page.check('#trail');page.select_option('#speed','0.25');page.check('#loop');page.click('#attack')
    quarter_states=[]
    for _ in range(9):
        page.wait_for_timeout(400)
        quarter_states.append(page.evaluate('window.study.state'))
    assert len({s['index'] for s in quarter_states})>=6,'Quarter playback did not advance through poses'
    assert quarter_states[-1]['playing'],'Loop stopped unexpectedly'
    page.click('#stop');assert pixels()==ready
    page.screenshot(path=str(OUT/'browser-preview.png'),full_page=True)
    gif_sizes=page.locator('.views img').evaluate_all('(imgs)=>imgs.map(i=>({complete:i.complete,width:i.naturalWidth,height:i.naturalHeight}))')
    assert all(i['complete'] and i['width']==256 and i['height']==256 for i in gif_sizes)
    report={'browser':browser.version,'viewport':[1050,1000],'page_errors':errors,
            'normal_attack_reached_strike':active,'one_shot_returns_exact_ready':True,
            'stop_clears_trail_returns_exact_ready':True,'trail_can_be_hidden_on_same_pose':True,
            'quarter_speed_loop_observed_states':quarter_states,'GIF_images_loaded':gif_sizes,
            'ready_pixel_sha256':hashlib.sha256(ready.encode()).hexdigest(),
            'scope':'Browser study only; not a target-game test or approval of artistic quality'}
    assert not errors
    (OUT/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    browser.close()
