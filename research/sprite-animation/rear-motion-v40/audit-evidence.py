"""Audit a rejected artwork honestly; a sound negative result is not art approval."""
import hashlib,importlib.util,json,re,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,value):
    checks.append(dict(name=name,pass_=bool(value)))
    if not value:raise ValueError(name)
def module(name,file):
    s=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35','neck-motion-v36','proportion-audit-v37','coherent-motion-v38','recovery-key-v39']:
    manifest=json.loads((P.parent/folder/'evidence-manifest.json').read_text());check(folder+' exact frozen evidence unchanged',all(sha(ROOT/r['path'])==r['sha256'] for r in manifest['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13 exact protected W files',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
check('same sole authorized branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
accept=json.loads((P/'user-v39-acceptance.json').read_text());check('scoped exact v39 user acceptance bindings',len(accept['files'])==12 and all(sha(ROOT/b['path'])==b['sha256'] for b in accept['files']))
ledger=json.loads((P/'generation-ledger.json').read_text());bindings=[b for job in ledger['jobs'] for b in [job['prompt'],job['output']]+job['inputs']]
check('7 genuine still jobs exact direct inputs and outputs',ledger['actual_still_image_jobs']==7 and len(ledger['jobs'])==7 and all(sha(ROOT/b['path'])==b['sha256'] for b in bindings))
check('no provider video MiniMax or old own attacks',not any(ledger[k] for k in ['generated_video','minimax_called','old_own_attack_used']))
repro=json.loads((P/'reference-reproduction.json').read_text());check('12 exact provider reference plates reproduced',repro['exact'] and len(repro['files'])==12 and all(r['before']==r['reproduced']==sha(ROOT/r['path']) for r in repro['files']))
source=json.loads((P/'source/source.json').read_text());old=json.loads((P.parent/'pickup-pilot-v31/source/source.json').read_text());tool=module('camera','skills/modular-eight-direction-sprites/scripts/physical-view-source-audit.py');actual=tool.audit(old,source);sq=json.loads((P/'source-view-qa.json').read_text())
check('source camera/world/clock and independent136point projection',actual['source_view_pass'] and actual['max_world_error']==0 and actual['max_projection_error_px']<.001 and len(actual['projected_joint_depths'])==136 and actual['projected_joint_depths']==sq['projected_joint_depths'] and sq['source_view_pass'])
check('actual source GLB and all captured pixels',sha(ROOT/source['source_file'])==source['source_sha256'] and all(sha(ROOT/f['path'])==f['sha256'] for f in source['frames']))
case=json.loads((P/'motion-contract.json').read_text());motion=module('motion','skills/modular-eight-direction-sprites/scripts/view-conditioned-motion.py');q=json.loads((P/'motion-qa.json').read_text());check('all current actual pixel metrics independently reproduced',q==motion.run(case,ROOT,P/'renders'))
review=q['variants']['review'];check('phase-only false positive caught by strict fixed guide',review['phase_neck_support_pass'] and not review['metrics_pass'] and 26<review['guide_fidelity']['maximum_error_px']<26.1 and review['guide_fidelity']['budget_px']==8)
check('visible neck and separated boot gates unchanged',max(x['endpoint_residual_px'] for x in review['neck'])<.784 and all(x['pass_'] for x in review['neck']) and review['boot_component_review']['pass_'] and all(v['rendered_range_px']==[5,2] for v in review['support'].values()) and case['planted_surface_budget_px']==6 and case['receiver_endpoint_budget_px']==3 and case['phase_warning_fraction']==.25)
check('retained before keys still fail temporal phase',not q['variants']['raw8']['projected_phase']['pass_'])
native=Image.open(P/'body-attempt3-raw.png').convert('RGBA');packing=json.loads((P/'packing-receipt.json').read_text());valid=True
for i in range(8):
    crop=native.crop((i%4*384,i//4*512,(i%4+1)*384,(i//4+1)*512));out=Image.new('RGBA',(384,512));out.paste(crop,(0,23 if i>=4 else 0));valid &= np.array_equal(np.array(out),np.array(Image.open(P/f'body-canonical/{i:02}.png')))
check('common row packing exact and low-alpha clipping disclosed',valid and packing['row_offsets']==[[0,0],[0,23]] and packing['clipped_nonzero_alpha_pixels']==10 and packing['clipped_max_alpha']==1 and not packing['visible_foreground_cut_alpha128'])
norm=json.loads((P/'normalization.json').read_text());valid=True
for r in norm:
    raw=Image.open(ROOT/r['raw']['path']).convert('RGBA');w,h=raw.size;expected=[w/512,0,w/8,0,h/512,0];valid &= r['inverse_matrix']==expected and np.array_equal(np.array(raw.transform((384,512),Image.Transform.AFFINE,expected,Image.Resampling.BICUBIC)),np.array(Image.open(P/f'repaired-key{r["key"]}.png')))
check('two exact known-canvas repair inverses no feature fit',valid and len(norm)==2)
same=[]
for i in [0,2,3,5,6,7]:
    for mode in ['full','body','head','collar']:same.append(np.array_equal(np.array(Image.open(P/f'renders/review/{mode}/{i:02}.png')),np.array(Image.open(P/f'renders/raw8/{mode}/{i:02}.png'))))
check('6 other keys and24actual render passes unchanged',len(same)==24 and all(same))
alpha=module('alpha','skills/modular-eight-direction-sprites/scripts/coherent-strip-alpha.py');aq=alpha.audit_sheet(P/'body-attempt3-raw.png');check('native A1failure retained no fabricated alpha approval',not aq['empty_patch_pass'] and any(o['art_index']==3 and o['maximum_alpha']==1 and not o['pass_'] for o in aq['observations']))
cmd=[sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/view-conditioned-motion.py'),'--contract',str(P/'motion-contract.json'),'--renders',str(P/'renders'),'--out',str(P/'strict-recomputed-qa.json'),'--root',str(ROOT),'--require-motion'];strict=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
(P/'strict-gate-receipt.json').write_text(json.dumps(dict(returncode=strict.returncode,expected_returncode=1,reason='Actual painted candidate must remain rejected for fixed-guide mismatch',stdout=strict.stdout,stderr=strict.stderr),indent=2)+'\n');check('strict actual command refuses candidate exit1',strict.returncode==1 and json.loads((P/'strict-recomputed-qa.json').read_text())==q)
for file,count in [('source-test-receipt.json',8),('motion-test-receipt.json',13)]:
    t=json.loads((P/file).read_text());check(file+' executed controls',t['tests']==count and t['failures']==t['errors']==0)
b=json.loads((P/'browser-qa.json').read_text());check('19actual browser checks and no errors',len(b['checks'])==19 and all(c['pass'] for c in b['checks']) and not b['errors'])
play=json.loads((P/'playback-receipt.json').read_text());check('8GIFs actual decoded clocks and hashes',len(play)==8 and all(sha(P/name)==r['sha256'] and r['encoded_frames']==8 and r['decoded_durations_ms']==case['clocks']['source' if '-source.' in name else 'game'] for name,r in play.items()))
visual=json.loads((P/'visual-review.json').read_text());check('exact-image manual rejection bound to inspected images',not visual['agent_motion_pass'] and all(sha(ROOT/b['path'])==b['sha256'] for b in visual['inspected']))
decision=json.loads((P/'review-decision.json').read_text());check('no new art or anatomy production approval',decision['source_camera_proof_pass'] and decision['user_previous_v39_accepted'] and not any(decision[k] for k in ['strict_numeric_pass','agent_motion_pass','user_new_art_approved','proportion_family_locked','hidden_anatomy_certified','production_pass']))
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/physical-view-phase-and-guide-fidelity.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('all new documentation links resolve',not bad)
(P/'audit-report.json').write_text(json.dumps(dict(checks=checks,passed_checks=len(checks),decision=decision['decision'],agent_motion_pass=False,production_pass=False),indent=2)+'\n');print(json.dumps(dict(checks=len(checks),decision=decision['decision'])))
