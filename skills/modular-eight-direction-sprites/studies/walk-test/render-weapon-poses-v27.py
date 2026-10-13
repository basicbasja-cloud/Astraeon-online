"""Eight actual projected source weapons. No 2D rotation or per-key rescaling."""
import bpy,json,math,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[4];D=R/'research/sprite-animation/weighted-slash-v27';index=json.loads((D/'rig-source/source-index.json').read_text());p=R/index['blend'];assert hashlib.sha256(p.read_bytes()).hexdigest()==index['blend_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False);s=bpy.context.scene;bpy.data.objects['facing.pivot'].rotation_euler.z=math.pi/4
for o in s.objects:
 if o.type=='MESH':o.hide_render=o.get('slot')!='weapon.sword.right'
folder=D/'weapon-source';folder.mkdir(exist_ok=True);sheet=Image.new('RGBA',(2048,1024));rows=[]
for i,t in enumerate([0,100,180,230,280,360,460,560]):
 s.frame_set(t);bpy.context.view_layer.update();path=folder/f'{i:02}.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=Image.open(path).convert('RGBA');sheet.paste(im,(i%4*512,i//4*512));rows.append({'key':i,'time_ms':t,'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_grip_xy':index['records'][i]['right_grip_xy'],'source_tip_xy':index['records'][i]['blade_tip_xy']})
sheet.save(folder/'eight-weapon-guide.png');(folder/'manifest.json').write_text(json.dumps({'source_blend_sha256':index['blend_sha256'],'render_method':'Actual independently evaluated projected mesh at each body key; fixed camera; NO 2D rotate','frames':rows},indent=2)+'\n');print('WEAPON_SOURCE_EXPORTED',len(rows))
