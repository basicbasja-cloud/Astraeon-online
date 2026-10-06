"""Finish native source72 vegetation contacts and actual paving-joint registration."""
import bpy,json,runpy,random,sys
from pathlib import Path
from mathutils import Vector
from PIL import Image
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_blueprint_planting_version')==72 and not scene.get('ro3_blueprint_contacts_version')
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');record=json.loads(scene['ro3_blueprint_review_json'])
for o in terrain.objects:
 if o.name.startswith('lot69-') and '-rim-' in o.name:o['render_visible']=False;o['walkable']=False;record['retiredLegacyMeshes'].append(o.name)
fit=runpy.run_path(str(ROOT/'tools/fit-ro3-grass-contact-v70.py'))['fit'](scene)
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
# Register grass into the NEW actual top paving joints, with no stone-image pads.
images={};wear=json.loads(scene['ro3_path_wear_review_json']);rng=random.Random(7045)
def sample(p):
 hit,normal,idx,dist=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)
 spec=data['materials'][mats[idx]].get('texture',{}) if hit is not None else {}
 if spec.get('file') not in ('assets/wayfarer-aged-pavers-v69.webp','assets/wayfarer-street-stone-v70.webp') or not uvs[idx]:return None
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
wear['jointArtworks']=sorted(images);wear['sourcePass']=72;scene['ro3_path_wear_review_json']=json.dumps(wear)

scene['ro3_blueprint_contacts_version']=72;record['jointGrassClumps']=wear['jointGrassClumps'];record['retiredLegacyMeshes']=sorted(set(record['retiredLegacyMeshes']));scene['ro3_blueprint_review_json']=json.dumps(record)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS source72 actual native joint grass',wear['jointGrassClumps'],'clumps; all legacy rim ends retired')
