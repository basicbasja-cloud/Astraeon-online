"""Resample CC0 donor clips to ASTRAEON timing without importing donor geometry.

Only rest matrices and sampled skeleton transforms leave this isolated scene.
The source clips are named explicitly; action durations remain the game contract.
"""
import bpy, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01'
DATA=ROOT/'.character-tools/free-assets/quaternius-motions'
catalog=json.loads((DATA/'rig-catalog.json').read_text())
clips=json.loads((OUT/'clips.json').read_text())['clips']
mapping={'Idle':(0,['Idle_Loop']), 'Walk':(0,['Walk_Loop']), 'Run':(0,['Jog_Fwd_Loop']),
         'Sprint':(0,['Sprint_Loop']), 'BasicAttack':(0,['Sword_Attack']),
         'SkillAction':(1,['Sword_Regular_B','Sword_Regular_B_Rec']),
         'CastChannel':(0,['Spell_Simple_Idle_Loop']), 'CastRelease':(0,['Spell_Simple_Shoot']),
         'Guard':(1,['Sword_Block']), 'Dash':(1,['Sword_Dash']), 'Hit':(0,['Hit_Chest']),
         'Death':(0,['Death01']), 'Interact':(0,['Interact']), 'Pickup':(1,['Farm_Harvest']),
         'ItemUse':(1,['Consume']), 'Sit':(0,['Sitting_Idle_Loop']), 'Respawn':(1,['LayToIdle'])}
bones=['root','pelvis','spine_01','spine_02','spine_03','neck_01','Head',
       'clavicle_r','upperarm_r','lowerarm_r','hand_r','clavicle_l','upperarm_l','lowerarm_l','hand_l',
       'thigh_r','calf_r','foot_r','ball_r','thigh_l','calf_l','foot_l','ball_l']
records={}
for packid,pack in enumerate(catalog):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/pack['path']))
    rig=bpy.data.objects[pack['rig']];rig.animation_data_create()
    for clip in clips:
        name=clip['name'];pid,actions=mapping[name]
        if pid!=packid:continue
        spans=[float(bpy.data.actions[a].frame_range[1]-bpy.data.actions[a].frame_range[0]) for a in actions]
        total=sum(spans);frames=[]
        for f in range(clip['frames']+(1 if clip['loop'] else 0)):
            t=f/clip['frames'] if clip['loop'] else f/(clip['frames']-1)
            # Guard holds the actual blocked pose rather than repeatedly entering/exiting.
            sample_t=.38+.08*math.sin(math.tau*t) if name=='Guard' else t
            if clip['loop'] and f==clip['frames']:sample_t=0 if name!='Guard' else .38
            pos=min(total,max(0,sample_t*total));selected=len(actions)-1
            for i,length in enumerate(spans):
                if pos<=length:selected=i;break
                pos-=length
            a=bpy.data.actions[actions[selected]];rig.animation_data.action=a
            rig.animation_data.action_slot=a.slots[0]
            frame=float(a.frame_range[0])+pos;bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame))
            bpy.context.view_layer.update()
            frames.append({'t':t,'sourceAction':actions[selected],'sourceFrame':frame,
                           'bones':{n:{'matrix':[list(row) for row in rig.pose.bones[n].matrix],
                                       'head':list(rig.pose.bones[n].head),'tail':list(rig.pose.bones[n].tail)} for n in bones}})
        records[name]={'pack':pack['pack'],'file':pack['path'],'fileSHA256':hashlib.sha256((ROOT/pack['path']).read_bytes()).hexdigest(),
                       'sourceActions':actions,'rest':{n:pack['bones'][n] for n in bones},'frames':frames,
                       'sourceDurationSeconds':total/pack['fps'],'targetDurationMs':sum(clip['durationsMs'])}
        print('FREE_MOTION_SAMPLED '+name,flush=True)
path=OUT/'factory/free-motion-samples.json'
path.write_text(json.dumps({'kind':'CC0 donor skeleton samples','clips':records,'noDonorMeshes':True},separators=(',',':'))+'\n')
