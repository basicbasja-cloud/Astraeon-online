"""Fresh-source phase guide, authored neutral proportions; not recovered image anatomy."""
from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];SRC=P.parent/'pickup-pilot-v31/source/source.json';source=json.loads(SRC.read_text())
def arr(x):return np.array(x,dtype=float)
def angle(v):return math.atan2(v[1],v[0])
def rot(v,t):return arr([v[0]*math.cos(t)-v[1]*math.sin(t),v[0]*math.sin(t)+v[1]*math.cos(t)])
def ik(a,b,l1,l2,sign=1):
 delta=b-a;d=float(np.linalg.norm(delta));assert abs(l1-l2)<d<l1+l2;u=delta/d;q=(l1*l1-l2*l2+d*d)/(2*d);return a+u*q+arr([-u[1],u[0]])*math.sqrt(l1*l1-q*q)*sign
base=source['frames'][0]['points'];restspine=arr([-4,-130]);basis=angle(restspine)-angle(arr(base['head']['xy'])-arr(base['pelvis']['xy']));factor=np.linalg.norm(restspine)/np.linalg.norm(arr(base['head']['xy'])-arr(base['pelvis']['xy']))
board=Image.new('RGBA',(1536,1024));records=[];neutral=Image.open(P/'neutral-reference.png').convert('RGBA')
for i,f in enumerate(source['frames']):
 points=f['points'];delta=lambda n:arr(points[n]['xy'])-arr(base[n]['xy']);pelvis=arr([195,310])+delta('pelvis')*arr([1,2.2]);neck=pelvis+rot(arr(points['head']['xy'])-arr(points['pelvis']['xy']),basis)*factor;turn=angle(neck-pelvis)-angle(restspine);j=dict(pelvis=pelvis,neck=neck)
 for side,hipoff,ankle,lengths,shoulderoff,wrist,arm in [('right',[-17,6],[170,440],[67,59],[-17,47],[150,304],[45,43]),('left',[15,7],[226,458],[72,72],[27,47],[220,307],[45,43])]:
  j[side+'.hip']=pelvis+arr(hipoff);j[side+'.ankle']=arr(ankle);j[side+'.knee']=ik(j[side+'.hip'],j[side+'.ankle'],*lengths);j[side+'.shoulder']=neck+rot(arr(shoulderoff),turn);j[side+'.wrist']=arr(wrist)+delta(side+'.wrist')*.9;j[side+'.elbow']=ik(j[side+'.shoulder'],j[side+'.wrist'],*arm,sign=1 if side=='right' else -1)
 im=Image.new('RGBA',(384,512));d=ImageDraw.Draw(im)
 # Actual first-neutral boot surfaces are fixed visual stencils, not runtime parts.
 for box in [(132,420,201,467),(201,435,258,486)]:im.alpha_composite(neutral.crop(box),box[:2])
 d.polygon([tuple(j[n]) for n in ['right.shoulder','left.shoulder','left.hip','right.hip']],fill=(155,170,190,100))
 for side,color in [('right','#329bff'),('left','#ff9e32')]:
  for chain in [('shoulder','elbow','wrist'),('hip','knee','ankle')]:
   xy=[tuple(j[side+'.'+n]) for n in chain];d.line(xy,fill=color,width=9)
   for x,y in xy:d.ellipse((x-5,y-5,x+5,y+5),fill=color)
 d.ellipse((neck[0]-65,neck[1]-115,neck[0]+65,neck[1]-6),fill=(135,145,160,70),outline='#5f7085',width=2);d.text((max(5,neck[0]-60),neck[1]-85),'HEAD SPACE / OMIT',fill='#aab8c9');d.rectangle((1,1,382,510),outline='#586879',width=1);d.line([tuple(pelvis),tuple(neck)],fill='white',width=5);d.ellipse((neck[0]-8,neck[1]-5,neck[0]+8,neck[1]+5),outline='#6effc7',width=2)
 d.text((8,8),f'{i+1} / source {f["source_time_seconds"]:.3f}s',fill='white');d.text((8,27),'R blue/far; L orange/near',fill='white');board.alpha_composite(im,(i%4*384,i//4*512));records.append(dict(index=i,source_time_seconds=f['source_time_seconds'],joints={n:v.tolist() for n,v in j.items()},turn_radians=turn,definition='Authored proportional guide driven by fresh source deltas; not hidden joints observed in artwork'))
board.save(P/'motion-guide.png');(P/'motion-guide.json').write_text(json.dumps(dict(source_file=str(SRC.relative_to(ROOT)),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),frames=records,canvas=[384,512],source_anatomical_owner_names_preserved=True,old_own_attack_used=False,source_body_proportions_adapted=True,painted_anatomy_approved=False),indent=2)+'\n')
