"""Independent source-only wrist target/plane comparison, no painted images."""
from pathlib import Path
import json,numpy as np,hashlib
P=Path(__file__).resolve().parent;S=json.loads((P/'source/cc0-motion.json').read_text());D=json.loads((P/'source/retargeted-endpoints.json').read_text());N=D['neutral_world'];V=lambda b,e='head':np.array(b[e],dtype=float);gains={};max_wrist=0.;min_plane_dot=1.;rows=[]
for side,s in [('left','l'),('right','r')]:
 length=sum(np.linalg.norm(V(N[side+'.'+b],'tail')-V(N[side+'.'+b]))for b in ['upperarm','forearm']);den=max(np.linalg.norm(V(r['bones']['lowerarm.'+s])-V(r['bones']['upperarm.'+s]))+np.linalg.norm(V(r['bones']['hand.'+s])-V(r['bones']['lowerarm.'+s]))for c in S['clips'].values()for r in c['frames']);gains[side]=(length-.001)/den
for key,clip in D['clips'].items():
 reference=S['clips'][clip['source_clip']]['frames'];assert len(reference)==len(clip['frames'])==257
 for i,(a,b)in enumerate(zip(clip['frames'],reference)):
  for side,s in [('left','l'),('right','r')]:
   w=a['world_bones'];r=b['bones'];shoulder=V(w[side+'.upperarm']);elbow=V(w[side+'.forearm']);wrist=V(w[side+'.hand']);su=V(r['upperarm.'+s]);se=V(r['lowerarm.'+s]);sw=V(r['hand.'+s]);target=shoulder+(sw-su)*gains[side];err=float(np.linalg.norm(wrist-target));max_wrist=max(max_wrist,err);n=np.cross(elbow-shoulder,wrist-elbow);m=np.cross(se-su,sw-se)
   if np.linalg.norm(m)>1e-7 and np.linalg.norm(n)>1e-7:min_plane_dot=min(min_plane_dot,float(np.dot(n,m)/np.linalg.norm(n)/np.linalg.norm(m)))
assert max_wrist<.00001 and min_plane_dot>.99999,(max_wrist,min_plane_dot)
r={'pass':True,'samples_per_action':257,'constant_whole_arm_gains':gains,'max_actual_saved_wrist_target_error_m':max_wrist,'minimum_actual_vs_reference_elbow_plane_dot':min_plane_dot,'saved_source_sha256':hashlib.sha256((P/'source/retargeted-endpoints.json').read_bytes()).hexdigest(),'external_cc0_sha256':hashlib.sha256((P/'source/cc0-motion.json').read_bytes()).hexdigest(),'scope':'Actual saved3D wrist relative to shoulder and elbow plane match external CC0 references after one length gain. Original target limb lengths, in-place pelvis/feet, and closed wrist are authored adaptations. No painted anatomy or game impact proof.'};(P/'source/arm-retarget-review.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
