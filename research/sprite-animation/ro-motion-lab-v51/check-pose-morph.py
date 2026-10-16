"""Render every candidate; apply the frozen pre-candidate contour/contact gates."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,hashlib,importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;root=P.parents[2]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,root/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
motion=module('motion','sprite-motion-review.py');contact=module('contact','sprite-contact-review.py');profile=json.loads((P/'rejected-v49-motion-case.json').read_text());data=json.loads((P/'pose-morph-contract.json').read_text())
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1100,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/pose-morph-review.html');page.wait_for_function('window.READY===true')
 for name,variant in data['variants'].items():
  out=P/'morph-candidates'/name;out.mkdir(parents=True,exist_ok=True);frames=[];geometry=[]
  for i in range(16):
   r=page.evaluate('([name,i])=>study.frame(name,i)',[name,i]);f=out/f'{i:02}.png';f.write_bytes(base64.b64decode(r['png'].split(',')[1]));geometry.append(r['geometry']);frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
  c={**profile,'frames':frames,'durations':variant['durations']};m=motion.evaluate(c,P);s={'frames':frames,'surfaces':{n:{'window':box,'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}} for n,box in [('screen_left',[150,450,224,500]),('screen_right',[224,450,294,500])]}};r=contact.evaluate(s,P);geom_ok=all(g['min_triangle_area_ratio']>0 for g in geometry)
  report={'variant':name,'motion_profile':m,'contact':r,'geometry':geometry,'body_study_combined_pass':bool(m['motion_profile_pass'] and r['visible_surface_contact_pass'] and geom_ok),'full_action_pass':False,'pending':'Prop/hand receiver/occlusion and image review; body interpolation is not16new native drawings'};(out/'review.json').write_text(json.dumps(report,indent=2)+'\n');(out/'motion-case.json').write_text(json.dumps(c,indent=2)+'\n');(out/'contact-case.json').write_text(json.dumps(s,indent=2)+'\n');results.append({'variant':name,'body_study_combined_pass':report['body_study_combined_pass'],'motion_checks':m.get('checks'),**m.get('measurements',{})});print(results[-1],flush=True)
 assert not errors;browser.close()
server.shutdown();server.server_close();(P/'morph-candidate-results.json').write_text(json.dumps({'candidates':results,'browser_errors':errors,'thresholds_declared_before_candidate_renders':'rejected-v49-motion-case.json','all_action_release_pass':False},indent=2)+'\n')
passing=sorted([r for r in results if r['body_study_combined_pass']],key=lambda x:x['max_acceleration_px_s2'])
if passing:
 selected=passing[0]['variant'];out=P/'morph-candidates'/selected;ims=[Image.open(out/f'{i:02}.png').convert('RGBA') for i in range(16)];board=Image.new('RGB',(1536,560),(40,43,48));draw=ImageDraw.Draw(board);gif=[]
 for i,im in enumerate(ims):
  thumb=im.resize((192,256));board.paste(thumb,(i%8*192,i//8*280+20),thumb);draw.text((i%8*192+3,i//8*280+2),str(i+1),(230,230,230));bg=Image.new('RGBA',im.size,(40,43,48,255));bg.alpha_composite(im);gif.append(bg.convert('RGB'))
 board.save(P/'morph-body-selected-sixteen.png');gif[0].save(P/'morph-body-selected.gif',save_all=True,append_images=gif[1:],duration=data['variants'][selected]['durations'],loop=0);(P/'morph-body-selection.json').write_text(json.dumps({'selected':selected,'selection':'Lowest measured crown acceleration among candidates passing fixed temporal/contact/positive-area profile. Body study only, no prop/full-action pass.'},indent=2)+'\n')
else:print('NO_BODY_CANDIDATE_PASSES')
