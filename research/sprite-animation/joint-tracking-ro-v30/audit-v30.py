"""Evidence-integrity audit; passing is not art/anatomy/production acceptance."""
import gzip,hashlib,json,math,re,struct,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];STUDY=Path(__file__).resolve().parent
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),'detail':detail})
 if not ok:raise ValueError(name+': '+str(detail))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((ROOT/'research/sprite-animation/rpg-motion-foundation-v29/protected-W.json').read_text());pfiles=[]
for f in protected['files']:
 actual=sha(ROOT/f['path']);pfiles.append(dict(f,actual_sha256=actual,unchanged=actual==f['expected_sha256']))
check('exact accepted W preserved',len(pfiles)==13 and all(f['unchanged'] for f in pfiles))
(STUDY/'protected-W.json').write_text(json.dumps({'baseline':protected['baseline'],'files':pfiles},indent=2)+'\n')
render=json.loads((STUDY/'benchmark/render-receipt.json').read_text());check('actual external render source bound',sha(ROOT/render['source_file'])==render['source_sha256'])
images=0
for directory in (STUDY/'benchmark').iterdir():
 if not directory.is_dir():continue
 c=json.loads((directory/'case.json').read_text());truth=json.loads((directory/'truth.json').read_text())
 for f,t in zip(c['frames'],truth['frames']):
  assert sha(ROOT/f['path'])==f['sha256']==t['candidate_image_sha256'];assert abs(f['source_time_seconds']-t['source_time_seconds'])<1e-6
  with Image.open(ROOT/f['path']) as im:assert list(im.size)==[320,320]
  images+=1
 for filename,casefile in [('tracks.json','case.json'),('assisted-tracks.json','assisted-case.json')]:
  tr=json.loads((directory/filename).read_text());assert tr['case_sha256']==sha(directory/casefile);assert tr['reference_source_sha256']==truth['source_sha256'];assert not tr['production_pass'] and not tr['anatomy_pass'];assert all(f['image_sha256']==t['candidate_image_sha256'] for f,t in zip(tr['frames'],truth['frames']))
  if filename.startswith('assisted'):assert tr['future_reference_coordinates_used'] and not tr['future_unseeded_truth_used'] and tr['labelled_seed_frames']==[0,5,10,15]
check('48 fixed-canvas images, case/report/truth bindings and seed disclosure',images==48)
for reportfile in ('tracking-benchmark.json','assisted-tracking-benchmark.json'):
 report=json.loads((STUDY/reportfile).read_text());assert report['seed_frames_excluded_from_scoring'] and report['art_anatomy_accuracy'] is None and report['percentile_method']=='numpy.percentile linear'
 for r in report['runs']:assert r['proposal_count']<r['held_out_target_count'] and abs(r['coverage']-r['proposal_count']/r['held_out_target_count'])<1e-12
check('coverage with held-out error metrics, no anatomy inference',True)
inv=json.loads((STUDY/'new-preset-inventory.json').read_text());samples=json.loads(gzip.decompress((STUDY/'new-preset-samples.json.gz').read_bytes()));records=0;poses=0
for f,bank in zip(inv['files'],samples['banks']):
 source=ROOT/f['path'];assert sha(source)==f['sha256']==bank['source_sha256'];raw=source.read_bytes();size,kind=struct.unpack('<II',raw[12:20]);gltf=json.loads(raw[20:20+size]);assert [len(s['joints']) for s in gltf['skins']]==[23];assert len(gltf['animations'])==len(f['clips'])==len(bank['clips']);assert len(bank['bones'])==23
 records+=len(bank['clips']);poses+=sum(len(c['samples']) for c in bank['clips'])
check('14 actual licensed source banks /173 records /1397 evaluated poses',len(inv['files'])==14 and records==173 and poses==1397)
index=json.loads((STUDY/'preset-clip-index.json').read_text());check('rest and terminal pose names separately counted',index['categories']=={'motion_candidate':153,'rest':14,'terminal_or_inactive_pose_name':6})
check('CC0 license present, source exact bytes retained','CC0' in (STUDY/'preset-source/KayKit-License.txt').read_text())
ro=json.loads((STUDY/'ro-action-audit.json').read_text());ok=[r for r in ro['requests'] if r['status']=='decoded'];failed=[r for r in ro['requests'] if r['status']=='failed'];check('RO audit actual request/exposure counts',len(ro['requests'])==1340 and len(ok)==1275 and len(failed)==65 and sum(len(r['frames']) for r in ok)==5927)
family=ro['class_family_render_ids'];available={r['job'] for r in ok if r['gender']=='male' and r['direction']==7 and r['job'] in family};check('indexed family coverage retains 5 gaps',len(family)==85 and len(available)==80 and set(family)-available=={20,4021,4069,4264,4305})
untimed=0
for r in ok:
 time=0
 if any(f['duration_ms'] is None for f in r['frames']):
  assert len(r['frames'])==1 and r['duration_ms'] is None;untimed+=1
  cache=STUDY/r['file']
  if cache.exists():assert sha(cache)==r['sha256']
  continue
 for f in r['frames']:assert abs(f['source_pts_ms']-time)<1e-6;assert f['duration_ms']>0;time+=f['duration_ms']
 assert abs(time-r['duration_ms'])<1e-6
 cache=STUDY/r['file']
 if cache.exists():assert sha(cache)==r['sha256']
check('RO known native clocks and285explicitly untimed single images',untimed==285)
boards=0
for name in ('ro-grid-manifest.json','ro-full-frame-manifest.json'):
 for b in json.loads((STUDY/name).read_text())['boards']:assert sha(STUDY/b['file'])==b['sha256'];boards+=1
check('37 bounded RO review boards',boards==37)
pose=json.loads((STUDY/'pose-proposals.json').read_text());check('5 actual pose model inputs bound to unchanged images',len(pose['results'])==5 and all(sha(Path(r['file']) if Path(r['file']).is_absolute() else ROOT/r['file'])==r['image_sha256'] for r in pose['results']))
check('model outputs not accuracy probabilities',all(not p['score_is_accuracy_probability'] and not p['anatomical_identity_verified'] for r in pose['results'] for p in r['points'].values()))
qa=json.loads((STUDY/'browser-qa.json').read_text());check('12 browser checks passed',qa['checks']==12 and all(t['pass'] for t in qa['tests']))
run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'skills/modular-eight-direction-sprites/scripts/tests'),'-p','test_joint_image_track.py','-v'],capture_output=True,text=True);(STUDY/'python-tests.txt').write_text(run.stdout+run.stderr);check('15 focused regression tests passed',run.returncode==0 and 'Ran 15 tests' in run.stderr)
# Verify current local documentation links only; external receipts retain retrieval state.
bad=[]
for p in STUDY.glob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if '://' in target or target.startswith('#'):continue
  if not (p.parent/target.split('#')[0]).resolve().exists():bad.append([p.name,target])
check('current local documentation links',not bad,bad)
report={'schema':'sprite-v30-evidence-audit-v1','checks':checks,'passed_checks':len(checks),'production_pass':False,'anatomy_accuracy_proved':False,'scope':'Bound evidence integrity and executable regressions only; no universal detector/art/retarget/parts approval.'};(STUDY/'audit-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(checks),'production_pass':False}))
