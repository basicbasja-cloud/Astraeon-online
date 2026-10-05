"""Independent saved-source check for decorative path/planting contacts and source preservation."""
import bpy,json,runpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);before=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());output=Path(sys.argv[sys.argv.index('--')+2]);vs=[];fs=[]
for s in w['terrain']['surfaces']:
 if not s.get('walkable'):continue
 off=len(vs);vs.extend(s['vertices']);fs.extend(tuple(off+face[i] for i in (0,k,k+1)) for face in s['faces'] for k in range(1,len(face)-1))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def height(v):
 p=floor.ray_cast(Vector((v[0],v[1],100)),Vector((0,0,-1)),150)[0];assert p is not None,tuple(v);return p.z
wear=json.loads(scene['ro3_path_wear_review_json']);plants=json.loads(scene['ro3_planting_edge_review_json']);props=json.loads(scene['ro3_prop_detail_review_json']);moved={name for record in plants['beds']+plants['orphanGroundFlowerGroups'] for name in record['parts']};preserved=0
for old in before['objects']:
 current=next(o for o in w['objects'] if o['id']==old['id']);assert {k:v for k,v in old.items() if k!='parts'}=={k:v for k,v in current.items() if k!='parts'},old['id'];assert len(old['parts'])==len(current['parts'])
 for p in old['parts']:
  q=next(p2 for p2 in current['parts'] if p2['id']==p['id'])
  for key in ('role','shadow','material','faces','uvs','visible'):assert p.get(key)==q.get(key),(p['id'],key)
  if p['id'] not in moved:assert p['vertices']==q['vertices'],p['id'];preserved+=1
for key in ('navigation','spawn','route','districts','safeSpawn'):assert before.get(key)==w.get(key),key
for key in before['terrain']:
 if key!='surfaces':assert before['terrain'][key]==w['terrain'][key],key
old_surfaces={s['id']:s for s in before['terrain']['surfaces']};new=[s for s in w['terrain']['surfaces'] if s['id'] not in old_surfaces]
for s in w['terrain']['surfaces']:
 if s['id'] in old_surfaces:assert s==old_surfaces[s['id']],s['id']
 else:assert not s['walkable'] and s['id'].startswith(('walkwear69-','plantedge69-')),s['id']
contacts=0
for s in new:
 if s['id'].startswith('walkwear69-joint-grass-'):continue
 offset=.021 if s['id'].startswith('walkwear69-') else .017
 for v in s['vertices']:assert abs(v[2]-height(v)-offset)<.0002,(s['id'],v);contacts+=1
for patch in wear['patches']:
 s=next(s for s in new if s['id']==patch['id']);a,b,c,d=[Vector(v) for v in s['vertices']]
 for u in range(9):
  for v in range(9):
   p=a+(b-a)*u/8+(d-a)*v/8;assert abs(p.z-height(p)-.021)<.003,(s['id'],'interior floor',tuple(p));contacts+=1
 for root in patch['roots']:assert abs(root[2]-height(root)-.021)<.0002;contacts+=1
for record in plants['beds']:
 soil=next(p for o in w['objects'] for p in o['parts'] if p['id']=='organic-v47-bed-'+str(record['group']));assert all(abs(v[2]-height(v)-.020)<.003 for v in soil['vertices']);contacts+=len(soil['vertices'])
for record in plants['orphanGroundFlowerGroups']:
 assert abs(record['floor']-height(record['after']))<.003
 assert len(record['parts'])>=4
assert w['materials']['avenuePaving']['texture']['file']==w['materials']['paving']['texture']['file']=='assets/wayfarer-aged-pavers-v69.webp'
assert w['materials']['vergeGroundcover']['texture']['file']==w['materials']['plantingEdgeGrass']['texture']['file']
used={p['material'] for o in w['objects'] for p in o['parts'] if p.get('visible')is not False}|{s['material'] for s in w['terrain']['surfaces'] if s.get('visible')is not False}
plain=sorted(k for k in used if not w['materials'][k].get('texture'));assert set(plain)<={'forgeEmber','forgeHotCore','lanternGlow','lanternLight','marketAmber'},plain
assert len(wear['patches'])>=12 and len(plants['beds'])==5 and len(plants['orphanGroundFlowerGroups'])>0
report={'sourcePass':69,'wornPathPatches':len(wear['patches']),'jointGrassClumps':wear['jointGrassClumps'],'relocatedBeds':len(plants['beds']),'relocatedOrphanGroundFlowerGroups':len(plants['orphanGroundFlowerGroups']),'plantingGrassIslands':plants['grassPatches'],'contactChecks':contacts,'newDecorativeSurfaces':len(new),'walkableFloorsAndOriginalSolidsPreserved':True,'unchangedParts':preserved,'movedPlantParts':len(moved),'updatedPlainMaterialCount':len(props['updatedMaterials']),'remainingPlainVisibleMaterials':plain,'currentFloorBake':w['lighting'].get('groundShadow')}
assert report['currentFloorBake'],'Rebake before verifying source completion';output.write_text(json.dumps(report,indent=2)+'\n');print('PASS native city detail and meaningful planting contacts',json.dumps(report))
