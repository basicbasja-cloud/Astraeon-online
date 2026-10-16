"""Continuous garment skin separated from cape in source UV space."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib,copy,sys,shutil
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W';assert view in ['W','E']
d=json.loads((P/f'{view}-articulated-contract.json').read_text());old=json.dumps(d,separators=(',',':'));body=d['definitions']['body'];im=Image.open(P/body['texture']);out=P/'inputs/split-drape'/view;out.mkdir(parents=True,exist_ok=True)
if view=='W':
    rest=json.loads((P.parent/'articulated-sprites-v54/walk-rig-contract.json').read_text())
    for n,a in d['definitions'].items():
        if a.get('role')=='leg':
            end=rest['definitions'][n]['bands'][3];a['bands'][2:]=[end-8,end]
            a['partition_note']='Original flat-boot UV boundary; prevents toe art entering rotating shin.'
poly=([[210,278],[279,278],[284,300],[292,328],[299,357],[301,382],[197,383],[201,326]] if view=='W' else [[251,288],[308,283],[323,390],[226,390],[234,339],[244,310]])
mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(poly,fill=255)
waist=im.copy();waist.putalpha(ImageChops.multiply(im.getchannel('A'),mask));waist.save(out/'waist.png')
remove=mask.copy();ImageDraw.Draw(remove).rectangle((0,0,512,306),fill=0)
upper=im.copy();upper.putalpha(ImageChops.multiply(im.getchannel('A'),ImageChops.invert(remove)));upper.save(out/'upper.png')
body['texture']=str((out/'upper.png').relative_to(P));body['texture_sha256']=hashlib.sha256((out/'upper.png').read_bytes()).hexdigest()
w=copy.deepcopy(body);w['texture']=str((out/'waist.png').relative_to(P));w['texture_sha256']=hashlib.sha256((out/'waist.png').read_bytes()).hexdigest();w['hanging_cloth']={'x':[0,1,511,512],'y':([285,500] if view=='W' else [286,440])};w['source_partition_polygon']=poly;w['source_overlap_rows']=[278,306];d['definitions']['waist']=w;d['order'].insert(d['order'].index('body'),'waist');new=json.dumps(d,separators=(',',':'));(P/f'{view}-split-drape5-articulated-contract.json').write_text(new+'\n')
html=(P/f'{view}-articulated-review.html').read_text();assert old in html
html=html.replace(old,new).replace("n==='body'?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer", "(n==='body'||n==='waist')?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer")
(P/f'{view}-split-drape5-articulated-review.html').write_text(html)
shutil.copyfile(P.parents[2]/'tools/sprite-segmented-player.js',P/'inputs/sprite-segmented-player.js')
