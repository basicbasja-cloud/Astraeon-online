"""Actual isolated-arm renders of LBS/DQ, not a painted character or body capture."""
import bpy,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P/'skinned-arm-proof';r=json.loads((O/'skin-receipt.json').read_text());worst=min(r['frames'],key=lambda f:min(f['mesh_measurements']['left']['lbs_ring_area_ratios']));i=worst['index'];bpy.ops.wm.open_mainfile(filepath=str(O/'continuous-arm-skin.blend'));sc=bpy.context.scene;tick=1+39*i/7;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick))
for o in sc.objects:
 if o.type=='MESH':o.hide_render=not o.name.endswith('.continuous_arm')
rows=[]
for mode in ['LBS','DQ']:
 for o in sc.objects:
  for m in o.modifiers:
   if m.type=='ARMATURE' and o.name.endswith('.continuous_arm'):m.use_deform_preserve_volume=mode=='DQ'
 bpy.context.view_layer.update()
 for v in ['W','NW']:
  sc.camera=bpy.data.objects[v];path=O/f'isolated-{mode}-{v}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);rows.append(dict(mode=mode,view=v,source_index=i,path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(O/'isolated-comparison.json').write_text(json.dumps(dict(frames=rows,scope='Isolated arm meshes only; body hidden intentionally. Same bone pose/camera between LBS andDQ.'),indent=2)+'\n');print('ISOLATED_SKIN_COMPARISON_RENDERED')
