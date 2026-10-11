"""Browser checks through real study controls. No production game assets loaded."""
import json,pathlib,time
from playwright.sync_api import sync_playwright

out=pathlib.Path(__file__).parent/'evidence'
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1200,'height':1180},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.wait_for_timeout(150)
    page.click('#pause')
    page.locator('#phase').fill('260')
    before=page.evaluate('window.motionStudy.snapshot()')
    page.select_option('#hat','crest')
    page.select_option('#coat','red')
    after=page.evaluate('window.motionStudy.snapshot()')
    assert before['elapsed']==after['elapsed'] and before['action']==after['action']
    assert after['appearance']['hat']=='crest' and after['appearance']['coat']=='red'
    page.screenshot(path=str(out/'walk-eight-directions.png'))
    snapshots=[]
    for speed in ['1','.25']:
        page.select_option('#speed',speed)
        page.click('#pause')
        start=page.evaluate('window.motionStudy.snapshot()');t=time.monotonic()
        page.wait_for_timeout(850)
        end=page.evaluate('window.motionStudy.snapshot()');elapsed=time.monotonic()-t
        ratio=(end['elapsed']-start['elapsed'])/elapsed
        assert abs(ratio-float(speed))<.12,(speed,ratio)
        snapshots.append({'requested_speed':float(speed),'observed_time_ratio':ratio})
        page.click('#pause')
    page.select_option('#action','attack')
    page.locator('#phase').fill('375')
    page.select_option('#shield','large')
    attack_before=page.evaluate('window.motionStudy.snapshot()')
    page.select_option('#weapon','wand')
    attack_after=page.evaluate('window.motionStudy.snapshot()')
    assert attack_before['elapsed']==attack_after['elapsed']
    page.screenshot(path=str(out/'attack-eight-directions.png'))
    page.select_option('#yaw','2')
    page.locator('#pitch').fill('70')
    page.screenshot(path=str(out/'camera-yaw-pitch.png'))
    page.select_option('#yaw','0')
    page.locator('#pitch').fill('46')
    page.select_option('#action','walk')
    page.select_option('#sampling','eight')
    page.locator('#phase').fill('124')
    page.screenshot(path=str(out/'held-pose-diagnostic.png'))
    for rate in ['30','60']:
        page.select_option('#sampling',rate)
        page.screenshot(path=str(out/f'walk-{rate}fps.png'))
    assert not errors,errors
    report={'status':'passed','browser':browser.version,'console_errors':errors,'playback':snapshots,
            'checks':['paused mid-walk swaps preserve exact elapsed time','normal and quarter playback clock advance',
                      'mid-attack weapon swap preserves elapsed time','eight directional views render',
                      'camera yaw/pitch controls render','held-pose diagnostic renders','30 and 60 FPS pose targets render'],
            'limitations':['No pixel art production or game integration','No start/stop/turn transition controller',
                           'Painter depth approximation can misorder crossing surfaces','Playback checked for clock advancement; screenshots require visual inspection']}
    (out/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    browser.close()
