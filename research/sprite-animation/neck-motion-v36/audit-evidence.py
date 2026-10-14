"""Audit evidence integrity and preserve the real nonpassing motion decision."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
checks=[]
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def check(name, value):
    checks.append(dict(name=name, pass_=bool(value)))
    if not value:
        raise ValueError(name)


for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35']:
    manifest=json.loads((P.parent/folder/'evidence-manifest.json').read_text())
    check(folder+' frozen evidence unchanged',all(sha(ROOT/f['path'])==f['sha256'] for f in manifest['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text())
check('exact 13 protected W files unchanged',len(w['files'])==13 and all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files']))
check('sole authorized branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text())
check('four actual still jobs bound and provenance gaps explicit',ledger['actual_imagegen_jobs']==4 and not ledger['full_provenance_complete'] and not ledger['minimax_called'] and not ledger['old_own_attack_used'] and all(sha(ROOT/b['path'])==b['sha256'] for j in ledger['jobs'] for b in [j['prompt'],j['output']]+j['retained_known_inputs']))
spec=importlib.util.spec_from_file_location('review',ROOT/'skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py')
review=importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
neutral=json.loads((P/'neutral-neck-qa.json').read_text())
binding=json.loads((P/'neck-bind.json').read_text())
row=dict(body_matrix=binding['body_matrix'],head_matrix=binding['head_matrix'],body_collar_lip_points_native=binding['body_receiver_points_native'])
case=dict(head_insertion_points_native=binding['head_insertion_points_native'],receiver_endpoint_budget_px=binding['endpoint_budget_px'])
passes={mode:np.array(Image.open(P/f'neck-{name}.png').convert('RGBA')) for mode,name in [('full','both'),('body','body'),('head','head'),('collar','collar')]}
check('neutral report remeasured from current actual pixels',all(neutral[k]==v for k,v in review.neck_metrics(row,case,passes).items()))
check('neutral actual receiver/coverage/foreground pixels pass',neutral['pass_'] and neutral['endpoint_residual_px']<=2 and neutral['wrong_collar_pixels']==0 and all(sha(ROOT/b['path'])==b['sha256'] for b in neutral['input_bindings']))
report=json.loads((P/'motion-qa.json').read_text())
contract=json.loads((P/'motion-contract.json').read_text())
check('motion report recomputed from current actual pixels and sources',report==review.audit(contract,ROOT,P/'renders'))
check('all bound source and structural checks pass',all(report['integrity_checks'].values()))
selected=report['variants']['review'];raw=report['variants']['raw8']
check('all eight actual motion receivers connected without whole-body fitting',selected['neck_pass'] and selected['common_body_transform'] and selected['exact_raw_grid_crops'] and selected['distinct_body_drawings']==6)
check('raw overshoot retained; explicit selected hold removes only overshoot',not raw['phase']['pass_'] and raw['phase']['recovery_overshoot_px']>8 and selected['phase']['pass_'] and selected['phase']['recovery_overshoot_px']==0)
far=selected['support']['far']
check('true native contact failure preserved despite raster rounding',far['raw_range_at_display_scale_px'][0]>6 and far['rendered_range_px'][0]==6 and not selected['contact_pass'] and not selected['motion_metrics_pass'] and not selected['production_pass'])
qa=json.loads((P/'browser-qa.json').read_text())
check('15 actual Chromium behavior/pixel checks pass',len(qa['checks'])==15 and all(c['pass'] for c in qa['checks']) and not qa['errors'])
tests=json.loads((P/'test-receipt.json').read_text())
check('13 real-image and negative-control regressions passed',tests['returncode']==0 and tests['tests_run']==13 and tests['test_script_sha256']==sha(P/'test-neck-motion.py') and tests['tool_sha256']==sha(ROOT/'skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py'))
visual=json.loads((P/'visual-review.json').read_text())
check('manual review bound to exact inspected images, no automatic motion approval',all(sha(ROOT/f['path'])==f['sha256'] for f in visual['inspected']) and not visual['motion_approved'] and not visual['user_new_art_approved'] and not visual['production_pass'])
play=json.loads((P/'playback-receipt.json').read_text())
check('four actual GIF exports/clocks decoded, repeated exposure merge disclosed',len(play)==4 and all(sha(P/n)==v['sha256'] and sum(v['decoded_durations_ms'])==v['total_ms']==sum(v['logical_durations_ms']) for n,v in play.items()))
feedback=json.loads((P/'user-neck-feedback.json').read_text())
check('exact bad-neck user feedback and old pixels retained',sha(ROOT/feedback['prior_bad_case']['path'])==feedback['prior_bad_case']['sha256'] and not feedback['approval_transfer'])
# The README links this output. Materialize an explicitly incomplete report
# before checking links, then replace it only after every remaining check passes.
(P/'audit-report.json').write_text(json.dumps(dict(state='INCOMPLETE',checks=checks,production_pass=False),indent=2)+'\n')
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/painted-neck-receivers-and-coherent-motion.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():
            bad.append([str(file),target])
check('new documentation links resolve',not bad)
out=dict(checks=checks,passed_checks=len(checks),decision='INTEGRITY_VERIFIED_NECK_CONNECTED_MOTION_CONTACT_REPAIR_REQUIRED',motion_pass=False,production_pass=False)
(P/'audit-report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['passed_checks','decision']}))
