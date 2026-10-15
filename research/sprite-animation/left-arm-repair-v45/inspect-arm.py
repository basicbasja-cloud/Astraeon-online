"""Independently evaluate actual saved before/after rigs; never call authoring pose()."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;OLD=P.parent/'free-character-v44';V=Vector;contract=json.loads((P/'arm-contract.json').read_text());S=json.loads((P.parent/'continuous-arm-v43/source/source.json').read_text());D=[0,.18,.72,1,.82,.38,.06,0]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def vertices(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return vs

def expected(i):
 p={k:V(v['world_xyz']) for k,v in S['frames'][i]['points'].items()};up=(p['neck']-p['pelvis']).normalized();front=V((0,-up.z,up.y));depth=D[i];g=p['pelvis']-up*(.10-.10*depth)+front*(-.015+.125*depth)+V((.32,0,0));a=p['left.shoulder'];pole=a-up*.35-front*.12+V((.04,0,0));dv=g-a;dist=dv.length;n=dv/dist;v=pole-a;v-=n*v.dot(n);v.normalize();along=(.29**2-.39**2+dist**2)/(2*dist);e=a+n*along+v*math.sqrt(.29**2-along**2);f=(g-e).normalized();p.update({'left.elbow':e,'left.wrist':e+f*.27,'left.palm':e+f*.34,'left.grip':g});return p

def scan(path,new):
 bpy.ops.wm.open_mainfile(filepath=str(path));sc=bpy.context.scene;r=bpy.data.objects['Astraeon_Free_Local'];gem=bpy.data.objects['collectible'];objects=[o for o in sc.objects if o.type=='MESH' and 'runtime_slot' in o];missing=[o.name for o in objects if sum(m.type=='ARMATURE' and m.object==r and m.show_viewport and m.show_render for m in o.modifiers)!=1];weight_error=max(abs(sum(g.weight for g in v.groups)-1) for o in objects for v in o.data.vertices);invalid_weights=sum(not math.isfinite(g.weight) or g.weight<0 for o in objects for v in o.data.vertices for g in v.groups);sc.frame_set(1);arm=bpy.data.objects['left.continuous_arm'];rest=vertices(arm);edges={}
 for face in arm.data.polygons:
  for a,b in zip(list(face.vertices),list(face.vertices)[1:]+list(face.vertices)[:1]):
   k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
 nonmanifold=sum(n!=2 for n in edges.values());feet={o.name:vertices(o) for o in objects if o.name.endswith(('.sole','.boot','.boot_seam'))};records=[];previous=None;max_bind=0
 for o in objects:
  vs=vertices(o)
  if len(vs)==len(o.data.vertices):max_bind=max(max_bind,max((a-o.matrix_world@b.co).length for a,b in zip(vs,o.data.vertices)))
 def rings(vs):return [vs[j*24:(j+1)*24] for j in range(29)]
 def areas(ring):
  center=sum(ring,V())/24;n=V()
  for a,b in zip(ring,ring[1:]+ring[:1]):n+=(a-center).cross(b-center)
  return n.length/2
 areas0=[areas(ring) for ring in rings(rest)];restcenters=[sum(v,V())/24 for v in rings(rest)];spacing0=[(a-b).length for a,b in zip(restcenters,restcenters[1:])]
 for j in range(313):
  t=j/312;tick=1+39*t;sc.frame_set(int(tick),subframe=tick-int(tick));u=r.pose.bones['left.upperarm'];f=r.pose.bones['left.forearm'];h=r.pose.bones['left.hand'];up=(r.pose.bones['torso'].tail-r.pose.bones['torso'].head).normalized();lat=(u.head-r.pose.bones['right.upperarm'].head).normalized();a=(u.tail-u.head).normalized();b=(f.tail-f.head).normalized();n=a.cross(b)
  if n.length<1e-6:raise ValueError('Undefined elbow plane; UNKNOWN cannot pass')
  n.normalize();abduction=math.degrees(math.asin(min(1,abs(a.dot(lat)))));plane=math.degrees(math.acos(min(1,abs(n.dot(lat)))));flex=math.degrees(math.acos(max(-1,min(1,a.dot(b)))));step=None if previous is None else math.degrees(math.acos(max(-1,min(1,n.dot(previous)))));previous=n.copy();vs=vertices(arm);rr=rings(vs);cs=[sum(v,V())/24 for v in rr];ratios=[areas(v)/x for v,x in zip(rr,areas0)];spacing=[(a-b).length/base for a,b,base in zip(cs,cs[1:],spacing0)];foot=max(max((a-b).length for a,b in zip(vertices(bpy.data.objects[name]),base)) for name,base in feet.items());length=max(abs((r.pose.bones['left.'+bone].tail-r.pose.bones['left.'+bone].head).length-l) for bone,l in [('upperarm',.29),('forearm',.27),('hand',.07)]);grip=None
  if 3/7<t<1:grip=(r.pose.bones['right.hand'].tail+(r.pose.bones['right.hand'].tail-r.pose.bones['right.hand'].head).normalized()*.05-(gem.location+V((0,0,.075)))).length
  records.append(dict(t=t,abduction_degrees=abduction,plane_deviation_degrees=plane,flexion_degrees=flex,normal_step_degrees=step,ring_area_min=min(ratios),ring_area_max=max(ratios),ring_spacing_min=min(spacing),foot_vertex_drift=foot,bone_length_error=length,right_held_socket_error=grip))
 errors=[]
 for i in range(8):
  tick=1+39*i/7;sc.frame_set(int(tick),subframe=tick-int(tick));p=expected(i) if new else {k:V(v['world_xyz']) for k,v in S['frames'][i]['points'].items()};es={}
  for name,a,b in [('root','pelvis',None),('torso','pelvis','neck'),('head','head',None)]+[(side+'.'+bone,side+'.'+a,side+'.'+b) for side in ['left','right'] for bone,a,b in [('upperarm','shoulder','elbow'),('forearm','elbow','wrist'),('hand','wrist','palm'),('thigh','hip','knee'),('shin','knee','ankle'),('foot','ankle','toe')]]:
   pb=r.pose.bones[name];es[name+'.head']=(pb.head-p[a]).length
   if b:es[name+'.tail']=(pb.tail-p[b]).length
  errors.append(dict(index=i,max_error=max(es.values()),errors=es))
 return dict(blend_sha256=sha(path),mesh_count=len(objects),arm_nonmanifold_edges=nonmanifold,missing_actual_modifiers=missing,maximum_weight_sum_error=weight_error,invalid_weights=invalid_weights,actual_bind_vertex_error=max_bind,source_key_errors=errors,frames=records,summary=dict(max_abduction_degrees=max(f['abduction_degrees'] for f in records),max_plane_deviation_degrees=max(f['plane_deviation_degrees'] for f in records),min_flexion_degrees=min(f['flexion_degrees'] for f in records),max_flexion_degrees=max(f['flexion_degrees'] for f in records),max_normal_step_degrees=max(f['normal_step_degrees'] or 0 for f in records),min_ring_area_ratio=min(f['ring_area_min'] for f in records),max_ring_area_ratio=max(f['ring_area_max'] for f in records),min_ring_spacing_ratio=min(f['ring_spacing_min'] for f in records),max_foot_vertex_drift=max(f['foot_vertex_drift'] for f in records),max_bone_length_error=max(f['bone_length_error'] for f in records),max_right_socket_error=max(f['right_held_socket_error'] or 0 for f in records)))
before=scan(OLD/'original-character.blend',False);after=scan(P/'original-character.blend',True);out=dict(kind='Actual saved-rig body-relative elbow and deformed-surface inspection',script_sha256=sha(Path(__file__)),contract_sha256=sha(P/'arm-contract.json'),before=before,after=after,scope='Authored relaxed free-arm pickup constraint. Not a universal elbow anatomy classifier, painted-image tracker, self-collision solver or user approval.',production_pass=False);(P/'arm-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print('BEFORE',before['summary']);print('AFTER',after['summary'])
