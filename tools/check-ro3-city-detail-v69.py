"""Independent saved-source check for decorative path/planting contacts and source preservation."""
import bpy,json,runpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);before=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());output=Path(sys.argv[sys.argv.index('--')+2]);vs=[];fs=[];triangle_uvs=[];triangle_materials=[]
for s in w['terrain']['surfaces']:
 if not s.get('walkable'):continue
 off=len(vs);vs.extend(s['vertices'])
 for fi,face in enumerate(s['faces']):
  for k in range(1,len(face)-1):
   corners=(0,k,k+1);fs.append(tuple(off+face[i] for i in corners));triangle_uvs.append([s['uvs'][fi][i] for i in corners] if s.get('uvs') else None);triangle_materials.append(s['material'])
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
assert wear['stoneImagePads']==0 and wear['removedStonePads']==20
assert 'agedPathPatch' not in w['materials']
assert not any('path-wear-v69.webp' in m.get('texture',{}).get('file','') for m in w['materials'].values())
assert not any(s['id'].startswith('walkwear69-') and not s['id'].startswith('walkwear69-joint-grass-') for s in new)
art=Image.open(ROOT/wear['jointArtwork']).convert('RGB');checked_roots=set()
for region in wear['regions']:
 assert not any(s['id']==region['formerPad'] for s in w['terrain']['surfaces'])
 for joint in region['joints']:
  s=next(s for s in new if s['id']==joint['id']);root=(Vector(s['vertices'][0])+Vector(s['vertices'][1]))/2
  assert (root-Vector(joint['point'])).length<.0001
  hit,normal,idx,distance=floor.ray_cast(Vector((root.x,root.y,100)),Vector((0,0,-1)),150)
  assert hit is not None and abs(root.z-hit.z-.012)<.0002,(s['id'],'root contact')
  assert w['materials'][triangle_materials[idx]]['texture']['file']==wear['jointArtwork']
  # Independently solve the planar 2D triangle for the actual authored UV.
  a,b,c=[vs[i] for i in fs[idx]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  wa=((b[1]-c[1])*(hit.x-c[0])+(c[0]-b[0])*(hit.y-c[1]))/den
  wb=((c[1]-a[1])*(hit.x-c[0])+(a[0]-c[0])*(hit.y-c[1]))/den
  uv=[sum(weight*pair[k] for weight,pair in zip((wa,wb,1-wa-wb),triangle_uvs[idx])) for k in (0,1)]
  rgb=art.getpixel((int((uv[0]%1)*art.width)%art.width,int((1-uv[1]%1)*art.height)%art.height))
  luma=(.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2])/255
  assert luma<wear['jointThreshold'] and abs(luma-joint['jointLuma'])<1e-5,(s['id'],'paving joint',luma)
  checked_roots.add(s['id']);contacts+=1
assert len(checked_roots)==wear['jointGrassClumps']==160
for record in plants['beds']:
 soil=next(p for o in w['objects'] for p in o['parts'] if p['id']=='organic-v47-bed-'+str(record['group']));assert all(abs(v[2]-height(v)-.020)<.003 for v in soil['vertices']);contacts+=len(soil['vertices'])
for record in plants['orphanGroundFlowerGroups']:
 assert abs(record['floor']-height(record['after']))<.003
 assert len(record['parts'])>=4
assert w['materials']['avenuePaving']['texture']['file']==w['materials']['paving']['texture']['file']=='assets/wayfarer-aged-pavers-v69.webp'
assert w['materials']['vergeGroundcover']['texture']['file']==w['materials']['plantingEdgeGrass']['texture']['file']
used={p['material'] for o in w['objects'] for p in o['parts'] if p.get('visible')is not False}|{s['material'] for s in w['terrain']['surfaces'] if s.get('visible')is not False}
plain=sorted(k for k in used if not w['materials'][k].get('texture'));assert set(plain)<={'forgeEmber','forgeHotCore','lanternGlow','lanternLight','marketAmber'},plain
assert len(wear['regions'])==20 and len(plants['beds'])==5 and len(plants['orphanGroundFlowerGroups'])>0
report={'sourcePass':69,'stoneImagePads':0,'removedStonePads':wear['removedStonePads'],'integratedGrassRegions':len(wear['regions']),'jointGrassClumps':wear['jointGrassClumps'],'relocatedBeds':len(plants['beds']),'relocatedOrphanGroundFlowerGroups':len(plants['orphanGroundFlowerGroups']),'plantingGrassIslands':plants['grassPatches'],'contactChecks':contacts,'newDecorativeSurfaces':len(new),'walkableFloorsAndOriginalSolidsPreserved':True,'unchangedParts':preserved,'movedPlantParts':len(moved),'updatedPlainMaterialCount':len(props['updatedMaterials']),'remainingPlainVisibleMaterials':plain,'currentFloorBake':w['lighting'].get('groundShadow')}
assert report['currentFloorBake'],'Rebake before verifying source completion';output.write_text(json.dumps(report,indent=2)+'\n');print('PASS native city detail and meaningful planting contacts',json.dumps(report))
