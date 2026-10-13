"""Blender: evaluate NEW external source rigs, never an old own attack rig.
Nine real native key times per included motion action; key selections are overview
samples, not optimal sprite keys, container exposures or verified contacts.
"""
import argparse,gzip,hashlib,json,math,sys
from pathlib import Path
import bpy
def matrix(value):return [list(row) for row in value]
p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
inventory=json.loads((a.study/'clip-inventory.json').read_text());outputs=[]
for f in inventory['files']:
 source=a.study/f['path']
 if hashlib.sha256(source.read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Source changed')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1
 bpy.ops.import_scene.gltf(filepath=str(source))
 rigs=[o for o in scene.objects if o.type=='ARMATURE']
 if len(rigs)!=1:raise ValueError('Expected one rig')
 rig=rigs[0]
 for t in rig.animation_data.nla_tracks:t.mute=True
 bone_names=list(rig.data.bones.keys())
 clips=[]
 for clip in f['clips']:
  if clip['exclusion']:continue
  actions=[x for x in bpy.data.actions if x.name in (clip['name'],clip['name']+'_'+rig.name)]
  if len(actions)!=1:raise ValueError('Ambiguous source action '+clip['name']+': '+str([x.name for x in actions]))
  action=actions[0]
  if abs(action.frame_range[-1]-clip['end_seconds']*30)>.001:raise ValueError('Native endpoint/import mismatch')
  rig.animation_data.action=action;ts=clip['native_key_times_seconds']
  indices=sorted({round(i*(len(ts)-1)/8) for i in range(9)})
  samples=[]
  for i in indices:
   t=ts[i];frame=t*30;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
   samples.append({'native_key_index':i,'source_time_seconds':t,'object_world_matrix':matrix(rig.matrix_world),'world_joints':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in bone_names},'world_bone_matrices':{n:matrix(rig.matrix_world@rig.pose.bones[n].matrix) for n in bone_names},'parent_local_bone_matrices':{n:matrix(rig.pose.bones[n].parent.matrix.inverted()@rig.pose.bones[n].matrix if rig.pose.bones[n].parent else rig.pose.bones[n].matrix) for n in bone_names}})
  clips.append({'name':clip['name'],'action_name':action.name,'duration_seconds':clip['duration_seconds'],'samples':samples,'contact_semantics':'unknown'})
 outputs.append({'source_id':f['source_id'],'source_sha256':f['sha256'],'source_file':f['path'],'bones':{n:{'parent':rig.data.bones[n].parent.name if rig.data.bones[n].parent else None,'armature_rest_matrix':matrix(rig.data.bones[n].matrix_local),'parent_local_rest_matrix':matrix(rig.data.bones[n].parent.matrix_local.inverted()@rig.data.bones[n].matrix_local if rig.data.bones[n].parent else rig.data.bones[n].matrix_local)} for n in bone_names},'clips':clips,'blender':bpy.app.version_string,'fps_set_before_import':30})
report={'schema':'new-external-preset-samples-v1','files':outputs,'scope':'Actual source evaluations at selected native key times; no target retarget, no old own rig or attacks, no reconstructed contact labels, no production approval.'}
out=a.study/'preset-samples.json.gz'
with out.open('wb') as stream:
 with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0) as zipped:zipped.write(json.dumps(report,separators=(',',':')).encode())
print('NEW_SOURCE_SAMPLES',[(f['source_id'],len(f['clips']),len(f['bones'])) for f in outputs])
