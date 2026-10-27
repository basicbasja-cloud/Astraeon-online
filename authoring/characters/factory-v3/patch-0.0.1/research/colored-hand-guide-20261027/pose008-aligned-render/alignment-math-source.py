"""Compute a staff-specific reference grip; body motion remains source-authored."""
import math
import numpy as np


def alignment_angles(forearm_axis,knuckle_axis,up=(0,0,1)):
    def unit(v):
        v=np.asarray(v,dtype=float);length=np.linalg.norm(v)
        if not np.isfinite(v).all() or length<1e-9:raise ValueError('Nonzero finite grip axes required')
        return v/length
    d,v,z=map(unit,[forearm_axis,knuckle_axis,up]);a=v-d*np.dot(d,v);b=z-d*np.dot(d,z)
    if min(np.linalg.norm(a),np.linalg.norm(b))<1e-8:raise ValueError('Degenerate forearm/grip alignment')
    a=unit(a);b=unit(b);roll=math.atan2(np.dot(d,np.cross(a,b)),np.dot(a,b))
    rotated=v*math.cos(roll)+np.cross(d,v)*math.sin(roll)+d*np.dot(d,v)*(1-math.cos(roll))
    flex=math.acos(float(np.clip(np.dot(rotated,z),-1,1)))
    return {'forearm_roll_radians':roll,'wrist_flex_radians':flex,'rolled_knuckle_axis':rotated.tolist(),'target_axis':z.tolist()}
