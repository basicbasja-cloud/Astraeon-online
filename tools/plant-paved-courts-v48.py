"""Add small planted tree courts in the paved interior; apply after v48 (safe to rerun).

The vegetation family covers both individual trees and grouped gardens. Only
individual editable tree placements receive pits. Decorative rims do not change
road collision, entrances or patrol routes.
"""
import bpy,bmesh,json,math,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('paved_city_version')==48
owner=bpy.data.collections['court-terrain']
def mesh(name,vs,fs,mat):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
 for f in data.polygons:
  for li in f.loop_indices:
   p=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p.x/3,p.y/3)
 o=bpy.data.objects.new(name,data);owner.objects.link(o);o['role']='decorative';o['shadow']=False
 return o
source=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
def inside(x,y,poly):
 return sum((a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0] for a,b in zip(poly,poly[1:]+poly[:1]))%2
pave=bpy.data.objects['city-v48-continuous-stone-interior'];outline=[tuple(v.co[:2]) for v in pave.data.vertices]
if not scene.get('paved_tree_pits'):
 count=0
 for tree in source['objects']:
  if tree['family']!='vegetation' or not tree.get('presentation'):continue
  x,y,_=tree['presentation']['position']
  if not inside(x,y,outline):continue
  r=1.03;n=14;angles=[k*math.tau/n for k in range(n)]
  soil=[(x+math.cos(a)*r,y+math.sin(a)*r,.045) for a in angles]
  mesh('city-v48-tree-soil-'+tree['id'],soil,[list(range(n))],'soil')
  vs=[(x+math.cos(a)*rr,y+math.sin(a)*rr,z) for z in (.04,.16) for rr in (r,r+.12) for a in angles]
  fs=[]
  for k in range(n):
   j=(k+1)%n;fs.extend([[k,j,n+j,n+k],[2*n+k,3*n+k,3*n+j,2*n+j],[k,2*n+k,2*n+j,j],[n+k,n+j,3*n+j,3*n+k]])
  mesh('city-v48-tree-curb-'+tree['id'],vs,fs,'stoneLight');count+=1
 scene['paved_tree_pits']=count
# Decorative geometry belongs to each tree collection. Terrain export only
# includes surfaces, so unmarked meshes in court-terrain would not ship.
for o in list(bpy.data.objects):
 prefix=next((p for p in ('city-v48-tree-soil-','city-v48-tree-curb-') if o.name.startswith(p)),None)
 if not prefix:continue
 collection=bpy.data.collections[o.name[len(prefix):]]
 if collection not in o.users_collection:
  for old in list(o.users_collection):old.objects.unlink(o)
  collection.objects.link(o)
 placement=next(p for p in collection.objects if p.get('kind')=='presentation');root=placement.parent or placement
 if o.parent!=root:
  world=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=world
count=scene['paved_tree_pits']
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Planted',count,'paved tree courts')
