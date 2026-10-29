"""Render a separately identified source-frame sampling study under Blender.

Samples are explicit source poses, not interpolated sprites or a production job.
The canonical renderer remains unchanged. Only the sampling statement is varied.
"""
import hashlib,json,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
CANONICAL=HERE/'render_patch001_guides.py'
MARKER='f=start+(end-start)*local'

def validate_samples(job):
 frames=job.get('study_source_frames')
 if len(job['source_actions'])!=1 or job['loop'] or not isinstance(frames,list) or len(frames)!=job['frames'] or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in frames) or any(a>=b for a,b in zip(frames,frames[1:])):raise ValueError('Study needs one action and strictly increasing finite source frames')
 return frames

def main():
 args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());validate_samples(job)
 source=CANONICAL.read_text()
 if source.count(MARKER)!=1:raise ValueError('Canonical sampling statement changed; review study')
 if hashlib.sha256(CANONICAL.read_bytes()).hexdigest()!=job['renderer_sha256']:raise ValueError('Canonical renderer differs from pinned job')
 source=source.replace(MARKER,"f=job['study_source_frames'][i]\n        if not start<=f<=end:raise ValueError('Study frame outside action range')")
 scope={'__name__':'__main__','__file__':str(CANONICAL)}
 exec(compile(source,str(CANONICAL),'exec'),scope)
if __name__=='__main__':main()
