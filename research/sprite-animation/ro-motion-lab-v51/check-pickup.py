"""Actual native-cleanup buffers; unchanged gates; world-item visibility receipt."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,base64,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;root=P.parents[2]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,root/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
motion=module('motion','sprite-motion-review.py');contact=module('contact','sprite-contact-review.py');profile=json.loads((P/'rejected-v49-motion-case.json').read_text());data=json.loads((P/'pickup-contract.json').read_text());frames=[];item=[];errors=[];checks={}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1100,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/pickup-review.html');page.wait_for_function('window.READY===true')
 for i in range(16):
  for name,prop in [('pickup-body',False),('pickup-composite',True)]:
   f=P/name/f'{i:02}.png';f.parent.mkdir(exist_ok=True);s=page.evaluate('([i,p])=>study.frame(i,p)',[i,prop]);f.write_bytes(base64.b64decode(s.split(',')[1]))
  f=P/'pickup-body'/f'{i:02}.png';frames.append({'path':str(f.relative_to(P)),'sha256':contact.sha(f)});a=np.asarray(Image.open(f));c=np.asarray(Image.open(P/'pickup-composite'/f'{i:02}.png'));different=np.any(a!=c,axis=2);yy,xx=np.where(different);item.append({'index':i,'visible_item_pixel_count':int(different.sum()),'visible_item_bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if xx.size else None,'post_collect_composite_exact_body':bool(np.array_equal(a,c)) if i>=8 else None});page.evaluate('i=>study.select(i)',i);assert page.locator('#frame').input_value()==str(i)
 checks['all16_frame_controls']=True
 for speed in ['1','0.25']:
  page.locator('#speed').select_option(speed);page.locator('#play').click();page.wait_for_function('study.clock.finished',timeout=11000);assert page.locator('#frame').input_value()=='15';checks['actual_playback_'+speed]=True
 page.locator('#loop').check();page.locator('#speed').select_option('1');page.locator('#play').click();page.wait_for_function('study.clock.iteration>=1',timeout=4000);page.locator('#play').click();r=page.evaluate('study.clock.sample()');page.wait_for_timeout(100);assert r==page.evaluate('study.clock.sample()');checks['loop_pause']=True;page.evaluate('study.select(5)');page.screenshot(path=str(P/'pickup-verified-player.png'),full_page=True);assert not errors;b.close()
server.shutdown();server.server_close();assert (P/'pickup-body/00.png').read_bytes()==(P/'pickup-body/15.png').read_bytes();checks['neutral_return_exact_complete_frame']=True
case={**profile,'frames':frames,'durations':data['durations']};r=motion.evaluate(case,P);s={'frames':frames,'surfaces':{n:{'window':box,'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}} for n,box in [('screen_left',[150,450,224,500]),('screen_right',[224,450,294,500])]}};c=contact.evaluate(s,P)
for name,obj in [('pickup-motion-case.json',case),('pickup-motion-review.json',r),('pickup-contact-case.json',s),('pickup-contact-review.json',c),('pickup-browser-qa.json',{'pass':True,'checks':checks,'page_errors':errors}),('pickup-item-visibility.json',{'frames':item,'scope':'Fixed world item before authored720ms collect event, fully removed afterward. Occluded item is not a recovered hand contact. No actual inventory mutation.'})]:(P/name).write_text(json.dumps(obj,indent=2)+'\n')
ims=[Image.open(P/'pickup-composite'/f'{i:02}.png').convert('RGBA') for i in range(16)];gif=[];board=Image.new('RGB',(1536,560),(40,43,48));draw=ImageDraw.Draw(board)
for i,im in enumerate(ims):
 thumb=im.resize((192,256));board.paste(thumb,(i%8*192,i//8*280+20),thumb);draw.text((i%8*192+3,i//8*280+2),str(i+1),(230,230,230));bg=Image.new('RGBA',im.size,(40,43,48,255));bg.alpha_composite(im);gif.append(bg.convert('RGB'))
board.save(P/'pickup-cleaned-sixteen.png');gif[0].save(P/'pickup-cleaned.gif',save_all=True,append_images=gif[1:],duration=data['durations'],loop=0);print(json.dumps({'motion':r['motion_profile_pass'],'motion_checks':r.get('checks'),'measurements':r.get('measurements'),'contact':c['visible_surface_contact_pass'],'surfaces':c['summary'],'item_visibility':item,'browser':checks}))
