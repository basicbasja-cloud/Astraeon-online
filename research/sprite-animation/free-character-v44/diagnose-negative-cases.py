import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;out={}
for name in ['attempt1-bind-axis-REJECTED','attempt4-unbound-details-REJECTED']:
 f=P/name/'original-character.blend';bpy.ops.wm.open_mainfile(filepath=str(f));r=bpy.data.objects['Astraeon_Free_Local'];bpy.context.scene.frame_set(1);out[name]=dict(blend_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),missing_actual_deform_modifiers=[o.name for o in bpy.context.scene.objects if o.type=='MESH' and 'runtime_slot' in o and sum(m.type=='ARMATURE' and m.object==r for m in o.modifiers)!=1],maximum_actual_bind_matrix_error=max(abs(a-b) for bone in r.data.bones for ra,rb in zip(r.pose.bones[bone.name].matrix,bone.matrix_local) for a,b in zip(ra,rb)))
(P/'known-negative-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
