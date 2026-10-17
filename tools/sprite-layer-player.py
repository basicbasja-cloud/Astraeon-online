"""Build an offline four-slot sprite player with SHA-bound source comparison.

Diagnostic visual review; masks/complete hidden anatomy and art approval stay
separate from render equivalence. No body part animation or image transforms.
"""
from pathlib import Path
import argparse,base64,hashlib,json,html,importlib.util
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(clip_path,full_path,out):
    clip_path=Path(clip_path).resolve();full_path=Path(full_path).resolve();out=Path(out)
    spec=importlib.util.spec_from_file_location('whole_body',Path(__file__).with_name('whole-body-toolchain.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    _,clip=m.clip_input(clip_path);full=json.loads(full_path.read_text());assert full['canvas']==clip['canvas']
    assert len(full['frames'])==len(clip['frames'])
    assets={};frames=[]
    def asset(path,digest):
        path=path.resolve();assert path.is_file() and sha(path)==digest,'Missing or stale source asset'
        assert list(Image.open(path).size)==clip['canvas'],'Unexpected canvas'
        key=str(path)
        if key not in assets:assets[key]={'sha256':digest,'data':'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()}
        return key
    for a,b in zip(clip['frames'],full['frames']):
        assert a['duration_ms']==b['duration_ms'],'Clock mismatch'
        assert a['duration_ms']%10==0,'GIF-compatible authored10ms clock required'
        row={'duration':a['duration_ms'],'order':a['order'],'slots':{}}
        for name,slot in a['slots'].items():row['slots'][name]=asset(clip_path.parent/slot['asset'],slot['sha256'])if slot else None
        row['full']=asset(full_path.parent/b['path'],b['sha256']);frames.append(row)
    data={'title':clip.get('title','Four-slot review'),'canvas':clip['canvas'],'frames':frames,'assets':assets}
    serialized=json.dumps(data,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Whole-body layer review</title><style>body{background:#20242a;color:#eee;font:16px system-ui;margin:20px}canvas{max-width:100%;height:auto;border:1px solid #69717c}button,select,input{margin:7px;padding:7px}#row{display:flex;gap:14px;flex-wrap:wrap}label{white-space:nowrap}small{display:block;color:#bcc5ce}</style>
<h1 id="title"></h1><div id="row"><canvas id="art"></canvas><div><button id="play">Play</button><select id="rate"><option value="1">1×</option><option value="0.25">¼×</option></select><input id="seek" type="range" min="0" value="0"><div id="layers"></div><p id="status"></p><small>Whole posed body + complete visible head. Weapon and trail are optional.</small><small>Diagnostic player; visual and motion acceptance are recorded separately.</small></div></div>
<script>const DATA=__DATA__;
const canvas=document.querySelector('#art'),ctx=canvas.getContext('2d',{willReadFrequently:true}),seek=document.querySelector('#seek');
canvas.width=DATA.canvas[0];canvas.height=DATA.canvas[1];document.querySelector('#title').textContent=DATA.title;seek.max=DATA.frames.length-1;
const enabled={body:true,head:true,weapon:true,trail:true};const images={};
for(const name of Object.keys(enabled)){const l=document.createElement('label'),c=document.createElement('input');c.type='checkbox';c.checked=true;c.id='slot-'+name;c.onchange=()=>{enabled[name]=c.checked;draw()};l.append(c,document.createTextNode(name));document.querySelector('#layers').append(l,document.createElement('br'))}
const durations=DATA.frames.map(f=>f.duration),total=durations.reduce((a,b)=>a+b,0);let index=0,playing=false,start=0,rate=1;
function at(t){t=((t%total)+total)%total;let end=0;for(let i=0;i<durations.length;i++){end+=durations[i];if(t<end)return i}return 0}
function draw(){ctx.fillStyle='#343941';ctx.fillRect(0,0,canvas.width,canvas.height);const f=DATA.frames[index];for(const name of f.order){const key=f.slots[name];if(enabled[name]&&key)ctx.drawImage(images[key],0,0)}seek.value=index;document.querySelector('#status').textContent=`Frame ${index+1}/${durations.length} · ${durations[index]}ms`}
function select(i){playing=false;index=Math.max(0,Math.min(DATA.frames.length-1,i));draw()}
function compare(){const ref=document.createElement('canvas');ref.width=canvas.width;ref.height=canvas.height;const r=ref.getContext('2d',{willReadFrequently:true});r.fillStyle='#343941';r.fillRect(0,0,ref.width,ref.height);r.drawImage(images[DATA.frames[index].full],0,0);const a=ctx.getImageData(0,0,canvas.width,canvas.height).data,b=r.getImageData(0,0,ref.width,ref.height).data;let changed=0,max=0;for(let i=0;i<a.length;i++){const d=Math.abs(a[i]-b[i]);if(d)changed++;if(d>max)max=d}return{changed_channels:changed,max_error:max}}
function tick(now){if(playing){index=at((now-start)*rate);draw()}requestAnimationFrame(tick)}
document.querySelector('#play').onclick=()=>{if(!playing){start=performance.now()-durations.slice(0,index).reduce((a,b)=>a+b,0)/rate}playing=!playing};seek.oninput=()=>select(Number(seek.value));document.querySelector('#rate').onchange=e=>{rate=Number(e.target.value);start=performance.now()-durations.slice(0,index).reduce((a,b)=>a+b,0)/rate};
window.review={select,at,compare,ctx,durations,enabled,get index(){return index},get playing(){return playing}};
Promise.all(Object.entries(DATA.assets).map(([key,a])=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{images[key]=im;resolve()};im.onerror=reject;im.src=a.data}))).then(()=>{draw();window.READY=true;requestAnimationFrame(tick)}).catch(e=>window.LOAD_ERROR=String(e));
</script>'''.replace('__DATA__',serialized)
    out.mkdir(parents=True,exist_ok=False);(out/'review.html').write_text(page)
    report={'source_clip_sha256':sha(clip_path),'source_full_frames_sha256':sha(full_path),'frames':len(frames),'assets':len(assets),'durations_ms':[f['duration']for f in frames],'html_sha256':sha(out/'review.html'),'canvas':clip['canvas'],'image_transforms':'identity only; full-canvas raster slots','external_urls':0,'production_pass':False}
    (out/'player-build.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clip',required=True,type=Path);p.add_argument('--full',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();print(json.dumps(build(a.clip,a.full,a.out)))
