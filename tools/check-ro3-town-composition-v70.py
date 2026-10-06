"""Read-only native floor/solid/access, curb and joint alignment checks for source70."""
import bpy,json,runpy,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;w=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))['export'](scene);before=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());output=Path(sys.argv[sys.argv.index('--')+2]);hierarchy=json.loads(scene['ro3_spatial_hierarchy_review_json']);wear=json.loads(scene['ro3_path_wear_review_json']);curbs=json.loads(scene['ro3_road_curb_review_json'])['curbBlocks'];roadsides=json.loads(scene['ro3_curb_grass_review_json'])['strips'];composition=json.loads(scene['ro3_town_composition_review_json']) if scene.get('ro3_town_composition_review_json') else {}
for key in ('navigation','spawn','route','districts','safeSpawn'):assert w.get(key)==before.get(key),key
part_count=0;solid_count=0;hidden=set(composition.get('hiddenOriginalDecorations',[]))
grass_fit=json.loads(scene.get('ro3_grass_contact_v70_json','{}'));patch_fit={r['id'] for r in grass_fit.get('patches',[])};clump_fit={r['id']:r for r in grass_fit.get('clumps',[])}
for old in before['objects']:
 current=next(o for o in w['objects'] if o['id']==old['id']);assert {k:v for k,v in old.items() if k!='parts'}=={k:v for k,v in current.items() if k!='parts'},old['id'];parts={p['id']:p for p in current['parts']}
 for p in old['parts']:
  q=parts[p['id']];assert p['role']==q['role'],p['id']
  if p['id'] in patch_fit|set(clump_fit):
   assert len(p['vertices'])==len(q['vertices']) and p['role']!='solid'
   for a,b in zip(p['vertices'],q['vertices']):
    if p['id'] in clump_fit:assert max(abs(a[i]-b[i]) for i in (0,1))<.00002,(p['id'],'grass clump XY moved')
    else:
     helper=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));poly=helper['hull'](p['vertices'])
     assert helper['inside'](b,poly) or min(helper['distance'](b,u,v) for u,v in zip(poly,poly[1:]+poly[:1]))<.00003,(p['id'],'patch left original footprint')
    if p['id'] in clump_fit:assert abs(b[2]-a[2]-clump_fit[p['id']]['zOffset'])<.00003,p['id']
  else:assert p['vertices']==q['vertices'],p['id']
  assert p['faces']==q['faces'],p['id'];assert p.get('uvs')==q.get('uvs'),p['id'];part_count+=1
  if p.get('visible')!=q.get('visible'):assert p['id'] in hidden and q.get('visible')==False,p['id']
  if p['role']=='solid':solid_count+=1;assert p.get('visible')==q.get('visible'),p['id']
allowed={r['id'] for r in curbs+roadsides}|{r['id'] for region in wear['regions'] for r in region['joints']};oldsurfs={s['id']:s for s in before['terrain']['surfaces']};changed=[]
for s in w['terrain']['surfaces']:
 if s['id'] in oldsurfs:
  old=oldsurfs[s['id']]
  if s['id'] not in allowed:
   for key in ('vertices','faces','uvs','walkable','visible'):assert s.get(key)==old.get(key),(s['id'],key)
  elif s['vertices']!=old['vertices']:changed.append(s['id'])
 else:assert not s['walkable'],('Unexpected new walkable floor',s['id'])
vs=[];fs=[];tri_uv=[];tri_mat=[]
for s in w['terrain']['surfaces']:
 if not s['walkable']:continue
 off=len(vs);vs.extend(s['vertices'])
 for fi,f in enumerate(s['faces']):
  for j in range(1,len(f)-1):
   ix=(0,j,j+1);fs.append(tuple(off+f[k] for k in ix));tri_uv.append([s['uvs'][fi][k] for k in ix] if s.get('uvs') else None);tri_mat.append(s['material'])
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def hit(p):
 result=floor.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),150);assert result[0] is not None;return result
contacts=0;images={}
for name in patch_fit:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  p=o.matrix_world@v.co;assert abs(p.z-hit(p)[0].z-.017)<.003,(name,'refitted foundation patch');contacts+=1
for name,rec in clump_fit.items():
 p=Vector(rec['newRoot']);assert abs(p.z-hit(p)[0].z-.017)<.003,(name,'refitted foundation clump');contacts+=1
for rec in roadsides:
 s=next(s for s in w['terrain']['surfaces'] if s['id']==rec['id'])
 for v in s['vertices']:assert abs(v[2]-hit(v)[0].z-.017)<.0002,(s['id'],'grass floor');contacts+=1
for region in wear['regions']:
 for root in region['joints']:
  p=Vector(root['point']);s=next(s for s in w['terrain']['surfaces'] if s['id']==root['id']);assert ((Vector(s['vertices'][0])+Vector(s['vertices'][1]))/2-p).length<.0001
  point,normal,idx,distance=hit(p);assert abs(p.z-point.z-.012)<.0002;file=w['materials'][tri_mat[idx]]['texture']['file'];assert file==root['jointArtwork'],(root['id'],'changed paving artwork',file,root['jointArtwork'])
  if file not in images:images[file]=Image.open(ROOT/file).convert('RGB')
  a,b,c=[vs[k] for k in fs[idx]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);wa=((b[1]-c[1])*(point.x-c[0])+(c[0]-b[0])*(point.y-c[1]))/den;wb=((c[1]-a[1])*(point.x-c[0])+(a[0]-c[0])*(point.y-c[1]))/den;uv=[sum(weight*pair[k] for weight,pair in zip((wa,wb,1-wa-wb),tri_uv[idx])) for k in (0,1)];im=images[file];rgb=im.getpixel((int((uv[0]%1)*im.width)%im.width,int((1-uv[1]%1)*im.height)%im.height));luma=(.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2])/255;assert luma<.57 and abs(luma-root['jointLuma'])<1e-5,(root['id'],'joint alignment',luma);contacts+=1
for rec in curbs:
 s=next(s for s in w['terrain']['surfaces'] if s['id']==rec['id']);assert abs(max(v[2] for v in s['vertices'])-rec['ground']-.20)<.0002;assert s['walkable'] and s['material']=='roadCurbStone';assert .30<=rec['width']<=.40
bed_contacts=0;verge_samples=0
for rec in composition.get('ownedTreeBeds',[]):
 s=next(s for s in w['terrain']['surfaces'] if s['id']==rec['id'])
 assert not s['walkable'] and s['material']=='plantingEdgeGrass'
 for v in s['vertices']:assert abs(v[2]-hit(v)[0].z-.017)<.0002,(s['id'],'tree bed contact');bed_contacts+=1
for rec in composition.get('broadenedBuildingVergeStrips',[]):
 s=next(s for s in w['terrain']['surfaces'] if s['id']==rec['id']);a,b,c,d=map(Vector,s['vertices'])
 for i in range(5):
  for j in range(5):
   p=a+(b-a)*i/4+(d-a)*j/4
   assert abs(p.z-hit(p)[0].z-.017)<.035,(s['id'],'verge interior');verge_samples+=1
for rec in composition.get('evergreens',[]):
 root=bpy.data.objects[rec['root']]
 for name in rec['parts']:
  o=bpy.data.objects[name];assert o.parent==root.parent and o.get('conifer_v70') and o.get('role')=='overhead',name
  assert all(f.normal.z>0 for f in o.data.polygons),(name,'exposed bough normal')
  layer=o.data.color_attributes.get('BakedTownLight');assert layer and len(layer.data)==len(o.data.loops),(name,'native branch shading')
  for corner in layer.data:assert .69<=corner.color[0]<=1.001 and .119<=corner.color[1]<=1.001,(name,'branch light factors')
assert w['lighting']['sun'].get('angularRadius')==.018 and w['lighting']['groundShadow']['sunSamples']==8
assert w['materials']['avenuePaving']['texture']['file']!=w['materials']['houseApronPaving']['texture']['file'];assert w['materials']['avenuePaving']['texture']['file']==w['materials']['publicSquareStone']['texture']['file'];assert wear['stoneImagePads']==0 and 'agedPathPatch' not in w['materials'];assert w['lighting']['shadowColor']=='#514d44';assert w['lighting']['sun']['cast']==[-.42,.55];assert w['lighting']['ambientColor']==[1.04,1,.9];assert w['lighting'].get('groundShadow'),'Current floor bake required'
report={'sourcePass':70,'preservedOriginalParts':part_count,'preservedSolids':solid_count,'unchangedOriginalGeometryParts':part_count-len(patch_fit)-len(clump_fit),'foundationPatchesRefitted':len(patch_fit),'foundationClumpsRefitted':len(clump_fit),'metadataAndAccessPreserved':True,'curbBlocks':len(curbs),'widenedCurbs':hierarchy['widenedCurbs'],'darkFascias':len(hierarchy['darkFascias']),'curbRise':.20,'changedExistingSurfaces':len(changed),'newDecorativeSurfaces':sum(s['id'] not in oldsurfs for s in w['terrain']['surfaces']),'roadsideGrassContacts':len(roadsides)*4,'jointGrassRoots':wear['jointGrassClumps'],'nativeContactChecks':contacts+bed_contacts+verge_samples,'treeBedContacts':bed_contacts,'broaderVergeInteriorSamples':verge_samples,'streetAndBuildingPavingDistinct':True,'noStoneImagePads':True,'lighting':w['lighting'],'composition':composition};output.write_text(json.dumps(report,indent=2)+'\n');print('PASS native RO3 composition:',json.dumps({k:v for k,v in report.items() if k not in ('lighting','composition')}))
