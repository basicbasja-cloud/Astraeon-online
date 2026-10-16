"""Physical camera projection of CC0 source deltas onto static original rest meshes."""
from pathlib import Path
import json,hashlib,numpy as np
P=Path(__file__).resolve().parent;root=P.parents[2]
for name in ['sprite-mesh-player.js']:(P/'inputs'/name).write_bytes((root/'tools'/name).read_bytes())
capture=P.parent/'pickup-contact-v49/references/kaykit-captures.json';rows=[r for r in json.loads(capture.read_text())['frames'] if r['clip']=='Hit_A' and r['view']=='N'];base=rows[0];cameras={r['view']:np.array(r['camera_world']) for r in json.loads((P/'source/camera-receipts.json').read_text())['views']};out={}
for view in ['S','W','N','E']:
 cam=cameras[view];right=cam[:3,0];up=cam[:3,1];poses=[]
 for row in rows:
  delta={bone:np.array(row['actual_source_bones'][bone]['world'])-np.array(base['actual_source_bones'][bone]['world']) for bone in ['head','chest','hips','foot.l','foot.r']};floor=(delta['foot.l']+delta['foot.r'])/2;pose={}
  for bone in ['head','chest','hips']:
   d=delta[bone]-floor;pose[bone]=[float(d@right*150),float(-d@up*150)]
  poses.append(pose)
 # Complete endpoint lock is an authored neutral pose, not a fitted body patch.
 poses[0]=dict.fromkeys(['head','chest','hips'],[0,0]);poses[-1]=dict.fromkeys(['head','chest','hips'],[0,0]);bounds=[round(i*670/16/10)*10 for i in range(17)]
 out[view]={'texture':f'stage/idle/{view}/00.png','texture_sha256':hashlib.sha256((P/f'stage/idle/{view}/00.png').read_bytes()).hexdigest(),'adapter':{'width':512,'height':512,'grid_px':16,'bands':[{'y':0,'channel':'head'},{'y':212,'channel':'head'},{'y':268,'channel':'chest'},{'y':378,'channel':'hips'},{'y':432,'channel':'fixed'},{'y':512,'channel':'fixed'}]},'poses':poses,'durations_ms':[bounds[i+1]-bounds[i] for i in range(16)]}
data={'views':out,'source_capture_sha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'source_clip':'Hit_A','source_times_seconds':[r['source_time_seconds'] for r in rows],'projection_px_per_world_unit':150,'scope':'Small in-plane light recoil only; static texture rest mesh with rigid complete head and fixed distal band. Camera axes project actual external CC0 source world deltas. This does not reconstruct hidden anatomical joints or support out-of-plane poses.'};(P/'light-reaction-contract.json').write_text(json.dumps(data,indent=2)+'\n')
html='''<!doctype html><html><meta charset="utf-8"><style>body{background:#20252d;color:white;font:16px system-ui}canvas{background:#292b30}</style><p>ทดสอบสะดุ้งเบา · ภาพเดิมและเมชคงรูปเท้า</p><canvas id="c"></canvas><script src="inputs/sprite-mesh-player.js"></script><script>const D=__DATA__,canvas=document.getElementById('c'),cache=new Map();let mesh;Promise.all(Object.entries(D.views).map(([v,a])=>new Promise((ok,no)=>{let im=new Image();im.onload=()=>{cache.set(v,im);ok()};im.onerror=no;im.src=a.texture}))).then(()=>{window.READY=true});window.study={data:D,choose(v){if(mesh)mesh.dispose();mesh=new SpriteMesh(canvas,cache.get(v),D.views[v].adapter)},get mesh(){return mesh},frame(v,i){mesh.draw(D.views[v].poses[i]);return canvas.toDataURL('image/png')}};</script></html>''';(P/'light-reaction-review.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))));print('Four projected source views')
