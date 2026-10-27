from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,math,shutil
b=Path('authoring/characters/factory-v3/patch-0.0.1');o=b/'research/tall-sword-anatomical-fit-20261027';o.mkdir(exist_ok=True);manifest=json.loads((b/'guides/c297971fcef09188ff60/manifest.json').read_text());s=json.loads((b/'research/native-rig-library-20261026/source/c297971fcef09188ff60.json').read_text());bones=s['frames'][0]['bones'];names=['pelvis','spine_01','spine_02','spine_03','neck_01','head','clavicle_r','upperarm_r','lowerarm_r','hand_r','clavicle_l','upperarm_l','lowerarm_l','hand_l','thigh_r','calf_r','foot_r','thigh_l','calf_l','foot_l'];proof={};contact=Image.new('RGBA',(1536,768),'#ddd')
for col,view in enumerate(['SW','NW','NE','SE']):
 c=manifest['views'][view]['camera'];x,y,z=c['rotation'];rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]]);ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]]);rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]]);R=rz@ry@rx;loc=np.array(c['location']);ppm=768/c['ortho_scale'];f=lambda v:[384+np.dot(np.array(v)-loc,R[:,0])*ppm,384-np.dot(np.array(v)-loc,R[:,1])*ppm];p=b/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack'/view/'Master/000.png';original=Image.open(p).convert('RGBA');im=original.copy();d=ImageDraw.Draw(im);points={}
 for name in names:
  if name not in bones:continue
  a=f(bones[name]['head']);z=f(bones[name]['tail']);d.line([tuple(a),tuple(z)],fill=(10,220,255,240),width=1);d.ellipse((a[0]-2,a[1]-2,a[0]+2,a[1]+2),fill='red');points[name]=a
 for n in ['head','upperarm_r','lowerarm_r','hand_r','pelvis']:
  a=points[n];d.text((a[0]+3,a[1]),n,fill='black')
 original.save(o/f'{view}-master.png');im.save(o/f'{view}-overlay.png');contact.alpha_composite(original.crop((192,256,576,640)),(col*384,0));contact.alpha_composite(im.crop((192,256,576,640)),(col*384,384));ImageDraw.Draw(contact).text((col*384+4,4),view+' APPROVED STYLE BASELINE',fill='black');proof[view]={'projected_bone_heads':points,'maximum_seven_landmark_projection_error_authoring_px':max(np.linalg.norm(np.array(f(bones[n]['head']))-np.array(manifest['views'][view]['frames'][0]['landmarks'][n])*.5)for n in ['head','hand_r','hand_l','pelvis','foot_r','foot_l'])}
contact.convert('RGB').save(o/'baseline-versus-source-joints.jpg',quality=98);(o/'projection-proof.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copy2(__file__,o/'overlay-source.py');print({v:r['maximum_seven_landmark_projection_error_authoring_px']for v,r in proof.items()})
