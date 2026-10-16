"""Source-projected front torso plane + thigh-driven waist + fixed-bank head pitch parts.
This is an explicitly authored 2D surface adapter, not reconstructed painted3D anatomy.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import copy,json,hashlib,shutil
P=Path(__file__).resolve().parent;d=json.loads((P/'S-articulated-contract.json').read_text());old=json.dumps(d,separators=(',',':'));defs=d['definitions'];out=P/'inputs/front-S';out.mkdir(exist_ok=True)
src=json.loads((P/'source/controlled-retiming-v1.json').read_text())['views']['S']['frames'];source_rest=src[0]['source_bones']['torso'];dy0=source_rest['tail']['xy'][1]-source_rest['head']['xy'][1];artist_dy=defs['body']['rest']['neck'][1]-defs['body']['rest']['hips'][1];ratios=[]
for p,row in zip(d['poses'],src):
 b=row['source_bones']['torso'];ratio=(b['tail']['xy'][1]-b['head']['xy'][1])/dy0;assert ratio>0;p['source_neck_delta']=p['neck'].copy();p['neck'][1]=p['hips'][1]+artist_dy*(ratio-1);ratios.append(ratio)
d['front_torso_retarget']={'method':'Relative actual source projected bone length applied to authored rest length. No image/crown fitting. Raw additive neck deltas retained for diagnosis.','source_rest_dy':dy0,'artist_rest_dy':artist_dy,'actual_source_length_ratios':ratios,'scope':'Corrects artist/source rest-bone length mismatch; actual source torso never reverses projected winding.'}
body=defs['body'];im=Image.open(P/body['texture']);poly=[[197,280],[303,280],[309,392],[196,392]];mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(poly,fill=255);waist=im.copy();waist.putalpha(ImageChops.multiply(im.getchannel('A'),mask));waist.save(out/'waist.png');remove=mask.copy();ImageDraw.Draw(remove).rectangle((0,0,512,300),fill=0);upper=im.copy();upper.putalpha(ImageChops.multiply(im.getchannel('A'),ImageChops.invert(remove)));upper.save(out/'upper.png')
def texture(a,p):a['texture']=str(p.relative_to(P));a['texture_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
texture(body,out/'upper.png');body['front_plane']='torso';body['geometry_policy']='Source projected rigid front plane, not blended skin. Preserve X axis; signed projected Y follows actual source torso; source orientation must remain positive, invalid reversal rejected. Uniform near-edge foreshortening is measured separately from local mesh folds.'
w=copy.deepcopy(body);texture(w,out/'waist.png');w['front_plane']='waist';w['geometry_policy']='Positive thigh-projected waist foreshortening, separate from torso plane.'
for side in ['left','right']:
 a=defs[side+'_leg']['rest'];w['rest'][side+'.hip']=a[side+'.hip'];w['rest'][side+'.knee']=a[side+'.knee']
defs['waist']=w
for i in [1,2,3]:
 a=copy.deepcopy(defs['head']);texture(a,P/f'inputs/S-pitch-head-parts1/{i}.png');defs['head'+str(i)]=a
progress=[0,.03,.11,.23,.38,.55,.72,.89,1,.92,.77,.59,.41,.23,.08,0]
for p,t in zip(d['poses'],progress):p['head_card']=[0 if t<.15 else 1 if t<.45 else 2 if t<.80 else 3,0]
d['order']=['left_leg','right_leg','waist','left_arm','body','head','right_arm'];d['scope']+=' Front-plane relative source projection; pitch-head part bank at one shared scale and static rest neck origins. No full-image scale/registration or per-frame fitting.';new=json.dumps(d,separators=(',',':'));(P/'S-front2-articulated-contract.json').write_text(new+'\n')
html=(P/'S-articulated-review.html').read_text();assert old in html;html=html.replace(old,new).replace("n==='body'?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer", "d.front_plane?SpritePickupFrontPlane:n==='body'?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer").replace("n==='body'?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer", "d.front_plane?SpritePickupFrontPlane:n==='body'?SpritePickupTorso:n==='waist'?SpriteArticulatedLayer");html=html.replace('let m=layers.get(n);',"let m=layers.get(n==='head'&&p.head_card[0]?'head'+p.head_card[0]:n);");html=html.replace("n==='head'", "n==='head'",1)
# Extra pitch heads use the same rigid head class, never a torso fallback.
html=html.replace(":SpritePickupHead;",":SpritePickupHead;")
html=html.replace('height="512"','height="576"').replace('ctx.clearRect(0,0,512,512)','ctx.clearRect(0,0,512,576)').replace("layers.set(n,new K(document.createElement('canvas'),im,d));ok()", "const layer=new K(document.createElement('canvas'),im,d);layer.setViewport(512,576);layers.set(n,layer);ok()")
(P/'S-front2-articulated-review.html').write_text(html);shutil.copyfile(P.parents[2]/'tools/sprite-segmented-player.js',P/'inputs/sprite-segmented-player.js')
