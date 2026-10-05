"""Distinct public stones, rectangular lot walks, readable curbs and warm native light."""
import bpy,json,runpy,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_spatial_hierarchy_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');art=json.loads((ROOT/'authoring/materials/wayfarer-street-stone-v70.json').read_text())
m=bpy.data.materials['avenuePaving'];m['texture_json']=json.dumps(art['texture']);m.diffuse_color=(.46,.445,.37,1)
square=m.copy();square.name='publicSquareStone';square.diffuse_color=(.53,.50,.40,1)
walk=bpy.data.materials['paving'];walk.diffuse_color=(.60,.545,.435,1)
for name in ('cityPaving','houseApronPaving'):bpy.data.materials[name].diffuse_color=(.57,.515,.405,1)
public=[];walks=[]
for o in terrain.objects:
 if o.type!='MESH' or not o.data.materials:continue
 name=o.data.materials[0].name
 if o.name=='organic-v47-civic-court':o.data.materials[0]=square;public.append(o.name)
 elif name=='avenuePaving' and o.get('surface_role')=='forecourt':o.data.materials[0]=walk;walks.append(o.name)
 elif name=='cityPaving' and o.get('surface_role')=='primary' and o.get('road_segment'):o.data.materials[0]=m;public.append(o.name)
 # The continuous underlay remains rectangular so building-side zones read as walks.
scene['sun_cast_x']=-.42;scene['sun_cast_y']=.55;scene['sun_angular_radius']=.018;scene['ambient']=.44;scene['sun_strength']=.65;scene['ambient_color_json']=json.dumps([1.04,1.00,.90]);scene['sun_color_json']=json.dumps([1.18,1.05,.79]);scene['shadow_color']='#514d44'
base=bpy.data.materials['roadCurbStone'];base.diffuse_color=(.48,.49,.435,1)
side=base.copy();side.name='roadCurbFace';side.diffuse_color=(.255,.27,.235,1)
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];protected=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])]
review=json.loads(scene['ro3_road_curb_review_json']);kit=Kit(terrain,None);kit.prefix='curb70-';widened=0;fascias=[]
for rec in review['curbBlocks']:
 o=bpy.data.objects[rec['id']];p=[o.matrix_world@v.co for v in o.data.vertices];n=p[1]-p[0];n.z=0;n.normalize();a,b=p[0],p[6];ground=rec['ground'];width=.40
 q=[tuple((v+n*d)[:2]) for v,d in ((a,0),(b,0),(b,width),(a,width))]
 if any(h['overlap'](q,s,.06) for s in solids) or any(h['inside'](p,q) or min(h['distance'](p,a,b) for a,b in zip(q,q[1:]+q[:1]))<.70 for p in protected):width=.30
 if width>.30:widened+=1
 profile=[(0,.012),(width,.012),(width,.15),(width-.035,.20),(.035,.20),(0,.15)];points=[v+n*d+Vector((0,0,ground+z-v.z)) for v in (a,b) for d,z in profile];inv=o.matrix_world.inverted()
 for v,p in zip(o.data.vertices,points):v.co=inv@p
 # Dark vertical fascia is native geometry on both sides; bevel and top stay gray.
 verts=[];faces=[]
 for k,direction in ((1,n),(5,-n)):
  f=[points[k]+direction*.001,points[(k+1)%6]+direction*.001,points[(k+1)%6+6]+direction*.001,points[k+6]+direction*.001];off=len(verts);verts.extend(tuple(v) for v in f);faces.append([off+i for i in range(4)])
 fascia=kit.mesh('fascia-'+rec['id'],verts,faces,'roadCurbFace',False);del fascia['role'];fascia['surface_role']='forecourt';fascia['walkable']=False;fascia['curb_fascia_v70']=True;fascias.append(fascia.name);rec.update(rise=.20,width=width,sourcePass=70)
scene['ro3_road_curb_review_json']=json.dumps(review)
bpy.context.view_layer.update()
def floor_data():
 data=exporter['export'](scene);vs=[];fs=[];uvs=[];mats=[]
 for s in data['terrain']['surfaces']:
  if not s['walkable']:continue
  off=len(vs);vs.extend(s['vertices'])
  for fi,f in enumerate(s['faces']):
   for j in range(1,len(f)-1):
    corners=(0,j,j+1);fs.append(tuple(off+f[k] for k in corners));uvs.append([s['uvs'][fi][k] for k in corners] if s.get('uvs') else None);mats.append(s['material'])
 return data,vs,fs,uvs,mats,BVHTree.FromPolygons(vs,fs,all_triangles=True)
data,vs,fs,uvs,mats,floor=floor_data()
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
# Keep existing roadside grass beyond the wider curb and refit each corner.
grass=json.loads(scene['ro3_curb_grass_review_json'])
for rec in grass['strips']:
 o=bpy.data.objects[rec['id']];pts=[o.matrix_world@v.co for v in o.data.vertices];n=pts[3]-pts[0];n.z=0;n.normalize();inv=o.matrix_world.inverted()
 for v,p in zip(o.data.vertices,pts):p+=n*.15;p.z=ground(p)+.017;v.co=inv@p
 rec['curbOffsetAdded']=.15
 rec['vertices']=[list(o.matrix_world@v.co) for v in o.data.vertices]
scene['ro3_curb_grass_review_json']=json.dumps(grass)
# Register grass into the NEW actual top paving joints, with no stone-image pads.
images={};wear=json.loads(scene['ro3_path_wear_review_json']);rng=random.Random(7045)
def sample(p):
 hit,normal,idx,dist=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)
 spec=data['materials'][mats[idx]].get('texture',{}) if hit is not None else {}
 if spec.get('file') not in ('assets/wayfarer-aged-pavers-v69.webp',art['texture']['file']) or not uvs[idx]:return None
 file=spec['file']
 if file not in images:images[file]=Image.open(ROOT/file).convert('RGB')
 im=images[file];a,b,c=[Vector(vs[k]) for k in fs[idx]];v0=b-a;v1=c-a;v2=hit-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01;t=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;u=(d00*v2.dot(v1)-d01*v2.dot(v0))/den;uv=[uvs[idx][0][k]+t*(uvs[idx][1][k]-uvs[idx][0][k])+u*(uvs[idx][2][k]-uvs[idx][0][k]) for k in (0,1)];rgb=im.getpixel((int((uv[0]%1)*im.width)%im.width,int((1-uv[1]%1)*im.height)%im.height));luma=(.2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2])/255;return hit,luma,file
for region in wear['regions']:
 a,b,c,d=[Vector(p) for p in region['vertices']];candidates=[]
 for u in range(2,39):
  for v in range(2,39):
   result=sample(a+(b-a)*u/40+(d-a)*v/40)
   if result and result[1]<.57:candidates.append(result)
 rng.shuffle(candidates);chosen=[]
 for result in candidates:
  if all((result[0].xy-p[0].xy).length>.19 for p in chosen):chosen.append(result)
  if len(chosen)==len(region['joints']):break
 assert len(chosen)==len(region['joints']),(region['formerPad'],len(candidates),len(chosen))
 for rec,(hit,luma,file) in zip(region['joints'],chosen):
  o=bpy.data.objects[rec['id']];old=Vector(rec['point']);root=hit+Vector((0,0,.012));inv=o.matrix_world.inverted()
  for v in o.data.vertices:v.co=inv@(root+(o.matrix_world@v.co-old))
  rec.update(point=list(root),jointLuma=luma,jointArtwork=file);o['paving_joint_root']=list(root);o['paving_joint_luma']=luma
wear['jointArtworks']=sorted(images);wear['sourcePass']=70;scene['ro3_path_wear_review_json']=json.dumps(wear)
scene['ro3_spatial_hierarchy_version']=70;scene['ro3_spatial_hierarchy_review_json']=json.dumps({'publicStone':art,'publicMaterials':['avenuePaving','publicSquareStone'],'buildingSideMaterials':['paving','cityPaving','houseApronPaving'],'publicSurfaceOverrides':public,'stairWalkOverrides':walks,'curbs':len(review['curbBlocks']),'widenedCurbs':widened,'curbRise':.20,'curbWidths':[.30,.40],'darkFascias':fascias,'roadsideGrassRefits':len(grass['strips']),'jointGrassClumps':wear['jointGrassClumps'],'lighting':{'ambient':.44,'ambientColor':[1.04,1,.90],'sunStrength':.65,'sunColor':[1.18,1.05,.79],'shadowColor':'#514d44','sunCast':[-.42,.55],'sunAngularRadius':.018,'sunSamples':8},'protected':'Original house solids, actor artwork/scale, services, doors, routes and open crossings; no stone-image pads'})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS source70 hierarchy:',len(review['curbBlocks']),'readable curbs;',widened,'wider;',len(public),'public surface overrides;',len(walks),'rectangular stair walks; warm light')
