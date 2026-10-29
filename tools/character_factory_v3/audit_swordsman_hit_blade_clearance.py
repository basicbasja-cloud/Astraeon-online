"""Sample a thin sword-guide centerline against the frozen Hit mannequin surface."""
import argparse,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
JOB=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-object-freeze-20261029/job.json'
CHANNELS={'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale'}

def main():
 import bpy
 from mathutils import Matrix,Vector
 from mathutils.bvhtree import BVHTree
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists() or a.output.is_symlink():raise ValueError('Choose fresh output')
 job=json.loads(JOB.read_text());source=ROOT/job['source_file'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
 if digest!=job['source_sha256'] or job['source_actions']!=['Hit_Chest'] or not job.get('freeze_source_object_transform'):raise ValueError('Unexpected source/job')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
 if rig.parent is not None:raise ValueError('Unexpected parent')
 for track in rig.animation_data.nla_tracks:track.mute=True
 action=bpy.data.actions.get('Hit_Chest_'+rig.name)
 if action is None:raise ValueError('Missing Hit action')
 for curve in action.fcurves:
  if curve.data_path in CHANNELS:curve.mute=True
 rig.animation_data.action=action
 if hasattr(rig.animation_data,'action_slot') and action.slots:rig.animation_data.action_slot=action.slots[0]
 rig.matrix_world=Matrix.Identity(4);mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig)
 records=[];start,end=action.frame_range
 for i in range(job['frames']):
  frame=start+(end-start)*i/(job['frames']-1);bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1);rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
  deps=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(mesh,deps);inv=mesh.matrix_world.inverted()
  def bone(name):return rig.matrix_world@rig.pose.bones[name].head
  index=bone('index_01_r');pinky=bone('pinky_01_r');grip=(index+pinky)*.5;axis=(index-pinky).normalized()
  begin=grip+axis*.12;endpt=grip+axis*.8;local=inv@begin;delta=(inv@endpt)-local
  hit,_,_,_=tree.ray_cast(local,delta.normalized(),delta.length)
  ca=inv@(bone('head')+Vector((0,0,.3)));cb=inv@(bone('pelvis')-Vector((0,0,.3)));cv=cb-ca;control,_,_,_=tree.ray_cast(ca,cv.normalized(),cv.length)
  records.append({'frame':i,'source_frame':frame,'centerline_hit':hit is not None,'hit_world':list(mesh.matrix_world@hit) if hit is not None else None,'torso_positive_control_hit':control is not None,'begin_world':list(begin),'end_world':list(endpt)})
 result={'status':'THIN_CENTERLINE_DIAGNOSTIC_NOT_COLLISION_APPROVAL','source_sha256':digest,'job_sha256':hashlib.sha256(JOB.read_bytes()).hexdigest(),
         'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':records,
         'limitations':['Only one centerline from 0.12m to 0.8m beyond grip; excludes hilt, blade thickness and swept volume.',
                        'Checks sampled mannequin surface, not costume, head, underlayers, trail or game collision.',
                        'No grasp, natural motion, paint, animation or runtime acceptance.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('HIT_BLADE_AUDIT',len(records),'frames',flush=True)
if __name__=='__main__':main()
