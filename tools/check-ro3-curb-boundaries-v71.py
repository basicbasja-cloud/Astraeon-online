"""Independent saved-source checks for town-wide curb/public-path separation."""
import bpy,json,runpy,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;exp=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exp['export'](scene);h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));args=sys.argv[sys.argv.index('--')+1:];before=json.loads(Path(args[0]).read_text());out=Path(args[1]);record=json.loads(scene['ro3_curb_boundaries_review_json']);review=json.loads(scene['ro3_road_curb_review_json']);verges=json.loads(scene['ro3_curb_grass_review_json'])
for key in ('objects','navigation','spawn','route','districts','safeSpawn','materials'):assert w.get(key)==before.get(key),(key,'unexpected change')
allowed={r['id'] for r in record['curbChanges']+record['grassChanges']}|{r['fascia'] for r in record['curbChanges']};surfs={s['id']:s for s in w['terrain']['surfaces']};old={s['id']:s for s in before['terrain']['surfaces']};assert surfs.keys()==old.keys()
for id,s in surfs.items():
 if id not in allowed:assert s==old[id],(id,'unrecorded terrain change')
 else:assert s['faces']==old[id]['faces'] and s['material']==old[id]['material'] and s['role']==old[id]['role'],id
public=[s for s in surfs.values() if s.get('visible',True) and s['walkable'] and ((s.get('centerline') and s.get('width',0)>=1.8) or s['material']=='publicSquareStone' or s['role']=='forecourt' and ('stair' in s['id'] or 'processional' in s['id'] or 'landing' in s['id'] or s['id'] in ('civic-terrace','terrace-v49-upper-civic-floor')))];public_polys=[(s['id'],h['hull'](s['vertices'])) for s in public]
solids=[(p['id'],h['hull'](p['vertices'])) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];aprons=[(s['id'],h['hull'](s['vertices'])) for s in surfs.values() if s['material']=='houseApronPaving'];accepted=[];curbcontacts=0
for rec in review['curbBlocks']:
 s=surfs[rec['id']];fascia=surfs['curb70-fascia-'+rec['id']]
 if not rec['active']:assert not s['visible'] and not s['walkable'] and not fascia['visible'];continue
 assert s['visible'] and s['walkable'] and fascia['visible'] and not fascia['walkable'];q=h['hull'](s['vertices'])
 assert math.dist(s['vertices'][0][:2],s['vertices'][6][:2])>=.1599
 for name,p in public_polys+solids+aprons+accepted:assert not h['overlap'](q,p,-.0001),(s['id'],'overlapping',name)
 assert abs(max(v[2] for v in s['vertices'])-rec['ground']-.20)<.0002;accepted.append((s['id'],q));curbcontacts+=1
vs=[];fs=[]
for s in surfs.values():
 if not s['walkable']:continue
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  for j in range(1,len(f)-1):fs.append((off+f[0],off+f[j],off+f[j+1]))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True);grasscontacts=0
for rec in verges['strips']:
 s=surfs[rec['id']]
 if not rec['active']:assert not s['visible'] and not s['walkable'];continue
 assert s['visible'] and not s['walkable'];q=h['hull'](s['vertices'])
 for name,p in public_polys:assert not h['overlap'](q,p,-.0001),(s['id'],'public grass overlap',name)
 a,b,c,d=map(Vector,s['vertices'])
 for i in range(5):
  for j in range(5):
   u,v=i/4,j/4;p=a+(b-a)*u+(c-b)*v if u>=v else a+(c-d)*u+(d-a)*v;hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None and abs(p.z-hit.z-.017)<.035,(s['id'],'grass contact');grasscontacts+=1
assert w['lighting'].get('groundShadow') and w['lighting']['groundShadow']['geometryDigest']==exp['shadow_geometry_digest'](w),'stale floor bake'
report={**record,'status':'passed','publicFootprintsChecked':len(public),'activeCurbsChecked':curbcontacts,'remainingCurbPublicOverlaps':0,'remainingCurbIntersections':0,'remainingCurbSolidOrApronOverlaps':0,'grassContactSamples':grasscontacts,'remainingRoadsideGrassPublicOverlaps':0,'allObjectGeometryAndActorMetadataExact':True,'unrecordedTerrainChanges':0,'currentGroundShadow':w['lighting']['groundShadow'],'cost':{'allParts':sum(len(o['parts']) for o in w['objects']),'visibleParts':sum(p.get('visible',True) for o in w['objects'] for p in o['parts']),'terrainSurfaces':len(surfs),'walkableSurfaces':sum(s['walkable'] for s in surfs.values())}};out.write_text(json.dumps(report,indent=2)+'\n');print('PASS native curb boundaries:',json.dumps({k:v for k,v in report.items() if k not in ('curbChanges','grassChanges','publicSurfaceIds')}))
