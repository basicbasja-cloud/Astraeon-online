"""SHA-bound, visible-surface part measurements; abstain on hidden anatomy.

This is an observation/comparison tool, not automatic image-to-skeleton inference.
Line endpoints must be inspected on the actual pixels. A fixed family height is
the denominator: normalizing each frame separately would conceal size drift.
"""
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image

REQUIRED = ('head_width','head_height','shoulder_breadth','torso_length',
            'chest_width','waist_width','pelvis_width','upper_arm_length',
            'forearm_length','arm_thickness','hand_width','thigh_length',
            'shin_length','leg_thickness','ankle_width','boot_length','boot_height',
            'neck_attachment')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def observe(frame, name, root):
    o = frame.get('observations', {}).get(name, {})
    base = dict(metric=name, image_sha256=frame['image']['sha256'])
    if o.get('visibility') != 'visible':
        return dict(base, status='UNKNOWN', reason=o.get('reason','Not observed'))
    pts = o.get('points'); uncertainty = o.get('endpoint_uncertainty_px')
    if not o.get('reviewed_on_pixels') or not o.get('definition') or not isinstance(uncertainty,(int,float)) or uncertainty < 0:
        return dict(base, status='UNKNOWN', reason='Missing pixel review, surface definition or endpoint uncertainty')
    if not isinstance(pts,list) or len(pts)!=2 or any(len(p)!=2 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in p) for p in pts):
        return dict(base, status='UNKNOWN', reason='Two finite visible endpoints required')
    im=Image.open(root/frame['image']['path']).convert('RGBA')
    if any(not (1<=x<im.width-1 and 1<=y<im.height-1) for x,y in pts):
        return dict(base, status='UNKNOWN', reason='Endpoint outside safe image boundary')
    # An internal visible edge can touch transparent antialiasing: inspect a
    # small neighborhood, never snap a point to a different part automatically.
    for x,y in pts:
        if im.crop((int(x)-2,int(y)-2,int(x)+3,int(y)+3)).getchannel('A').getextrema()[1]<128:
            return dict(base,status='UNKNOWN',reason='Endpoint has no visible foreground nearby')
    length=math.dist(*pts)
    return dict(base,status='MEASURED',value_px=length,
                interval_px=[max(0,length-2*uncertainty),length+2*uncertainty],
                points=pts,definition=o['definition'],protocol=o.get('protocol'),
                covers_required_dimension=o.get('covers_required_dimension') is True,
                scope='Projected visible surface segment; not hidden joint length, volume or anatomical side inference')

def run(c, root):
    root=Path(root);frames=c['frames'];byid={f['id']:f for f in frames}
    bindings=[c['approval_receipt'],c['approved_gif']]+[f['image'] for f in frames]
    hashes=all((root/b['path']).is_file() and sha(root/b['path'])==b['sha256'] for b in bindings)
    receipt=json.loads((root/c['approval_receipt']['path']).read_text())
    covered=all(any(b['path']==r['path'] and b['sha256']==r['sha256'] for r in receipt['files']) for b in [c['approved_gif']]+[f['image'] for f in frames if f['role']=='approved'])
    measured={f['id']:{k:observe(f,k,root) for k in REQUIRED} for f in frames}
    h=c['fixed_family_height_px']
    for rows in measured.values():
        for o in rows.values():
            if o['status']=='MEASURED': o['fraction_of_fixed_family_height']=o['value_px']/h
    comparisons=[]
    for pair in c['comparisons']:
        a,b=[byid[i] for i in pair['frames']]
        for name in REQUIRED:
            x,y=measured[a['id']][name],measured[b['id']][name]
            row=dict(frames=pair['frames'],metric=name,status='UNKNOWN')
            if x['status']==y['status']=='MEASURED':
                row['projected_ratio']=y['value_px']/x['value_px'] if x['value_px'] else None
                row['difference_px']=y['value_px']-x['value_px']
                if a['view_id']!=b['view_id'] or a['pose_group']!=b['pose_group']:
                    row['reason']='Different view/pose: projected ratio is diagnostic only; matched-view reference or independently validated projection adapter required'
                elif not x['protocol'] or x['protocol']!=y['protocol']:
                    row['reason']='Measurement protocols differ'
                else:
                    tol=c['same_view_relative_budget'];lo,hi=x['interval_px'];yl,yh=y['interval_px']
                    if yl>hi*(1+tol) or yh<lo*(1-tol):row['status']='FAIL'
                    elif lo>0 and yl>=lo*(1-tol) and yh<=hi*(1+tol):row['status']='PASS'
                    else:row['reason']='Uncertainty overlaps the tolerance boundary'
            else:row['reason']='Missing, occluded or clipped visible endpoints'
            comparisons.append(row)
    candidate=[f for f in frames if f['role']=='candidate']
    approved=[f for f in frames if f['role']=='approved']
    coverage=len(candidate)==8 and sorted(f['index'] for f in candidate)==list(range(8))
    reference_pairs=all(any(f['id'] in p['frames'] and any(a['id'] in p['frames'] for a in approved) for p in c['comparisons']) for f in candidate)
    checks=dict(all_input_hashes=hashes,approved_images_covered_by_acceptance=covered,
                approved_part_reference_present=bool(approved),every_candidate_compared_with_approved=reference_pairs,
                eight_candidate_exposures=coverage,positive_fixed_family_height=isinstance(h,(int,float)) and h>0,
                every_required_part_observed=all(measured[f['id']][k]['status']=='MEASURED' and measured[f['id']][k]['covers_required_dimension'] for f in candidate for k in REQUIRED),
                comparisons_present=bool(comparisons),all_required_comparisons_pass=bool(comparisons) and all(r['status']=='PASS' for r in comparisons))
    return dict(checks=checks,measurements=measured,comparisons=comparisons,
                fixed_family_height_px=h,required_metrics=list(REQUIRED),
                part_proportion_pass=all(checks.values()),production_pass=False,
                scope='Visible projected lengths/widths and same-view/pose size continuity only. Unknowns block approval. No volume, hidden anatomy, camera equivalence, semantic segmentation or whole-animation acting proof.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);p.add_argument('--require-proportions',action='store_true');a=p.parse_args()
    q=run(json.loads(a.contract.read_text()),a.root);a.out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q['checks']));return int(a.require_proportions and not q['part_proportion_pass'])

if __name__=='__main__':raise SystemExit(main())
