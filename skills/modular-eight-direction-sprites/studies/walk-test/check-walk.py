"""Reopen actual .blend, evaluate saved walk and inspect actual modeled sole patches."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.output.exists():raise ValueError('Use a new check report')
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;rig=bpy.data.objects['original.walk.rig'];meta=json.loads((a.blend.parent/'motion.json').read_text())
max_pose=0;frames=[];length_ranges={};patches={}
for side in ['right','left']:
    for part in ['heel','toe']:
        n=f'sole.{side}.{part}';o=bpy.data.objects[n]
        patches[n]=[v.index for v in o.data.vertices if v.co.z<.003]
        if not patches[n]:raise ValueError('No actual rest sole patch vertices')
for f in meta['frames']:
    t=f['time_seconds'];pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    j={n:list(rig.matrix_world@rig.pose.bones[n].head) for n in f['in_place_joints']}
    max_pose=max(max_pose,max((Vector(j[n])-Vector(f['in_place_joints'][n])).length for n in j))
    for pb in rig.pose.bones:
        if pb.parent and pb.name not in ['pelvis','cape.upper','cape.lower']:
            length=(pb.head-pb.parent.head).length;length_ranges.setdefault(pb.name,[]).append(length)
    soles={}
    for n,indices in patches.items():
        o=bpy.data.objects[n].evaluated_get(deps);mesh=o.to_mesh()
        try:
            all_points=[o.matrix_world@v.co for v in mesh.vertices];points=[all_points[i] for i in indices]
            centroid=sum(points,Vector())/len(points);world=centroid+Vector(f['root_world'])
            soles[n]={'minimum_mesh_z':min(v.z for v in all_points),'patch_centroid_in_place':list(centroid),'patch_centroid_world':list(world),'patch_indices':indices}
        finally:o.to_mesh_clear()
    frames.append({'source_index':f['source_index'],'time_seconds':t,'soles':soles})
length_change=max(max(v)-min(v) for v in length_ranges.values())
if max_pose>2e-5 or length_change>2e-5:raise ValueError(f'Saved rig replay failed {max_pose} {length_change}')
summary={}
for name in patches:
    zs=[f['soles'][name]['minimum_mesh_z'] for f in frames]
    summary[name]={'min_z':min(zs),'max_z':max(zs),'below_floor_samples':sum(z<-.002 for z in zs),'ground':'World Z=0; threshold -0.002 is engineering tolerance, not an anatomy/contact approval'}
report={'schema':'walk-saved-rig-check-v1','blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'source_samples_replayed':len(frames),'max_saved_pose_replay_error':max_pose,'max_anatomical_length_variation':length_change,'actual_sole_meshes':summary,'frames':frames,'gate_pose_replay':True,'gate_floor_clearance':all(x['below_floor_samples']==0 for x in summary.values()),'floor_contact_verified':False,'scope':'Actual deformed mesh floor penetration and world patch trajectories only; no support interval/contact-lock/balance assertion','release_ready':False}
a.output.write_text(json.dumps(report,indent=2)+'\n');print('SAVED_RIG_CHECK',max_pose,length_change,summary)
