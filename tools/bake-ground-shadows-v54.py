"""Bake native building casts and local floor contact depth from the saved city.

Uses actual visible caster triangles, four nearby sun directions and
four short contact rays. Foliage rays sample the original cutout alpha rather
than baking rectangular cards as solid tree canopies. It does not alter
models, navigation, UVs or actor artwork. Repeat after any geometry/light edit.
"""
import bpy,json,math,runpy,time,os,base64,zlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))
data=exporter['export'](scene);digest=exporter['shadow_geometry_digest'](data)
bounds=data['terrain']['bounds'];size=int(scene.get('ground_shadow_resolution',1024))
assert 64<=size<=4096

def tree_from(parts):
 vertices=[];triangles=[]
 for p in parts:
  base=len(vertices);vertices.extend(p['vertices'])
  for face in p['faces']:
   triangles.extend((base+face[0],base+face[i],base+face[i+1]) for i in range(1,len(face)-1))
 return BVHTree.FromPolygons(vertices,triangles,all_triangles=True)

casters=[p for o in data['objects'] for p in o['parts'] if p.get('shadow') and p.get('visible') is not False]
cache_path=os.environ.get('ASTRAEON_SHADOW_ALPHA_CACHE')
alpha_cache=json.loads(Path(cache_path).read_text()) if cache_path else {}
for info in alpha_cache.values():info['pixels']=zlib.decompress(base64.b64decode(info['alpha']))
vertices=[];triangles=[];cutouts=[]
for p in casters:
 base=len(vertices);vertices.extend(p['vertices']);spec=data['materials'][p['material']].get('texture',{})
 for fi,face in enumerate(p['faces']):
  for i in range(1,len(face)-1):
   indices=[face[0],face[i],face[i+1]];triangles.append(tuple(base+j for j in indices))
   if spec.get('alphaCutoff'):
    assert spec['file'] in alpha_cache,'Run prepare-shadow-alpha.py and set ASTRAEON_SHADOW_ALPHA_CACHE'
    cutouts.append((spec,[p['uvs'][fi][j] for j in (0,i,i+1)]))
   else:cutouts.append(None)
caster_tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
def cast_ray(origin,direction,distance):
 travelled=0
 for _ in range(48):
  hit,normal,index,length=caster_tree.ray_cast(origin,direction,distance-travelled)
  if hit is None:return None
  cutout=cutouts[index]
  if cutout:
   spec,uvs=cutout;a,b,c=[Vector(vertices[j]) for j in triangles[index]]
   v0=b-a;v1=c-a;v2=hit-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
   v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;u=1-v-w
   tx=sum(weight*uv[0] for weight,uv in zip((u,v,w),uvs))%1;ty=sum(weight*uv[1] for weight,uv in zip((u,v,w),uvs))%1
   cols,rows=spec['grid'];tile=spec['tile'];info=alpha_cache[spec['file']];width,height=info['size']
   px=min(width-1,int((tile%cols+tx)*width/cols));py=min(height-1,int((tile//cols+1-ty)*height/rows))
   if info['pixels'][py*width+px]/255>=spec['alphaCutoff']:return travelled+length
   travelled+=length+.002;origin=hit+direction*.002
   if travelled>=distance:return None
  else:return travelled+length
 raise RuntimeError('Cutout ray exceeds 48 intersections')
floors=[s for s in data['terrain']['surfaces'] if s.get('walkable') and s.get('vertices')]
floor_tree=tree_from(floors)
land=[data['terrain']['walkablePolygon']]+[s['polygon'] for s in floors]
def inside(x,y,poly):
 result=False
 for a,b in zip(poly,poly[-1:]+poly[:-1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result

cast=data['lighting']['sun']['cast'];sun=Vector((-cast[0],-cast[1],1)).normalized()
right=sun.cross(Vector((0,0,1))).normalized();up=right.cross(sun).normalized()
directions=[(sun+right*x*.006+up*y*.006).normalized() for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
contact=[Vector((x,y,.60)).normalized() for x,y in [(.8,0),(-.8,0),(0,.8),(0,-.8)]]
pixels=[1.0,1.0,1.0,0.0]*(size*size);start=time.monotonic();occupied=0;shadowed=0
for iy in range(size):
 y=bounds['minY']+(iy+.5)/size*(bounds['maxY']-bounds['minY'])
 for ix in range(size):
  x=bounds['minX']+(ix+.5)/size*(bounds['maxX']-bounds['minX'])
  if not any(inside(x,y,p) for p in land):continue
  occupied+=1
  hit=floor_tree.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  z=max(data['terrain']['elevation'],hit[0].z if hit[0] is not None else data['terrain']['elevation'])
  origin=Vector((x,y,z+.045))
  sun_occ=sum(cast_ray(origin,d,100) is not None for d in directions)/len(directions)
  ao=0
  for d in contact:
   hit=cast_ray(origin,d,1.4)
   if hit is not None:ao+=1-hit/1.4
  direct=sun_occ*data['lighting']['sun']['strength'];local=ao/len(contact)*.18
  opacity=direct+(1-direct)*local
  # Blender image buffers have a bottom-left origin. The PNG atlas is authored
  # top-left/minY to match the runtime's existing floor UV convention.
  pixels[((size-1-iy)*size+ix)*4+3]=opacity
  if opacity>.01:shadowed+=1
 if iy%128==0:print('GROUND BAKE',iy,'/',size,'seconds',round(time.monotonic()-start,1),flush=True)
image=bpy.data.images.new('Wayfarer native ground shadows v54',width=size,height=size,alpha=True)
image.pixels.foreach_set(pixels);image.file_format='PNG';image.filepath_raw=str(ROOT/'assets/wayfarer-ground-shadow-v54.png');image.save()
metadata={'file':'assets/wayfarer-ground-shadow-v54.png','resolution':size,'geometryDigest':digest,'strengthIncluded':True,'sunSamples':4,'contactSamples':4,'alphaCutoutCanopies':'original-alpha-tested'}
scene['ground_shadow_bake_json']=json.dumps(metadata,separators=(',',':'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
# Export only when this task is run after active gameplay reviews have ended.
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved native floor shadow bake',occupied,'land pixels,',shadowed,'shadowed;',round(time.monotonic()-start,1),'seconds',flush=True)
