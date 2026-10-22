"""Actual Blender regression for the retained CC0 bow donor and human rig."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from kaykit_motion_adapter import KayKitMotionAdapter

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'authoring/characters/factory-v3/motions/raw/kaykit-cc0/Rig_Medium_CombatRanged.glb'))
source=next(o for o in bpy.data.objects if o.type=='ARMATURE');old=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb'))
target=next(o for o in bpy.data.objects if o not in old and o.type=='ARMATURE');target_world=target.matrix_world.copy()
for actor in [source,target]:
    for track in actor.animation_data.nla_tracks:track.mute=True

def select(name,frame):
    chosen=bpy.data.actions.get(name+'_'+source.name)
    if chosen is None:raise AssertionError('Missing source action '+name)
    for bone in source.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    source.animation_data.action=chosen
    if hasattr(source.animation_data,'action_slot')and chosen.slots:source.animation_data.action_slot=chosen.slots[0]
    bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()

def toe_error():
    return max(abs((target.matrix_world@target.pose.bones['ball_'+s].head).z-(source.matrix_world@source.pose.bones['toes.'+s].head).z)for s in ['l','r'])

baseline=KayKitMotionAdapter(source,target);select('Ranged_Bow_Draw',32);baseline.apply();baseline_error=toe_error()
assert baseline_error>.08,('Expected retained donor to reproduce the old rear-toe defect',baseline_error)
target.matrix_world=target_world;adapter=KayKitMotionAdapter(source,target,archery_contact='cheek-anchor-arm-IK-floor-elbow-v3')
assert all(adapter.left_grip[f'index_0{i}_l'].to_quaternion().angle>.2 for i in [1,2,3]),'Left native grip is not closed'
assert all(adapter.right_string_grip[f'{finger}_01_r'].to_quaternion().angle>.2 for finger in ['index','middle','ring']),'Right hook grip reference is missing'
records=[]
for name,frames in [('Ranged_Bow_Idle',[0]),('Ranged_Bow_Aiming_Idle',[0,22,44]),('Ranged_Bow_Draw',[8,12.363636,16.727273,21.090909,25.454545,29.818182,32]),('Ranged_Bow_Release',[0,2.909091,8.727273,14.545455,20.363636,26.181818,32])]:
    for frame in frames:
        select(name,frame);adapter.apply();error=toe_error()
        assert error<1e-4,(name,frame,'toe contact error',error)
        assert all(math.isfinite(v)for bone in target.pose.bones for row in bone.matrix for v in row),'Nonfinite pose matrix'
        if name in ['Ranged_Bow_Draw','Ranged_Bow_Aiming_Idle']:
            assert all(target.pose.bones[f'{finger}_01_r'].rotation_quaternion.angle>.2 for finger in ['index','middle','ring']),'Draw fingers opened unexpectedly'
        elif name=='Ranged_Bow_Release':
            assert all(target.pose.bones[f'{finger}_01_r'].rotation_quaternion.angle<1e-4 for finger in ['index','middle','ring']),'Release fingers retained draw pose'
        if name=='Ranged_Bow_Idle' or(name=='Ranged_Bow_Release'and frame==32):assert 'l'not in adapter.contact_diagnostics and'r'not in adapter.contact_diagnostics,'Stale arm diagnostics leaked across poses'
        records.append({'action':name,'frame':frame,'toe_error_m':error})

def points():return {name:list(target.matrix_world@target.pose.bones[name].head)for name in ['head','pelvis','hand_l','hand_r','foot_l','foot_r']}
select('Ranged_Bow_Idle',0);adapter.apply();start=points();select('Ranged_Bow_Release',32);adapter.apply();end=points();seam=max(math.dist(start[n],end[n])for n in start)
assert seam<1e-4,('Ready/recovery seam',seam)
print('ARCHER_CONTACT_REGRESSION '+json.dumps({'status':'PASS','sampled_poses':len(records),'old_retarget_max_toe_error_m':baseline_error,'corrected_max_toe_error_m':max(r['toe_error_m']for r in records),'ready_recovery_seam_m':seam,'grip_states_checked':True,'finite_matrices_checked':True,'stale_diagnostics_checked':True,'records':records}),flush=True)
