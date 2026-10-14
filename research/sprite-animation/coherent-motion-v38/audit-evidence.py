"""Integrity audit that requires the real failed-motion outcome to remain visible."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
    checks.append(dict(name=name,pass_=bool(ok)))
    if not ok:raise ValueError(name)
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35','neck-motion-v36','proportion-audit-v37']:
    data=json.loads((P.parent/folder/'evidence-manifest.json').read_text())
    check(folder+' exact frozen evidence unchanged',all(sha(ROOT/r['path'])==r['sha256'] for r in data['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text())
check('13 accepted W files unchanged',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
check('same sole authorized branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text())
check('five actual still jobs and exact direct inputs bound',ledger['actual_still_image_jobs']==5 and ledger['selected_body_job']==2 and ledger['direct_generation_inputs_complete'] and all(sha(ROOT/b['path'])==b['sha256'] for j in ledger['jobs'] for b in [j['request'],j['prompt'],j['output']]+j['inputs']))
check('no generated video MiniMax or old own attacks',not ledger['generated_video'] and not ledger['minimax_called'] and not ledger['old_own_attack_used'])
check('guides not substituted for final art',not ledger['guide_only_transform_used_in_final'])
repro=json.loads((P/'guide-reproduction.json').read_text())
check('four exact later conditioning guides retained',repro['exact_reproduction'] and all(sha(P/name)==value for name,value in repro['sha256'].items()))
contract=json.loads((P/'motion-contract.json').read_text());report=json.loads((P/'motion-qa.json').read_text())
parent=module('parent','skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py')
check('parent reports recomputed from real current pixels and source',report==parent.audit(contract,ROOT,P/'renders'))
selected=report['variants']['review']
check('seven exact body drawings share one matrix and unchanged head scale',selected['distinct_body_drawings']==7 and selected['exact_raw_grid_crops'] and selected['common_body_transform'] and contract['head_scale']==.11 and all(r['generation_job']==2 for r in contract['variants']['review']))
check('all actual receiver and foreground pixels pass',selected['neck_pass'] and max(r['endpoint_residual_px'] for r in selected['neck'])<1.2)
check('native and raster forefoot metrics meet unchanged 6px budget',contract['planted_surface_budget_px']==6 and selected['contact_pass'] and selected['support']['far']['raw_range_at_display_scale_px'][0]<5.55 and selected['support']['near']['rendered_range_px'][0]==5)
check('no standing substitute at penultimate key',contract['variants']['review'][6]['body']['sha256']!=contract['variants']['review'][7]['body']['sha256'])
spacing=module('spacing','skills/modular-eight-direction-sprites/scripts/coherent-motion-spacing.py');source=json.loads((ROOT/contract['source']['path']).read_text());sq=json.loads((P/'spacing-qa.json').read_text())
recomputed={v:spacing.audit_sequence(rows,source,report['variants'][v]['support'],contract['recovery_overshoot_budget_px'],contract['lateral_recovery_monotonic_expected']) for v,rows in contract['variants'].items()}
check('two-axis source-time diagnostics reproduced',sq==recomputed)
check('real 10px lateral hitch is rejected despite parent metrics passing',selected['motion_metrics_pass'] and sq['review']['maximum_lateral_backtrack_px']>10 and not sq['review']['recovery_key_pass'])
alpha=module('alpha','skills/modular-eight-direction-sprites/scripts/coherent-strip-alpha.py');ar=json.loads((P/'alpha-qa.json').read_text())
check('five actual alpha probe reports reproduced',len(ar)==5 and all(r['observations']==alpha.audit_sheet(ROOT/r['path'])['observations'] for r in ar))
chosen=next(r for r in ar if r['path'].endswith('attempt2-raw.png'))
check('strict selected empty patches pass; unused key0 speck still fails',not chosen['empty_patch_pass'] and all(r['pass_'] for r in chosen['observations'] if r['art_index']!=0))
matte=next(r for r in ar if r['path'].endswith('attempt3-raw.png'))
check('actual translucent matte retained as failed evidence',not matte['empty_patch_pass'] and max(r['maximum_alpha'] for r in matte['observations'])>40)
edits=module('edits','skills/modular-eight-direction-sprites/scripts/native-strip-edit-audit.py')
for job,allowed in [(3,[6]),(4,[5,6]),(5,[6])]:
    old=json.loads((P/f'attempt{job}-edit-scope.json').read_text());new=edits.audit(P/'attempt2-raw.png',P/f'attempt{job}-raw.png',allowed)
    check(f'job{job} unrequested visible changes retained',old['rows']==new['rows'] and not old['unrequested_cells_preserved'])
decision=json.loads((P/'review-decision.json').read_text())
check('combined motion and production cannot inherit partial parent pass',decision['numeric_parent_metrics_pass'] and not decision['combined_motion_pass'] and not decision['lateral_recovery_pass'] and not decision['production_pass'] and not decision['proportion_family_locked'])
strict=json.loads((P/'strict-gate-receipt.json').read_text())
check('strict sequence command rejected real defect',strict['returncode']==1)
tests=json.loads((P/'test-receipt.json').read_text())
check('10 new plus13 unchanged regressions executed',tests['total_tests']==23 and sorted(r['tests_run'] for r in tests['runs'])==[10,13] and all(r['returncode']==0 and sha(ROOT/r['script']['path'])==r['script']['sha256'] for r in tests['runs']) and all(sha(ROOT/r['path'])==r['sha256'] for r in tests['tools']))
browser=json.loads((P/'browser-qa.json').read_text())
check('18 actual browser checks pass with explicit failure label',len(browser['checks'])==18 and all(r['pass'] for r in browser['checks']) and not browser['errors'])
play=json.loads((P/'playback-receipt.json').read_text())
check('four GIFs actually decoded with source/game clocks',len(play)==4 and all(sha(P/name)==r['sha256'] and sum(r['decoded_durations_ms'])==r['total_ms'] for name,r in play.items()) and play['review-source.gif']['total_ms']==1900 and play['review-game.gif']['total_ms']==1300)
visual=json.loads((P/'visual-review.json').read_text())
check('exact inspected images bound to a rejected-motion receipt',all(sha(ROOT/r['path'])==r['sha256'] for r in visual['inspected']) and not visual['motion_approved'] and not visual['user_new_art_approved'] and not visual['production_pass'])
(P/'audit-report.json').write_text(json.dumps(dict(state='INCOMPLETE',production_pass=False))+'\n')
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/coherent-motion-repair-and-two-axis-review.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('new documentation links resolve',not bad)
out=dict(checks=checks,passed_checks=len(checks),decision=decision['decision'],motion_pass=False,production_pass=False)
(P/'audit-report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),decision=out['decision'])))
