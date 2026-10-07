"""Pure source-fingerprint helpers for scoped, reproducible preservation checks."""
import hashlib,json,collections
def fingerprint(a):return hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def unlit(a):return {k:v for k,v in a.items() if k!='bakedLighting'}
def metadata(o):return {k:v for k,v in o.items() if k!='parts'}
def facekeys(owner,maxz=None):
 result=collections.Counter()
 for a in owner['parts']:
  if not a.get('visible',True):continue
  for fi,f in enumerate(a['faces']):
   vs=[a['vertices'][i] for i in f]
   if maxz is not None and max(v[2] for v in vs)>maxz:continue
   corners=tuple(tuple(round(v,5) for v in point)+tuple(round(v,5) for v in uv) for point,uv in zip(vs,a['uvs'][fi]));canonical=min(corners[j:]+corners[:j] for j in range(len(corners)))
   result[fingerprint([a['material'],a['role'],canonical])]+=1
 return result
