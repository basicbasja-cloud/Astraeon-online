"""Measure source mesh foot vertices for the isolated object-frozen Hit study.

These are mesh-vertex diagnostics, not verified shoe-ground contacts.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
JOB=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-hit-object-freeze-20261029/job.json'
CHANNELS={'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale'}

def indices_by_weight(mesh,side):
 groups=[mesh.vertex_groups.get(f'{part}_{side}') for part in ('foot','ball')]
 ids={g.index for g in groups if g is not None}
 if not ids:raise ValueError('missing foot/ball vertex groups: '+side)
 result=[v.index for v in mesh.data.vertices if any(g.group in ids and g.weight>=0.5 for g in v.groups)]
 if not result:raise ValueError('empty foot selection: '+side)
 return result

def main():
 import bpy
 from mathutils import Matrix
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
 rig.matrix_world=Matrix.Identity(4)
 mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig)
 ids={side:indices_by_weight(mesh,side) for side in ('l','r')}
 records=[];start,end=action.frame_range;count=job['frames']
 for i in range(count):
  frame=start+(end-start)*i/(count-1);bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1);rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
  evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());geometry=evaluated.to_mesh()
  try:
   if len(geometry.vertices)!=len(mesh.data.vertices):raise ValueError('evaluated topology changed')
   feet={}
   for side in ('l','r'):
    pts=[(index,evaluated.matrix_world@geometry.vertices[index].co) for index in ids[side]]
    index,point=min(pts,key=lambda value:value[1].z)
    feet[side]={'lowest_selected_vertex':index,'world_xyz':list(point),'selection_count':len(pts)}
   records.append({'frame':i,'source_frame':frame,'feet':feet})
  finally:evaluated.to_mesh_clear()
 result={'status':'DIAGNOSTIC_NOT_CONTACT_APPROVAL','source_sha256':digest,'job_sha256':hashlib.sha256(JOB.read_bytes()).hexdigest(),
         'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':records,
         'limitations':['Selected vertices have foot or ball group weight >= 0.5; lowest vertex may change and need not be the true contact.',
                        'Assumes source world z=0 as a tentative floor. No gameplay surface or painted boot was measured.',
                        'No inference of plant state, continuity between samples, grasp, collision or art acceptance.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('HIT_FOOT_AUDIT',len(records),'frames',flush=True)
if __name__=='__main__':main()
