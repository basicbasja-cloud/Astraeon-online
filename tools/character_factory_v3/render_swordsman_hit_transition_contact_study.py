"""Sample evaluated foot skin during an experimental object-frozen Hit transition."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_swordsman_hit_frozen_study as study
from audit_swordsman_hit_frozen_feet import indices_by_weight
MARK="            path=folder/f'{i:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)"

def main():
 args=sys.argv[sys.argv.index('--')+1:];job=Path(args[args.index('--job')+1]);out=Path(args[args.index('--output')+1]);data=json.loads(job.read_text())
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 if data.get('source_actions')!=['Hit_Chest'] or data.get('freeze_source_object_transform') is not True or data.get('directions')!=['SW'] or data.get('exit_transition',{}).get('action')!='Idle_Sword':raise ValueError('Requires explicit SW frozen Hit-to-Idle study')
 import bpy
 records=[];indices={}
 def capture(rig,index,rec):
  mesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.parent==rig)
  if not indices:
   for side in ('l','r'):indices[side]=indices_by_weight(mesh,side)
  evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());geometry=evaluated.to_mesh()
  try:
   if len(geometry.vertices)!=len(mesh.data.vertices):raise ValueError('topology changed')
   feet={}
   for side in ('l','r'):
    points=[(i,evaluated.matrix_world@geometry.vertices[i].co) for i in indices[side]]
    vertex,point=min(points,key=lambda x:x[1].z);feet[side]={'lowest_selected_vertex':vertex,'world_xyz':list(point),'selection_count':len(points)}
   records.append({'frame':index,'source_action':rec['action'],'source_frame':rec['source_frame'],'transition_weight':rec.get('transition_weight'),'feet':feet})
  finally:evaluated.to_mesh_clear()
 source=study.patched_source(study.BASE.read_text())
 if source.count(MARK)!=1:raise ValueError('base output marker changed')
 source=source.replace(MARK,'            capture(rig,i,rec)\n'+MARK)
 exec(compile(source,str(study.BASE),'exec'),{'__name__':'__main__','__file__':str(study.BASE),'capture':capture})
 receipt={'status':'SKIN_VERTEX_DIAGNOSTIC_NOT_CONTACT_APPROVAL','job_sha256':hashlib.sha256(job.read_bytes()).hexdigest(),
          'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frames':records,
          'limitations':['Lowest >=0.5 foot/ball-weighted mesh vertex can change and is not a verified sole contact.',
                         'No continuous collision, root/game floor, skin volume, cloth or painted boot validation.',
                         'This joint blend and its grip are not approved.']}
 (out/'transition-feet.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
