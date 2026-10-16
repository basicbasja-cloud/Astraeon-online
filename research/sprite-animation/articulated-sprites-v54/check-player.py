"""Drive real controls/animation clocks, including pause-resume and world one-shot."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,sys
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W';prefix='' if view=='W' else view+'-'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start();checks={};errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1100,'height':900});p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{s.server_port}/{P.name}/{prefix}walk-review.html');p.wait_for_function('window.READY===true');D=p.evaluate('study.data');count=len(D['durations_ms'])
 for i in range(count):
  p.locator('#frame').evaluate('(e,i)=>{e.value=i;e.dispatchEvent(new Event("input"))}',i);assert p.locator('#frame').input_value()==str(i);assert abs(p.evaluate('study.clock.time')-sum(D['durations_ms'][:i]))<1e-8
 checks['all_'+str(count)+'_frame_controls_and_seek_clock']=True;p.locator('#loop').uncheck()
 for speed in ['1','0.25']:
  p.evaluate('study.select(0)');p.locator('#speed').select_option(speed);p.locator('#play').click();p.wait_for_function('study.clock.finished',timeout=10000);assert p.locator('#frame').input_value()==str(count-1);checks['actual_one_shot_'+speed]=True
 p.locator('#speed').select_option('1');p.locator('#loop').check();p.locator('#play').click();p.wait_for_function('study.clock.iteration>=1',timeout=5000);p.locator('#play').click();state=p.evaluate('study.clock.sample()');pixels=p.evaluate("document.getElementById('c').toDataURL()");p.wait_for_timeout(100);assert state==p.evaluate('study.clock.sample()');assert pixels==p.evaluate("document.getElementById('c').toDataURL()");checks['pause_freezes_exact_pixels_and_clock']=True
 p.evaluate('study.select(20)');instant=p.locator('#play').evaluate('(e)=>{const before=study.clock.sample();e.click();return{before,after:study.clock.sample()}}');assert instant['before']['time']==instant['after']['time'] and instant['after']['running'];p.wait_for_function('study.clock.time>200');p.locator('#play').click();checks['resume_retains_selected_phase']=True
 p.locator('#travel').check();assert p.locator('#loop').is_disabled() and not p.locator('#loop').is_checked();p.locator('#play').click();p.wait_for_function('study.clock.finished',timeout=5000);assert p.evaluate("document.getElementById('c').width")==768;checks['world_one_shot_no_loop_teleport']=True
 p.locator('#travel').uncheck();assert not p.locator('#loop').is_disabled();p.evaluate('study.select(40)');p.screenshot(path=str(P/('player-verified-'+view+'.png')),full_page=True);assert not errors;b.close()
s.shutdown();s.server_close();(P/(prefix+'player-qa.json')).write_text(json.dumps({'pass':True,'checks':checks,'page_errors':errors,'scope':'Actual standalone browser player; not game-engine integration or arbitrary locomotion transition physics'},indent=2)+'\n');print(checks)
