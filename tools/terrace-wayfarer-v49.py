"""Source-owned upper civic precinct, stair approaches and deeper river bank.

Repeatable after the v49 architectural pass. Changes floors, actor contacts,
building roots and retaining solids together; no runtime height overrides.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('concept_architecture_version')==49
PREFIX='terrace-v49-';HEIGHT=1.4
outline=[(25,17),(32,8),(48,8),(54,6),(60,8),(78,8),(78,33.3),(65.4,33.3),(65.4,40.6),(58,40.6),(58,35),(50,35),(50,40.6),(42.6,40.6),(42.6,35),(25,35)]
def inside(x,y):
 return sum((a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0] for a,b in zip(outline,outline[1:]+outline[:1]))%2
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for d in list(bpy.data.meshes):
 if d.name.startswith(PREFIX) and d.users==0:bpy.data.meshes.remove(d)
terrain=bpy.data.collections['court-terrain']
walls=bpy.data.collections.get('civic-terrace-retaining')
if not walls:walls=bpy.data.collections.new('civic-terrace-retaining');scene.collection.children.link(walls)
walls['family']='civic';owner=walls
def mesh(name,vs,fs,mat,role='decorative',walkable=False,bevel=0):
 d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(vs,[],fs)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=bevel,segments=2,affect='EDGES',clamp_overlap=True)
 bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(d);bm.free()
 d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
 for f in d.polygons:
  for li in f.loop_indices:
   p=d.vertices[d.loops[li].vertex_index].co;n=f.normal
   d.uv_layers.active.data[li].uv=(p.x/3,p.y/3) if abs(n.z)>.65 else (p.x/3,p.z/3) if abs(n.y)>abs(n.x) else (p.y/3,p.z/3)
 o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o['role']=role;o['shadow']=owner!=terrain
 if owner==terrain:o['surface_role']='forecourt';o['walkable']=walkable
 return o
def box(name,c,size,mat='stone',role='decorative'):
 x,y,z=c;a,b,h=[v/2 for v in size]
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,bevel=min(.055,min(size)*.1))
# Large buildings retain all registered services and material UVs through their
# editable roots. Each root baseline is saved once, never incrementally raised.
names=['guild-hall','district-garden-row-house','district-northern-townhouse','frontage-garden-home','frontage-scribe','consortium-forecourt-arcades','north-gate']
roots=[]
for name in names:
 r=bpy.data.objects.get(name+'-placement')
 if not r:
  # Some inherited civic parts are grouped without a placement root.
  r=bpy.data.objects.new(name+'-placement',None);bpy.data.collections[name].objects.link(r)
  for o in list(bpy.data.collections[name].objects):
   if o==r or o.parent:continue
   m=o.matrix_world.copy();o.parent=r;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=m
 if 'terrace_v49_base_z' not in r:r['terrace_v49_base_z']=r.location.z
 r.location.z=r['terrace_v49_base_z']+HEIGHT;roots.append(r)
 bpy.data.collections[name]['concept_terrace_height']=HEIGHT
bpy.context.view_layer.update()
# Plant the two inherited grove components beside the upper garden lane,
# clear of the west flight. Each entire tree keeps one source translation.
for prefix,dx,dy in [('grove-v44-16-',-.2,-5.6),('grove-v44-17-',1.1,-5.3)]:
 for o in bpy.data.objects:
  if not o.name.startswith(prefix):continue
  if 'terrace_v49_grove_origin' not in o:o['terrace_v49_grove_origin']=list(o.location)
  base=o['terrace_v49_grove_origin'];o.location.x=base[0]+dx;o.location.y=base[1]+dy
bpy.context.view_layer.update()
def follows_root(o):
 while o:
  if o in roots:return True
  o=o.parent
 return False
# Compact props and individual tree placements follow their physical court.
# Large grouped groves/street collections use their individual source meshes.
for c in bpy.data.collections:
 if not c.get('family') or c['family']=='terrain' or c==walls or c.name in names:continue
 for o in c.objects:
  if follows_root(o) or o.type!='MESH' or not o.get('render_visible',True):continue
  vs=[o.matrix_world@v.co for v in o.data.vertices]
  if not vs:continue
  p=sum(vs,Vector())/len(vs)
  if not inside(p.x,p.y):continue
  if c['family']=='fortification':
   # Curtain walls keep their water-side feet and stretch the upper masonry.
   if not o.get('terrace_v49_wall_stretched'):
    inv=o.matrix_world.inverted()
    for v in o.data.vertices:
     q=o.matrix_world@v.co
     if q.z>=-.05:q.z+=HEIGHT;v.co=inv@q
    o['terrace_v49_wall_stretched']=True
  else:
   if 'terrace_v49_base_world_z' not in o:o['terrace_v49_base_world_z']=o.matrix_world.translation.z
   m=o.matrix_world.copy();m.translation.z=o['terrace_v49_base_world_z']+HEIGHT;o.matrix_world=m
# Existing steps/landing share the Hall root. Other terrain overlays remain
# beneath the new precinct, whose concave top is triangulated in Blender.
owner=terrain
mesh('upper-civic-floor',[(x,y,HEIGHT+.045) for x,y in outline],[list(range(len(outline)))],'cityPaving',walkable=True)
# The old corridors crossed the moved houses and tavern wing. Re-author the
# affected streets so connected paving does not conceal a contradictory plan.
for o in list(terrain.objects):
 if o.name.startswith(('organic-v47-plan-v44-north-garden-street-','organic-v47-plan-v44-inn-lane-')):bpy.data.objects.remove(o,do_unlink=True)
def lane(name,points,width,z):
 for i,(a,b) in enumerate(zip(points,points[1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*width/2,dx/length*width/2
  vs=[(a[0]+nx,a[1]+ny,z),(b[0]+nx,b[1]+ny,z),(b[0]-nx,b[1]-ny,z),(a[0]-nx,a[1]-ny,z)]
  o=mesh(name+'-'+str(i),vs,[[0,1,2,3]],'cityPaving',walkable=True);o['surface_role']='primary';o['road_segment']=True;o['legacy_role']='street'
lane('north-garden-street',[(26.3,32.65),(33,32.65),(42,32.70),(50,32.65),(58,32.65),(65,32.10),(76.8,32.10)],1.8,HEIGHT+.053)
lane('inn-lane',[(23.7,31.7),(23.7,41.8),(21.3,44.7),(17,44.7)],2.0,.054)
# A flat top is a contact surface, the side walls are actual blocked geometry.
# Keep openings for three public flights: axial, west and east.
gaps=[(35,50,58),(35,25.1,27.5),(33.3,73.1,74.9)]
owner=walls
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);segments=[(0,1)]
 if abs(dy)<.001:
  for y,x0,x1 in gaps:
   if abs(a[1]-y)>.01:continue
   p,q=sorted(((x0-a[0])/dx,(x1-a[0])/dx));remaining=[]
   for lo,hi in segments:
    if p>lo:remaining.append((lo,min(hi,p)))
    if q<hi:remaining.append((max(lo,q),hi))
   segments=[(lo,hi) for lo,hi in remaining if hi-lo>.001]
 for j,(lo,hi) in enumerate(segments):
  aa=Vector((a[0]+dx*lo,a[1]+dy*lo,0));bb=Vector((a[0]+dx*hi,a[1]+dy*hi,0));v=bb-aa;n=Vector((-v.y,v.x,0)).normalized()*.19
  vs=[tuple(p+s*n+Vector((0,0,z))) for z in (-.08,HEIGHT+.53) for p in (aa,bb) for s in (-1,1)]
  mesh('retaining-wall-'+str((i,j)),vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],'stone','solid',bevel=.05)
  # Coped stone crown with short pilasters gives the edge architectural depth.
  vs=[tuple(p+s*n*1.33+Vector((0,0,z))) for z in (HEIGHT+.49,HEIGHT+.65) for p in (aa,bb) for s in (-1,1)]
  mesh('wall-coping-'+str((i,j)),vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],'stoneLight',bevel=.035)
  for k in range(int(v.length/3.6)+1):
   p=aa+v*k/max(1,int(v.length/3.6));box('wall-buttress-'+str((i,j,k)),(p.x,p.y,HEIGHT*.53),(.60,.60,HEIGHT+1.0),'stoneLight','solid')
for name,x0,x1,y,run in [('processional',50,58,35,4.2),('garden-west',25.1,27.5,35,3.6),('scribe-east',73.1,74.9,33.3,3.6)]:
 for k in range(8):
  top=(k+1)*HEIGHT/8+.045;y0=y+run*(7-k)/8;y1=y+run*(8-k)/8
  owner=walls;box(name+'-riser-'+str(k),((x0+x1)/2,(y0+y1)/2,top/2),(x1-x0,y1-y0,top),'stoneLight')
  owner=terrain;mesh(name+'-tread-'+str(k),[(x0,y0,top),(x1,y0,top),(x1,y1+.035,top),(x0,y1+.035,top)],[[0,1,2,3]],'cityPaving',walkable=True)
 for x in (x0-.23,x1+.23):
  owner=walls
  for k in range(8):
   top=(k+1)*HEIGHT/8+.58;y0=y+run*(7-k)/8;y1=y+run*(8-k)/8
   box(name+'-stair-cheek-'+str((x,k)),(x,(y0+y1)/2,top/2),(.36,y1-y0+.02,top),'stone','solid')
# The city is set above water: deepen the existing source bank, pier feet and
# river together without changing bridge decks, ground routes or map bounds.
if not scene.get('river_depth_version_v49'):
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  vs=[o.matrix_world@v.co for v in o.data.vertices]
  if not vs or min(v.z for v in vs)>-1:continue
  inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z<0:p.z*=1.8;v.co=inv@p
 scene['river_depth_version_v49']=49
scene['civic_terrace_height_v49']=HEIGHT;scene['terraced_city_version']=49
scene['layout_id']='wayfarer-concept-terraced-town-v49'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved raised civic precinct, three eight-tread flights, source retaining walls and deepened river bank')
