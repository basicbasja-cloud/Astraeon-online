import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,ok):
 checks.append(dict(name=n,pass_=bool(ok)))
 if not ok:raise ValueError(n)
for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34']:
 r=json.loads((P.parent/folder/'evidence-manifest.json').read_text());check(folder+' frozen evidence unchanged',all(sha(ROOT/f['path'])==f['sha256'] for f in r['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13 approved W files unchanged',len(w['files'])==13 and all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files']))
check('same sole authorized research branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
source=json.loads((P/'source/receipt.json').read_text());check('reopened RO renderer matches pinned Git tree blob',source['git_blob_sha1']==source['expected_tree_blob_sha1']=='87242ad5a9012f17af784e9792769f1eef74dd5c' and source['matches_pinned_tree'])
l=json.loads((P/'generation-ledger.json').read_text());check('2 actual image jobs retained, first body selected, no MiniMax/old slash',l['actual_imagegen_jobs']==2 and l['selected_job']=='coherent_body' and not l['minimax_called'] and not l['old_own_attack_used'] and all(sha(ROOT/r['path'])==r['sha256'] for j in l['jobs'] for r in [j['prompt'],j['output']]+j['inputs']))
c=json.loads((P/'slot-contract.json').read_text());check('one coherent bound body outfit, no individual limb scaling',c['pose_count']==1 and c['body']['slot']=='body_outfit' and c['body']['independent_limb_transform_allowed'] is False and c['body']['matrix'][0]==c['body']['matrix'][3]>0 and sha(ROOT/c['body']['file']['path'])==c['body']['file']['sha256'])
check('4 complete head caches share one mount and scale',len(c['head']['variants'])==4 and c['head']['matrix'][0]==c['head']['matrix'][3]>0 and all(sha(ROOT/r['path'])==r['sha256'] for r in c['head']['variants'].values()))
draws=json.loads((P/'draw-receipt.json').read_text());check('actual Canvas draw calls match only body/head matrices',len(draws)==2 and np.allclose(draws[0]['matrix'],c['body']['matrix']) and np.allclose(draws[1]['matrix'],c['head']['matrix']))
qa=json.loads((P/'browser-qa.json').read_text());check('10 actual browser checks pass',len(qa['checks'])==10 and all(r['pass'] for r in qa['checks']) and not qa['errors'])
check('head reduced by11.1percent around same neck mount, not body-resized',abs(c['head']['size_change']['linear_reduction_fraction']-1/9)<1e-8 and c['head']['matrix'][0]==.4 and c['head']['size_change']['body_matrix_unchanged'])
a=np.array(Image.open(P/'body-halo-raw.png').convert('RGBA'));check('selected original art exterior samples really transparent despite RGB',all(a[y,x,3]==0 for x,y in [(0,0),(200,200),(100,500),(900,1000)]))
comparison=json.loads((P/'comparison-inputs.json').read_text());check('original W/v34/new actual comparison images bound, no anatomical accuracy claim',len(comparison['images'])==3 and all(sha(ROOT/r['path'])==r['sha256'] and not r['automated_anatomical_ratio_claim'] for r in comparison['images']))
feedback=json.loads((P/'user-proportion-feedback.json').read_text());check('exact user criticism retained without relabeling old evidence',feedback['status']=='USER_PROPORTION_CORRECTION_REQUIRED' and all(sha(ROOT/r['path'])==r['sha256'] for r in feedback['bound_evidence']))
check('no new animation or user proportion approval inferred',not c['animation_approval'] and not c['user_proportion_approved'] and not c['production_pass'])
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/body-outfit-production-slots.md']:
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('new documentation links resolve',not bad)
result=dict(checks=checks,passed_checks=len(checks),decision='TWO_LOGICAL_SLOTS_VERIFIED_PROPORTION_CANDIDATE',user_proportion_approved=False,animation_pass=False,production_pass=False)
(P/'audit-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['passed_checks','decision']}))
