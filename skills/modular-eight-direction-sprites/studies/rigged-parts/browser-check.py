"""Exercise actual exported strips, swaps and interruptions in Chromium."""
import hashlib,json,sys,time,mimetypes
from urllib.parse import urlparse,unquote
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8772/'
OFFLINE=URL=='--offline'
if OFFLINE:URL='http://sprite-proof.local/'
def digest(p):return hashlib.sha256(bytes(p.evaluate('rigProof.getPixels()'))).hexdigest()
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1200,'height':920})
 if OFFLINE:
  def local_asset(route):
   url=urlparse(route.request.url)
   relative=unquote(url.path).lstrip('/') or 'index.html'
   path=(OUT/relative).resolve()
   if url.hostname!='sprite-proof.local' or not path.is_relative_to(OUT) or not path.is_file():
    route.fulfill(status=404,body='Missing local asset');return
   mime='text/javascript' if path.suffix=='.mjs' else mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
   route.fulfill(status=200,body=path.read_bytes(),content_type=mime)
  # Entirely filesystem-backed requests; no socket/server/external connection.
  context.route('**/*',local_asset)
 page=context.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(URL);page.wait_for_function('window.rigProof && rigProof.ready()',timeout=30000)
 report={'url':URL,'offline_filesystem_routes':OFFLINE,'browser':browser.version,'checks':[],'scope':'Standalone CPU compositor only; not game integration or artistic approval.'}
 def check(name,ok,**detail):
  report['checks'].append({'check':name,'pass':bool(ok),**detail});assert ok,(name,detail)
 page.evaluate('rigProof.setTime(367)');before=digest(page)
 elapsed=page.evaluate('rigProof.state.elapsed');frame=page.evaluate('rigProof.state.frame')
 page.select_option('#hair','hair.chestnut');page.wait_for_function('rigProof.ready()')
 check('Paused hair swap preserves pose and subframe',page.evaluate('rigProof.state.elapsed')==elapsed and page.evaluate('rigProof.state.frame')==frame and digest(page)!=before,time_ms=elapsed,key=frame)
 page.select_option('#headgear','headgear.helm');page.wait_for_function('rigProof.ready()');helmet=digest(page)
 check('Helmet removes hair from equipped parts',not page.evaluate("rigProof.state.parts.some(p=>p.startsWith('hair.'))"))
 page.select_option('#hair','hair.silver');page.wait_for_function('rigProof.ready()')
 check('Covered hair swap has no visible ghost',helmet==digest(page))
 page.select_option('#headgear','');page.select_option('#weapon','weapon.falchion');page.select_option('#torso','torso.travel');page.select_option('#cape','cape.teal');page.wait_for_function('rigProof.ready()')
 check('Other equipment swaps retain shared phase',page.evaluate('rigProof.state.elapsed')==elapsed)
 check('Weapon variant retains declared right-hand socket',page.evaluate("rigProof.state.parts.includes('weapon.falchion') && rigProof.manifest.parts['weapon.falchion'].attached_bones.every(n=>n==='weapon.right')"))
 distinct=[];memory=[];snapshots=[]
 for d in page.evaluate('rigProof.manifest.directions'):
  page.select_option('#direction',d);page.wait_for_function(f"rigProof.ready() && rigProof.state.direction === '{d}'",timeout=30000)
  page.evaluate('rigProof.setTime(180)');hashes=[]
  for ms in [0,180,280,340,400,520]:page.evaluate('(ms)=>rigProof.setTime(ms)',ms);hashes.append(digest(page))
  check(d+' six body poses render distinctly',len(set(hashes))==6)
  memory.append(page.evaluate('rigProof.cacheBytes()'));distinct.append({'direction':d,'six_pose_hashes':hashes})
  page.evaluate('rigProof.setTime(340)');page.locator('#sprite').screenshot(path=str(OUT/f'browser-cut-{d}.png'));snapshots.append(str(OUT/f'browser-cut-{d}.png'))
 check('All facing caches bounded',all(n==17*2048*256*4*2 for n in memory),decoded_arrays_bytes_each=memory[0])
 page.evaluate('rigProof.setTime(367)');page.select_option('#viewPolicy','paired')
 for requested,source in {'S':'SW','SW':'SW','W':'NW','NW':'NW','N':'NE','NE':'NE','E':'SE','SE':'SE'}.items():
  page.select_option('#direction',requested);page.wait_for_function(f"rigProof.ready() && rigProof.state.direction === '{source}'",timeout=30000)
  check('Paired attack view '+requested+' resolves '+source,page.evaluate('rigProof.state.elapsed')==367)
 page.select_option('#viewPolicy','eight');page.wait_for_function('rigProof.ready()')
 page.select_option('#direction','SE');page.wait_for_function("rigProof.ready() && rigProof.state.direction==='SE'")
 page.evaluate('rigProof.setTime(340)');page.check('#fx');with_fx=digest(page);page.uncheck('#fx');without_fx=digest(page)
 check('Ribbon contributes during strike',with_fx!=without_fx)
 page.check('#fx');page.click('#stop');cleared=digest(page);page.uncheck('#fx')
 check('Interruption clears trail and returns ready',cleared==digest(page) and page.evaluate('rigProof.state.interrupted && rigProof.state.elapsed===0 && !rigProof.state.playing'))
 page.check('#fx');page.select_option('#speed','1');page.click('#once');page.wait_for_function('!rigProof.state.playing && rigProof.state.interrupted',timeout=3000)
 check('Normal one-shot completes to ready',page.evaluate('rigProof.state.frame===0'))
 page.select_option('#speed','0.25');page.click('#once');page.wait_for_function('!rigProof.state.playing && rigProof.state.interrupted',timeout=6500)
 check('Quarter-speed one-shot completes to ready',page.evaluate('rigProof.state.frame===0'))
 page.select_option('#direction','S');page.select_option('#direction','N');page.select_option('#direction','E');page.wait_for_function("rigProof.ready() && rigProof.state.direction==='E'",timeout=30000)
 check('Rapid direction requests commit the newest complete view',page.evaluate("rigProof.state.loadedFacing==='E' && rigProof.cacheBytes()===17*2048*256*4*2"))
 page.select_option('#direction','SE');page.wait_for_function("rigProof.ready() && rigProof.state.direction==='SE'")
 page.evaluate('rigProof.setTime(180)');page.check('#diagnostic');page.screenshot(path=str(OUT/'browser-preview.png'))
 report['facing_checks']=distinct;report['page_errors']=errors;check('No page errors during happy-path checks',not errors)
 # Deliberate missing required asset: explicit failure, no fallback/mirroring.
 broken=context.new_page();broken.route('**/strips/hair.silver/NE.png',lambda route:route.fulfill(status=404,body='deliberate missing fixture'))
 broken.goto(URL);broken.wait_for_function('window.rigProof && rigProof.ready()',timeout=30000)
 broken.select_option('#direction','NE');broken.wait_for_function('rigProof.state.error!==null',timeout=30000)
 error=broken.evaluate('rigProof.state.error');check('Missing diagonal part fails visibly',error.startswith('Missing required part:'),error=error)
 # Read-only records use the actual browser pixel results above.
 (OUT/'browser-qa.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'checks':len(report['checks']),'all_pass':all(c['pass'] for c in report['checks']),'page_errors':errors,'decoded_part_arrays_bytes':memory[0]},indent=2))
 browser.close()
