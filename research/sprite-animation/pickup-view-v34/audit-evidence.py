"""Recompute bounded checks and require a separately authored visual receipt."""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
from PIL import Image,ImageSequence
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,ok):
 checks.append(dict(name=n,pass_=bool(ok)))
 if not ok:raise ValueError(n)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33']:
 frozen=json.loads((P.parent/folder/'evidence-manifest.json').read_text());check(folder+' all published evidence unchanged',all(sha(ROOT/f['path'])==f['sha256'] for f in frozen['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13 protected W files unchanged',len(w['files'])==13 and all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files']))
check('sole authorized branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
ledger=json.loads((P/'generation-ledger.json').read_text());check('5 actual generation job prompts/raw files/inputs unchanged; no MiniMax',ledger['actual_imagegen_jobs']==len(ledger['jobs'])==5 and not ledger['minimax_called'] and not ledger['provider_generated_video'] and all(sha(ROOT/r['path'])==r['sha256'] for j in ledger['jobs'] for r in [j['output'],j['prompt']]+j['input_files']) and all(not j['old_own_slash_used'] for j in ledger['jobs']))
check('CC0 source license bound',sha(ROOT/ledger['source_license']['path'])==ledger['source_license']['sha256'])
reviewer=load('viewreview',ROOT/'skills/modular-eight-direction-sprites/scripts/directional-part-review.py');case=json.loads((P/'view-case.json').read_text());fresh=reviewer.review(case,ROOT);check('fresh bound new-view authoring and image-region checks pass',fresh['numeric_view_check_pass'] and not fresh['production_pass'])
check('stored view report equals fresh result',fresh==json.loads((P/'view-review.json').read_text()))
observer=load('observerv2',ROOT/'skills/modular-eight-direction-sprites/scripts/rigid-surface-observer-v2.py');surface=load('surface',ROOT/'skills/modular-eight-direction-sprites/scripts/planted-surface-review.py');pixels=json.loads((P/'pixel-review.json').read_text())
for style in ['original','silver','bald']:
 obs=observer.observe(json.loads((P/(style+'-observer-case.json')).read_text()),ROOT);check(style+' actual pixel observations recompute exactly',obs==pixels[style]['actual_pixel_observations'])
 report=surface.audit(json.loads((P/(style+'-surface-case.json')).read_text()),ROOT);check(style+' 0px planted shoes / source phase under unchanged gates',report==pixels[style]['surface_review'] and report['numerical_surface_check_pass'] and all(report['markers'][n]['range_xy_px']==[0,0] for n in ['surface.near_boot_toe','surface.far_boot_toe']))
bundle=json.loads((P/'frames.json').read_text())
for style in bundle['styles']:
 for clock,durations in bundle['clocks'].items():
  with Image.open(P/f'{style}-{clock}-clock.gif') as im:check(style+'/'+clock+' actual GIF sample timing',im.n_frames==8 and [f.info['duration'] for f in ImageSequence.Iterator(im)]==durations)
with Image.open(P/'two-view-compare.gif') as im:check('synchronized original/new physical view comparison',im.n_frames==8 and [f.info['duration'] for f in ImageSequence.Iterator(im)]==bundle['clocks']['game'])
for name,count in [('regression-tests.txt',12),('observer-regression-tests.txt',5)]:check(str(count)+' focused regressions pass',bool(re.search(r'Ran '+str(count)+r' tests.*\n\nOK\s*$',(P/name).read_text(),re.S)))
browser=json.loads((P/'browser-qa.json').read_text());check('12 actual browser checks pass',len(browser['checks'])==12 and all(c['pass'] for c in browser['checks']) and not browser['errors'])
visual=json.loads((P/'visual-review.json').read_text());expected=[dict(path=r['path'],sha256=r['sha256']) for rows in case['styles'].values() for r in rows];check('separate exact-image agent visual receipt, no user approval transfer',visual['frames']==expected and visual['reviewer']=='agent' and visual['decision']=='PASS_SECOND_VIEW_PART_MOTION_REVIEW' and all(c['pass'] for c in visual['checks']) and not visual['user_new_art_approved'])
check('actual failed hair and source matcher abstentions retained',all((P/f).exists() for f in ['failure-controls/hair-misfit.png','failure-controls/thigh-opening-exposure.png','failure-controls/large-cuff-patch-review.json','failure-controls/small-cuff-patch-review.json']))
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',ROOT/'skills/modular-eight-direction-sprites/references/physical-view-and-texture-support.md']:
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('new local documentation links resolve',not bad)
result=dict(checks=checks,passed_checks=len(checks),view_numeric_checks=len(fresh['checks']),approval='AGENT_SECOND_VIEW_PART_MOTION_REVIEW',user_new_art_approved=False,full_factory_production_pass=False,scope='Second physical camera/one source action,18styled parts. Not all directions, automatic anatomy, object contact or game admission.')
(P/'audit-report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['passed_checks','view_numeric_checks','approval']}))
