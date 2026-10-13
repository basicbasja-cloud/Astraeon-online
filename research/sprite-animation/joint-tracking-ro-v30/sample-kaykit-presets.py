"""Blender: real current creator Free1.1 rig/preset samples, exact input times.
No retarget/painted art/contact inference; preserve native source bone names.
"""
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
import bpy
def matrix(m):return [list(row) for row in m]
p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);inventory=json.loads((a.study/'new-preset-inventory.json').read_text());banks=[]
for f in inventory['files']:
 source=Path(f['path'])
 if hashlib.sha256(source.read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Source changed')
 bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30
 bpy.ops.import_scene.gltf(filepath=str(source));rigs=[o for o in scene.objects if o.type=='ARMATURE']
 if len(rigs)!=1:raise ValueError('Expected1actualrig')
 rig=rigs[0]
 for track in rig.animation_data.nla_tracks:track.mute=True
 bones={b.name:{'parent':b.parent.name if b.parent else None,'rest_matrix':matrix(b.matrix_local)} for b in rig.data.bones};clips=[]
 for clip in f['clips']:
  actions=[ac for ac in bpy.data.actions if ac.name in (clip['name'],clip['name']+'_'+rig.name)]
  if len(actions)!=1:raise ValueError('Action binding ambiguity '+clip['name'])
  rig.animation_data.action=actions[0];times=clip['native_key_times_seconds'];samples=[]
  for i in sorted({round(n*(len(times)-1)/8) for n in range(9)}):
   t=times[i];frame=t*30;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();samples.append({'native_key_index':i,'source_time_seconds':t,'world_joints':{b.name:list(rig.matrix_world@b.head) for b in rig.pose.bones}})
  clips.append({'name':clip['name'],'samples':samples,'rest_pose_name_flag':clip['rest_pose'],'contact':'unknown','anatomy_or_acting_accepted':False})
 banks.append({'source_file':f['path'],'source_sha256':f['sha256'],'blender':bpy.app.version_string,'bones':bones,'clips':clips})
report={'schema':'current-kaykit-evaluated-presets-v1','banks':banks,'scope':'Actualexternalrigposes at9selectednativekeytimes; repeatednames/restclips remainexplicit, no source-to-our-character retarget or grip/sole verification.'}
with (a.study/'new-preset-samples.json.gz').open('wb') as stream:
 with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0) as zip:zip.write(json.dumps(report,separators=(',',':')).encode())
print('NEW_PRESETS_EVALUATED',len(banks),sum(len(b['clips']) for b in banks),sum(len(c['samples']) for b in banks for c in b['clips']))
