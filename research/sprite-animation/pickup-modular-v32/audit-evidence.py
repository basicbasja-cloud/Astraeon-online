"""Check real files, unchanged prior evidence and limited passing review scope."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageSequence
import numpy as np
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'name':n,'pass':bool(v)})
 if not v:raise ValueError(n)
for directory,count in [('joint-tracking-ro-v30',180),('pickup-pilot-v31',71)]:
 d=json.loads((P.parent/directory/'evidence-manifest.json').read_text());check('all'+str(count)+'published '+directory+' files unchanged',len(d['files'])==count and all(sha(ROOT/r['path'])==r['sha256'] for r in d['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13exact approved W files unchanged',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
check('sole authorized research branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text());check('three actual raw generations/prompts/neutral part inputs bound',len(ledger['jobs'])==3 and all(sha(ROOT/r['path'])==r['sha256'] for j in ledger['jobs'] for r in [j['output'],j['prompt']]+j['input_files']) and all(not j['old_own_slash_used'] for j in ledger['jobs']))
parts=json.loads((P/'parts.json').read_text())['parts'];check('16 selected original painted slots, no claimed independent hair bank',len(parts)==16 and len({r['name'] for r in parts})==16 and 'head_hair' in {r['name'] for r in parts} and all(sha(ROOT/r['file'])==r['sha256'] and not r['mirrored'] for r in parts))
frames=json.loads((P/'frames.json').read_text());arrays=[]
for r in frames['frames']:
 assert sha(ROOT/r['path'])==r['sha256'];a=np.array(Image.open(ROOT/r['path']).convert('RGBA'));assert a.shape==(512,384,4);mask=a[:,:,3]>=128;assert not mask[0].any() and not mask[-1].any() and not mask[:,0].any() and not mask[:,-1].any();arrays.append(a)
check('8fixed384x512RGBA frames without opaque foreground cuts',len(arrays)==8)
check('full RGBA first/last images identical',np.array_equal(arrays[0],arrays[-1]))
for name,key,total in [('pickup-source-clock.gif','source_clock_gif_ms',1900),('pickup-game-clock.gif','game_clock_gif_ms',1300)]:
 with Image.open(P/name) as im:
  durations=[f.info['duration'] for f in ImageSequence.Iterator(im)];assert im.n_frames==8 and durations==frames[key] and sum(durations)==total
check('both8key GIF clocks/retiming decode exactly',True)
observer=json.loads((P/'pixel-observations.json').read_text());check('24actual visible surface matches without future pose input',not observer['later_pose_coordinates_used'] and len(observer['tracks'])==3 and all(len(v)==8 and all(r['status']=='visible' for r in v) for v in observer['tracks'].values()))
px=json.loads((P/'pixel-validation.json').read_text());check('both planted raw RGBA patches identical / held-out cuff under1px',all(r['all8_RGBA_patches_identical'] for r in px['planted_patch_pixels'].values()) and px['held_out_cuff_max_error_px']<1)
qa=json.loads((P/'browser-qa.json').read_text());check('13actual browser checks including negative binds and exact pixel reproduction',len(qa['checks'])==13 and all(c['pass'] for c in qa['checks']) and not qa['errors'])
check('12focused regressions passed',bool(re.search(r'Ran 12 tests.*\n\nOK\s*$',(P/'regression-tests.txt').read_text(),re.S)))
file=ROOT/'skills/modular-eight-direction-sprites/scripts/modular-motion-review.py';s=importlib.util.spec_from_file_location('motion',file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);fresh=m.review(json.loads((P/'review-case.json').read_text()),ROOT)
check('recomputed19bounded motion checks pass without factory/user approval claims',fresh['motion_review_pass'] and len(fresh['checks'])==19 and not fresh['full_factory_production_pass'] and not fresh['user_art_approved'])
check('old6px/.25criteria retain zerofoot drift and source phase under.01',all(v==[0,0] for v in fresh['observed_planted_range_px'].values()) and fresh['held_out_source_phase_max_difference']<.01)
check('unchanged generic surface checker still declines anatomy/contact/production',all(not json.loads((P/'surface-review.json').read_text())[n] for n in ('anatomy_pass','contact_pass','production_pass')))
# Placeholder allows its documentation link to be checked on first invocation.
(P/'audit-report.json').write_text('{}\n')
bad=[]
for p in [*P.glob('*.md'),ROOT/'skills/modular-eight-direction-sprites/references/source-driven-part-motion.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).exists():bad.append([str(p),target])
check('new documentation links resolve',not bad)
report={'checks':checks,'passed_checks':len(checks),'motion_review_pass':True,'approval':'AGENT_MOTION_REVIEW_PASS','full_factory_production_pass':False,'scope':'Evidence integrity, unchanged historical failures and one authored-view motion review. Not full anatomical detector/physics/user art approval.'};(P/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'evidence_checks':len(checks),'motion_review_pass':True,'full_factory_production_pass':False}))
