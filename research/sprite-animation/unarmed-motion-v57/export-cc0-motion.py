"""Fresh actual CC0 source evaluations. Never reuse older authored attack motion."""
from pathlib import Path
import bpy,json,math,hashlib
P=Path(__file__).resolve().parent;library=P.parent/'joint-tracking-ro-v30/preset-source';out=P/'source';out.mkdir(exist_ok=True);names=['hips','spine','chest','head']+[n+'.'+s for s in ['l','r'] for n in ['upperarm','lowerarm','hand','upperleg','lowerleg','foot','toes']];sources=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(file):
 p=library/file;bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(rigs)==1;rig=rigs[0]
 for track in rig.animation_data.nla_tracks:track.mute=True
 sources.append({'path':str(p.relative_to(P.parent)),'sha256':sha(p)});return rig
def action(rig,name):
 actions=[a for a in bpy.data.actions if a.name in [name,name+'_'+rig.name]];assert len(actions)==1,(name,[a.name for a in bpy.data.actions]);rig.animation_data.action=actions[0]
def sample(rig,time):
 scene=bpy.context.scene;scene.render.fps=30;frame=time*30;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();bones={}
 for n in names:
  b=rig.pose.bones[n];mat=rig.matrix_world@b.matrix;q=mat.to_quaternion();bones[n]={'head':list(rig.matrix_world@b.head),'tail':list(rig.matrix_world@b.tail),'rotation_wxyz':list(q)}
 return {'source_time_seconds':time,'bones':bones}
rig=load('Rig_Medium_General.glb');action(rig,'Idle_A');neutral=sample(rig,0)
rig=load('Rig_Medium_CombatMelee.glb');clips={}
for name,duration in [('Melee_Unarmed_Idle',32/30),('Melee_Unarmed_Attack_Punch_A',35/30)]:
 action(rig,name);frames=[sample(rig,duration*i/256) for i in range(257)];clips[name]={'duration_seconds':duration,'sampling':'257 actual Blender evaluations including original endpoints; not new source drawings or modified native timing','frames':frames}
license=library/'KayKit-License.txt';(out/'KayKit-License.txt').write_bytes(license.read_bytes());data={'creator':'Kay Lousberg','creator_url':'https://kaylousberg.com/game-assets/character-animations','original_acquisition':'../joint-tracking-ro-v30/kaykit-acquisition.json','license':'CC0','license_sha256':sha(license),'files':sources,'blender':bpy.app.version_string,'neutral_general_idle_clip':'Idle_A','neutral_general_idle':neutral,'clips':clips,'scope':'Fresh actual external unarmed source poses and rest calibration only. Not original painted anatomy, completed retargeting or game integration.'};(out/'cc0-motion.json').write_text(json.dumps(data,separators=(',',':'))+'\n');print('EXTERNAL_UNARMED_SOURCE',len(clips),sum(len(c['frames']) for c in clips.values()))
