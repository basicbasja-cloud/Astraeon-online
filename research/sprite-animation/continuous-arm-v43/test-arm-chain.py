from pathlib import Path
import json,copy,importlib.util,subprocess,sys,tempfile
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];script=ROOT/'skills/modular-eight-direction-sprites/scripts/arm-chain-audit.py'
s=importlib.util.spec_from_file_location('arms',script);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=json.loads((P.parent/'proportion-repair-v42/source/source.json').read_text());new=json.loads((P/'source/source.json').read_text());checks=[]
def check(name,ok):
    assert ok,name
    checks.append(dict(name=name,pass_=True))
q=m.audit(old);check('actual user-rejected source now fails105degree wrist',not q['source_arm_metrics_pass'] and 105<q['max_wrist_deviation_deg']<106)
q=m.audit(new);check('current corrected actual source passes bounded chain checks',q['source_arm_metrics_pass'])
check('painted anatomy remains unknown even after source pass',q['painted_anatomy_status'].startswith('UNKNOWN') and not q['production_pass'])
d=copy.deepcopy(old);d['limb_lengths']['forearm']=.27;check('changing a length label cannot fix wrist axes',not m.audit(d)['source_arm_metrics_pass'])
d=copy.deepcopy(new);del d['frames'][3]['points']['right.palm'];check('hidden/missing palm cannot silently pass',not m.audit(d)['source_arm_metrics_pass'])
d=copy.deepcopy(new)
for f in d['frames']:del f['points']['right.palm']
check('missing whole distal track abstains without crashing',not m.audit(d)['source_arm_metrics_pass'])
check('missing data serializes as strict JSON null rather than Infinity',m.audit(d)['length_variation']['right']==[None,None,None] and bool(json.dumps(m.audit(d),allow_nan=False)))
d=copy.deepcopy(new);d['frames'][3]['points']['right.palm']['world_xyz']=d['frames'][3]['points']['right.wrist']['world_xyz'];check('zero hand vector fails',not m.audit(d)['source_arm_metrics_pass'])
d=copy.deepcopy(new);d['frames'][3]['points']['right.palm']['world_xyz'][0]=float('nan');check('NaN joint fails',not m.audit(d)['source_arm_metrics_pass'])
d=copy.deepcopy(new)
for f in d['frames']:
    for suffix in ['shoulder','elbow','wrist','palm']:
        f['points']['left.'+suffix],f['points']['right.'+suffix]=f['points']['right.'+suffix],f['points']['left.'+suffix]
check('swapped complete owner tracks fail canonical world ownership',not m.audit(d)['source_arm_metrics_pass'])
d=copy.deepcopy(new);d['limb_lengths']['upperarm']*=1.2;check('false declared arm length fails actual vector check',not m.audit(d)['source_arm_metrics_pass'])
# A global frame translation preserves anatomy (not image root continuity).
d=copy.deepcopy(new)
for f in d['frames']:
    for v in f['points'].values():v['world_xyz']=(np.array(v['world_xyz'])+[2,3,4]).tolist()
check('world position is not confused with joint-angle quality',m.audit(d)['source_arm_metrics_pass'])
with tempfile.TemporaryDirectory() as td:
    cmds=[]
    for label,path,flag in [('old',P.parent/'proportion-repair-v42/source/source.json','--require-source'),('new',P/'source/source.json','--require-source'),('production',P/'source/source.json','--require-production')]:
        r=subprocess.run([sys.executable,str(script),'--source',str(path),'--out',str(Path(td)/(label+'.json')),flag],capture_output=True,text=True);cmds.append(dict(label=label,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    check('strict real CLIs reject old, pass new source, reject production',[x['returncode'] for x in cmds]==[1,0,1])
(P/'arm-test-receipt.json').write_text(json.dumps(dict(checks=checks,cli=cmds,scope='Source-chain regressions, not art approval'),indent=2)+'\n');print(len(checks),'arm-chain controls passed')
