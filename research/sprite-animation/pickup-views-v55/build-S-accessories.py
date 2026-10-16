"""Separate scarf pitch assets and gravity-hanging cape from projected chest.
No per-frame image fitting; same shared part-bank scale and static neck rest origins.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib,copy,shutil
P=Path(__file__).resolve().parent;d=json.loads((P/'S-front2-articulated-contract.json').read_text());old=json.dumps(d,separators=(',',':'));defs=d['definitions'];original=Image.open(P/'inputs/pickup-parts/S/body.png');out=P/'inputs/S-accessories4';out.mkdir(exist_ok=True)
cape_poly=[[309,200],[290,244],[300,280],[306,320],[322,355],[320,512],[512,512],[512,200]]
def mask(poly):
 m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);return m
cape_mask=mask(cape_poly);scarf_mask=mask([[199,200],[309,200],[309,244],[199,244]])
def cut(im,m,path):
 a=im.copy();a.putalpha(ImageChops.multiply(im.getchannel('A'),m));a.save(path)
def texture(a,f):a['texture']=str(f.relative_to(P));a['texture_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
cut(original,cape_mask,out/'cape.png');cut(original,scarf_mask,out/'scarf0.png')
upper=Image.open(P/defs['body']['texture']);a=upper.copy();a.putalpha(ImageChops.multiply(upper.getchannel('A'),ImageChops.invert(ImageChops.lighter(cape_mask,scarf_mask))));a.save(out/'chest.png');texture(defs['body'],out/'chest.png')
waist=Image.open(P/defs['waist']['texture']);waist.putalpha(ImageChops.multiply(waist.getchannel('A'),ImageChops.invert(cape_mask)));waist.save(out/'waist.png');texture(defs['waist'],out/'waist.png')
c=copy.deepcopy(defs['body']);c['front_plane']='cape';c['hang_rows']=[211,390];c['geometry_policy']='Authored2D gravity-hanging adapter between actual neck and pelvis motions; not exact simulated source cape.';texture(c,out/'cape.png');defs['cape']=c
raw=Image.open(P/'raw/S-pitched-body-parts1.png');cell=raw.width//2;s=96/(577-348);polys={1:[[192,142],[243,137],[325,143],[365,163],[385,204],[378,243],[344,280],[290,293],[237,281],[195,254],[171,217],[169,181]],2:[[216,116],[273,108],[345,120],[402,148],[429,191],[420,229],[380,261],[317,284],[256,278],[214,252],[198,211],[199,167]],3:[[226,114],[274,110],[323,127],[370,162],[405,198],[413,233],[398,263],[364,286],[313,300],[263,292],[217,272],[182,245],[164,212],[170,175],[193,143]]};pivots={1:[282,190],2:[320,176],3:[278,218]};part_meta=[]
for i in [0,1,2,3]:
 f=out/f'scarf{i}.png'
 if i:
  tile=raw.crop((i%2*cell,i//2*cell,i%2*cell+cell,i//2*cell+cell));m=Image.new('L',tile.size);ImageDraw.Draw(m).polygon(polys[i],fill=255);tile.putalpha(ImageChops.multiply(tile.getchannel('A'),m));x,y=pivots[i];tx=256-x*s;ty=207-y*s;tile=tile.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC);tile.save(f);part_meta.append({'slot':i,'bank_scale':s,'raw_neck_receiver':pivots[i],'static_rest_translation':[tx,ty],'source_polygon':polys[i]})
 a=copy.deepcopy(defs['head']);texture(a,f);defs['scarf'+str(i)]=a
d['order']=['cape','left_leg','right_leg','waist','left_arm','body','scarf0','head','right_arm'];d['costume_adapter']={'source':'Original visible cape/scarf0; generated static scarf1..3 source UV partitions. Remaining generated posed torsos not used as frames.','scarf_shared_bank_scale':s,'scale_calibration':'Unused neutral costume buckle348→hem577 maps original294→390; all3 scarf pitch parts share this one scale. No independent pose or head resizing.','static_scarf_parts':part_meta,'cape_source_region':cape_poly,'cape_hang_rows':[211,390],'scope':'2D original costume adapter and explicit static part ownership; not automatic segmentation, hidden anatomy recovery or exact cloth simulation.'};new=json.dumps(d,separators=(',',':'));(P/'S-front4-articulated-contract.json').write_text(new+'\n');html=(P/'S-front2-articulated-review.html').read_text();assert old in html;html=html.replace(old,new).replace("n==='head'&&p.head_card[0]?'head'+p.head_card[0]:n", "n==='head'&&p.head_card[0]?'head'+p.head_card[0]:n==='scarf0'?'scarf'+p.head_card[0]:n");(P/'S-front4-articulated-review.html').write_text(html);shutil.copyfile(P.parents[2]/'tools/sprite-segmented-player.js',P/'inputs/sprite-segmented-player.js')
