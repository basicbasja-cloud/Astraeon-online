"""Original 3D walk reference with two-bone IK and measured planted feet.

Authoring reference only: no runtime asset or town scene is replaced. The
render's fixed pelvis origin is retained; stance boots retract relative to it.
Aligning every pose to its lowest boot would erase that necessary travel.
"""
import bpy,math,json,argparse
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/gait-rig-v50';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='Standard';scene.render.fps=24
scene.world=bpy.data.worlds.new('Guide studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.70,.77,.87,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.85;return m
mats={k:material(k,c) for k,c in {'coat':(.12,.19,.23),'tunic':(.84,.77,.60),'cloak':(.87,.49,.08),'bronze':(.31,.18,.10),'left-guide':(.14,.34,.60),'right-guide':(.66,.20,.12),'silver':(.55,.59,.67),'skin':(.88,.67,.47),'gold':(.77,.51,.17)}.items()}
stride=.70;duty=.62;distance=stride/duty;length=.57
def pose(phase):
 lift=.015*math.cos(phase*math.tau*2);hipz=1.03+lift;result={'spine':((0,0,hipz),(0,0,1.66+lift)),'head':((0,0,1.66+lift),(0,0,2.0+lift))};feet={}
 for side,name in [(-1,'L'),(1,'R')]:
  q=(phase+(.5 if side==-1 else 0))%1;stance=q<duty;u=q/duty if stance else (q-duty)/(1-duty)
  y=stride/2-stride*u if stance else -stride/2+stride*(u*u*(3-2*u));z=.10+(0 if stance else .15*math.sin(u*math.pi))
  hip=Vector((side*.17,0,hipz));ankle=Vector((side*.17,y,z));delta=ankle-hip;dist=delta.length
  assert dist<2*length,(phase,name,dist)
  mid=(hip+ankle)/2;bend=Vector((0,-delta.z,delta.y)).normalized();knee=mid+bend*math.sqrt(length*length-dist*dist/4)
  result[name+'-thigh']=(hip,knee);result[name+'-shin']=(knee,ankle);result[name+'-boot']=(ankle,ankle+Vector((0,.23,0)))
  shift=-side*.15*math.cos(phase*math.tau);sh=Vector((side*.30,0,1.59+lift));el=Vector((side*.36,shift,1.28+lift));hand=Vector((side*.38,shift*1.3,1.06+lift))
  result[name+'-upper-arm']=(sh,el);result[name+'-forearm']=(el,hand)
  feet[name]={'stance':stance,'ankle':list(ankle),'rootLocalToe':list(ankle+Vector((0,.23,-.06))),'virtualRootY':phase*distance,'virtualToeY':phase*distance+y+.23}
 return result,feet
rest,_=pose(0);data=bpy.data.armatures.new('Walk IK guide');rig=bpy.data.objects.new('Walk IK guide',data);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name,(a,b) in rest.items():
 bone=data.edit_bones.new(name);bone.head=a;bone.tail=b
bpy.ops.object.mode_set(mode='OBJECT')
def bind(o,bone,mat):
 o.data.materials.append(mats[mat]);group=o.vertex_groups.new(name=bone);group.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Rigid articulated guide','ARMATURE');mod.object=rig
 return o
def box(name,center,size,bone,mat,bevel=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:m=o.modifiers.new('Soft edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return bind(o,bone,mat)
def limb(name,a,b,width,bone,mat):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,(b-a).length,width),bone,mat,.05);o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,1,0)).rotation_difference(b-a);return o
def ball(name,c,scale,bone,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=c);o=bpy.context.object;o.name=name;o.scale=scale;return bind(o,bone,mat)
box('Torso armor',(0,0,1.41),(.55,.34,.53),'spine','coat',.09)
box('Cream tabard',(0,.19,1.26),(.44,.08,.60),'spine','tunic',.04)
box('Belt',(0,0,1.13),(.61,.39,.11),'spine','bronze',.035)
ball('Head',(0,0,1.98),(.25,.21,.29),'head','skin');ball('Silver hair',(0,-.015,2.10),(.27,.23,.22),'head','silver')
for side in (-1,1):ball('Eye '+str(side),(side*.09,.198,2.01),(.038,.015,.043),'head','bronze')
for side,name in [(-1,'L'),(1,'R')]:
 color='left-guide' if name=='L' else 'right-guide'
 for suffix,w in [('thigh',.23),('shin',.20),('upper-arm',.19),('forearm',.16)]:
  a,b=rest[name+'-'+suffix];limb(name+' '+suffix,a,b,w,name+'-'+suffix,color if suffix in ('thigh','shin') else 'coat')
 a,b=rest[name+'-thigh'];ball(name+' knee',b,(.14,.14,.14),name+'-thigh',color)
 ankle,_=rest[name+'-boot'];box(name+' planted boot',Vector(ankle)+Vector((0,.08,-.035)),(.23,.39,.13),name+'-boot',color,.035)
 sh,_=rest[name+'-upper-arm'];ball(name+' shoulder',sh,(.18,.17,.14),name+'-upper-arm','gold')
 _,hand=rest[name+'-forearm'];ball(name+' hand',hand,(.10,.08,.12),name+'-forearm','skin')
# Quiet cape volume shows body orientation without hiding the guide legs.
box('Short reference cape',(0,-.24,1.41),(.69,.11,.61),'spine','cloak',.06)
records=[]
for frame in range(1,10):
 phase=(frame-1)/8;positions,feet=pose(phase%1)
 for name,(a,b) in positions.items():
  bone=rig.pose.bones[name];a,b=Vector(a),Vector(b);q=Vector((0,1,0)).rotation_difference(b-a);bone.rotation_mode='QUATERNION';bone.matrix=Matrix.Translation(a)@q.to_matrix().to_4x4();bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame)
  bpy.context.view_layer.update()
 records.append({'frame':frame,'phase':phase,'feet':feet})
scene.frame_start=1;scene.frame_end=8
bpy.ops.object.camera_add(location=(0,7,3.75));camera=bpy.context.object;camera.name='Fixed sprite guide camera';camera.rotation_euler=(Vector((0,0,1.13))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.30;scene.camera=camera
for name,position,power,size in [('Key',(-3,4,6),450,4),('Fill',(3,1,4),220,4)]:
 bpy.ops.object.light_add(type='AREA',location=position);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
scene['purpose']='Pose reference only; preserve original illustrated Warrior identity in final art';scene['cycle_distance']=distance;scene['duty']=duty;scene['leg_length']=length
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'walk-reference.blend'),compress=True)
# Validate actual evaluated rig ankle endpoints against each analytic target.
errors=[]
for record in records[:8]:
 scene.frame_set(record['frame']);bpy.context.view_layer.update()
 for name in ('L','R'):
  actual=rig.pose.bones[name+'-boot'].head;expected=Vector(record['feet'][name]['ankle']);error=(actual-expected).length;errors.append(error)
  assert error<1e-5,(record['frame'],name,tuple(actual),tuple(expected),error)
(OUT/'walk-reference.json').write_text(json.dumps({'referenceOnly':True,'units':'world-unit','cycleDistance':distance,'duty':duty,'legLength':length,'maxEvaluatedAnkleError':max(errors),'frames':records[:8]},indent=2)+'\n')
for frame in range(1,9):
 scene.frame_set(frame);scene.render.filepath=str(OUT/f'S-{frame:02d}.png');bpy.ops.render.render(write_still=True);print('Rendered controlled gait pose',frame,flush=True)
