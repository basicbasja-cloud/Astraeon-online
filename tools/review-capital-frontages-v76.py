"""Serial source-matched lighting and checks for the frontage/landscape candidate.

Uses the repository's existing checks, original-alpha bakes and native source.
Gameplay and visual acceptance are recorded separately after these steps.
"""
import subprocess, os, time, json, hashlib, argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
env=os.environ.copy();env.update(PYTHONPATH=os.environ.get('ASTRAEON_GEOMETRY_PYTHONPATH',os.environ.get('PYTHONPATH','/tmp/astraeon-curb-geometry')),
    ASTRAEON_CAPITAL_REVIEW_DIR='docs/review/wayfarer-capital-v76',
    ASTRAEON_SHADOW_ALPHA_CACHE=os.environ.get('ASTRAEON_SHADOW_ALPHA_CACHE','/tmp/astraeon-ro3-72/composition-alpha.json'))
steps=[('building-light',['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python','tools/bake-town-depth-v48.py']),('foliage-light',['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python','tools/bake-ro3-foliage-v70.py']),('ground-light',['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python','tools/bake-ground-shadows-v54.py']),('native-parity',['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python','tools/check-blender-export-v3.py']),('geometry',['python3','tools/check-capital-architecture-v76.py']),('assembly',['python3','tools/check-wayfarer-capital-v75.py']),('density',['python3','tools/check-capital-density-v75.py']),('traversal',['node','tools/check-ro3-traversal-v68.cjs',str(O/'traversal.json')]),('schemas',['python3','tools/validate-world-v3.py']),('node-checks',['python3','tools/check-current-capital-tests.py']),('blueprint',['python3','tools/draw-capital-architecture-v76.py'])]
steps.extend([('property-preservation',['python3','tools/check-capital-property-preservation-v76.py']),('landscape',['python3','tools/check-capital-landscape-v76.py'])])
parser=argparse.ArgumentParser();parser.add_argument('--from-stage',choices=[name for name,_ in steps]);args=parser.parse_args()
results=[]
if args.from_stage:
 start_index=[name for name,_ in steps].index(args.from_stage)
 previous=json.loads((O/'verification-progress.json').read_text())
 results=previous[:start_index]
 assert len(results)==start_index and all(a['exitCode']==0 for a in results),'Cannot resume across an incomplete earlier stage'
 steps=steps[start_index:]
for name,args in steps:
 print('START',name,time.strftime('%H:%M:%S'),flush=True);start=time.monotonic()
 with (O/(name+'.log')).open('w') as f:res=subprocess.run(args,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 results.append({'name':name,'exitCode':res.returncode,'seconds':round(time.monotonic()-start,1)})
 (O/'verification-progress.json').write_text(json.dumps(results,indent=2)+'\n')
 print('END',name,res.returncode,time.strftime('%H:%M:%S'),flush=True)
 if res.returncode:raise SystemExit(res.returncode)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes()
(O/'verified-source.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(raw).hexdigest(),'nativeSHA256':hashlib.sha256((R/'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest(),'steps':results,'visualAcceptance':'Pending gameplay inspection'},indent=2)+'\n')
