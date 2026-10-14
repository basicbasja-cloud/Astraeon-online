"""Bind one-view motion acceptance to actual isolated repair evidence."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];V=P.parent/'coherent-motion-v38';checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
    checks.append(dict(name=name,pass_=bool(ok)))
    if not ok:raise ValueError(name)
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35','neck-motion-v36','proportion-audit-v37','coherent-motion-v38']:
    data=json.loads((P.parent/folder/'evidence-manifest.json').read_text())
    check(folder+' exact frozen evidence unchanged',all(sha(ROOT/r['path'])==r['sha256'] for r in data['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text())
check('13 exact accepted W files preserved',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
check('same sole authorized research branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text())
check('one genuine targeted native edit with exact direct inputs',ledger['actual_still_image_jobs']==1 and all(sha(ROOT/b['path'])==b['sha256'] for b in [ledger['request'],ledger['prompt'],ledger['output'],ledger['selected_canonical_body'],ledger['normalization'],ledger['bookkeeping_atlas']]+ledger['inputs']))
check('no video MiniMax or old own attack input',not ledger['generated_video'] and not ledger['minimax_called'] and not ledger['old_own_attack_used'])
repro=json.loads((P/'reference-reproduction.json').read_text())
check('both exact square reference plates reproduced',repro['exact'] and all(sha(P/name)==value for name,value in repro['images'].items()))
before=json.loads((V/'motion-contract.json').read_text());after=json.loads((P/'motion-contract.json').read_text());norm=json.loads((P/'normalization.json').read_text())
isolated=module('isolated','skills/modular-eight-direction-sprites/scripts/isolated-key-review.py')
actual=isolated.audit(before,after,V/'renders/review',P/'renders/review',norm,ROOT)
iq=json.loads((P/'isolation-qa.json').read_text())
check('isolation report independently reproduced',iq==actual)
check('seven protected pose records and28actual passes unchanged',iq['isolation_pass'] and iq['other_seven_unchanged'] and len(iq['protected_keys'])==7 and all(all(r['actual_pass_pixels_identical'].values()) for r in iq['protected_keys']))
check('normalization uses fixed known plate rather than feature fitting',iq['known_canvas_normalization_pass'] and not norm['foreground_or_foot_fit_used'])
parent=module('parent','skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py')
report=json.loads((P/'motion-qa.json').read_text())
check('actual neck contact source-phase and atlas crop metrics reproduced',report==parent.audit(after,ROOT,P/'renders'))
selected=report['variants']['review']
check('unchanged budgets pass for actual repaired motion',selected['motion_metrics_pass'] and selected['neck_pass'] and selected['contact_pass'] and selected['distinct_body_drawings']==7 and selected['neck'][6]['endpoint_residual_px']<1.01 and after['planted_surface_budget_px']==6)
spacing=module('spacing','skills/modular-eight-direction-sprites/scripts/coherent-motion-spacing.py');source=json.loads((ROOT/after['source']['path']).read_text())
sq=json.loads((P/'spacing-qa.json').read_text());current={v:spacing.audit_sequence(rows,source,report['variants'][v]['support'],after['recovery_overshoot_budget_px'],after['lateral_recovery_monotonic_expected']) for v,rows in after['variants'].items()}
check('actual two-axis recovery metrics reproduced',sq==current)
check('before still fails; new recovery has no unintended X reversal',not sq['raw8']['recovery_key_pass'] and sq['raw8']['maximum_lateral_backtrack_px']>10 and sq['review']['recovery_key_pass'] and sq['review']['maximum_lateral_backtrack_px']==0)
alpha=module('alpha','skills/modular-eight-direction-sprites/scripts/coherent-strip-alpha.py');aq=json.loads((P/'alpha-qa.json').read_text())[0]
check('all32reviewed empty patches remain exactly zero alpha',aq['empty_patch_pass'] and aq['observations']==alpha.audit_sheet(P/'packed-reference-atlas.png')['observations'])
strict=json.loads((P/'strict-gate-receipt.json').read_text())
check('strict combined sequence command passed this bounded case',strict['returncode']==0 and strict['bounded_motion_only'])
tests=json.loads((P/'test-receipt.json').read_text())
check('8 focused actual/negative-control tests executed',tests['tests_run']==8 and tests['returncode']==0 and all(sha(ROOT/b['path'])==b['sha256'] for b in [tests['script'],tests['tool']]))
browser=json.loads((P/'browser-qa.json').read_text())
check('19actual browser checks include current provenance receipt',len(browser['checks'])==19 and all(r['pass'] for r in browser['checks']) and not browser['errors'])
play=json.loads((P/'playback-receipt.json').read_text())
check('four before-after/current GIFs decoded with unchanged clocks',len(play)==4 and all(sha(P/name)==r['sha256'] and sum(r['decoded_durations_ms'])==r['total_ms'] for name,r in play.items()) and play['review-source.gif']['total_ms']==1900 and play['review-game.gif']['total_ms']==1300)
visual=json.loads((P/'visual-review.json').read_text())
check('explicit agent review bound to exact inspected pixels',visual['agent_motion_pass'] and all(sha(ROOT/r['path'])==r['sha256'] for r in visual['inspected']))
decision=json.loads((P/'review-decision.json').read_text())
check('bounded motion accepted without user art/proportion/production transfer',decision['bounded_numeric_pass'] and decision['agent_motion_pass'] and not decision['user_new_art_approved'] and not decision['proportion_family_locked'] and not decision['hidden_anatomy_certified'] and not decision['production_pass'])
(P/'audit-report.json').write_text(json.dumps(dict(state='INCOMPLETE',production_pass=False))+'\n')
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/isolated-motion-key-repair.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('documentation links resolve',not bad)
out=dict(checks=checks,passed_checks=len(checks),decision=decision['decision'],agent_motion_pass=True,production_pass=False)
(P/'audit-report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),decision=out['decision'])))
