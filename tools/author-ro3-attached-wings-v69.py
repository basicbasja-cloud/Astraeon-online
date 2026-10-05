"""Pierced, framed native shells for eleven inherited plain attached wings.

Retain hidden collision cores and roof ownership. Only outward-facing glazing
with clear rays is authored, avoiding buried windows at main-building junctions.
"""
import bpy,bmesh,json,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_house_life_version')==69
# Repeat only this saved wing migration after a geometric clearance iteration.
if scene.get('ro3_wing_detail_version'):
 for record in json.loads(scene['ro3_wing_detail_review_json']):
  bpy.data.objects[record['hiddenWingCore']]['render_visible']=True
  bpy.data.objects[record['hiddenWingCore']]['shadow']=True
 bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('wing69-')])
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def hull(pts):
 p=sorted(set((round(v.x,5),round(v.y,5)) for v in pts))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def chain(seq):
  out=[]
  for v in seq:
   while len(out)>1 and cross(out[-2],out[-1],v)<=0:out.pop()
   out.append(v)
  return out
 return chain(p)[:-1]+chain(reversed(p))[:-1]
def fit(objects,a,t,n):
 for o in objects:
  for v in o.data.vertices:
   q=v.co.copy();v.co=a+t*q.x+n*q.y+Vector((0,0,q.z))
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
records=[]
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 wings=[o for o in c.objects if o.type=='MESH' and len(o.data.vertices)==8 and o.get('render_visible',True) and 'wing' in o.name and o.data.materials[0].name in ('plaster','homeLimewash','merchantLimewash','workshopLimewash')]
 for index,core in enumerate(wings):
  root=core.parent
  if root is None:
   main=next(o for o in c.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls')))
   root=main.parent
   prefix=core.name.removesuffix('-wall')
   for part in c.objects:
    if part.type=='MESH' and part.name.startswith(prefix) and part.parent is None:
     original=part.matrix_world.copy();part.parent=root;part.matrix_parent_inverse=root.matrix_world.inverted();part.matrix_world=original
  assert root,c.name;inv=root.matrix_world.inverted();points=[inv@core.matrix_world@v.co for v in core.data.vertices];outline=hull(points);base=min(v.z for v in points);top=max(v.z for v in points)
  core['render_visible']=False;core['shadow']=False;kit=Kit(c,root);kit.prefix='wing69-'+c.name[:18]+'-'
  vertices=[];triangles=[]
  for o in c.objects:
   if o==core or o.type!='MESH' or not o.get('render_visible',True) or o.data.materials[0].name=='frontageGlazing':continue
   off=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();triangles.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
  tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);windows=0
  for edge,(aa,bb) in enumerate(zip(outline,outline[1:]+outline[:1])):
   a,b=Vector((*aa,0)),Vector((*bb,0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));length=(b-a).length;openings=[]
   z=base+1.85;ww=.94;hh=1.32
   for j,s in enumerate([length*.31,length*.69] if length>3.6 else [length*.5] if length>1.8 else []):
    direction=(root.matrix_world.to_3x3()@n).normalized()
    if any(tree.ray_cast(root.matrix_world@(a+t*(s+dx)+n*(-.065)+Vector((0,0,z+dz))),direction,.75)[0] is not None for dx in (-.36,0,.36) for dz in (-.47,0,.47)):continue
    openings.append((s-ww/2,s+ww/2,z-hh/2,z+hh/2));before=set(c.objects)
    kit.window(f'window-{edge}-{j}',s,0,z,ww,hh,recess=.105,low=True)
    fit(set(c.objects)-before,a,t,n)
    glass=next(o for o in set(c.objects)-before if o.name.endswith('-glass'));glass['wing69_normal']=list(n);windows+=1
   xs=sorted({0,length,*[v for h in openings for v in h[:2]]});zs=sorted({base,top,min(base+2.7,top),*[v for h in openings for v in h[2:]]})
   before=set(c.objects)
   for xi,(l,r) in enumerate(zip(xs,xs[1:])):
    for zi,(lo,hi) in enumerate(zip(zs,zs[1:])):
     if any(h[0]<(l+r)/2<h[1] and h[2]<(lo+hi)/2<h[3] for h in openings):continue
     mat='streetBrickLime' if hi<base+2.7 else 'homeLimewash'
     kit.box(f'panel-{edge}-{xi}-{zi}',((l+r)/2,-.10,(lo+hi)/2),(r-l,.20,hi-lo),mat)
   for j,s in enumerate([.10,length-.10]+[length*.5] if length>3.6 else [.10,length-.10]):
    if any(h[0]-.14<s<h[1]+.14 for h in openings):continue
    kit.box(f'post-{edge}-{j}',(s,.04,(base+top)/2),(.18,.08,top-base),'timber')
   for j,(zz,mat) in enumerate([(base+.18,'stoneLight'),(top-.15,'timber')]):kit.box(f'belt-{edge}-{j}',(length*.5,.04,zz),(length,.08,.20),mat)
   # Braces only above windows, avoiding the street-level body clearance.
   if top-base>3.7:
    for side in (-1,1):
     xx=.25 if side<0 else length-.25
     kit.beam(f'knee-{edge}-{side}',(xx,.04,top-.23),(xx-side*.42,.04,top-.83),.11)
   fit(set(c.objects)-before,a,t,n)
  records.append({'owner':c.name,'hiddenWingCore':core.name,'clearWindows':windows,'sourceTop':top,'sourceBase':base})
assert len(records)==11,len(records)
scene['ro3_wing_detail_version']=69;scene['ro3_wing_detail_review_json']=json.dumps(records)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Detailed',len(records),'attached wings;',sum(p['clearWindows'] for p in records),'pierced windows; rebake both lights')
