"""Actual Blender GLB re-import comparison; reports, does not silently repair."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,kdtree
P=Path(__file__).resolve().parent;corrected='--corrected' in sys.argv;asset=P/('original-character-corrected.glb' if corrected else 'original-character-experimental.glb')
def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return p
bpy.ops.wm.open_mainfile(filepath=str(P/'original-character.blend'));sc=bpy.context.scene;names=[o.name for o in sc.objects if o.type=='MESH' and 'runtime_slot' in o];frames=list(range(1,41)) if corrected else [1,18,40];src={}
for t in frames:
 sc.frame_set(t);src[t]={n:points(bpy.data.objects[n]) for n in names}
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(asset));rig=next(o for o in sc.objects if o.type=='ARMATURE');action=rig.animation_data.action;start=float(action.frame_range[0]);records=[]
for t in frames:
 tick=start+t-1;sc.frame_set(int(tick),subframe=tick-int(tick));errors={}
 for n in names:
  a=src[t][n];b=points(bpy.data.objects[n]);tree=kdtree.KDTree(len(a))
  for k,v in enumerate(a):tree.insert(v,k)
  tree.balance();forward=max(tree.find(v)[2] for v in b);tree=kdtree.KDTree(len(b))
  for k,v in enumerate(b):tree.insert(v,k)
  tree.balance();back=max(tree.find(v)[2] for v in a);errors[n]=max(forward,back)
 records.append(dict(source_frame=t,import_frame=tick,max_surface_vertex_distance=max(errors.values()),objects=errors))
limit=.0001;worst=max(r['max_surface_vertex_distance'] for r in records);out=dict(glb_sha256=hashlib.sha256((asset).read_bytes()).hexdigest(),comparison='Actual evaluated mesh vertices; symmetric nearest-vertex distance, same30fps integer sample times, one explicit imported-action-start offset. Not triangle Hausdorff or engine playback.',imported_action_frame_range=list(action.frame_range),source_uses_dual_quaternion=True,imported_armature_preserve_volume_flags=sorted(set(m.use_deform_preserve_volume for o in sc.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE')),provisional_surface_limit_world=.0001,maximum_surface_error_world=worst,roundtrip_surface_pass=worst<limit,frames=records,production_pass=False);(P/('corrective-glb-roundtrip.json' if corrected else 'glb-roundtrip.json')).write_text(json.dumps(out,indent=2)+'\n');print('ACTUAL_GLB_ROUNDTRIP',worst,'PASS',worst<limit)
