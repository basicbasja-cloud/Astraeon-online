"""Front-view posed-key authoring, same whole-bank affine and fixed distal rows.
The interpolated artwork is conditioning material, never a passed full-body action.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
P=Path(__file__).resolve().parent;out=P/'inputs/S-morph-keys';out.mkdir(exist_ok=True)
crowns=[95,145,228,273,211,140,86,86];belts=[294,314,365,416,365,310,293,293];hems=[383,387,408,429,410,384,383,383];knees=[414,415,430,439,432,414,414,414]
keys=[];cages=[]
for i in range(8):
 im=Image.new('RGBA',(512,512));im.alpha_composite(Image.open(P/'key-textures/S'/f'{i:02}.png'),(32,0));f=out/f'{i:02}.png';im.save(f);keys.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});cages.append([0,crowns[i]-8,crowns[i]+40,crowns[i]+90,belts[i],hems[i],knees[i],450,512])
progress=[0,.03,.11,.23,.38,.55,.72,.89,1,.92,.77,.59,.41,.23,.08,0];samples=[]
for i,t in enumerate(progress):
 target=crowns[0]+(crowns[3]-crowns[0])*t;ids=[0,1,2,3] if i<=8 else [3,4,5,0]
 a,b=ids[-2:]
 for a1,b1 in zip(ids,ids[1:]):
  if min(crowns[a1],crowns[b1])<=target<=max(crowns[a1],crowns[b1]):a,b=a1,b1;break
 f=(target-crowns[a])/(crowns[b]-crowns[a]);samples.append({'a':a,'b':b,'f':max(0,min(1,f)),'authored_crown':target})
samples[0]=samples[-1]={'a':0,'b':0,'f':0,'authored_crown':crowns[0]}
d={'width':512,'height':512,'grid_px':16,'textures':[f['path'] for f in keys],'texture_sha256':[f['sha256'] for f in keys],'cage_y':cages,'samples':samples,'durations_ms':[90]*15+[550],'scope':'Authored image-contour/garment bands, no recovered anatomy. Same original neutral-calibrated whole-bank scale, +32px common horizontal padding. Distal rows fixed >=450, native source shoe drift remains independently testable. Interpolation ghosts require native redraw; not final art.','production_pass':False};(P/'S-morph-contract.json').write_text(json.dumps(d,indent=2)+'\n');shutil.copyfile(P.parents[2]/'tools/sprite-pose-morph.js',P/'inputs/sprite-pose-morph.js')
profile=json.loads((P/'W-motion-profile.json').read_text());profile.update({'crown_window':[100,40,375,405],'profile':{**profile['profile'],'min_excursion_px':120,'max_excursion_px':260},'scope':'S projection amplitude declared before candidate exports; actual source head origin213px after fixed gain, pose-art visible contour178px. No smaller-amplitude frozen-body substitute.'});(P/'S-motion-profile.json').write_text(json.dumps(profile,indent=2)+'\n')
html='''<!doctype html><meta charset="utf-8"><canvas id="c"></canvas><script src="inputs/sprite-pose-morph.js"></script><script>const D=__DATA__,c=document.getElementById('c');let m;Promise.all(D.textures.map(f=>new Promise((ok,no)=>{let im=new Image;im.onload=()=>ok(im);im.onerror=no;im.src=f}))).then(ims=>{m=new SpritePoseMorph(c,ims,D);window.READY=true});window.study={frame(i){const geometry=m.draw(D.samples[i]);return {png:c.toDataURL(),geometry}}};</script>''';(P/'S-morph-review.html').write_text(html.replace('__DATA__',json.dumps(d,separators=(',',':'))))
