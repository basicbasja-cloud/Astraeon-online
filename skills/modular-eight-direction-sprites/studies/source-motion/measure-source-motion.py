"""Geometric source measurements; these do not certify dynamics or ground contact."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);a=p.parse_args();data=json.loads(a.input.read_text())
def sub(a,b):return [x-y for x,y in zip(a,b)]
def norm(v):return math.sqrt(sum(x*x for x in v))
def angle(a,b,c):
    u=sub(a,b);v=sub(c,b)
    return math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(u,v))/norm(u)/norm(v)))))
report={}
for clip in data['clips']:
    fs=clip['frames'];height=[f['root_relative_joints']['pelvis'][2] for f in fs];yaw=[];knee=[];elbow=[]
    for f in fs:
        j=f['root_relative_joints'];shoulder=sub(j['right.shoulder'],j['left.shoulder']);hips=sub(j['right.hip'],j['left.hip'])
        difference=math.atan2(shoulder[1],shoulder[0])-math.atan2(hips[1],hips[0]);yaw.append(math.degrees(math.atan2(math.sin(difference),math.cos(difference))))
        knee.append(angle(j['right.hip'],j['right.knee'],j['right.ankle']));elbow.append(angle(j['right.shoulder'],j['right.elbow'],j['right.wrist']))
    report[clip['name']]={'pelvis_root_relative_z_range':[min(height),max(height)],'shoulder_vs_hip_yaw_degrees_range':[min(yaw),max(yaw)],
                         'right_knee_joint_angle_degrees':[min(knee),max(knee)],'right_elbow_joint_angle_degrees':[min(elbow),max(elbow)],
                         'root_displacement_world':sub(fs[-1]['root_world'],fs[0]['root_world']),
                         'scope':'Landmark geometry measurements, not physics simulation, center-of-mass or sole-contact validation'}
(a.input.parent/'mechanics-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
