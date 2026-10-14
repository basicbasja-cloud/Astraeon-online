"""Neutral size continuity to an immutable approved character, not pose bbox fit.

Only neutral poses are height-comparable. Bent/crouched silhouettes may change.
One neutral can calibrate a BANK transform; other neutrals must stay held out.
Head/body proportions require their own current exact-image review/layer proof.
"""
import argparse,hashlib,json,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extent(path):
    a=np.array(Image.open(path).convert('RGBA'));y,x=np.where(a[:,:,3]>=128)
    if not len(x):return dict(known=False,reason='Empty visible foreground')
    border=np.zeros(a.shape[:2],dtype=bool);border[0,:]=border[-1,:]=True;border[:,0]=border[:,-1]=True
    return dict(known=True,bbox_xyxy=[int(x.min()),int(y.min()),int(x.max()),int(y.max())],height=int(y.max()-y.min()+1),width=int(x.max()-x.min()+1),bottom_y=int(y.max()),visible_boundary_pixels=int(((a[:,:,3]>=128)&border).sum()),scope='Alpha128 foreground extent; body/head neutral with no weapon/FX extending it. Not an anatomical height/width estimator.')


def run(c,root):
    root=Path(root);ref=c['reference'];bindings=[ref,c['reference_gif'],c['approval_receipt']]+c['candidate_frames']+c['raw_frames']
    receipt=json.loads((root/c['approval_receipt']['path']).read_text());mats=c['matrices'];m=mats[0]
    checks=dict(all_input_hashes=all(sha(root/b['path'])==b['sha256'] for b in bindings),approved_reference_covered_by_acceptance=all(any(f['path']==b['path'] and f['sha256']==b['sha256'] for f in receipt['files']) for b in [ref,c['reference_gif']]),one_positive_uniform_bank_transform=len(mats)==len(c['candidate_frames'])==8 and all(a==m for a in mats) and m[0]>0 and m[0]==m[3] and m[1]==m[2]==0,declared_neutral_calibration_only=c['calibration_index']==0 and c['neutral_indices']==[0,7])
    re=extent(root/ref['path']);raw=[extent(root/f['path']) for f in c['raw_frames']];current=[extent(root/f['path']) for f in c['candidate_frames']];rows=[]
    checks['reference_foreground_observable']=re['known'] and re['visible_boundary_pixels']==0
    checks['all_raw_frame_contours_unclipped']=all(r['known'] and r['visible_boundary_pixels']==0 for r in raw)
    for i in c['neutral_indices']:
        a=current[i];known=a['known'] and raw[i]['known'];clipped=not known or raw[i]['visible_boundary_pixels']>0
        rows.append(dict(index=i,role='calibration' if i==0 else 'held_out_terminal_neutral',observed_height_px=a.get('height'),reference_height_px=re['height'],height_error_px=a.get('height',0)-re['height'],bottom_y_error_px=a.get('bottom_y',0)-re['bottom_y'],raw_complete_silhouette=not clipped,measurement_status='CLIPPED_LOWER_BOUND' if clipped else 'VISIBLE_EXTENT',pass_=bool(known and not clipped and abs(a['height']-re['height'])<=c['height_budget_px'] and abs(a['bottom_y']-re['bottom_y'])<=c['floor_budget_px'])))
    checks['neutral_height_and_ground']=all(r['pass_'] for r in rows)
    review=c.get('head_body_family_review',{})
    checks['head_body_family_review_bound']=review.get('pass') is True and review.get('reference_sha256')==ref['sha256'] and review.get('candidate_sha256')==[f['sha256'] for f in c['candidate_frames']]
    exact_accepted=all(any(f['path']==b['path'] and f['sha256']==b['sha256'] for f in receipt['files']) for b in c['candidate_frames']) and len({b['sha256'] for b in c['candidate_frames']})>=7
    part=None;binding=c.get('part_proportion_contract')
    if binding and sha(root/binding['path'])==binding['sha256']:
        spec=importlib.util.spec_from_file_location('part_proportions',Path(__file__).with_name('part-proportion-audit.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        contract=json.loads((root/binding['path']).read_text());bound=[f['image'] for f in contract['frames'] if f['role']=='candidate']
        part=module.run(contract,root)
        checks['part_dimensions_and_ratios']=bound==c['candidate_frames'] and part['part_proportion_pass']
    else:checks['part_dimensions_and_ratios']=exact_accepted
    return dict(checks=checks,reference_visible_extent=re,neutral_comparison=rows,all_candidate_visible_extents=current,raw_visible_extents=raw,part_proportions=part,head_body_family_status='REVIEWED' if checks['head_body_family_review_bound'] and checks['part_dimensions_and_ratios'] else 'UNKNOWN: full-height matching alone cannot establish part dimensions, ratios or a compatible head bank',height_budget_px=c['height_budget_px'],floor_budget_px=c['floor_budget_px'],character_size_pass=all(checks.values()),production_pass=False,scope='One rest-only global size calibration and held-out neutral continuity. Crouch height/cloth width are not forced to neutral bounds. All new pixels additionally require bound multi-part proportion evidence; exact accepted masters are only an identity control.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);p.add_argument('--require-size',action='store_true');a=p.parse_args();r=run(json.loads(a.contract.read_text()),a.root);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(checks=r['checks'],neutrals=r['neutral_comparison'])));return int(a.require_size and not r['character_size_pass'])


if __name__=='__main__':raise SystemExit(main())
