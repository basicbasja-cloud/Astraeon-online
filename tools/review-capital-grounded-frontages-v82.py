"""Serial full-quality native checks, then exact transport and normal captures."""
import json,hashlib,subprocess,os,time,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v82';V=O/'grounded-frontages'
env=os.environ.copy();env.update(PYTHONPATH='/tmp/astraeon-curb-geometry',ASTRAEON_CAPITAL_REVIEW_DIR='docs/review/wayfarer-capital-v82',ASTRAEON_SHADOW_ALPHA_CACHE='/tmp/astraeon-capital-v82-alpha.json')
steps=[('geometry-delta',['python3','tools/check-capital-grounded-frontages-v82.py','--pending-light']),
       ('prepare-alpha',['python3','tools/prepare-shadow-alpha.py','--output',env['ASTRAEON_SHADOW_ALPHA_CACHE']])]
steps += [(n,['blender','-b','authoring/wayfarer-spatial.blend','--python-exit-code','1','--python',f]) for n,f in [
    ('building-light','tools/bake-town-depth-v48.py'),('foliage-light','tools/bake-ro3-foliage-v70.py'),
    ('ground-light','tools/bake-ground-shadows-v54.py'),('native-parity','tools/check-blender-export-v3.py')]]
steps += [('declared-delta',['python3','tools/check-capital-grounded-frontages-v82.py']),
          ('architecture',['python3','tools/check-capital-architecture-v76.py']),
          ('assembly',['python3','tools/check-wayfarer-capital-v75.py']),
          ('density',['python3','tools/check-capital-density-v75.py']),
          ('traversal',['node','tools/check-ro3-traversal-v68.cjs',str(V/'traversal.json')]),
          ('schema',['python3','tools/validate-world-v3.py']),
          ('node',['python3','tools/check-current-capital-tests.py'])]
ap=argparse.ArgumentParser();ap.add_argument('--from-stage',choices=[n for n,_ in steps]);args=ap.parse_args()
records=[]
if args.from_stage:
    i=[n for n,_ in steps].index(args.from_stage)
    records=json.loads((V/'progress.json').read_text())[:i]
    assert len(records)==i and all(a['exitCode']==0 for a in records);steps=steps[i:]
    (V/'progress.json').write_text(json.dumps(records,indent=2)+'\n')
for name,cmd in steps:
    print('START',name,time.strftime('%H:%M:%S'),flush=True);start=time.monotonic()
    with (V/(name+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
    records.append({'name':name,'exitCode':r.returncode,'seconds':round(time.monotonic()-start,1)})
    (V/'progress.json').write_text(json.dumps(records,indent=2)+'\n')
    print('END',name,r.returncode,flush=True)
    if r.returncode:raise SystemExit(r.returncode)
seal={'sourceSHA256':hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest(),
      'nativeSHA256':hashlib.sha256((R/'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest(),
      'steps':records,'pass':True,'visualAcceptance':'Pending normal paired gameplay review'}
(V/'verified-source.json').write_text(json.dumps(seal,indent=2)+'\n')
