from playwright.sync_api import sync_playwright
from pathlib import Path
from PIL import Image
import json,base64,io,sys,threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(("127.0.0.1",0),QuietHandler)
threading.Thread(target=server.serve_forever,daemon=True).start()
sys.path.insert(0,'tools/character_factory_v3')
from audit_gif_source_geometry import compare
out=Path('docs/character-factory/review/patch001-png-gif-geometry-20261027')
masters=Path('authoring/characters/factory-v3/patch-0.0.1/review/mage-coherent-component-masters-20261026')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
 page=browser.new_page(viewport={'width':1400,'height':1100},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
 page.goto('http://127.0.0.1:'+str(server.server_port)+'/'+str(out/'index.html'));page.wait_for_function('window.spriteGeometryReview?.ready === true')
 page.click('#play'); records=[]
 for sex in ['male','female']:
  page.evaluate('(s)=>window.spriteGeometryReview.select(s)',sex)
  for i in range(24):
   draws=page.evaluate('(i)=>window.spriteGeometryReview.render(i)',i)
   data=page.evaluate("document.querySelector('#png').toDataURL('image/png').split(',')[1]")
   actual=Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB')
   for col,draw in enumerate(draws):
    source=Image.open(masters/sex/draw['view']/'Master'/f'{i:03d}.png').convert('RGBA').crop((96,96,416,416))
    expected=Image.new('RGB',(320,320),'#dcdcd8');expected.paste(source,(0,0),source)
    records.append({'sex':sex,**draw,**compare(expected,actual.crop((col*320,28,(col+1)*320,348)))})
  page.select_option('#sex',sex)
  page.evaluate('window.spriteGeometryReview.render(10)')
  page.screenshot(path=str(out/f'{sex}-chromium-png-player.png'),full_page=True)
 browser.close()
(out/'browser-draw-evidence.json').write_text(json.dumps({'engine':'Chromium / actual AstraeonModularSprites.draw','frames_checked':len(records),'draws':records,'page_errors':errors,'all_best_decode_offsets_zero':all(r['best_decode_translation_xy']==[0,0] for r in records),'full_gameplay_scene_exercised':False},indent=2)+'\n')
print('Checked draws',len(records),'best offsets zero',all(r['best_decode_translation_xy']==[0,0] for r in records),'max MAE',max(r['zero_translation_error_255'] for r in records),'pageerrors',errors)
