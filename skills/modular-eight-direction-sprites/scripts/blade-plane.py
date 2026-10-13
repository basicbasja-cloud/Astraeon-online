"""Source blade-plane and independently annotated painted blade-direction review.

Contract is this SE descending slash; no universal definition of every sword cut.
Source-only proofs never approve painted anatomy, grip or production.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(v):
    a=np.asarray(v,dtype=float);return a/np.linalg.norm(a)
def angle(v):return math.degrees(math.atan2(v[1],v[0]))
def audit(source,art,root):
    issues=[];measurements={};records=source['records']
    view=norm(np.asarray(source['camera_matrix_world'])[:3,2])
    basis=np.asarray(source.get('grip_basis_local',np.eye(3)))
    normals=[norm(np.asarray(r['hand_matrix_world'])[:3,:3]@basis[:,2]) for r in records]
    visibility=min(abs(float(n@view)) for n in normals)
    measurements['minimum_source_blade_plane_view_dot']=visibility
    if visibility<.12:issues.append('source_plane_reads_edge_on_in_declared_camera')
    drift=max(float(np.linalg.norm(n-normals[0])) for n in normals)
    measurements['source_edge_normal_drift']=drift
    if drift>1e-5:issues.append('source_edge_changes_outside_declared_fixed_plane')
    values=[]
    for i in [4,5]:
        r=records[i];v=np.subtract(r['blade_tip_xy'],r['right_grip_xy']);values.append(angle(v))
    measurements['source_follow_settle_blade_angles_screen_degrees']=values
    if any(not 30<=a<=65 for a in values):issues.append('source_finish_outside_declared_SE_diagonal_band')
    travel=np.subtract(records[4]['blade_tip_xy'],records[2]['blade_tip_xy'])
    measurements['source_coil_to_follow_tip_travel_xy']=travel.tolist()
    measurements['source_tip_travel_angle_screen_degrees']=angle(travel)
    if not(travel[0]>0 and travel[1]>0 and 30<=angle(travel)<=75):issues.append('source_tip_path_not_declared_downward_diagonal')
    observations=[]
    if art is None:issues.append('painted_blade_observations_unknown')
    else:
        for f in art['frames']:
            p=root/f['path']
            if not p.is_file() or sha(p)!=f['sha256']:
                issues.append('painted_image_binding_changed');continue
            points=f.get('visible_blade')
            if f.get('raw_cell_opaque_edge_touch'):issues.append('raw_pose_cell_clipping_or_spill')
            if points is None or any(point is None for point in points.values()):issues.append('painted_blade_observation_unknown');continue
            im=Image.open(p).convert('RGBA')
            for name,point in points.items():
                x,y=map(round,point)
                if not(0<=x<im.width and 0<=y<im.height) or im.getpixel((x,y))[3]<100:
                    issues.append('painted_'+name+'_not_on_visible_pixels')
            vector=np.subtract(points['tip'],points['guard']);ref=records[f['key']]
            expected=np.subtract(ref['blade_tip_xy'],ref['right_grip_xy'])
            dot=float(norm(vector)@norm(expected));observations.append({'key':f['key'],'painted_angle_degrees':angle(vector),'source_direction_dot':dot})
            if dot<.8:issues.append('painted_blade_direction_disagrees_with_source')
            if f['key'] in [4,5] and not 30<=angle(vector)<=65:issues.append('painted_finish_outside_declared_SE_diagonal_band')
        if not art.get('grip_and_right_chain_independently_verified'):issues.append('painted_grip_right_chain_unverified')
    return {'schema':'blade-plane-review-v1','issues':sorted(set(issues)),'measurements':measurements,'painted_observations':observations,
        'status':'INCOMPLETE' if issues else 'REVIEW_REQUIRED','production_pass':False,
        'scope':'Camera-specific authored diagonal-slash contract. Source matrices and manual painted guard/tip points are distinct; no hidden3Dedge or palm/finger reconstruction.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--art',type=Path);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=audit(json.loads(a.source.read_text()),json.loads(a.art.read_text()) if a.art else None,a.root)
    result['source_index_sha256']=sha(a.source)
    if a.art:result['art_case_sha256']=sha(a.art)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['measurements'],result['issues'])
if __name__=='__main__':main()
