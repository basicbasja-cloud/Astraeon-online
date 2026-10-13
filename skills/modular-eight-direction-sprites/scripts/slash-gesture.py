"""Image-bound manual-observation audit for a declared cross-body slash family.

Not an automatic hand detector. Source bones, visible contours and acceptance are
independent authorities. Passing these diagnostics cannot unlock production.
"""
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(case, root):
    issues=[]; measurements={}; frames=case['frames']; contract=case['contract']
    for f in frames:
        p=root/f['path']
        if not p.is_file() or sha(p)!=f['sha256']:
            issues.append({'kind':'binding','key':f['key']}); continue
        im=Image.open(p).convert('RGBA')
        for name in ['palm','wrist']:
            point=f.get('visible_points',{}).get(name)
            if point is None:
                issues.append({'kind':'unknown_observation','key':f['key'],'point':name});continue
            x,y=map(round,point)
            if not (0<=x<im.width and 0<=y<im.height) or im.getpixel((x,y))[3]<128:
                issues.append({'kind':'point_not_on_foreground','key':f['key'],'point':name})
    a,b=(frames[i] for i in contract['cut_follow_keys'])
    if all(f.get('visible_points',{}).get('palm') for f in [a,b]):
        d=math.dist(a['visible_points']['palm'],b['visible_points']['palm'])
        u=a.get('uncertainty_px',0)+b.get('uncertainty_px',0)
        measurements['cut_to_follow_palm_distance_px']=d
        measurements['uncertainty_subtracted_distance_px']=max(0,d-u)
        if d-u<contract['minimum_distinct_follow_distance_px']:
            issues.append({'kind':'insufficient_distinct_follow_pose','keys':contract['cut_follow_keys']})
    c,e=(frames[i] for i in contract['coil_finish_keys'])
    for f in [c,e]:
        if f.get('visible_points',{}).get('right_shoulder') is None:
            issues.append({'kind':'unknown_right_shoulder_contour','key':f['key']})
    if all(f.get('visible_points',{}).get('right_shoulder') and f.get('visible_points',{}).get('palm') for f in [c,e]):
        offsets=[f['visible_points']['palm'][0]-f['visible_points']['right_shoulder'][0] for f in [c,e]]
        measurements['coil_finish_screen_x_palm_relative_to_right_shoulder']=offsets
        if offsets[1]-offsets[0]<contract['minimum_crossing_progress_px']:
            issues.append({'kind':'insufficient_declared_cross_body_progress'})
    binding=case.get('source_index')
    if binding:
        p=root/binding['path']
        if sha(p)!=binding['sha256']:issues.append({'kind':'source_binding'})
        else:
            source=json.loads(p.read_text());records=source['records']
            i,j=contract['cut_follow_keys']
            sv=[records[j]['right_grip_xy'][k]-records[i]['right_grip_xy'][k] for k in [0,1]]
            av=[frames[j]['visible_points']['palm'][k]-frames[i]['visible_points']['palm'][k] for k in [0,1]]
            denominator=math.hypot(*sv)*math.hypot(*av)
            dot=sum(x*y for x,y in zip(sv,av))/denominator if denominator else None
            measurements['source_cut_follow_distance_px']=math.hypot(*sv)
            measurements['source_art_follow_direction_dot']=dot
            if dot is None or dot<contract['minimum_source_follow_direction_dot']:
                issues.append({'kind':'source_art_follow_direction_mismatch'})
            i,j=contract['coil_finish_keys'];times=[records[k]['time_ms'] for k in [i,j]]
            wrists=[next(v['right_wrist_joint'][0] for v in source['dense_bake'] if v['time_ms']==t) for t in times]
            measurements['source_coil_finish_facing_local_right_wrist_x']=wrists
            if not wrists[0]<0<wrists[1]:issues.append({'kind':'source_never_crosses_declared_body_side'})
    else:issues.append({'kind':'unknown_source_matching'})
    pack=case.get('packing')
    if pack:
        p=root/pack['path']
        if sha(p)!=pack['sha256']:issues.append({'kind':'packing_binding'})
        else:
            data=json.loads(p.read_text())
            for axis in ['x','y']:
                value=data['max_held_out_'+axis+'_delta_px'];measurements['held_out_boot_'+axis+'_delta_px']=value
                if value>contract['maximum_held_out_boot_'+axis+'_delta_px']:
                    issues.append({'kind':'held_out_boot_'+axis+'_variation','value_px':value})
    else:issues.append({'kind':'unknown_independent_boot_observation'})
    ledger=root/'research/sprite-animation/attack-rejections.json'
    if ledger.is_file():
        known=set()
        for binding in json.loads(ledger.read_text())['receipts']:
            p=root/binding['path']
            if not p.is_file() or sha(p)!=binding['sha256']:
                issues.append({'kind':'rejection_receipt_binding'});continue
            r=json.loads(p.read_text())
            if r['status']=='USER_REJECTED':known.update(b['sha256'] for b in r['bindings'])
        affected=[f['key'] for f in frames if f['sha256'] in known]
        if affected:issues.append({'kind':'known_rejected_pixels','keys':affected})
    else:issues.append({'kind':'unknown_rejection_history'})
    if case.get('user_status')=='USER_REJECTED':issues.append({'kind':'user_rejection'})
    if case.get('grip_edge_alignment_review')!='verified':issues.append({'kind':'unverified_grip_edge_alignment'})
    return {'schema':'slash-gesture-review-v1','status':'REJECTED_OR_INCOMPLETE' if issues else 'REVIEW_REQUIRED',
            'measurements':measurements,'issues':issues,'production_pass':False,
            'observation_scope':'SHA-bound manually estimated visible glove/cuff/shoulder contours. Internal joints, finger wrap and hidden limb ownership are not detected.',
            'contract_scope':'Explicit candidate SE diagonal cross-body slash; thresholds are provisional diagnostics, not universal sword physics or another-character approval.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-production',action='store_true');a=p.parse_args()
    result=audit(json.loads(a.case.read_text()),a.root);result['case_sha256']=sha(a.case)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['measurements'],[i['kind'] for i in result['issues']])
    if a.require_production and not result['production_pass']:raise SystemExit(2)
if __name__=='__main__':main()
