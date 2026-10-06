"""Bake original-alpha sun/contact shade into the native evergreen face corners.

Uses the same original alpha, affine UV projection and bounded transparent-ray
continuation as the floor bake. No geometry, UV, floor or runtime raycast changes.
Run after the architecture bake when either foliage or sunlight changes.
"""
import bpy,json,math,runpy,os,base64,zlib,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));world=exporter['export'](scene)
cache=json.loads(Path(os.environ['ASTRAEON_SHADOW_ALPHA_CACHE']).read_text())
for spec in cache.values():spec['pixels']=zlib.decompress(base64.b64decode(spec['alpha']))
vertices=[];triangles=[];cutouts=[]
for owner in world['objects']:
 for part in owner['parts']:
  if not part.get('shadow') or not part.get('visible',True):continue
  off=len(vertices);vertices.extend(part['vertices']);spec=world['materials'][part['material']].get('texture',{})
  for fi,face in enumerate(part['faces']):
   for j in range(1,len(face)-1):
    corners=(0,j,j+1);indices=[face[k] for k in corners];triangles.append(tuple(off+k for k in indices))
    if not spec.get('alphaCutoff'):cutouts.append(None);continue
    a,b,c=map(Vector,(part['vertices'][k] for k in indices));ab=b-a;ac=c-a;den=ab.dot(ab)*ac.dot(ac)-ab.dot(ac)**2;assert den>1e-15
    vb=(ac.dot(ac)*ab-ab.dot(ac)*ac)/den;wb=(ab.dot(ab)*ac-ab.dot(ac)*ab)/den;uv=[part['uvs'][fi][k] for k in corners];grad=[]
    for axis in (0,1):
     g=vb*(uv[1][axis]-uv[0][axis])+wb*(uv[2][axis]-uv[0][axis]);grad.append((g,uv[0][axis]-g.dot(a)))
    cutouts.append((grad,spec,cache[spec['file']]))
tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);max_steps=0
def ray(origin,direction,distance):
 global max_steps
 travelled=0
 for step in range(256):
  max_steps=max(max_steps,step);hit,normal,index,length=tree.ray_cast(origin,direction,distance-travelled)
  if hit is None:return None
  cutout=cutouts[index]
  if cutout:
   grad,spec,info=cutout;u=(grad[0][0].dot(hit)+grad[0][1])%1;v=(grad[1][0].dot(hit)+grad[1][1])%1;cols,rows=spec['grid'];tile=spec['tile'];width,height=info['size'];x=min(width-1,int((tile%cols+u)*width/cols));y=min(height-1,int((tile//cols+1-v)*height/rows))
   if info['pixels'][y*width+x]>=spec['alphaCutoff']*255:return travelled+length
   travelled+=length+.002;origin=hit+direction*.002
   if travelled>=distance:return None
  else:return travelled+length
 raise RuntimeError('Foliage ray exceeds 256 transparent intersections')
cast=world['lighting']['sun']['cast'];sun=Vector((-cast[0],-cast[1],1)).normalized();right=sun.cross(Vector((0,0,1))).normalized();up=right.cross(sun).normalized();angular=world['lighting']['sun']['angularRadius'];directions=[(sun+right*math.cos(k*math.tau/4)*angular+up*math.sin(k*math.tau/4)*angular).normalized() for k in range(4)]
samples=[(.55,0,.835),(-.55,0,.835),(0,.55,.835),(0,-.55,.835)]
exported_parts={part['id'] for owner in world['objects'] for part in owner['parts']}
count=0;shadowed=0;start=time.monotonic();minimum=1.;maximum=0.;mesh_count=0
for o in bpy.data.objects:
 if not o.get('conifer_v70') or o.name not in exported_parts:continue
 data=o.data;old=data.color_attributes.get('BakedTownLight')
 if old:data.color_attributes.remove(old)
 layer=data.color_attributes.new(name='BakedTownLight',type='FLOAT_COLOR',domain='CORNER');mesh_count+=1
 for face in data.polygons:
  normal=(o.matrix_world.to_3x3()@face.normal).normalized();center=o.matrix_world@face.center;tangent=normal.cross(Vector((0,0,1)))
  if tangent.length<.1:tangent=normal.cross(Vector((0,1,0)))
  tangent.normalize();other=normal.cross(tangent).normalized()
  for li in face.loop_indices:
   point=(o.matrix_world@data.vertices[data.loops[li].vertex_index].co).lerp(center,.04)+normal*.025
   visible=.12+.88*sum(ray(point,d,100) is None for d in directions)/len(directions)
   occ=0
   for x,y,z in samples:
    distance=ray(point,tangent*x+other*y+normal*z,.85)
    if distance is not None:occ+=max(0,1-distance/.85)
   ao=1-.30*occ/len(samples);layer.data[li].color=(ao,visible,0,1);count+=1;shadowed+=visible<.9;minimum=min(minimum,visible);maximum=max(maximum,visible)
scene['ro3_foliage_light_v70_json']=json.dumps({'meshes':mesh_count,'corners':count,'shadedCorners':shadowed,'sunVisibilityRange':[minimum,maximum],'sunRays':4,'contactRays':4,'originalAlpha':True,'maxTransparentIntersections':max_steps,'geometryAndUVUnchanged':True})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS original-alpha foliage light:',mesh_count,'meshes;',count,'corners;',shadowed,'shaded;',round(time.monotonic()-start,1),'seconds')
