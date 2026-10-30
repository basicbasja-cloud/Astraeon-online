"""Measure evaluated foot skin during explicit BasicAttack-to-Idle guide capture."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_swordsman_basicattack_idle_study as study
from audit_swordsman_hit_frozen_feet import indices_by_weight
MARK="            path=folder/f'{i:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)"

def main():
 args=sys.argv[sys.argv.index('--')+1:];jobpath=Path(args[args.index('--job')+1]);out=Path(args[args.index('--output')+1]);job=json.loads(jobpath.read_text());study.samples(job)
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 if job.get('directions')!=['SW']:raise ValueError('contact capture requires one SW camera')
 canonical=Path(__file__).with_name('render_patch001_guides.py')
 if job.get('renderer_sha256')!=study.sha(canonical) or job.get('explicit_sampling_implementation_sha256')!=study.sha(Path(study.explicit.__file__)):raise ValueError('capture implementation changed')
 import bpy
 records=[];indices={}
 def capture(rig,index,rec):
  mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig)
  if not indices:
   for side in ('l','r'):indices[side]=indices_by_weight(mesh,side)
  obj=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());geo=obj.to_mesh()
  try:
   if len(geo.vertices)!=len(mesh.data.vertices):raise ValueError('topology changed')
   feet={}
   for side in ('l','r'):
    selected=[(j,obj.matrix_world@geo.vertices[j].co) for j in indices[side]];vertex,point=min(selected,key=lambda x:x[1].z);feet[side]={'lowest_vertex':vertex,'world_xyz':list(point),'selection_count':len(selected)}
   records.append({'frame':index,'action':rec['action'],'source_frame':rec['source_frame'],'transition_weight':rec.get('transition_weight'),'feet':feet})
  finally:obj.to_mesh_clear()
 source=canonical.read_text()
 if source.count(MARK)!=1:raise ValueError('renderer marker changed')
 source=source.replace(MARK,'            capture(rig,i,rec)\n'+MARK)
 scope={'__file__':str(canonical),'__name__':'basicattack_idle_contact_study','_explicit_pose_samples':study.samples,'capture':capture}
 exec(compile(study.explicit.instrument(source),str(canonical),'exec'),scope);scope['main']()
 result={'status':'SKIN_VERTEX_DIAGNOSTIC_NOT_CONTACT_APPROVAL','job_sha256':study.sha(jobpath),'implementation_sha256':study.sha(__file__),'records':records,
         'limitations':['Foot/ball weighted lowest skin vertices are proxies and can change; they are not confirmed painted or game-floor contact.', 'No between-sample collision, pose acceptance, gameplay floor, blade thickness, or artwork validation.']}
 (out/'feet-diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
