"""Frozen baseline, real appearances, rejection controls and scoped approval."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageSequence
import numpy as np
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,ok):
 checks.append({'name':n,'pass':bool(ok)})
 if not ok:raise ValueError(n)
for directory,count in [('joint-tracking-ro-v30',180),('pickup-pilot-v31',71),('pickup-modular-v32',91)]:
 r=json.loads((P.parent/directory/'evidence-manifest.json').read_text());check(str(count)+'published '+directory+' files unchanged',len(r['files'])==count and all(sha(ROOT/f['path'])==f['sha256'] for f in r['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13protected approved W files unchanged',len(w['files'])==13 and all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files']))
feedback=json.loads((P/'user-v32-smoothness-feedback.json').read_text());check('exact v32positive smoothness feedback bound without approval transfer',feedback['user_quote']=='สมูทขึ้นเยอะ ต่อเลย' and all(sha(ROOT/r['path'])==r['sha256'] for r in feedback['files']))
check('sole authorized branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text());check('3actual raw imagegen jobs and exact prompts/input assets preserved',len(ledger['jobs'])==3 and all(sha(ROOT/r['path'])==r['sha256'] for j in ledger['jobs'] for r in [j['output'],j['prompt']]+j['input_files']) and all(not j['old_own_slash_motion_input'] for j in ledger['jobs']))
parts=json.loads((P/'parts.json').read_text())['parts'];check('complete5source parts with originalraw hashes retained',len(parts)==5 and all(sha(ROOT/r['path'])==r['sha256'] and sha(ROOT/r['raw_file'])==r['raw_sha256'] and r['retained_RGBA_unchanged'] and not r['mirrored'] for r in parts))
file=ROOT/'skills/modular-eight-direction-sprites/scripts/hair-swap-review.py';s=importlib.util.spec_from_file_location('hairreview',file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);case=json.loads((P/'swap-case.json').read_text());fresh=m.review(case,ROOT);check('86fresh actual pixel/bind/clock/eye checks pass',fresh['replacement_numeric_pass'] and len(fresh['checks'])==86)
check('actual body outside head union unchanged / styles distinct',all(f['changed_pixels_outside_head_pass_union']==0 for v in fresh['actual_pixel_measurements'].values() for f in v) and fresh['distinct_silhouette_pixels']==6673)
check('all8projected eye interiors identical across new appearances',len(fresh['projected_eye_pixel_checks'])==8 and all(r['silver_vs_auburn_different_pixels']==r['silver_vs_bald_different_pixels']==0 for r in fresh['projected_eye_pixel_checks']))
qa=json.loads((P/'browser-qa.json').read_text());check('14actual browser controls/reproduction/live switching pass',len(qa['checks'])==14 and all(r['pass'] for r in qa['checks']) and not qa['errors'])
check('12focused replacement regressions pass',bool(re.search(r'Ran 12 tests.*\n\nOK\s*$',(P/'regression-tests.txt').read_text(),re.S)))
source=json.loads((P/'source-motion-review.json').read_text());check('3new appearances retain old0px/.25phase support gates',set(source)=={'silver','auburn','bald'} and all(r['surface_review']['numerical_surface_check_pass'] and r['source_phase_max_difference']<.01 and all(v['range_xy_px']==[0,0] for n,v in r['surface_review']['markers'].items() if 'boot' in n) and not r['surface_review']['production_pass'] for r in source.values()))
opacity=json.loads((P/'opacity-control-review.json').read_text());check('executed alpha leak counterfactual retained and corrected',opacity['without_material_differing_eye_pixels']==538 and opacity['without_material_max_channel_difference']==3 and opacity['with_material_RGBA_identical'])
material=json.loads((P/'material-receipt.json').read_text());check('explicit opaque head material policy, original exempt',material['changed_alpha_pixels']==409028 and 'alpha>=240' in material['policy'])
clock=json.loads((P.parent/'pickup-modular-v32/frames.json').read_text())
for style in ['original','silver','auburn','bald']:
 for name,key in [('game-clock','game_clock_gif_ms'),('source-clock','source_clock_gif_ms')]:
  with Image.open(P/(style+'-'+name+'.gif')) as im:assert im.n_frames==8 and [f.info['duration'] for f in ImageSequence.Iterator(im)]==clock[key]
check('8standalone GIFs decode exact old8key source/game clocks',True)
with Image.open(P/'hair-swap-compare.gif') as im:check('synchronized comparison has8same-clock exposures',im.n_frames==8 and [f.info['duration'] for f in ImageSequence.Iterator(im)]==clock['game_clock_gif_ms'])
visual=json.loads((P/'visual-review.json').read_text());expected=[{'path':r['path'],'sha256':r['sha256']} for style in ['silver','auburn','bald'] for r in case['styles'][style]];check('separate exact24image agent visual receipt matches',visual['reviewer']=='agent' and visual['decision']=='PASS_ONE_VIEW_HAIR_SWAP_REVIEW' and visual['frames']==expected and all(r['pass'] for r in visual['checks']))
check('3official sources actually acquired with bounded review levels',all(json.loads((P/('source-'+n+'.json')).read_text())['http_status']==200 for n in ('skins','attachments','canvasitem')))
(P/'audit-report.json').write_text('{}\n');bad=[]
for p in [*P.glob('*.md'),ROOT/'skills/modular-eight-direction-sprites/references/hair-replacement-and-appearance-stability.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).exists():bad.append([str(p),target])
check('new local documentation links resolve',not bad)
report={'checks':checks,'passed_checks':len(checks),'approval':'AGENT_ONE_VIEW_HAIR_SWAP_REVIEW_PASS','replacement_review_pass':True,'user_new_hair_art_approved':False,'full_factory_production_pass':False,'scope':'One fixed camera/one action, complete shared head/two style pairs and unchanged v32 motion. No all-view, learned anatomy or prop/physics approval.'};(P/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'evidence_checks':len(checks),'approval':report['approval']}))
