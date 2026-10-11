"""Blender: sample explicitly chosen source clips at their real glTF input times.

No retarget, generated pose, or approved game art. Retain root-world travel.
Set scene FPS before import so glTF seconds are not mistaken for Blender frames.
"""
import argparse,hashlib,json,math,struct,sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=False)
blob=a.source.read_bytes();size,_=struct.unpack_from('<II',blob,12);gltf=json.loads(blob[20:20+size]);base=20+size;n,_=struct.unpack_from('<II',blob,base);binary=blob[base+8:base+8+n]
def times(anim):
    values=set()
    for sampler in anim['samplers']:
        ac=gltf['accessors'][sampler['input']];view=gltf['bufferViews'][ac['bufferView']]
        if ac['componentType']!=5126 or ac['type']!='SCALAR' or view.get('byteStride') or ac.get('sparse'):raise ValueError('Unsupported source time accessor')
        start=view.get('byteOffset',0)+ac.get('byteOffset',0)
        values.update(struct.unpack_from('<'+'f'*ac['count'],binary,start))
    return sorted(values)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
bpy.ops.import_scene.gltf(filepath=str(a.source))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
for track in rig.animation_data.nla_tracks:track.mute=True
names={'root':'root','pelvis':'pelvis','spine.low':'spine_01','spine.mid':'spine_02','chest':'spine_03','neck':'neck_01','head':'Head'}
for side,s in [('right','r'),('left','l')]:
    for joint,bone in [('clavicle','clavicle'),('shoulder','upperarm'),('elbow','lowerarm'),('wrist','hand'),('hip','thigh'),('knee','calf'),('ankle','foot'),('ball','ball'),('toe','ball_leaf')]:names[side+'.'+joint]=bone+'_'+s
    for finger in ['thumb','index','middle','ring','pinky']:
        for j in range(1,5):names[f'{side}.{finger}.{j}']=f'{finger}_{j:02}'+('_leaf' if j==4 else '')+'_'+s
missing=[v for v in names.values() if v not in rig.pose.bones]
if missing:raise ValueError('Missing source bones: '+str(missing))
clips=[]
for wanted in ['Walk_Loop','Sword_Attack']:
    animation=next(x for x in gltf['animations'] if x['name']==wanted);input_times=times(animation)
    action=bpy.data.actions.get(wanted+'_Armature')
    if action is None:raise ValueError('Imported action name not found')
    if abs(action.frame_range[1]-input_times[-1]*30)>1e-3:raise ValueError('Import frame range does not match glTF seconds at configured FPS')
    rig.animation_data.action=action;frames=[]
    for i,t in enumerate(input_times):
        position=t*30;scene.frame_set(math.floor(position),subframe=position-math.floor(position));bpy.context.view_layer.update()
        world={k:list(rig.matrix_world@rig.pose.bones[v].head) for k,v in names.items()};root=world['root']
        relative={k:[v[j]-root[j] for j in range(3)] for k,v in world.items()}
        frames.append({'source_index':i,'time_seconds':t,'duration_seconds':input_times[i+1]-t if i+1<len(input_times) else None,
                       'world_joints':world,'root_relative_joints':relative,'root_world':root})
    clips.append({'name':wanted,'duration_seconds':input_times[-1]-input_times[0],'source_sample_count':len(frames),
                  'source_input_times':input_times,'source_frame_range':list(action.frame_range),'frames':frames,
                  'last_sample':'Endpoint pose; no invented playback hold'})
report={'schema':'source-rig-motion-study-v1','source_filename':a.source.name,'source_sha256':hashlib.sha256(blob).hexdigest(),
        'source':'Quaternius Universal Animation Library Standard, direct author free download, 2026-10-11',
        'source_bone_mapping':names,'source_bone_count':len(rig.data.bones),'blender':bpy.app.version_string,'scene_fps_before_import':30,
        'coordinate_basis':'Blender import world X/right, Y/back, Z/up; anatomical labels from named source hierarchy',
        'clips':clips,'scope':'External motion/rig study only; not retargeted to original proportions, no weapon mesh or certified grip/contact geometry',
        'registration':'World joints/root preserved. Root-relative joint guides explicitly subtract measured source root, not per-frame image bbox or pelvis.'}
(a.output/'source-motion.json').write_text(json.dumps(report,indent=2)+'\n')
print('SOURCE_SAMPLED',[(x['name'],x['source_sample_count'],x['duration_seconds']) for x in clips])
