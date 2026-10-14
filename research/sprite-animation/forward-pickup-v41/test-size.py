"""Actual approved character + held-out neutral and visible-contour failures."""
import copy,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def mod(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
size=mod('character-size-audit');floor=mod('visible-floor-surfaces');checks=[]
def check(name,ok):
    assert ok,name
    checks.append(dict(name=name,pass_=True))
def binding(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
c=json.loads((P/'size-locked-contract.json').read_text());before=json.loads((P/'before-size-contract.json').read_text());baseline=copy.deepcopy(c);baseline['candidate_frames']=[binding(P.parent/f'recovery-key-v39/renders/review/full/{i:02}.png') for i in range(8)];baseline['raw_frames']=baseline['candidate_frames'];baseline['matrices']=[[1,0,0,1,0,0] for _ in range(8)]
baseline.pop('part_proportion_contract',None) # exact accepted-image identity control
# Positive control is the exact approved reference itself, not a new proportion
# approval manufactured for a generated character.
baseline['head_body_family_review']=dict(pass_=True,reference_sha256=baseline['reference']['sha256'],candidate_sha256=[f['sha256'] for f in baseline['candidate_frames']]);baseline['head_body_family_review']['pass']=True
q=size.run(baseline,ROOT);current=size.run(c,ROOT);old=size.run(before,ROOT)
check('exact accepted reference is a positive size-control',q['character_size_pass'])
d=copy.deepcopy(baseline);d['reference']=d['reference_gif'];check('opaque GIF512px canvas is not a399px character measurement',not size.run(d,ROOT)['checks']['reference_foreground_observable'])
check('legitimate crouch height is not forced to standing399px',q['character_size_pass'] and q['all_candidate_visible_extents'][3]['height']<399)
check('before normalization wrong416px neutral rejected',old['neutral_comparison'][0]['height_error_px']==17 and not old['neutral_comparison'][0]['pass_'])
check('single rest calibration now399px and480ground',current['neutral_comparison'][0]['pass_'] and current['neutral_comparison'][0]['height_error_px']==current['neutral_comparison'][0]['bottom_y_error_px']==0)
check('held-out420px clipped return does not inherit calibration pass',not current['character_size_pass'] and current['neutral_comparison'][1]['observed_height_px']==420 and current['neutral_comparison'][1]['measurement_status']=='CLIPPED_LOWER_BOUND')
d=copy.deepcopy(baseline);d['head_body_family_review']={};check('matching overall height cannot certify head/body proportions',not size.run(d,ROOT)['checks']['head_body_family_review_bound'])
d=copy.deepcopy(baseline);d['matrices'][3][4]=1;check('per-frame root fit rejected',not size.run(d,ROOT)['checks']['one_positive_uniform_bank_transform'])
d=copy.deepcopy(baseline);d['matrices']=[[1,0,0,1.02,0,0] for _ in range(8)];check('anisotropic character stretch rejected',not size.run(d,ROOT)['checks']['one_positive_uniform_bank_transform'])
d=copy.deepcopy(c);d['candidate_frames'][2]['sha256']='0'*64;check('changed size-image binding rejected',not size.run(d,ROOT)['checks']['all_input_hashes'])
d=copy.deepcopy(baseline);d['head_body_family_review']['candidate_sha256'][3]='bad';check('head/body review cannot transfer to different pixels',not size.run(d,ROOT)['checks']['head_body_family_review_bound'])
ims=[Image.open(P/f'size-locked-review/{i:02}.png') for i in range(8)];windows=dict(near=dict(roi=[85,460,225,490],edge='min',material='foreground'),far=dict(roi=[236,440,308,488],edge='max',material='foreground'));f=floor.run(ims,windows,6,1)
check('actual outlineobserver still fails10and25px at unchanged6px',not f['surface_checks_pass'] and f['tracks']['near']['range_display_px']==[10,1] and f['tracks']['far']['range_display_px']==[25,3])
im=ims[0].convert('RGBA');im.putpixel((88,485),(255,255,255,255));pixels=np.array(im).copy();obs=floor.observe(im,windows['near']['roi'],'min','foreground');check('component observation filter does not edit raw stray pixels',np.array_equal(np.array(im),pixels) and im.getpixel((88,485))==(255,255,255,255) and obs['known'])
(P/'size-test-receipt.json').write_text(json.dumps(dict(checks=checks,production_pass=False),indent=2)+'\n');print(f'{len(checks)} size/outline regression controls passed')
