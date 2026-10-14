"""Verify this small static review without approving concept similarity."""
import hashlib,json,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
checks=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
    checks.append(dict(name=name,pass_=bool(ok)))
    if not ok:raise ValueError(name)

for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35','neck-motion-v36']:
    d=json.loads((P.parent/folder/'evidence-manifest.json').read_text())
    check(folder+' frozen evidence unchanged',all(sha(ROOT/r['path'])==r['sha256'] for r in d['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text())
check('exact approved W preserved',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
case=json.loads((P/'observations.json').read_text())
report=json.loads((P/'proportion-report.json').read_text())
check('all candidate image hashes bound',all(sha(ROOT/r['path'])==r['sha256'] for c in case['candidates'] for r in c['images'].values()))
for source,row in zip(case['candidates'],report['candidates']):
    im=np.array(Image.open(ROOT/source['images']['full']['path']).convert('RGBA'))
    ys,xs=np.nonzero(im[:,:,3]>=128)
    check(source['name']+' height measured from actual alpha',row['full_alpha128_bbox']==[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] and row['total_visible_height_px']==ys.max()+1-ys.min())
check('neck excluded from declared crown-to-jaw head height',report['candidates'][0]['visible_crown_to_jaw_px']==105 and report['candidates'][0]['head_alpha128_bbox'][3]-report['candidates'][0]['head_alpha128_bbox'][1]==116)
check('missing original concept provenance not fabricated',not case['concept_observation']['exact_attachment_file_available'] and case['concept_observation']['numerical_concept_target'] is None and not report['exact_concept_pixel_comparison'] and not report['matched_camera_reference_available'])
gap=case['concept_observation']['existing_gap_receipt']
check('prior actual attachment provenance gap bound unchanged',sha(ROOT/gap['path'])==gap['sha256'])
check('current geometry is not used to auto-approve concept or motion',not report['production_pass'] and not report['animation_keys_modified'] and all(not r['approved_against_concept'] for r in report['candidates']))
motion=json.loads((P.parent/'neck-motion-v36/motion-qa.json').read_text())
check('known prior contact failure preserved',not motion['variants']['review']['motion_metrics_pass'])
check('same sole branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
(P/'audit-report.json').write_text(json.dumps(dict(state='INCOMPLETE',production_pass=False))+'\n')
bad=[]
for file in [P/'README.md',ROOT/'skills/modular-eight-direction-sprites/references/concept-proportion-review.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        if '://' not in target and not target.startswith('#') and not (file.parent/target.split('#')[0]).exists():bad.append([str(file),target])
check('documentation links resolve',not bad)
out=dict(checks=checks,passed_checks=len(checks),decision=report['decision'],concept_proportion_pass=False,production_pass=False)
(P/'audit-report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),concept_proportion_pass=False)))
