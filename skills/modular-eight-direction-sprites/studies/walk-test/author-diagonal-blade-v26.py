"""v26 stable two-foot slash. Reuses source-geometry/IK plumbing, not rejected v21/v23 acting.

Sparse authored exposures, dense fixed-length IK bake and one fixed camera.
Geometry/contact/socket evidence is source-only, not painted anatomy approval.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent.parent/'source-motion'))
from retarget_math import two_segment

TIMES=[0,100,180,230,280,360,460,560]
PHASES=['ready','windup','coil','cross-body-cut','follow-through','settle','recover','ready']
DURATION=680

def main():
 p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not a.out.exists()
 parent_hash=hashlib.sha256(a.blend.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(a.blend),use_scripts=False);s=bpy.context.scene;r=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot'];pivot.rotation_euler.z=0;bpy.context.view_layer.update()
 names=[b.name for b in r.data.bones];rest={n:r.data.bones[n].matrix_local.copy() for n in names};parents={n:r.data.bones[n].parent.name if r.data.bones[n].parent else None for n in names}
 r.animation_data_clear();a.out.mkdir(parents=True)
 # hand_r.head is the wrist joint, NOT the center of the modeled palm.
 # Resolve the actual complete one-bone glove geometry before attaching a hilt.
 glove=bpy.data.objects['glove.right.palm'];assert {g.name for g in glove.vertex_groups}=={'hand_r'}
 palm_rest=sum((r.matrix_world.inverted()@glove.matrix_world@v.co for v in glove.data.vertices),Vector())/len(glove.data.vertices)
 palm_local=rest['hand_r'].inverted()@palm_rest
 def lerp(values,t):
  i=max(k for k,v in enumerate(TIMES) if t>=v)
  if i==7:return values[i]
  u=(t-TIMES[i])/(TIMES[i+1]-TIMES[i]);u=u*u*(3-2*u)
  if isinstance(values[i],list):return [x+(y-x)*u for x,y in zip(values[i],values[i+1])]
  return values[i]+(values[i+1]-values[i])*u
 def mat(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);o=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
 steel=mat('v26.blade',(.64,.72,.80));gold=mat('v26.guard',(.72,.39,.12));brown=mat('v26.handle',(.10,.045,.023))
 def weapon(name,verts,faces,material):
  mesh=bpy.data.meshes.new(name);mesh.from_pydata([rest['hand_r']@(Vector(v)+palm_local) for v in verts],[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);s.collection.objects.link(obj);obj.parent=r;obj.data.materials.append(material);obj['slot']='weapon.sword.right';obj['anatomical_owner']='right';g=obj.vertex_groups.new(name='hand_r');g.add(list(range(len(verts))),1,'REPLACE');mod=obj.modifiers.new('Right grip rig','ARMATURE');mod.object=r;return obj
 # Local +Y is the blade axis. The hilt passes through the actual palm center.
 weapon('v26.sword.blade',[(-.025,.070,0),(.025,.070,0),(.020,.49,0),(0,.59,0),(-.020,.49,0),(0,.070,.010),(0,.49,.008)],[(0,1,5),(1,2,6,5),(2,3,6),(3,4,6),(4,0,5,6)],steel)
 def box(name,c,z,m):
  verts=[(c[0]+x*z[0]/2,c[1]+y*z[1]/2,c[2]+v*z[2]/2) for x,y,v in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
  return weapon(name,verts,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m)
 box('v26.sword.guard',(0,.060,0),(.13,.018,.026),gold);box('v26.sword.handle',(0,0,0),(.022,.108,.022),brown);box('v26.sword.pommel',(0,-.068,0),(.035,.020,.030),gold)
 soles={}
 for side,suf,x,y in [('right','r',-.085,.085),('left','l',.085,-.075)]:
  ft='foot_'+suf;delta=Matrix.Translation(Vector((x,y,rest[ft].translation.z))-rest[ft].translation);verts=[]
  for part in ['heel','toe']:
   obj=bpy.data.objects[f'sole.{side}.{part}'];verts.extend(delta@obj.matrix_world@v.co for v in obj.data.vertices)
  delta.translation.z+=.001-min(v.z for v in verts);soles[side]=delta
 max_length=0;dense=[]
 def pose(t,bake=False):
  nonlocal max_length
  hip=Vector(lerp([[0,.010,.570],[0,.018,.568],[0,.025,.566],[0,.000,.563],[0,-.018,.560],[0,-.008,.564],[0,.005,.568],[0,.010,.570]],t))
  pelvis_yaw=math.radians(lerp([0,-6,-10,2,15,13,5,0],t));chest_yaw=math.radians(lerp([0,-13,-23,7,30,24,9,0],t));lean=math.radians(lerp([0,-1,-2,2,3,2,1,0],t))
  desired={};body=Matrix.Translation(hip)@Matrix.Rotation(chest_yaw,4,'Z')@Matrix.Rotation(lean,4,'X')@Matrix.Translation(-rest['pelvis'].translation)
  pelvis=Matrix.Translation(hip)@Matrix.Rotation(pelvis_yaw,4,'Z')@Matrix.Translation(-rest['pelvis'].translation)
  for n in names:desired[n]=body@rest[n]
  desired['root']=Matrix.Identity(4);desired['pelvis']=pelvis@rest['pelvis']
  # Keep head yaw in the facing basis while chest counterrotates.
  head=Matrix.Rotation(lean*.4,4,'X')@rest['Head'];head.translation=desired['Head'].translation
  head_delta=head@rest['Head'].inverted();desired['Head']=head
  for n in names:
   if 'Head' in [b.name for b in r.data.bones[n].parent_recursive]:desired[n]=head_delta@rest[n]
  for side,suf in [('right','r'),('left','l')]:
   ft='foot_'+suf
   for n in names:
    if n==ft or ft in [b.name for b in r.data.bones[n].parent_recursive]:desired[n]=soles[side]@rest[n]
   desired['thigh_'+suf]=pelvis@rest['thigh_'+suf]
   targets={'r':lerp([[-.18,-.10,.73],[-.23,-.015,.95],[-.22,.00,1.05],[-.105,-.14,.95],[.115,-.20,.76],[.145,-.14,.70],[-.05,-.13,.74],[-.18,-.10,.73]],t),
            'l':lerp([[.20,-.045,.73],[.21,-.075,.75],[.21,-.12,.78],[.20,.02,.78],[.21,.065,.76],[.20,.035,.74],[.20,-.025,.73],[.20,-.045,.73]],t)}
   for upper,lower,end,target,pole in [('thigh_'+suf,'calf_'+suf,ft,desired[ft].translation,Vector((0,-.30,-.2))),('upperarm_'+suf,'lowerarm_'+suf,'hand_'+suf,Vector(targets[suf]),Vector((-.20 if suf=='r' else .20,-.20,-.05)))]:
    start=desired[upper].translation.copy();l1=(rest[lower].translation-rest[upper].translation).length;l2=(rest[end].translation-rest[lower].translation).length;answer=two_segment(start,start+pole,target,l1,l2)
    if not answer['reachable']:raise ValueError(f'Unreachable {t} {upper}: {answer["reach_distance"]}, {l1+l2}')
    middle=Vector(answer['middle'].tolist())
    for b,c,base,tip in [(upper,lower,start,middle),(lower,end,middle,target)]:
     rot=(rest[c].translation-rest[b].translation).rotation_difference(tip-base).to_matrix()@rest[b].to_3x3();desired[b]=rot.to_4x4();desired[b].translation=base
    max_length=max(max_length,abs((middle-start).length-l1),abs((target-middle).length-l2))
   hand='hand_'+suf
   if suf=='r':
    # One world-facing swing plane: diagonal X/Z and forward Y.
    # The cutting edge lies in this plane; its normal is held constant.
    u=Vector((-.5,0,.8660254)).normalized();v=Vector((0,-1,0));normal=u.cross(v).normalized()
    theta=math.radians(lerp([145,15,20,75,125,150,135,145],t))
    axis=u*math.cos(theta)+v*math.sin(theta)
    desired[hand]=Matrix((axis.cross(normal),axis,normal)).transposed().to_4x4()
   else:
    axis=Vector((0,-.3,-.95)).normalized();desired[hand]=axis.to_track_quat('Y','Z').to_matrix().to_4x4()
   desired[hand].translation=Vector(targets[suf]);hd=desired[hand]@rest[hand].inverted()
   for n in names:
    if hand in [b.name for b in r.data.bones[n].parent_recursive]:desired[n]=hd@rest[n]
  for n in names:
   bone=r.data.bones[n];kw={'parent_matrix':desired[parents[n]],'parent_matrix_local':bone.parent.matrix_local} if parents[n] else {};pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix_basis=bone.convert_local_to_pose(desired[n],bone.matrix_local,invert=True,**kw)
   if bake:
    for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=t)
  bpy.context.view_layer.update()
  return {'time_ms':t,'hip':list(hip),'pelvis_yaw':pelvis_yaw,'chest_yaw':chest_yaw,'lean':lean,'right_wrist_joint':list(r.pose.bones['hand_r'].head),'right_grip':list(desired['hand_r']@palm_local),'left_hand':list(r.pose.bones['hand_l'].head),'blade_tip':list(desired['hand_r']@(palm_local+Vector((0,.59,0)))),'root':[0,0,0]}
 for t in range(0,DURATION+1,5):dense.append(pose(t,True))
 r.animation_data.action.name='original.diagonal.blade.slash.v26'
 for c in r.animation_data.action.fcurves:
  for k in c.keyframe_points:k.interpolation='LINEAR'
 s.frame_start=0;s.frame_end=DURATION;s.render.fps=1000;s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.device='CPU';s.use_nodes=False
 s.camera.data.ortho_scale=1.98
 # A single capture camera for every phase; includes raised blade with margin.
 s.camera.location=(0,-4*math.cos(math.pi/6),.65+4*math.sin(math.pi/6));s.camera.rotation_euler=(Vector((0,0,.65))-s.camera.location).to_track_quat('-Z','Y').to_euler()
 for o in s.objects:
  if o.type=='MESH':o.hide_render=o.get('slot') in ['hair.auburn','weapon.sword.right']
 pose(0);bpy.ops.wm.save_as_mainfile(filepath=str(a.out/'diagonal-blade-slash.blend'),compress=True)
 def xy(v):q=world_to_camera_view(s,s.camera,v);return [q.x*512,(1-q.y)*512]
 records=[];source_sole_min=1;plant={}
 for view,d in [('SE',1)]:
  pivot.rotation_euler.z=d*math.pi/4
  for i,t in enumerate(TIMES):
   s.frame_set(t);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rec={'view':view,'key':i,'time_ms':t,'phase':PHASES[i],'duration_ms':(TIMES[i+1] if i<7 else DURATION)-t,'root_xy':xy(Vector((0,0,0))),'bones':{b.name:{'xy':xy(r.matrix_world@b.head),'world':list(r.matrix_world@b.head)} for b in r.pose.bones},'soles':{},'right_grip_xy':xy(r.matrix_world@r.pose.bones['hand_r'].matrix@palm_local),'blade_tip_xy':xy(r.matrix_world@r.pose.bones['hand_r'].matrix@(palm_local+Vector((0,.59,0)))), 'hand_matrix_world':[list(row) for row in r.matrix_world@r.pose.bones['hand_r'].matrix]}
   for side in ['right','left']:
    for part in ['heel','toe']:
     o=bpy.data.objects[f'sole.{side}.{part}'].evaluated_get(deps);mesh=o.to_mesh()
     try:
      vertices=[o.matrix_world@v.co for v in mesh.vertices];low=min(vertices,key=lambda v:v.z);source_sole_min=min(source_sole_min,low.z);rec['soles'][side+'.'+part]={'minimum_mesh_z':low.z,'lowest_xy':xy(low),'world_vertex':list(vertices[0])}
     finally:o.to_mesh_clear()
   path=a.out/view/f'{i:02}.png';path.parent.mkdir(exist_ok=True);s.render.filepath=str(path.resolve());bpy.ops.render.render(write_still=True);rec['image']=str(path);rec['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();records.append(rec)
   guide=a.out/'grip-guide'/f'{i:02}.png';guide.parent.mkdir(exist_ok=True)
   for o in s.objects:
    if o.get('slot')=='weapon.sword.right':o.hide_render=False
   s.render.filepath=str(guide.resolve());bpy.ops.render.render(write_still=True)
   for o in s.objects:
    if o.get('slot')=='weapon.sword.right':o.hide_render=True
  for name in records[-1]['soles']:
   pts=[Vector(v['soles'][name]['world_vertex']) for v in records[-8:]];plant[view+'.'+name]=max((v-pts[0]).length for v in pts)
 if source_sole_min<-.002 or max_length>1e-5 or max(plant.values())>1e-5:raise ValueError('Source length/floor/plant checks failed')
 report={'schema':'diagonal-blade-slash-v26','parent_walk_blend':str(a.blend),'parent_walk_sha256':parent_hash,'blend':str(a.out/'diagonal-blade-slash.blend'),'blend_sha256':hashlib.sha256((a.out/'diagonal-blade-slash.blend').read_bytes()).hexdigest(),'palm_geometry_object':glove.name,'palm_geometry_local_in_hand':list(palm_local),'socket_is_wrist_joint':False,'finger_wrap_verified':False,'camera_matrix_world':[list(row) for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale,'records':records,'dense_bake':dense,'max_length_error_world':max_length,'minimum_source_sole_z':source_sole_min,'maximum_source_plant_drift_world':max(plant.values()),'weapon_owner':'anatomical_right','duration_ms':DURATION,'loop':False,'rendered_weapon':False,'swing_plane_normal_facing_local':list(Vector((-.5,0,.8660254)).normalized().cross(Vector((0,-1,0))).normalized()),'blade_key_angles_degrees':[145,15,20,75,125,150,135,145],'stance':'both modeled soles fixed; no suspended rear leg','source_acting_approved':False,'painted_contacts_verified':False,'scope':'Fresh authored source-only fixed-length/contact/palm-socket proof, not force simulation or painted finger/hand/anatomy acceptance.'}
 (a.out/'source-index.json').write_text(json.dumps(report,indent=2)+'\n');assert hashlib.sha256(a.blend.read_bytes()).hexdigest()==parent_hash;print('SWORD_SOURCE_OK',max_length,source_sole_min,max(plant.values()))

if __name__=='__main__':main()
