"""Sample foot-weighted source skin vertices for the native Walk guide."""
import argparse,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_swordsman_hit_frozen_feet import indices_by_weight

def main():
 import bpy
 from mathutils import Matrix
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if a.output.exists() or a.output.is_symlink():raise ValueError('choose fresh output')
 manifest=json.loads(GUIDE.read_text());job=manifest['job'];source=ROOT/job['source_file'];digest=hashlib.sha256(source.read_bytes()).hexdigest();frames=manifest['views']['SW']['frames']
 if digest!=job['source_sha256'] or job['source_actions']!=['Walk'] or len(frames)!=16 or not job['loop']:raise ValueError('unexpected source guide')
 if any(any(abs(v)>1e-6 for v in f['actor_root_delta']) for f in frames):raise ValueError('root motion requires explicit reconstruction')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
 if rig.parent is not None:raise ValueError('unexpected rig parent')
 for track in rig.animation_data.nla_tracks:track.mute=True
 action=bpy.data.actions.get('Walk_'+rig.name)
 if action is None:raise ValueError('missing source action')
 rig.animation_data.action=action
 if hasattr(rig.animation_data,'action_slot') and action.slots:rig.animation_data.action_slot=action.slots[0]
 rig.matrix_world=Matrix.Identity(4);mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig);ids={s:indices_by_weight(mesh,s) for s in ('l','r')};records=[]
 for i,f in enumerate(frames):
  t=f['source_frame'];bpy.context.scene.frame_set(math.floor(t),subframe=t%1);rig.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update()
  for name in ('head','foot_l','foot_r'):
   actual=rig.matrix_world@rig.pose.bones[name].head;expected=f['world_landmarks'][name]
   if max(abs(actual[k]-expected[k]) for k in range(3))>1e-4:raise ValueError(f'pose mismatch frame {i}: {name}')
  obj=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());m=obj.to_mesh()
  try:
   if len(m.vertices)!=len(mesh.data.vertices):raise ValueError('evaluated topology changed')
   feet={}
   for side in ('l','r'):
    selected=[(j,obj.matrix_world@m.vertices[j].co) for j in ids[side]];index,point=min(selected,key=lambda v:v[1].z)
    feet[side]={'lowest_vertex':index,'world_xyz':list(point),'candidate_count':len(selected)}
   records.append({'frame':i,'source_frame':t,'feet':feet})
  finally:obj.to_mesh_clear()
 result={'status':'SOURCE_SKIN_HEIGHT_DIAGNOSTIC_NOT_CONTACT_APPROVAL','source_sha256':digest,'guide_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),
         'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':records,
         'limitations':['Minimum foot/ball-weighted mesh vertex can change and is not a verified sole contact.', 'Source is in place; meaningful ground slip requires gameplay velocity and intended contact phase.', 'A tentative z=0 plane is not a verified game floor. No paint, grip, cutout or runtime is approved.']}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('WALK_FEET_SOURCE_AUDIT',len(records),'frames',flush=True)
if __name__=='__main__':main()
