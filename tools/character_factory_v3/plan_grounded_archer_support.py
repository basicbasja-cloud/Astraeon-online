"""Plan fixed support ankles for an explicitly standing Archer shot study."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--controls',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--direction',default='NW')
    p.add_argument('--maximum-extension',type=float,default=.95)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous support plans')
    if not .8<=a.maximum_extension<1:raise ValueError('Choose a non-straight support extension bound')
    rows=json.loads(a.controls.read_text())['views'][a.direction]['frames'];result={}
    for side in ['L','R']:
        def xyz(row,bone):return np.array(row['world_matrices'][bone+'.'+side])[:3,3]
        hip=np.array([xyz(r,'Thigh')for r in rows]);knee=np.array([xyz(r,'Shin')for r in rows]);ankle=np.array([xyz(r,'Foot')for r in rows])
        lengths=np.linalg.norm(knee-hip,axis=1)+np.linalg.norm(ankle-knee,axis=1)
        weights=np.array([2 if i<4 or i>len(rows)-5 else 1 for i in range(len(rows))])
        def objective(xy):return float(np.sum(weights[:,None]*(xy-ankle[:,:2])**2))
        def constraints(xy):return (a.maximum_extension*lengths)**2-(np.sum((xy-hip[:,:2])**2,axis=1)+(ankle[:,2]-hip[:,2])**2)
        solved=minimize(objective,np.average(ankle[:,:2],axis=0,weights=weights),constraints=[{'type':'ineq','fun':constraints}],method='SLSQP',options={'ftol':1e-12,'maxiter':200})
        if not solved.success or min(constraints(solved.x))< -1e-8:raise ValueError('No fixed support solution; author the motion explicitly')
        result[side]={'ankle_xy_world_m':solved.x.tolist(),'maximum_extension_ratio':a.maximum_extension,'solver_success':True,'minimum_reach_margin_squared_m2':float(min(constraints(solved.x))),'maximum_original_ankle_xy_travel_m':float(np.linalg.norm(ankle[:,:2]-ankle[0,:2],axis=1).max())}
    a.output.write_text(json.dumps({'status':'AUTHORED_SUPPORT_ANCHOR_PLAN_REQUIRES_MOTION_REVIEW','policy':'Static standing bow shot; both support ankles anchored in XY. Preserve upper body and foot orientation. This is an authored motion adaptation, not unchanged source motion.','feet':result,'source_controls':str(a.controls),'source_controls_sha256':hashlib.sha256(a.controls.read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_motion_changed':True,'runtime_admitted':False},indent=2)+'\n')


if __name__=='__main__':main()
