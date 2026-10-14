"""Local continuous-arm/DQ skin proof, not final character art.

Loads the retained source scene without overwriting it. New arm meshes are bound
in the exact rest configuration and actually deformed by Blender armature bones.
The other mannequin geometry is reconstructed per-key from source world points.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;OUT=P/'skinned-arm-proof';OUT.mkdir(exist_ok=True)
s=json.loads((P/'source/source.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'source/authoring-rig.blend'));sc=bpy.context.scene;sc.cycles.samples=4
V=Vector
def pts(i):return {k:V(v['world_xyz']) for k,v in s['frames'][i]['points'].items()}
rest=pts(0)
for side in ['left','right']:
 for k in ['upperarm','forearm','elbow']:
  obj=bpy.data.objects.get(side+'.'+k)
  if obj:bpy.data.objects.remove(obj,do_unlink=True)
# Independent real skin rig: exact bone roll at bind, not a texture pivot claim.
data=bpy.data.armatures.new('ContinuousArmSkin');rig=bpy.data.objects.new('ContinuousArmSkin',data);sc.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
chains=[]
for side in ['left','right']:
 for label,a,b,parent in [('upperarm','shoulder','elbow',None),('forearm','elbow','wrist','upperarm'),('hand','wrist','palm','forearm')]:
  name=side+'.'+label;start,end=rest[side+'.'+a],rest[side+'.'+b];bone=data.edit_bones.new(name);bone.head=start;bone.tail=end;bone.matrix=Matrix.LocRotScale(start,(end-start).to_track_quat('Y','Z'),V([1,1,1]));bone.length=(end-start).length
  if parent:bone.parent=data.edit_bones[side+'.'+parent];bone.use_connect=True
  chains.append((name,side+'.'+a,side+'.'+b))
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def material(k):return bpy.data.materials[k]
skins={};N=32;RINGS=25
for side in ['left','right']:
 a,b,c=[rest[side+'.'+k] for k in ['shoulder','elbow','wrist']];upper=(b-a).length;lower=(c-b).length;total=upper+lower;u=(b-a).normalized();v=(c-b).normalized();vertices=[];weights=[];faces=[]
 for j in range(RINGS):
  t=total*j/(RINGS-1);center=a+u*t if t<=upper else b+v*(t-upper);mix=max(0,min(1,(t-upper+.055)/.11));mix=mix*mix*(3-2*mix);tangent=(u*(1-mix)+v*mix).normalized();normal=V([1,0,0]);normal-=tangent*normal.dot(tangent)
  if normal.length<.01:normal=V([0,1,0])-tangent*tangent.y
  normal.normalize();binormal=tangent.cross(normal).normalized()
  # Narrow elbow, forearm/cuff taper; one continuous closed surface.
  knots=[(0,.053),(.15,.049),(.29,.043),(.34,.049),(.45,.042),(.56,.032)]
  radius=knots[-1][1]
  for (t0,r0),(t1,r1) in zip(knots,knots[1:]):
   if t0<=t<=t1:radius=r0+(r1-r0)*(t-t0)/(t1-t0);break
  for k in range(N):
   q=2*math.pi*k/N;vertices.append(center+normal*(math.cos(q)*radius)+binormal*(math.sin(q)*radius*.86));weights.append((1-mix,mix))
 for j in range(RINGS-1):
  for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 faces.extend([tuple(range(N-1,-1,-1)),tuple((RINGS-1)*N+k for k in range(N))]);mesh=bpy.data.meshes.new(side+'.continuous_arm');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(side+'.continuous_arm',mesh);sc.collection.objects.link(o)
 o.data.materials.append(material('navy'));o.data.materials.append(material('bronze'))
 for poly in o.data.polygons:
  poly.use_smooth=True;poly.material_index=1 if sum(v//N for v in poly.vertices)/len(poly.vertices)*total/(RINGS-1)>.32 else 0
 vg0=o.vertex_groups.new(name=side+'.upperarm');vg1=o.vertex_groups.new(name=side+'.forearm')
 for k,(w0,w1) in enumerate(weights):
  if w0:vg0.add([k],w0,'REPLACE')
  if w1:vg1.add([k],w1,'REPLACE')
 mod=o.modifiers.new('Real armature skin / preserve volume','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;skins[side]=(o,mod)
 # A wrist-to-palm volume prevents a gap between the sleeve and glove.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1);o=bpy.context.object;o.name=side+'.wrist_glove_bridge';o.data.materials.append(material('brown'))
def deformed(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();out=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();return out
def area(points):
 center=sum(points,V())/len(points);normal=V()
 for a,b in zip(points,points[1:]+points[:1]):normal+=(a-center).cross(b-center)
 return normal.length/2
def areas(o):
 vs=deformed(o);return [area(vs[j*N:(j+1)*N]) for j in range(RINGS)]
# Set exact rest pose before measuring the bind surfaces.
for name,a,b in chains:
 p=rig.pose.bones[name];p.rotation_mode='QUATERNION';p.matrix=Matrix.LocRotScale(rest[a],(rest[b]-rest[a]).to_track_quat('Y','Z'),V([1,1,1]))
bpy.context.view_layer.update();baseline={side:areas(o) for side,(o,_) in skins.items()};records=[]
for i,f in enumerate(s['frames']):
 p=pts(i);tick=1+39*i/7;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));attachment=[]
 for name,a,b in chains:
  bone=rig.pose.bones[name];bone.matrix=Matrix.LocRotScale(p[a],(p[b]-p[a]).to_track_quat('Y','Z'),V([1,1,1]));bpy.context.view_layer.update();attachment.extend([(bone.head-p[a]).length,(bone.tail-p[b]).length]);bone.keyframe_insert('location',frame=tick);bone.keyframe_insert('rotation_quaternion',frame=tick)
 # Reconstruct unchanged source mannequin body/garment geometry at this key.
 for side in ['left','right']:
  for kind,a,b in [('thigh','hip','knee'),('shin','knee','ankle')]:
   o=bpy.data.objects[side+'.'+kind];delta=p[side+'.'+b]-p[side+'.'+a];o.location=(p[side+'.'+a]+p[side+'.'+b])/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.scale=(o['radius'],o['radius'],delta.length)
  for k in ['shoulder','knee','palm']:bpy.data.objects[side+'.'+k].location=p[side+'.'+k]
  delta=p[side+'.palm']-p[side+'.wrist'];o=bpy.data.objects[side+'.wrist_glove_bridge'];o.location=(p[side+'.wrist']+p[side+'.palm'])/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.scale=(.034,.037,.065)
  o=bpy.data.objects[side+'.fingers'];o.location=p[side+'.palm']+(p[side+'.grip']-p[side+'.palm'])*.75;o.rotation_euler=(p[side+'.grip']-p[side+'.wrist']).to_track_quat('Z','Y').to_euler();o.scale=(.034,.038,.055)
 d=[0,.18,.72,1,.82,.38,.06,0][i];axis=(p['neck']-p['pelvis']).normalized();front=V([0,-axis.z,axis.y]);back=-front
 head=bpy.data.objects['head'];head.location=p['head'];head.rotation_euler=(math.radians(5+45*d),0,0)
 pelvis=bpy.data.objects['pelvis'];pelvis.location=p['pelvis'];pelvis.scale=(.185,.135,.16)
 neck=bpy.data.objects['neck_skin_bridge'];a=p['chest'];b=p['neck']+axis*.07;neck.location=(a+b)/2;neck.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();neck.scale=(.072,.072,(b-a).length)
 vs=[]
 for center,rx,ry in [(p['pelvis'],.18,.13),(p['chest'],.20,.13)]:
  for k in range(8):a=2*math.pi*k/8;vs.append(center+V([math.cos(a)*rx,0,0])+front*math.sin(a)*ry)
 for vertex,pos in zip(bpy.data.objects['body_outfit'].data.vertices,vs):vertex.co=pos
 cv=[]
 for center,width in [(p['neck']+back*.20,.25),(p['pelvis']+axis*.32+back*.30,.27),(p['pelvis']+back*.40+V([0,.16,-.38]),.31)]:cv.extend([center+V([-width,0,0]),center,center+V([width,0,0])])
 for vertex,pos in zip(bpy.data.objects['cape'].data.vertices,cv):vertex.co=pos
 gem=bpy.data.objects['collectible'];gem.hide_render=not f['object_visible'];gem.location=V(f['object_center']);bpy.context.view_layer.update()
 measures={}
 for side,(o,mod) in skins.items():
  mod.use_deform_preserve_volume=False;bpy.context.view_layer.update();lbs=areas(o);mod.use_deform_preserve_volume=True;bpy.context.view_layer.update();dq=areas(o);measures[side]=dict(lbs_ring_area_ratios=[a/b for a,b in zip(lbs,baseline[side])],dq_ring_area_ratios=[a/b for a,b in zip(dq,baseline[side])],deformed_vertex_count=len(deformed(o)),base_vertex_count=len(o.data.vertices))
 images={}
 for view in s['cameras']:
  sc.camera=bpy.data.objects[view];folder=OUT/view;folder.mkdir(exist_ok=True);path=folder/f'{i:02}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);images[view]=dict(path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 records.append(dict(index=i,max_real_pose_bone_attachment_error=max(attachment),mesh_measurements=measures,views=images))
receipt=dict(kind='Actual continuous closed 3D arm meshes weighted to actual Blender armature, dual-quaternion preserve-volume enabled. Mannequin/source study, not final painted character.',source_sha256=hashlib.sha256((P/'source/source.json').read_bytes()).hexdigest(),source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),ring_count=RINGS,vertices_per_ring=N,frames=records,body_geometry_scope='Other mannequin body meshes reconstructed per key; only arms are actual weighted deforming meshes in saved blend. Saved body is terminal snapshot.',production_pass=False)
(OUT/'skin-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'continuous-arm-skin.blend'));print('ACTUAL_SKINNED_ARMS_RENDERED')
