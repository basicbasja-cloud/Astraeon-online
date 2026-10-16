"""One rest binding across all phases; never solve individual frames or alter shoe art."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,sys
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W';prefix='' if view=='W' else view+'-'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.goto(f'http://127.0.0.1:{s.server_port}/{P.name}/{prefix}walk-review.html');p.wait_for_function('window.READY===true')
 result=p.evaluate('''()=>{const out=[],canvas=document.createElement('canvas'),area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);for(let width of[32,40,48,56,64])for(let ankleStart of[1,6,12]){const trial={width,ankle_start:ankleStart,layers:{},pass:true};for(const name of['left_leg','right_leg']){const src=study.layers.get(name),center=src.definition.rest[src.definition.nodes[1]][1],end=src.definition.rest[src.definition.nodes[2]][1]-9,definition={...src.definition,bands:[center-width/2,center+width/2,center+width/2+ankleStart,end]},m=new SpriteArticulatedLayer(canvas,src.image,definition);let min=Infinity,max=0,worst=null;for(let k=0;k<=256;k++){let pose=study.poseAt(k/256),v=m.rest.map(q=>m.point(q[0],q[1],pose));for(let j=0;j<v.length;j+=3){let ratio=area(v[j],v[j+1],v[j+2])/area(m.rest[j],m.rest[j+1],m.rest[j+2]);if(ratio<min){min=ratio;worst={phase:k/256,source_triangle:m.rest.slice(j,j+3)}}max=Math.max(max,ratio)}}trial.layers[name]={bands:definition.bands,min_area_ratio:min,max_area_ratio:max,worst};trial.pass&&=min>study.data.quality_profile.minimum_active_triangle_area_ratio;m.dispose()}out.push(trial)}return out}''');b.close()
s.shutdown();s.server_close();(P/(prefix+'static-binding-candidates.json')).write_text(json.dumps({'candidates':result,'selection_scope':'One static source binding, all257 evaluated phases used for authoring inspection; not blind validation. Shoe/head assets and actual source motion unchanged. Numeric pass still requires image/playback/contacts.'},indent=2)+'\n');print([{k:v for k,v in r.items() if k!='layers'} for r in result]);passing=[r for r in result if r['pass']]
if passing:
 chosen=max(passing,key=lambda r:min(v['min_area_ratio'] for v in r['layers'].values()));(P/(prefix+'static-binding-selection.json')).write_text(json.dumps(chosen,indent=2)+'\n');print('SELECTED',chosen['width'],chosen['ankle_start'])
