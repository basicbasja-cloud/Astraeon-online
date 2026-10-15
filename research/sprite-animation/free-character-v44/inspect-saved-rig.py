"""Read the saved .blend through Blender's evaluated dependency graph.
No imports/execution of the authoring script; no re-authoring of any pose.
"""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;V=Vector
source=P.parent/'continuous-arm-v43/source/source.json';S=json.loads(source.read_text());blend=P/'original-character.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;r=bpy.data.objects['Astraeon_Free_Local'];gem=bpy.data.objects['collectible'];objects=[o for o in sc.objects if o.type=='MESH' and 'runtime_slot' in o]
def verts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();vs=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear();return vs
weight_errors=[];unweighted=0;nonfinite=0;topology={};missing_modifiers=[]
for o in objects:
 if sum(m.type=='ARMATURE' and m.object==r and m.show_viewport and m.show_render for m in o.modifiers)!=1:missing_modifiers.append(o.name)
 for v in o.data.vertices:
  values=[g.weight for g in v.groups];unweighted+=not values;weight_errors.append(abs(sum(values)-1));nonfinite+=sum(not math.isfinite(x) or x<0 for x in values)
 if '.continuous_' in o.name:
  ec={}
  for f in o.data.polygons:
   for a,b in zip(list(f.vertices),list(f.vertices)[1:]+list(f.vertices)[:1]):key=tuple(sorted((a,b)));ec[key]=ec.get(key,0)+1
  topology[o.name]=dict(vertices=len(o.data.vertices),nonmanifold_edges=sum(n!=2 for n in ec.values()))
sc.frame_set(1);feet={o.name:verts(o) for o in objects if o.name.endswith(('.sole','.boot','.boot_seam'))};bind_errors={}
for o in objects:
 evaluated=verts(o)
 if len(evaluated)==len(o.data.vertices):bind_errors[o.name]=max((a-o.matrix_world@b.co).length for a,b in zip(evaluated,o.data.vertices))
key_errors=[]
for i,fr in enumerate(S['frames']):
 tick=1+39*i/7;sc.frame_set(int(tick),subframe=tick-int(tick));wanted={k:V(p['world_xyz']) for k,p in fr['points'].items()};errors={}
 for bone,a,b in [('root','pelvis',None),('torso','pelvis','neck'),('head','head',None)]+[(side+'.'+bone,side+'.'+a,side+'.'+b) for side in ['left','right'] for bone,a,b in [('upperarm','shoulder','elbow'),('forearm','elbow','wrist'),('hand','wrist','palm'),('thigh','hip','knee'),('shin','knee','ankle'),('foot','ankle','toe')]]:
  pb=r.pose.bones[bone];errors[bone+'.head']=(pb.head-wanted[a]).length
  if b:errors[bone+'.tail']=(pb.tail-wanted[b]).length
 key_errors.append(dict(index=i,max_error=max(errors.values()),errors=errors))
records=[];sole_min=999.;foot_drift=0;grasp_error=0;length_error=0;hinge_error=0;ring_min=999.;ring_max=0;areas0={}
def areas(vs):
 out=[]
 for j in range(29):
  ring=vs[j*24:(j+1)*24];center=sum(ring,V())/24;normal=V()
  for a,b in zip(ring,ring[1:]+ring[:1]):normal+=(a-center).cross(b-center)
  out.append(normal.length/2)
 return out
for j in range(157):
 t=j/156;tick=1+39*t;sc.frame_set(int(tick),subframe=tick-int(tick));localfoot=0;localgrip=None
 for name,rest in feet.items():localfoot=max(localfoot,max((a-b).length for a,b in zip(verts(bpy.data.objects[name]),rest)))
 foot_drift=max(foot_drift,localfoot)
 for side in ['left','right']:
  sole_min=min(sole_min,min(v.z for v in verts(bpy.data.objects[side+'.sole'])))
  for suffix,l in [('upperarm',.29),('forearm',.27),('hand',.07),('thigh',.42),('shin',.40)]:
   pb=r.pose.bones[side+'.'+suffix];length_error=max(length_error,abs((pb.tail-pb.head).length-l))
  u=r.pose.bones[side+'.upperarm'].matrix.to_3x3().normalized();f=r.pose.bones[side+'.forearm'].matrix.to_3x3().normalized();h=r.pose.bones[side+'.hand'].matrix.to_3x3().normalized();hinge_error=max(hinge_error,((u.inverted()@f)@V((0,0,1))-V((0,0,1))).length)
  for kind in ['arm','leg']:
   name=side+'.continuous_'+kind;ar=areas(verts(bpy.data.objects[name]));areas0.setdefault(name,ar);ratios=[x/y for x,y in zip(ar,areas0[name])];ring_min=min(ring_min,*ratios);ring_max=max(ring_max,*ratios)
 if 3/7<t<1:
  hand=r.pose.bones['right.hand'];socket=hand.tail+(hand.tail-hand.head).normalized()*.05;localgrip=(socket-(gem.location+V((0,0,.075)))).length;grasp_error=max(grasp_error,localgrip)
 records.append(dict(t=t,rig_frame=tick,foot_vertex_drift=localfoot,held_item_socket_error=localgrip,right_palm=list(r.pose.bones['right.hand'].tail)))
# Real known-bad bind, not a synthetic report with a renamed side.
runtime_slots=sorted(set(o['runtime_slot'] for o in objects))
bad=P/'attempt1-bind-axis-REJECTED/original-character.blend';bpy.ops.wm.open_mainfile(filepath=str(bad));old=bpy.data.objects['Astraeon_Free_Local'];bpy.context.scene.frame_set(1);bad_basis=max(abs(a-b) for name in ['root','torso','head'] for ra,rb in zip(old.pose.bones[name].matrix,old.data.bones[name].matrix_local) for a,b in zip(ra,rb))
receipt=dict(scope='Actual saved rig evaluated independently at157times; does not approve character art, self-collision, thumb anatomy, cloth simulation, game-ready layer exports or universal motion',blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),inspection_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),mesh_count=len(objects),runtime_slots=runtime_slots,missing_armature_modifiers=missing_modifiers,maximum_weight_sum_error=max(weight_errors),unweighted_vertices=unweighted,invalid_weights=nonfinite,actual_bind_vertex_errors=bind_errors,closed_limb_topology=topology,source_key_errors=key_errors,dense_sample_count=len(records),max_dense_foot_vertex_drift=foot_drift,min_dense_sole_world_z=sole_min,max_dense_bone_length_error=length_error,max_dense_right_grasp_socket_error=grasp_error,max_dense_hinge_axis_error=hinge_error,dense_limb_ring_area_ratio_range=[ring_min,ring_max],known_bad_bind_basis_error=bad_basis,frames=records,production_pass=False)
(P/'saved-rig-inspection.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SAVED_RIG_INSPECTED',json.dumps({k:v for k,v in receipt.items() if k.startswith(('max_','min_','dense_limb','known_bad'))}))
