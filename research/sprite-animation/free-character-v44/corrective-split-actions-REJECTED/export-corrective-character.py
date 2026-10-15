"""Free local glTF LBS correction at40 baked sample times.
DQ target surfaces are measured before conversion; no original .blend write.
Not a general continuous-time DQ equivalent or engine admission.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'original-character.blend'));sc=bpy.context.scene;r=bpy.data.objects['Astraeon_Free_Local'];objects=[o for o in sc.objects if o.type=='MESH' and 'runtime_slot' in o];mixed=[o for o in objects if any(sum(g.weight>0 for g in v.groups)>1 for v in o.data.vertices)]
def evaluated(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[v.co.copy() for v in me.vertices];ev.to_mesh_clear();return vs
# Capture the authority before any morph is added or DQ disabled.
targets={}
for t in range(1,41):
 sc.frame_set(t);targets[t]={o.name:evaluated(o) for o in mixed}
sc.frame_set(1);max_correction=0;sample_residual=0
for o in mixed:
 assert max(abs(a-b) for ra,rb in zip(o.matrix_world,Matrix.Identity(4)) for a,b in zip(ra,rb))<1e-6
 basis=o.shape_key_add(name='Basis');keys={}
 for t in range(1,41):
  sc.frame_set(t);matrices={pb.name:pb.matrix@pb.bone.matrix_local.inverted() for pb in r.pose.bones};corrected=[]
  for v,q in zip(o.data.vertices,targets[t][o.name]):
   ws=[(o.vertex_groups[g.group].name,g.weight) for g in v.groups if g.weight>0];mat=Matrix([[sum(matrices[n][i][j]*w for n,w in ws) for j in range(4)] for i in range(4)]);assert abs(mat.determinant())>1e-5;point=mat.inverted()@q;max_correction=max(max_correction,(point-v.co).length);corrected.append(point)
  if max((a-v.co).length for a,v in zip(corrected,o.data.vertices))<1e-6:continue
  key=o.shape_key_add(name=f'DQ_sample_{t:02}');keys[t]=key
  for v,q in zip(key.data,corrected):v.co=q
 for t in range(1,41):
  for k,key in keys.items():key.value=1 if k==t else 0;key.keyframe_insert('value',frame=t)
 for fc in o.data.shape_keys.animation_data.action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
# Bake the omitted cape shell at rest; this cape is rigidly torso-weighted.
sc.frame_set(1);cape=bpy.data.objects['original_cape'];bpy.ops.object.select_all(action='DESELECT');cape.select_set(True);bpy.context.view_layer.objects.active=cape
for mod in list(cape.modifiers):
 if mod.type=='SOLIDIFY':bpy.ops.object.modifier_apply(modifier=mod.name)
for t in range(1,41):
 sc.frame_set(t)
 for o in mixed:sample_residual=max(sample_residual,max((a-b).length for a,b in zip(evaluated(o),targets[t][o.name])))
assert sample_residual<1e-5,sample_residual
sc.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
for o in objects+[r]:o.select_set(True)
out=P/'original-character-corrected.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_skins=True,export_animations=True,export_frame_range=True,export_force_sampling=True,export_animation_mode='SCENE',export_morph=True,export_extras=True)
(P/'corrective-export-receipt.json').write_text(json.dumps(dict(source_blend_sha256=hashlib.sha256((P/'original-character.blend').read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),mixed_mesh_names=[o.name for o in mixed],target_sample_count=40,maximum_pre_skin_corrective_displacement=max_correction,maximum_local_evaluated_sample_residual=sample_residual,method='Pre-skin corrective morph targets invert each vertex weighted LBS matrix to reproduce measured DQ points at40samples. Rest cape shell baked in-memory. One SCENE clip; source .blend unchanged.',scope='Sampled export experiment; not guaranteed between samples, different poses, arbitrary engine blend shapes, painted-art quality or production',production_pass=False),indent=2)+'\n');print('CORRECTIVE_EXPORT',sample_residual)
