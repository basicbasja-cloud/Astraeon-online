"""Capture retained explicit BasicAttack samples plus an experimental idle blend."""
import hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_explicit_patch001_guides as explicit

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def samples(job,static=False):
 values=job.get('explicit_source_samples');transition=job.get('exit_transition',{});count=transition.get('frames')
 if job.get('source_actions')!=['Sword_Attack'] or job.get('loop') or job.get('entry_transition') or transition.get('action')!='Idle_Sword' or transition.get('source_frame')!=0 or count!=4 or job.get('frames')!=20 or not isinstance(values,list) or len(values)!=16:raise ValueError('unexpected explicit BasicAttack transition contract')
 if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=39 for x in values) or any(b<=a for a,b in zip(values,values[1:])):raise ValueError('invalid source samples')
 if values[-1]!=39:raise ValueError('unexpected terminal attack pose')
 records=[{'action':'Sword_Attack','source_frame':float(x),'segment_phase':float(x)/39} for x in values]
 if static:return records[:1]
 return records+[{'action':'Idle_Sword','source_frame':0,'segment_phase':0,'transition_from':'Sword_Attack','transition_frame':39,'transition_weight':(i+1)/count} for i in range(count)]

def main():
 args=sys.argv[sys.argv.index('--')+1:];jobpath=Path(args[args.index('--job')+1]);out=Path(args[args.index('--output')+1]);job=json.loads(jobpath.read_text());samples(job)
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 canonical=Path(__file__).with_name('render_patch001_guides.py')
 if job.get('renderer_sha256')!=sha(canonical) or job.get('explicit_sampling_implementation_sha256')!=sha(Path(explicit.__file__)):raise ValueError('retained capture implementation changed')
 scope={'__file__':str(canonical),'__name__':'basicattack_idle_study','_explicit_pose_samples':samples}
 exec(compile(explicit.instrument(canonical.read_text()),str(canonical),'exec'),scope);scope['main']()
 manifest_path=out/'manifest.json';manifest=json.loads(manifest_path.read_text())
 for direction,view in manifest['views'].items():
  if [(f['action'],f['source_frame']) for f in view['frames']]!=[(f['action'],f['source_frame']) for f in samples(job)]:raise ValueError('captured samples differ')
 manifest['experimental_status']='EXPLICIT_BASICATTACK_IDLE_STUDY_NOT_APPROVED';manifest['experimental_wrapper_sha256']=sha(__file__)
 manifest['limitations'].append('Four generated transition poses are a source-only experiment; no painted recovery or runtime transition is installed.')
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
