"""Recompute source/art evidence checks while retaining known production failures."""
import hashlib,json,math,re,subprocess,sys
from pathlib import Path
from PIL import Image,ImageSequence
import numpy as np
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
 checks.append({'name':name,'pass':bool(ok)})
 if not ok:raise ValueError(name)
# Preserve the previous published evidence/tools, not just selected new artifacts.
old=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/evidence-manifest.json').read_text());check('all180v30published evidence hashes unchanged',all(sha(ROOT/f['path'])==f['sha256'] for f in old['files']))
protected=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/protected-W.json').read_text());check('exact13accepted W files unchanged',len(protected['files'])==13 and all(sha(ROOT/f['path'])==f['expected_sha256'] for f in protected['files']))
s=json.loads((P/'source/source.json').read_text());check('freshCC0source exact hash and23named bones',sha(ROOT/s['source_file'])==s['source_sha256'] and len(s['named_bones'])==23 and not s['old_own_rig_or_motion_used'])
check('8actual source frames on fixed canvas and known clock',len(s['frames'])==8 and s['source_duration_ms']==1300 and all(sha(ROOT/f['path'])==f['sha256'] for f in s['frames']))
check('chest is not promoted into nonexistent source neck',all('neck' not in f['points'] and f['points']['chest']['source_bone']=='chest' for f in s['frames']))
ledger=json.loads((P/'generation-ledger.json').read_text())
for r in ledger['attempts']:
 assert sha(ROOT/r['file'])==r['sha256'];assert sha(ROOT/r['prompt_file'])==r['prompt_sha256'];assert all(sha(ROOT/f['path'])==f['sha256'] for f in r['input_files']);assert not r['old_own_attack_motion_input']
check('fiveactual generations bound to exact prompts and inputs',len(ledger['attempts'])==5)
check('known clipped attempts retained, selection unclipped at declared threshold',ledger['attempts'][2]['foreground_pixels_on_column_boundaries_at_alpha128']>0 and ledger['attempts'][3]['foreground_pixels_on_column_boundaries_at_alpha128']>0 and ledger['attempts'][4]['foreground_pixels_on_column_boundaries_at_alpha128']==0)
pack=json.loads((P/'packing.json').read_text());raw=np.array(Image.open(ROOT/pack['raw_file']).convert('RGBA'))
for f in pack['frames']:
 assert sha(ROOT/f['path'])==f['sha256'];im=np.array(Image.open(ROOT/f['path']).convert('RGBA'));x,y=f['cell_origin_in_raw'];dy=f['authoring_row_translation_px'][1];crop=raw[y:y+512-dy,x:x+384];current=im[dy:];mask=crop[:,:,3]>=128;assert np.array_equal(current[mask],crop[mask]);assert not (im[:dy,:,3]>=128).any()
check('fixedcells/share-scale/common row origin preserves opaque-enough pixels',pack['shared_scale']==1 and pack['row_origin_offsets']==[0,32] and not pack['per_frame_fit'])
for name in ('pickup-review.gif','source-review.gif'):
 with Image.open(P/name) as im:
  durations=[f.info['duration'] for f in ImageSequence.Iterator(im)];assert im.n_frames==8 and durations==pack['gif_durations_ms'] and sum(durations)==1900
check('both actual GIF clocks decode8frames/1900ms',True)
case=json.loads((P/'image-case.json').read_text());tr=json.loads((P/'image-tracking/tracks.json').read_text());check('surface tracker binds current imagecase and discloses later manual keys',tr['case_sha256']==sha(P/'image-case.json') and tr['future_manual_annotations_used'])
check('source joints stay unknown instead of inferring anatomy',not tr['hidden_joint_coordinates_inferred'] and all(p['status']=='unknown' for f in tr['frames'] for n,p in f['points'].items() if not n.startswith('surface.')))
proposals=sum(p['status']=='proposal' for f in tr['frames'] for n,p in f['points'].items() if n.startswith('surface.'));check('zero conservative surface proposals accurately reported',proposals==0)
# Recompute actual visible-surface diagnostics, never override failed production.
run=subprocess.run([sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/planted-surface-review.py'),'--case',str(P/'image-case.json'),'--root',str(ROOT),'--out',str(P/'surface-review.json')],capture_output=True,text=True);assert run.returncode==0
r=json.loads((P/'surface-review.json').read_text());check('known horizontal support drift caught',r['markers']['surface.far_boot_toe']['range_xy_px']==[55,2] and r['markers']['surface.near_boot_toe']['range_xy_px']==[62,5] and not r['production_pass'] and not r['contact_pass'])
check('held-out source-relative early-recovery issue retained',any(i.get('frame')==5 and i['kind']=='SOURCE_RELATIVE_PHASE_DISAGREEMENT' for i in r['issues']))
for pattern,count,log in [('test_planted_surface_review.py',11,'surface-tests.txt'),('test_joint_image_track.py',15,'baseline-tracker-tests.txt')]:
 run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'skills/modular-eight-direction-sprites/scripts/tests'),'-p',pattern,'-v'],capture_output=True,text=True);(P/log).write_text(run.stdout+run.stderr);check(str(count)+'focused regressions pass: '+pattern,run.returncode==0 and 'Ran '+str(count)+' tests' in run.stderr)
qa=json.loads((P/'browser-qa.json').read_text());check('8browser behavior checks pass',len(qa['checks'])==8 and all(c['pass'] for c in qa['checks']))
# Write receipt before checking links to its own filename.
(P/'audit-report.json').write_text('{}\n')
bad=[]
for p in P.glob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).exists():bad.append([p.name,target])
check('local documentation links exist',not bad)
report={'schema':'v31-pilot-evidence-audit-v1','checks':checks,'passed_checks':len(checks),'generation_attempts':5,'retained_surface_proposals':0,'visible_surface_warnings':r['issues'],'production_pass':False,'contact_pass':False,'anatomy_pass':False,'modular_parts_complete':False,'scope':'Evidence integrity and correct rejection/abstention behavior. Does not approve failed pickup art or universal tracking.'};(P/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'new_tests':11,'baseline_tests':15,'browser_checks':8,'production_pass':False}))
