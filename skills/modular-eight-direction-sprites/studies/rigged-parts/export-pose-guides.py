"""Project the reopened baked skeleton, not a guessed skeleton from artwork."""
import bpy,json,math,os
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('SPRITE_OUTPUT_ROOT',str(HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'))).resolve()
bpy.ops.wm.open_mainfile(filepath=str(OUT/'silver-scarf-modular-source.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['SilverScarfRig'];camera=scene.camera
source=json.loads((OUT/'rig-poses.json').read_text());manifest=json.loads((OUT/'rig-manifest.json').read_text())
def point(v):
 p=world_to_camera_view(scene,camera,v);return [p.x*128,(1-p.y)*128]
def world(v):return rig.matrix_world@Vector((v[0],-v[1],v[2]))
def head(name):return rig.matrix_world@rig.pose.bones[name].matrix.translation
poses=[];length_errors=[];grip_errors=[]
for d,direction in enumerate(manifest['directions']):
 rig.rotation_euler=(0,0,d*math.pi/4)
 for index,(key,ms) in enumerate(zip(source['keys'],source['times_ms'])):
  scene.frame_set(ms+1);bpy.context.view_layer.update()
  joints={'root':head('root'),'pelvis':head('pelvis'),'chest':head('chest'),'head':head('head')}
  for side in ['right','left']:
   names={'shoulder':'upperarm','elbow':'forearm','wrist':'hand','hip':'thigh','knee':'shin','ankle':'foot'}
   for joint,bone in names.items():joints[side+'.'+joint]=head(side+'.'+bone)
   for end in ['toe','heel']:joints[side+'.'+end]=world(key['feet'][side][end])
   for a,b,length in [('shoulder','elbow',.31),('elbow','wrist',.31),('hip','knee',.34),('knee','ankle',.34)]:
    length_errors.append(abs((joints[side+'.'+a]-joints[side+'.'+b]).length-length))
  joints['grip']=head('weapon.right');joints['blade_tip']=world(key['swordTip'])
  pixels={name:point(v) for name,v in joints.items()}
  grip_errors.append(math.dist(pixels['right.wrist'],pixels['grip']))
  basis=rig.matrix_world@rig.pose.bones['right.hand'].matrix
  # Source hand frame axes are orientation aids, not validated finger anatomy.
  axes={axis:point(basis@Vector(offset)) for axis,offset in [('x',[.09,0,0]),('y',[0,.09,0]),('z',[0,0,.09])]}
  poses.append({'direction':direction,'index':index,'time_ms':ms,'duration_ms':key['duration_ms'],'phase':key['phase'],
   'joints_native_px':pixels,'world_joints':{name:list(v) for name,v in joints.items()},'right_hand_axes_px':axes,
   'contacts':{side:key['feet'][side]['contact'] for side in ['right','left']},'weapon_owner':'anatomical_right',
   'joint_visibility':'Not inferred: skeleton guides include occluded joints. Toe/heel targets come from analytic pose source; other joints from reopened baked rig.'})
report={'schema':'modular-anatomical-pose-guide-v1','native_canvas':[128,128],'source':'Reopened original .blend action; no image-pose detector or third-party skeleton',
 'camera':'Same fixed export camera and facing transform','anatomical_colors':{'right':'blue','left':'orange','torso':'white','weapon':'yellow','contacts':'green'},
 'poses':poses,'checks':{'right_grip_max_error_px':max(grip_errors),'bone_lengths_max_error_world':max(length_errors)},
 'limits':['Not art or motion approval','Rig hand-frame axes do not validate finger curl or palm-to-hilt surface contact','No walk clip in this adapter','Hidden joints are source-known, not visible-image observations']}
assert report['checks']['right_grip_max_error_px']<1e-3
assert report['checks']['bone_lengths_max_error_world']<1e-5
(OUT/'pose-guides.json').write_text(json.dumps(report,indent=2)+'\n')
print('PROJECTED_GUIDES_PASS',len(poses),report['checks'])
