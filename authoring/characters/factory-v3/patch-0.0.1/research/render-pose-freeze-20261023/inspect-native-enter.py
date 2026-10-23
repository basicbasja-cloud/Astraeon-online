import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path('authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb').resolve()));rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
for t in rig.animation_data.nla_tracks:t.mute=True

def pose(name,frame,carry=None):
 for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
 action=bpy.data.actions.get(name+'_'+rig.name);rig.animation_data.action=action
 if hasattr(rig.animation_data,'action_slot')and action.slots:rig.animation_data.action_slot=action.slots[0]
 bpy.context.scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update()
 if carry:
  for n,m in carry.items():rig.pose.bones[n].matrix_basis=m.copy()
  bpy.context.view_layer.update()
 return {n:(rig.matrix_world@rig.pose.bones[n].matrix).copy()for n in ['head','pelvis','hand_r','hand_l','foot_r','foot_l']}
pose('Idle_Lantern',0);prefixes=('upperarm_','lowerarm_','hand_','index_','middle_','ring_','pinky_','thumb_');carry={b.name:b.matrix_basis.copy()for b in rig.pose.bones if b.name.endswith('_r')and b.name.startswith(prefixes)}
shoot=pose('Spell_Simple_Shoot',0,carry);idle=pose('Idle_Lantern',0,carry);rows=[]
for name in ['Spell_Simple_Enter','Spell_Simple_Idle','Spell_Simple_Shoot','Spell_Simple_Exit']:
 action=bpy.data.actions.get(name+'_'+rig.name);print('MAGE_RANGE',name,list(action.frame_range),flush=True)
 if name!='Spell_Simple_Enter':continue
 for f in range(math.ceil(action.frame_range[1])+1):
  p=pose(name,f,carry);rows.append({'frame':f,'left_hand_to_shoot_m':(p['hand_l'].translation-shoot['hand_l'].translation).length,'max_landmark_to_shoot_m':max((p[n].translation-shoot[n].translation).length for n in p),'max_landmark_to_idle_m':max((p[n].translation-idle[n].translation).length for n in p)})
Path('/tmp/mage-enter-join-analysis.json').write_text(json.dumps(rows,indent=2));print('MAGE_ENTER_JOINS '+json.dumps(rows),flush=True)
