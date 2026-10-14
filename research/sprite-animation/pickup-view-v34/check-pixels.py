"""Calibrate only frame-zero textures; validate held-out pose/source after detection."""
from pathlib import Path
import copy,hashlib,importlib.util,json,math
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];S=ROOT/'skills/modular-eight-direction-sprites/scripts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
observer=load('observer',S/'rigid-surface-observer-v2.py');auditor=load('surface',S/'planted-surface-review.py')
bundle=json.loads((P/'frames.json').read_text());poses=json.loads((P/'poses.json').read_text());reports={}
cal=P/'isolated/right.forearm-0.png'
patches={
 'surface.near_boot_toe':dict(seed_xy=[195,480],half_extent=[8,7],search_box=[120,453,220,512],rotation_search_degrees=[0,0,1]),
 'surface.far_boot_toe':dict(seed_xy=[268,450],half_extent=[8,7],search_box=[205,425,300,480],rotation_search_degrees=[0,0,1]),
 'surface.reaching_cuff':dict(seed_xy=[154,291],half_extent=[6,6],search_box=[100,245,260,430],rotation_search_degrees=[-100,100,2],isolated_first_frame=dict(path=str(cal.relative_to(ROOT)),sha256=sha(cal)))}
for spec in patches.values():spec.update(ambiguity_radius_px=8,minimum_ncc=.95,minimum_margin=.015)
for style,frames in bundle['styles'].items():
 case=dict(canvas=[384,512],frames=frames,patches=patches,calibration='Only frame0 visible surface textures and fixed windows; no later pose targets. Near/far are view labels, not anatomical inference.')
 obs=observer.observe(case,ROOT);surface=dict(canvas=[384,512],frames=copy.deepcopy(frames),surface_landmarks={n:dict(definition='visible painted '+n,policy='moving_surface' if n.endswith('cuff') else 'planted_surface_proxy',anatomical_owner='unknown') for n in patches},planted_budget_px=6,reference_phase=dict(source_file=str((P/'source/source.json').relative_to(ROOT)),source_sha256=sha(P/'source/source.json'),source_joint='right.wrist',marker='surface.reaching_cuff',axis=1,calibration_frames=[0,3],warning_fraction=.25,definition_gap='cuff surface versus source wrist bone: phase only'))
 for i,f in enumerate(surface['frames']):f['observations']={n:{k:v for k,v in rows[i].items() if k in ('status','xy','uncertainty_px','anatomical_owner')} for n,rows in obs['tracks'].items()}
 report=auditor.audit(surface,ROOT);errors=[dict(frame=i,error_px=math.dist(r['xy'],poses[i]['joints']['right.wrist'])) for i,r in enumerate(obs['tracks']['surface.reaching_cuff']) if r['status']=='visible' and i!=0]
 reports[style]=dict(surface_review=report,actual_pixel_observations=obs,held_out_cuff_errors=errors)
 (P/(style+'-observer-case.json')).write_text(json.dumps(case,indent=2)+'\n');(P/(style+'-surface-case.json')).write_text(json.dumps(surface,indent=2)+'\n')
(P/'pixel-review.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps({s:dict(pass_=r['surface_review']['numerical_surface_check_pass'],issues=r['surface_review']['issues'],retained=sum(o['status']=='visible' for track in r['actual_pixel_observations']['tracks'].values() for o in track),max_held_out_error=max((e['error_px'] for e in r['held_out_cuff_errors']),default=None)) for s,r in reports.items()}))
