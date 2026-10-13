"""Bound evidence diagnostics. Never infer owners/contacts from clothing or screen sorting."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def angle(v): return math.degrees(math.atan2(v[1],v[0]))
def delta(a,b): return (a-b+180)%360-180
def audit(case, root):
    warnings=[];unknown=[];metrics={};root=Path(root)
    if case.get('schema')!='motion-mechanics-v1':raise ValueError('Unknown schema')
    for asset in case.get('bindings',[]):
        if sha(root/asset['path'])!=asset['sha256']:raise ValueError('Stale binding: '+asset['path'])
    frames=case.get('frames',[])
    if len(frames)<2:raise ValueError('At least two observations required')
    times=[f['time_ms'] for f in frames]
    if any(not math.isfinite(t) for t in times) or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Nonmonotone clock')
    for f in frames:
        for key in ['image','source_image']:
            if f.get(key) and sha(root/f[key]['path'])!=f[key]['sha256']:raise ValueError('Stale image')
    feedback_status=None
    if case.get('feedback'):
        ref=case['feedback'];path=root/ref['path']
        if sha(path)!=ref['sha256']:raise ValueError('Stale feedback')
        item=json.loads(path.read_text())
        for key in ref['selector']:item=item[key]
        current=[f['image']['sha256'] for f in frames]
        if current!=[f['sha256'] for f in item['frames']]:raise ValueError('Feedback image bank mismatch')
        feedback_status=item['status']
    if case['action']=='attack':
        local=[];offsets=[];grips=[];blades=[];hands=[]
        for i,f in enumerate(frames):
            if f.get('balance_review','').startswith('USER_REJECTED'):warnings.append(f'frame {i}: user rejected visible stance/balance')
            elif f.get('balance_review')!='reviewed':unknown.append(f'frame {i}: visible stance/balance not reviewed')
            h=f.get('hand_matrix_world');w=f.get('weapon_matrix_world')
            if h is not None and w is not None:
                h=np.asarray(h,float);w=np.asarray(w,float)
                if h.shape!=(4,4) or w.shape!=(4,4) or not np.isfinite(h).all() or not np.isfinite(w).all():raise ValueError('Invalid rigid transforms')
                local.append((i,np.linalg.solve(h,w)))
            else:unknown.append(f'frame {i}: actual hand/weapon transforms unavailable')
            p=f.get('visible_points')
            if case.get('attack_representation')=='hand_sweep_tail':
                if p and all(p.get(k) is not None for k in ['palm','wrist','knuckles']):
                    hand=np.subtract(p['knuckles'],p['wrist'])
                    if np.shape(hand)!=(2,) or not np.isfinite(hand).all() or np.linalg.norm(hand)<1e-6:raise ValueError('Invalid hand-sweep axis')
                    hands.append(angle(hand))
                    if not f.get('right_hand_identity_reviewed',False):unknown.append(f'frame {i}: attacking-hand identity unresolved')
                else:unknown.append(f'frame {i}: visible hand-sweep axis incomplete')
                if f.get('hilt') or f.get('tip'):warnings.append(f'frame {i}: unexpected rendered-weapon claims in hand-tail mode')
                continue
            if p and all(p.get(k) is not None for k in ['palm','hilt','tip','wrist','knuckles']):
                points={k:np.asarray(p[k],float) for k in ['palm','hilt','tip','wrist','knuckles']}
                if any(v.shape!=(2,) or not np.isfinite(v).all() for v in points.values()):raise ValueError('Invalid visible point')
                hand=points['knuckles']-points['wrist'];blade=points['tip']-points['hilt']
                if np.linalg.norm(hand)<1e-6 or np.linalg.norm(blade)<1e-6:raise ValueError('Degenerate visible axis')
                hand_angle=angle(hand);blade_angle=angle(blade);offset=delta(blade_angle,hand_angle)
                tolerance=case.get('grip_tolerance_px',8)
                gap=float(np.linalg.norm(points['hilt']-points['palm']))
                if f.get('palm_hilt_same_feature_calibration'):unknown.append(f'frame {i}: palm/hilt point is one calibration feature, not independent grip validation')
                else:
                    grips.append(gap)
                    if gap>tolerance+f.get('uncertainty_px',0):warnings.append(f'frame {i}: observed hilt/palm gap')
                expected=f.get('reference_relative_blade_angle_deg')
                if expected is None:unknown.append(f'frame {i}: reference projected grip axis unavailable')
                elif abs(delta(offset,expected))>case.get('angle_tolerance_deg',25)+f.get('angle_uncertainty_deg',0):warnings.append(f'frame {i}: projected blade/hand orientation differs from bound reference')
                offsets.append(offset);blades.append(blade_angle);hands.append(hand_angle)
                if not f.get('right_hand_identity_reviewed',False):unknown.append(f'frame {i}: right hand identity unresolved')
            else:unknown.append(f'frame {i}: visible grip axis incomplete; no inferred wrist/knuckles')
        if local:
            deviations=[float(np.max(np.abs(m-local[0][1]))) for _,m in local]
            metrics['max_hand_local_weapon_matrix_delta']=max(deviations)
            if max(deviations)>case.get('local_transform_tolerance',1e-4):warnings.append('Weapon moves inside the hand-local grip frame')
        metrics['visible_hilt_palm_gaps_px']=grips;metrics['projected_blade_minus_hand_deg']=offsets
        metrics['blade_angle_steps_deg']=[delta(b,a) for a,b in zip(blades,blades[1:])]
        metrics['hand_angle_steps_deg']=[delta(b,a) for a,b in zip(hands,hands[1:])]
        metrics['geometry_scope']='Fixed hand-local attachment only. Wrist articulation/projection can change screen angles; no universal forearm-angle rule.'
    elif case['action']=='walk':
        leads=[];clear=[];mismatch=[];lift=[];tracks={'r':[],'l':[]}
        for i,f in enumerate(frames):
            feet=f.get('feet');expected=f.get('reference_lead')
            lead=f.get('observed_lead')
            if lead not in ['r','l','passing']:unknown.append(f'frame {i}: visual leading leg unresolved')
            else:
                if lead!='passing':leads.append(lead)
                if expected and expected!='passing' and lead!='passing' and lead!=expected:mismatch.append(i)
            if not feet or any(feet.get(s) is None for s in ['r','l']):
                unknown.append(f'frame {i}: paired feet unavailable');continue
            axis=np.asarray(f.get('travel_axis_xy',[0,0]),float);norm=np.linalg.norm(axis)
            if norm<1e-6:unknown.append(f'frame {i}: projected heading unavailable');continue
            axis/=norm
            pts=[np.asarray(feet[s]['sole_xy'],float) for s in ['r','l']]
            if any(p.shape!=(2,) or not np.isfinite(p).all() for p in pts):raise ValueError('Invalid paired sole points')
            signed=float(np.dot(pts[0]-pts[1],axis));separation=abs(signed);clear.append(separation)
            lateral=f.get('rest_lateral_separation_px')
            if lateral is None:unknown.append(f'frame {i}: projected left/right rest-lane offset unavailable')
            else:
                forward=signed-lateral
                geometric='passing' if abs(forward)<=case.get('lead_deadband_px',4) else 'r' if forward>0 else 'l'
                if lead in ['r','l'] and geometric!='passing' and lead!=geometric:warnings.append(f'frame {i}: stated lead contradicts owned sole geometry')
            if f.get('root_xy') is None:unknown.append(f'frame {i}: independent root unavailable for foot travel')
            else:
                for s,pt in zip(['r','l'],pts):tracks[s].append(pt-np.asarray(f['root_xy'],float))
            for s in ['r','l']:
                foot=feet[s]
                if not foot.get('identity_reviewed',False):unknown.append(f'frame {i}/{s}: hip-to-foot owner unresolved')
                ground=foot.get('ground_projection_xy')
                if ground is None:unknown.append(f'frame {i}/{s}: foot-local floor lane unknown')
                else:
                    clearance=float(np.asarray(ground,float)[1]-foot['sole_xy'][1]);lift.append(clearance)
                    if foot.get('contact')=='stance' and abs(clearance)>case.get('stance_tolerance_px',5)+foot.get('uncertainty_px',0):warnings.append(f'frame {i}/{s}: stance sole differs from own floor lane')
            if not f.get('contact_state_reviewed',False):unknown.append(f'frame {i}: stance/swing classification unresolved')
        switches=sum(a!=b for a,b in zip(leads,leads[1:]))
        if case.get('loop') and len(leads)>1:switches+=leads[-1]!=leads[0]
        if leads and switches<2:warnings.append('No complete left/right lead alternation in the observed loop')
        if mismatch:warnings.append('Visible leading-leg sequence disagrees with reference phases')
        if clear and max(clear)<case.get('min_projected_separation_px',8):warnings.append('Projected foot separation is too small for this reviewed camera; inspect depth/occlusion')
        travel={}
        for s,pts in tracks.items():
            if len(pts)==len(frames):
                travel[s]=float(np.max(np.linalg.norm(np.asarray(pts)-pts[0],axis=1)))
                if travel[s]<case.get('minimum_foot_travel_px',3):warnings.append(f'{s}: owned foot is stationary relative to root across walk')
        metrics.update(lead_switches=switches,reference_lead_mismatch_frames=mismatch,projected_separation_px=clear,foot_local_floor_clearance_px=lift,max_root_relative_foot_travel_px=travel)
        metrics['geometry_scope']='A source floor projection is not a painted floor observation. In-place feet must be checked with actual runtime ground speed before slide-free claims.'
    else:raise ValueError('Unknown action')
    rejected=(feedback_status or case.get('user_status','')).startswith('USER_REJECTED')
    if rejected:warnings.append('Current exact-image user rejection remains binding')
    return {'schema':'motion-mechanics-report-v1','status':'USER_REJECTED' if rejected else 'REVIEW_REQUIRED',
        'diagnostic_status':'WARN' if warnings else 'INCONCLUSIVE' if unknown else 'CHECKS_CLEAR',
        'warnings':warnings,'unknown':unknown,'metrics':metrics,'production_approved':False,'bound_feedback_status':feedback_status,
        'scope':'Computed evidence, not an automatic image-semantic anatomy detector or artistic acceptance.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-production',action='store_true');a=p.parse_args()
    try:
        c=json.loads(a.case.read_text());r=audit(c,a.root);r['case_sha256']=sha(a.case);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['diagnostic_status'],len(r['warnings']),'warnings',len(r['unknown']),'unknowns')
        return 2 if a.require_production else 0
    except (ValueError,KeyError,FileNotFoundError,np.linalg.LinAlgError) as e:print('INVALID',str(e));return 1
if __name__=='__main__':raise SystemExit(main())
