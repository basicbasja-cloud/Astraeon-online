"""Static inspection of actual binary GLB bytes; no game runtime claim."""
from pathlib import Path
import json,struct,hashlib,sys
import numpy as np
P=Path(__file__).resolve().parent;corrected='--corrected' in sys.argv;f=P/('original-character-corrected.glb' if corrected else 'original-character-experimental.glb');raw=f.read_bytes();magic,version,total=struct.unpack_from('<4sII',raw);assert (magic,version,total)==(b'glTF',2,len(raw));off=12;chunks={}
while off<len(raw):
 n,k=struct.unpack_from('<II',raw,off);off+=8;assert off+n<=len(raw);chunks[k]=raw[off:off+n];off+=n
j=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
def accessor(i):
 a=j['accessors'][i];b=j['bufferViews'][a['bufferView']];typ={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dt=np.dtype(typ);stride=b.get('byteStride',width*dt.itemsize);start=b.get('byteOffset',0)+a.get('byteOffset',0);end=start+(a['count']-1)*stride+width*dt.itemsize;assert end<=b.get('byteOffset',0)+b['byteLength']<=len(binary);v=np.ndarray((a['count'],width),dtype=dt,buffer=binary,offset=start,strides=(stride,dt.itemsize)).copy()
 if a.get('normalized'):v=v/(255 if a['componentType']==5121 else 65535)
 return v
weight_error=0;invalid=0;mesh_nodes=[];slots=set();joint_oob=0
for n in j['nodes']:
 if 'mesh' not in n:continue
 mesh_nodes.append(n['name']);slots.add(n.get('extras',{}).get('runtime_slot'))
 assert 'skin' in n,('unskinned exported character node',n['name']);skin=j['skins'][n['skin']]
 for prim in j['meshes'][n['mesh']]['primitives']:
  a=prim['attributes'];w=accessor(a['WEIGHTS_0']);ids=accessor(a['JOINTS_0']);weight_error=max(weight_error,float(np.abs(w.sum(axis=1)-1).max()));invalid+=int(np.sum(~np.isfinite(w)) +np.sum(w<0));joint_oob+=int(np.sum((ids>=len(skin['joints']))&(w>0)));assert len(accessor(a['POSITION']))==len(w)
times=[]
for anim in j.get('animations',[]):
 for sampler in anim['samplers']:
  t=accessor(sampler['input']).ravel();assert np.all(np.diff(t)>0);times.append([float(t[0]),float(t[-1]),len(t)])
checks=dict(valid_glb_container=True,all115_character_meshes_skinned=len(mesh_nodes)==115,two_authoring_slots=slots=={'body_outfit','complete_head'},normalized_weights=weight_error<1e-5,no_invalid_weights=invalid==0,no_invalid_joint_indices=joint_oob==0,animation_present=bool(times),single_synchronized_clip=len(j.get('animations',[]))==1,motion_duration_1_3s=all(abs(t[1]-t[0]-1.3)<1e-5 for t in times),collectible_excluded='collectible' not in mesh_nodes)
r=dict(checks=checks,pass_all=all(checks.values()),sha256=hashlib.sha256(raw).hexdigest(),mesh_nodes=len(mesh_nodes),skin_count=len(j['skins']),animation_count=len(j.get('animations',[])),sampler_time_ranges=sorted(set(tuple(x) for x in times)),max_weight_sum_error=weight_error,runtime_slots=sorted(slots),scope='Actual bytes and static glTF skin/animation accessors; not engine-import or visual playback verification',production_pass=False);(P/('corrective-glb-inspection.json' if corrected else 'glb-inspection.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert all(checks.values())
