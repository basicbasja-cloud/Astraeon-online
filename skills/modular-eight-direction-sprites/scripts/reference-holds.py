"""Captured repeated body pixels require exact repeated authored body keys.

This verifies the body timing/identity contract, never semantic pose accuracy.
"""
import hashlib,json
from pathlib import Path
from PIL import Image
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(case,root):
 root=Path(root);capture=case['capture'];p=root/capture['path']
 if sha(p)!=capture['sha256']:raise ValueError('Changed capture receipt')
 cap=json.loads(p.read_text());fs=cap['frames'];keys=case['body_keys'];mapping=case['exposure_to_body_key']
 if len(mapping)!=len(fs):raise ValueError('Missing exposure')
 unique=[]
 for f in fs:
  if sha(p.parent/f['file'])!=f['sha256']:raise ValueError('Changed captured body pixels')
  if f['sha256'] not in unique:unique.append(f['sha256'])
 if len(unique)!=len(keys):raise ValueError('Wrong unique body key count')
 seen={};art=[]
 for k,key in enumerate(keys):
  if key['source_sha256']!=unique[k] or sha(root/key['path'])!=key['sha256']:raise ValueError('Body/source binding changed')
  with Image.open(root/key['path']) as im:
   if list(im.size)!=case['canvas']:raise ValueError('Mixed canvas')
 for i,(f,k) in enumerate(zip(fs,mapping)):
  if not isinstance(k,int) or not 0<=k<len(keys) or keys[k]['source_sha256']!=f['sha256']:raise ValueError('Wrong source phase/body key')
  if f['sha256'] in seen and keys[k]['sha256']!=seen[f['sha256']]:raise ValueError('Captured hold has drifted')
  seen[f['sha256']]=keys[k]['sha256'];art.append(keys[k]['sha256'])
 if case.get('recovered_hidden_skeleton') or case.get('world_contacts_verified'):raise ValueError('Body pixel holds do not recover bones/world contact')
 return {'schema':'reference-body-holds-v1','status':'CAPTURED_HOLDS_AND_AUTHORED_KEY_BINDINGS_VERIFIED','captured_exposure_count':len(fs),'unique_body_keys':len(keys),'body_sha256_per_exposure':art,'exposure_to_body_key':mapping,'clock_ms':[f['duration_ms'] for f in fs],'duration_ms':sum(f['duration_ms'] for f in fs),'anatomy_approved':False,'natural_motion_approved':False,'production_ready':False,'scope':'Exact source pixel repeats retain identical authored body files, while weapon/FX may use a separate exposure clock.'}
