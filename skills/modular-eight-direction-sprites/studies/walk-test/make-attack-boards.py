"""Actual camera projection boards; figures are diagnostic fixed-scale copies."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--index',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--suffix',default='');a=p.parse_args();s=json.loads(a.index.read_text());a.out.mkdir(parents=True,exist_ok=True)
for view in ['SE','NE','NW','SW']:
 sheet=Image.new('RGBA',(1536,1024));lines=Image.new('RGBA',(1536,1024),'#272727');d=ImageDraw.Draw(lines)
 for i,r in enumerate(x for x in s['records'] if x['view']==view):
  path=Path(r['image']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'];im=Image.open(path).convert('RGBA').resize((384,384));sheet.alpha_composite(im,(i%4*384,i//4*512+64));lines.alpha_composite(im,(i%4*384,i//4*512+64))
  def point(x):return (x[0]*.75+i%4*384,x[1]*.75+i//4*512+64)
  for side,col in [('r','#2895ff'),('l','#ff881b')]:
   for chain in [['thigh_'+side,'calf_'+side,'foot_'+side,'ball_'+side],['upperarm_'+side,'lowerarm_'+side,'hand_'+side]]:d.line([point(r['bones'][n]['xy']) for n in chain],fill=col,width=3)
  d.line([point(r['right_grip_xy']),point(r['blade_tip_xy'])],fill='cyan',width=2);d.text((i%4*384+8,i//4*512+8),f'{i+1} {r["phase"]} {r["duration_ms"]}ms',fill='white')
 sheet.save(a.out/(view+'-source-eight'+a.suffix+'.png'));lines.save(a.out/(view+'-bone-review'+a.suffix+'.png'))
(a.out/('source-binding'+a.suffix+'.json')).write_text(json.dumps({'index':str(a.index),'sha256':hashlib.sha256(a.index.read_bytes()).hexdigest(),'palm_geometry_socket':not s.get('socket_is_wrist_joint',True),'scale':.75,'shared_offset_xy':[0,64],'records':[{k:r[k] for k in ['view','key','image','sha256','time_ms']} for r in s['records']]},indent=2)+'\n')
