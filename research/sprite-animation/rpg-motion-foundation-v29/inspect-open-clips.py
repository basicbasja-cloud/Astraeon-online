#!/usr/bin/env python3
"""Inspect actual glTF timestamps/channels, not an advertised preset count."""
import hashlib,json,math,shutil,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def read_glb(path):
 blob=path.read_bytes()
 magic,version,length=struct.unpack_from('<4sII',blob)
 if magic!=b'glTF' or version!=2 or length!=len(blob):raise ValueError('Invalid GLB')
 chunks={};at=12
 while at<len(blob):
  size,kind=struct.unpack_from('<II',blob,at);at+=8
  chunks[kind]=blob[at:at+size];at+=size
 return json.loads(chunks[0x4e4f534a]),chunks.get(0x004e4942,b'')

def input_times(gltf,binary,animation):
 all_times=set()
 for sampler in animation['samplers']:
  ac=gltf['accessors'][sampler['input']];view=gltf['bufferViews'][ac['bufferView']]
  if ac['componentType']!=5126 or ac['type']!='SCALAR' or ac.get('sparse'):raise ValueError('Unsupported input accessor')
  start=view.get('byteOffset',0)+ac.get('byteOffset',0);stride=view.get('byteStride',4)
  times=[struct.unpack_from('<f',binary,start+i*stride)[0] for i in range(ac['count'])]
  if any(not math.isfinite(t) for t in times) or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Invalid native input order')
  all_times.update(times)
 return sorted(all_times)

def main():
 out=ROOT/'open-data';out.mkdir(exist_ok=True);files=[]
 specs=[('ual2-oga','ual2-standard','UAL2_Standard.glb'),('kay-oga','kaykit-1.2','KayKit_AnimatedCharacter_v1.2.glb')]
 for id,archive,filename in specs:
  candidates=list((ROOT/'local-cache'/archive).rglob(filename))
  if len(candidates)!=1:raise ValueError('Ambiguous acquired GLB')
  original=candidates[0];folder=out/id;folder.mkdir(exist_ok=True);path=folder/filename;shutil.copyfile(original,path)
  licenses=list((ROOT/'local-cache'/archive).rglob('License.txt'))
  if len(licenses)!=1 or 'CC0' not in licenses[0].read_text():raise ValueError('Required creator CC0 receipt')
  shutil.copyfile(licenses[0],folder/'License.txt')
  gltf,binary=read_glb(path);clips=[]
  for a in gltf.get('animations',[]):
   ts=input_times(gltf,binary,a);name=a.get('name','')
   exclusion='rest_pose_not_motion' if name in ('A_TPose','BasePose') else None
   clips.append({'name':name,'start_seconds':ts[0],'end_seconds':ts[-1],'duration_seconds':ts[-1]-ts[0],'native_key_times_seconds':ts,'channels':len(a['channels']),'interpolations':sorted({s.get('interpolation','LINEAR') for s in a['samplers']}),'target_nodes':sorted({gltf['nodes'][c['target']['node']].get('name',str(c['target']['node'])) for c in a['channels']}),'exclusion':exclusion,'visual_semantic_review':'pending','contact_labels':'unknown','production_approved':False})
  files.append({'source_id':id,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'license_path':str((folder/'License.txt').relative_to(ROOT)),'license_sha256':hashlib.sha256((folder/'License.txt').read_bytes()).hexdigest(),'skins':[{'name':s.get('name'),'joints':len(s['joints'])} for s in gltf.get('skins',[])],'node_names':[n.get('name') for n in gltf['nodes']],'clips':clips,'scope':'Actual serialized glTF channels and key input times; no gameplay exposure clock or bone/palm contact inferred.'})
 report={'schema':'acquired-glb-motion-inventory-v1','files':files,'dash_policy':'optional_research','counts':{'serialized_animations':sum(len(f['clips']) for f in files),'dash_included':sum('dash' in c['name'].lower() and c['exclusion'] is None for f in files for c in f['clips']),'rest_poses_excluded':sum(c['exclusion']=='rest_pose_not_motion' for f in files for c in f['clips']),'motion_candidates':sum(c['exclusion'] is None for f in files for c in f['clips'])}}
 (ROOT/'clip-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts']))
if __name__=='__main__':main()
