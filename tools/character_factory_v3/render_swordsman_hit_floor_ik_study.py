"""Render an isolated Hit-to-Idle guide with bounded 3D foot IK diagnostics."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_swordsman_hit_frozen_study as base
from hit_transition_floor_ik import apply
MARK='            bones={n:rig.matrix_world@rig.pose.bones[b].head for n,b in names.items()}'

def main():
 args=sys.argv[sys.argv.index('--')+1:];job=Path(args[args.index('--job')+1]);out=Path(args[args.index('--output')+1]);data=json.loads(job.read_text())
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 if data.get('source_actions')!=['Hit_Chest'] or data.get('freeze_source_object_transform') is not True or data.get('exit_transition',{}).get('action')!='Idle_Sword' or data.get('floor_ik_experiment') is not True:raise ValueError('expected explicit native Hit-to-Idle floor IK study')
 source=base.patched_source(base.BASE.read_text())
 if source.count(MARK)!=1:raise ValueError('base marker changed')
 source=source.replace(MARK,'            results.append({"direction":direction,"frame":i,"correction":apply(rig,rec)})\n'+MARK)
 results=[];exec(compile(source,str(base.BASE),'exec'),{'__name__':'__main__','__file__':str(base.BASE),'apply':apply,'results':results})
 receipt={'status':'FLOOR_IK_CANDIDATE_NOT_APPROVED','job_sha256':hashlib.sha256(job.read_bytes()).hexdigest(),
          'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'ik_sha256':hashlib.sha256(Path(__file__).with_name('hit_transition_floor_ik.py').read_bytes()).hexdigest(),'records':results,
          'limitations':['Selected skin minima are proxies, not confirmed shoe-ground contacts.',
                         'Two-bone solution can alter knee motion and requires visual review; only sampled frames are measured.',
                         'No grip, swept collision, painted art, game floor or transition acceptance.']}
 (out/'floor-ik-diagnostic.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
