"""Independently verify recovered v79, seal compact v80 preservation inputs.
The full unbaked source snapshot is local. Reproducible final checks use sealed
owner/component/ground-face fingerprints, avoiding a second shipped world JSON.
"""
import json,hashlib,subprocess,runpy,gc
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'docs/review/wayfarer-capital-v79/painted-landscape';O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';helpers=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'));fingerprint=helpers['fingerprint'];unlit=helpers['unlit'];metadata=helpers['metadata'];facekeys=helpers['facekeys'];p=json.loads((O/'plan.json').read_text());garden=json.loads((A/'plan.json').read_text());gr=json.loads((A/'authoring.json').read_text())
path=O/'authored-landscape-baseline.json'
if path.exists():
 sealed=json.loads(path.read_text());assert sealed['beforeSourceSHA256']==p['beforeSourceSHA256'] and sealed['v79Pass'];print('PASS existing independently sealed v79 preservation inputs');raise SystemExit(0)
b=json.loads(subprocess.check_output(['git','show','c2a4a11:world/v3/wayfarer-spatial.json'],cwd=R));raw=Path('/tmp/astraeon-before-unique-homes-v80/wayfarer-spatial.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==p['beforeSourceSHA256'];middle=json.loads(raw);del raw;old={a['id']:a for a in b['objects']};mid={a['id']:a for a in middle['objects']};leaf=set(gr['changedLeafParts']);originals=0
assert set(mid)-set(old)=={gr['newGrassOwner']} and not set(old)-set(mid)
for n,o in old.items():
 q=mid[n];assert metadata(o)==metadata(q),(n,'v79 metadata')
 if n=='capital-beta-frontage-groundcover':
  a={v['id']:v for v in o['parts']};d={v['id']:v for v in q['parts']};assert set(a)-set(d)==set(gr['replacedLawnParts']) and set(d)-set(a)==set(gr['newLawnParts'])
  for name in set(a)&set(d):assert unlit(a[name])==unlit(d[name]),name
 else:
  assert len(o['parts'])==len(q['parts']),n
  for a,d in zip(o['parts'],q['parts']):
   x,y=unlit(a),unlit(d)
   if a['id'] in leaf:
    oldv=x.pop('vertices');newv=y.pop('vertices');assert x==y and len(oldv)==len(newv);assert all(abs(v[2]-w[2])<.000021 for v,w in zip(oldv,newv)),a['id']
   else:assert x==y,(n,a['id'],'v79 undeclared change');originals+=1
actualLawns={a['id']:a for a in mid['capital-beta-frontage-groundcover']['parts']}
for piece in garden['pieces']:
 a=actualLawns[piece['id']];assert a['faces']==piece['faces'] and len(a['vertices'])==len(piece['vertices'])
 assert max(abs(x-y) for v,w in zip(a['vertices'],piece['vertices']) for x,y in zip(v,w))<.00003,piece['id']
 assert max(abs(x-y) for x,y in zip(a['vertexOpacity'],piece['vertexOpacity']))<.000015,piece['id']
 assert a['material']=='grass' and not a['shadow'] and a['role']=='decorative'
newblades=mid[gr['newGrassOwner']]['parts'];assert all(a['role']=='decorative' and not a['shadow'] for a in newblades)
assert sum(len(f)-2 for a in newblades for f in a['faces'])==len(garden['grassRoots'])*3==gr['newGrassTriangles']
for key in b.keys()-{'objects','materials','lighting'}:assert b[key]==middle[key],key
assert b['materials'].keys()==middle['materials'].keys()
for n,a in b['materials'].items():assert middle['materials'][n]==gr['materialChanges'].get(n,{}).get('after',a),n
assert {k:v for k,v in b['lighting'].items() if k!='groundShadow'}=={k:v for k,v in middle['lighting'].items() if k!='groundShadow'}
changed={a['id'] for a in p['houses']};owners={}
for n,o in mid.items():
 entry={'metadata':fingerprint(metadata(o))}
 if n in changed:
  entry['retainedParts']={a['id']:fingerprint(unlit(a)) for a in o['parts'] if a['role']=='solid' or a['id'].endswith('-door-leaf') or a['id'].startswith('capital-v78-')};entry['groundFaces']=dict(facekeys(o,2.95))
 else:entry['parts']=fingerprint([unlit(a) for a in o['parts']])
 owners[n]=entry
sealed={'beforeSourceSHA256':p['beforeSourceSHA256'],'v79BaselineCommit':'c2a4a11','v79Pass':True,'v79OriginalPartsExactOutsideDeclaredGardensCrowns':originals,'owners':owners,'materials':fingerprint(middle['materials']),'common':fingerprint({k:v for k,v in middle.items() if k not in ('objects','materials','lighting')}),'lighting':fingerprint({k:v for k,v in middle['lighting'].items() if k!='groundShadow'}),'changedHousing':sorted(changed),'proof':'Independently compared pushed v78 against preserved unbaked v79; exact source identity, then SHA256 unlit components and oriented ground-face geometry/UV fingerprints.'}
path.write_text(json.dumps(sealed,indent=2)+'\n');(A/'independent-preservation.json').write_text(json.dumps({k:v for k,v in sealed.items() if k not in ('owners','materials','common','lighting')},indent=2)+'\n');print('PASS independently sealed v79 and v80 inputs:',originals,'unchanged original parts')
