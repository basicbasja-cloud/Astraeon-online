"""Research sweep omitting a heavily foreshortened, uncertain art endpoint."""
import argparse, math
from pathlib import Path
import numpy as np
import propose_swordsman_interpolated_sweep as study

def mapped_path(samples, annotations):
 if len(samples)!=65 or len(annotations)!=5:raise ValueError('expected five strike keys and 65 samples')
 lengths=[np.linalg.norm(np.asarray(a['weapon_tip'],float)-np.asarray(a['weapon_grip'],float)) for a in annotations]
 if min(lengths)<2 or not np.all(np.isfinite(lengths)):raise ValueError('invalid annotations')
 # A short projected blade can be legitimate foreshortening. Exclude only a
 # clearly isolated short measurement as an unverified *experimental* choice.
 rejected=[k for k in range(1,4) if lengths[k]<.4*min(lengths[k-1],lengths[k+1])]
 if len(rejected)>1:raise ValueError('multiple ambiguous endpoints')
 valid=[k for k in range(5) if k not in rejected]
 scales=[];angles=[];offsets=[]
 for k in valid:
  row=samples[k*16];g=np.asarray(row['grip'],float);t=np.asarray(row['tip'],float);pg=np.asarray(annotations[k]['weapon_grip'],float);pt=np.asarray(annotations[k]['weapon_tip'],float)
  v=t-g;w=pt-pg;vl=np.linalg.norm(v);wl=np.linalg.norm(w)
  if min(vl,wl)<2:raise ValueError('degenerate sword projection')
  scale=wl/vl;angle=math.atan2(w[1],w[0])-math.atan2(v[1],v[0]);matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])*scale
  scales.append(scale);angles.append(angle);offsets.append(pg-matrix@g)
 angles=np.unwrap(angles);results=[]
 for i,row in enumerate(samples):
  time=i/16;right=next((j for j,k in enumerate(valid) if k>=time),len(valid)-1);left=max(0,right-1)
  if right==left:f=0.
  else:f=(time-valid[left])/(valid[right]-valid[left])
  scale=math.exp((1-f)*math.log(scales[left])+f*math.log(scales[right]));angle=(1-f)*angles[left]+f*angles[right];trans=(1-f)*offsets[left]+f*offsets[right];matrix=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])*scale
  results.append(tuple(matrix@np.asarray(row[name],float)+trans for name in ('grip','tip')))
 for j,k in enumerate(valid):
  for z,name in enumerate(('grip','tip')):
   if np.linalg.norm(results[k*16][z]-np.asarray(annotations[k]['weapon_'+name]))>1e-5:raise ValueError('valid key mismatch')
 return results,{'scales':scales,'angles_radians':angles.tolist(),'excluded_key_indices':rejected,'annotation_lengths':lengths,'warning':'exclusion is experimental; short blade can be real perspective'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();study.mapped_path=mapped_path;study.build(a.output)
