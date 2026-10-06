"""Reorganize source74 into the integrated royal capital, once, in native Blender.

Existing complete assemblies retain their authored shape and UVs. New houses
use detailed component construction, while original civic masses have pierced
stone facades. The saved native source remains the sole exported authority.
"""
import bpy,json,math,runpy,bmesh,time
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_public_floor_version')==74 and not scene.get('capital_version')
p=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());assert p['royalGeometricCity'] and p['integratedCity']
FacadeKit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
terrain=bpy.data.collections['court-terrain'];original_collections=list(bpy.data.collections)
def collection(name,family):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);c['family']=family;return c
def root(c,position=(0,0,0),angle=0):
 o=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(o);o.location=position;o.rotation_euler.z=angle;return o
def kit(c,r=None):
 k=FacadeKit(c,r or root(c));k.prefix='capital-v75-';return k
def floor(spec):
 data=bpy.data.meshes.new(spec['id']);data.from_pydata(spec['vertices'],[],spec['faces']);data.materials.append(bpy.data.materials[spec['material']]);data.uv_layers.new(name='WorldUV')
 scale=8 if spec['material'] in ('publicTownStone','houseApronPaving') else json.loads(bpy.data.materials[spec['material']].get('texture_json','{}')).get('worldSize',2.4)
 for face in data.polygons:
  for li in face.loop_indices:
   v=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale)
 o=bpy.data.objects.new(spec['id'],data);terrain.objects.link(o);o['surface_role']=spec['role'];o['walkable']=spec.get('walkable',True)
 if spec.get('objectId'):o['object_id']=spec['objectId']
 if '-entry-contact-' in spec['id'] or '-entry-tread-' in spec['id']:o['render_visible']=False
 return o
# Retain original geometry as an editable archive; omit it from shipping export.
kept=set(p['transforms'])|{'caravan-gate','north-gate','court-terrain','food-market','market-spices','market-supplies','market-textiles'}
owned={o for c in original_collections if c.name in kept for o in c.objects}
def has_ancestor(o,objects):
 par=o.parent
 while par:
  if par in objects:return True
  par=par.parent
 return False
# Cross-owned detailing follows the original building, without double movement.
for c in original_collections:
 if not c.get('family') or c.name in kept:continue
 for o in list(c.objects):
  if has_ancestor(o,owned):
   par=o.parent
   while par and not any(cc.name in kept and cc.get('family')!='terrain' for cc in par.users_collection):par=par.parent
   if par:
    target=next(cc for cc in par.users_collection if cc.name in kept and cc.get('family')!='terrain')
    if o.name not in target.objects:target.objects.link(o)
 c['capital_reference_family']=c['family'];del c['family'];c.hide_render=True;c.hide_viewport=True
# All original part matrices are transformed from the same baseline frame.
all_moving={o for n in p['transforms'] for o in bpy.data.collections[n].objects}
for name,t in p['transforms'].items():
 mat=Matrix.Translation(Vector(t['after']))@Matrix.Rotation(t['rotation'],4,'Z')@Matrix.Translation(-Vector(t['before']))
 for o in bpy.data.collections[name].objects:
  if not has_ancestor(o,all_moving):o.matrix_world=mat@o.matrix_world
# Move native transitions and all their dependent anchors together.
def move_collection(name,before,after,angle=0):
 c=bpy.data.collections[name];members=set(c.objects);mat=Matrix.Translation(Vector(after))@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-Vector(before))
 for o in c.objects:
  if not has_ancestor(o,members):o.matrix_world=mat@o.matrix_world
move_collection('caravan-gate',[54,89.6,0],[18,144,0],math.pi/2)
move_collection('north-gate',[54,7.5,1.4],[128,20,0])
# Existing well-stocked market counters are moved whole onto flat market paving.
for name,pos in [('food-market',[184,156]),('market-spices',[196,156]),('market-supplies',[184,163]),('market-textiles',[196,163])]:
 c=bpy.data.collections[name];r=next(o for o in c.objects if o.parent is None and o.type!='MESH');before=r.matrix_world.translation.copy()
 move_collection(name,before,[*pos,.04]);c['capital_district']='Lantern Market'
# Original world contact geometry is never overlaid below new floor surfaces.
retained={a['id']:a for a in p['retainedFloors']}
for o in list(terrain.objects):
 if o.type!='MESH' or not o.get('surface_role'):continue
 if o.name in retained:
  a=retained[o.name];old=o.matrix_world@o.data.vertices[0].co;delta=Vector(a['vertices'][0])-old;o.matrix_world=Matrix.Translation(delta)@o.matrix_world
 else:o['export_reference_only']=True;o.hide_render=True
# Replace the terrain's actual triangulated land, with its perimeter explicitly indexed.
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
d=bpy.data.meshes.new('capital-land-contact');d.from_pydata(p['groundMesh']['vertices'],[],p['groundMesh']['faces']);d.materials.append(bpy.data.materials['publicTownStone']);ground.data=d;ground.matrix_world=Matrix.Identity(4)
ground['outline_vertex_indices']=json.dumps([next(i for i,v in enumerate(p['groundMesh']['vertices']) if abs(v[0]-a[0])<.001 and abs(v[1]-a[1])<.001) for a in p['land']])
for a in p['floors']:floor(a)
floor({'id':'capital-river-water','vertices':[[-32,-32,-6.7],[288,-32,-6.7],[288,320,-6.7],[-32,320,-6.7]],'faces':[[0,1,2,3]],'material':'water','role':'water','walkable':False})
# Invisible street metadata supplies minimap/QA centerlines without coplanar paving.
for road in p['roads']:
 for j,(a,b) in enumerate(zip(road['centerline'],road['centerline'][1:])):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2
  o=floor({'id':road['id']+'-'+str(j),'vertices':[[a[0]+nx,a[1]+ny,.025],[b[0]+nx,b[1]+ny,.025],[b[0]-nx,b[1]-ny,.025],[a[0]-nx,a[1]-ny,.025]],'faces':[[0,1,2,3]],'material':'publicTownStone','role':'primary','walkable':False});o['render_visible']=False;o['road_segment']=True;o['road_width']=road['width'];o['legacy_role']='avenue' if road['width']>=8 else 'street';o['centerline_json']=json.dumps([a,b])
# Closed private curbs use genuine side faces, paired with exact tread-top geometry.
c=collection('capital-owned-block-boundaries','civic');k=kit(c)
for i,loop in enumerate(p['privateLoops']):
 for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
  k.mesh(f'owned-curb-{i}-{j}',[(x,y,z) for z in (.025,.20) for x,y in (a,b)],[[0,1,3,2]],'roadCurbFace',False,recalculate_normals=False)
# Native component construction; no complete existing houses are copied.
new_houses=[l for l in p['lots'] if not l['existing']]
build_house=runpy.run_path(str(ROOT/'tools/capital-house-kit-v75.py'))['build_house']
for i,l in enumerate(new_houses):
 build_house(l,i,collection,root,kit,floor)
 if i%10==0:print('CAPITAL HOUSES',i,'/',len(new_houses),flush=True)
# Original monumental government, archive and exchange silhouettes.
create_civic=runpy.run_path(str(ROOT/'tools/capital-civic-kit-v75.py'))['build_civic']
for spec in p['landmarks']:
 c=collection(spec['id'],'civic');r=root(c,(*spec['center'],0));create_civic(spec,c,r,floor);c['capital_landmark_json']=json.dumps(spec)
 print('CIVIC',spec['id'],flush=True)
bpy.context.view_layer.update()
# Reuse complete original vegetation modules, grounded by actual trunk feet.
tree_specs=[]
for park in p['parks']:
 if park.get('wallGarden'):continue
 xs=[v[0] for v in park['polygon']];ys=[v[1] for v in park['polygon']];x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys)
 for x in (x0+2.5,x1-2.5):
  for y in (y0+2.5,y1-2.5):tree_specs.append((x,y,.035,.76))
for x in (119,137):
 for y in (100,116,176,200,224,244):tree_specs.append((x,y,.04,.84))
for i,l in enumerate(p['lots']):
 if l.get('pairedBlock') or l.get('denseTownhouse') or i%3 or l.get('fixed'):continue
 x,y=l['center'];a=l['angle'];dx,dy=4.35,-4.15;tree_specs.append((x+math.cos(a)*dx-math.sin(a)*dy,y+math.sin(a)*dx+math.cos(a)*dy,.04,.65))
for y in range(52,234,16):
 for x in (18,238):tree_specs.append((x,y,.025,.78))
for i,(x,y,z,scale) in enumerate(tree_specs):
 template=bpy.data.collections['tree-0' if i%2 else 'district-tree-0'];parts=[o for o in template.objects if o.type=='MESH'];stem=next(o for o in parts if o.get('role')=='solid');vv=[stem.matrix_world@v.co for v in stem.data.vertices];origin=Vector(((min(v.x for v in vv)+max(v.x for v in vv))/2,(min(v.y for v in vv)+max(v.y for v in vv))/2,min(v.z for v in vv)))
 c=collection(f'capital-tree-{i:03}','vegetation');rr=root(c,(x,y,z-.015));rr['root_embed']=.015
 for o in parts:
  obj=o.copy();obj.data=o.data.copy();obj.name=f'capital-tree-{i:03}-'+o.name;obj.parent=rr;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Scale(scale,4)@Matrix.Translation(-origin)@o.matrix_world;c.objects.link(obj)
# Formal planted parterres, broad stone paths, benches and owned flower beds.
c=collection('capital-civic-gardens','civic');k=kit(c)
for i,park in enumerate(p['parks']):
 if park.get('wallGarden'):continue
 xs=[v[0] for v in park['polygon']];ys=[v[1] for v in park['polygon']];x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys);x,y=(x0+x1)/2,(y0+y1)/2
 floor({'id':f'capital-parterre-path-{i}','vertices':[[x-.60,y0,.05],[x+.60,y0,.05],[x+.60,y1,.05],[x-.60,y1,.05]],'faces':[[0,1,2,3]],'material':'houseApronPaving','role':'garden'})
 for side in (-1,1):
  yy=y+side*2.0;k.box(f'park-{i}-bench-seat-{side}',(x,yy,.68),(3.2,.65,.15),'gardenBenchGreen');k.box(f'park-{i}-bench-back-{side}',(x,yy+side*.28,1.17),(3.2,.13,.9),'gardenBenchGreen')
  for dx in (-1.2,1.2):k.box(f'park-{i}-bench-leg-{side}-{dx}',(x+dx,yy,.33),(.20,.55,.64),'iron')
 # Parterre edging follows the complete formal boundary.
 for j,(a,b) in enumerate(zip(park['polygon'],park['polygon'][1:]+park['polygon'][:1])):k.beam(f'park-{i}-stone-edging-{j}',(*a,.16),(*b,.16),.20,'stoneLight')
# Native cliff rings have shared stations; every exposed edge closes at land/water.
points=[]
for a,b in zip(p['land'],p['land'][1:]+p['land'][:1]):
 length=math.dist(a,b);count=math.ceil(length/4)
 for j in range(count):points.append((a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count))
normals=[]
for i,a in enumerate(points):
 prev=(Vector(a)-Vector(points[i-1])).normalized();nex=(Vector(points[(i+1)%len(points)])-Vector(a)).normalized();normals.append(Vector((prev.y+nex.y,-prev.x-nex.x)).normalized())
c=collection('capital-river-bank','fortification');k=kit(c);rings=[(0,0),(.65,-1.15),(1.6,-3.35),(2.25,-5.35),(2.7,-7.05)]
for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
 vs=[(q[0]+norm.x*off,q[1]+norm.y*off,z) for off,z in rings for q,norm in [(a,normals[i]),(b,normals[(i+1)%len(points)])]]
 k.mesh(f'capital-bank-{i}',vs,[[j*2,j*2+2,j*2+3,j*2+1] for j in range(4)],'bankStone' if i%3 else 'bankStoneLight',recalculate_normals=False)
# Low-detail native waterline ribbons use the same atlas and no simulation cost.
foam_mat=next((m.name for m in bpy.data.materials if 'foam' in m.name.lower()),None)
if foam_mat:
 c=collection('capital-waterline','fortification');k=kit(c);distance=0
 for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
  na,nb=normals[i],normals[(i+1)%len(points)];length=math.dist(a,b);obj=k.mesh(f'capital-foam-{i}',[(q[0]+n.x*off,q[1]+n.y*off,-6.69) for off in (2.58,3.5) for q,n in [(a,na),(b,nb)]],[[0,2,3,1]],foam_mat,False,recalculate_normals=False)
  for f in obj.data.polygons:
   for li in f.loop_indices:
    ix=obj.data.loops[li].vertex_index;obj.data.uv_layers.active.data[li].uv=((distance+(length if ix%2 else 0))/2.4,ix//2)
  distance+=length
# Modular curtain geometry carries quality through the entire fortified bank.
c=collection('capital-curtain-walls','fortification');k=kit(c);wall_stations=0
for ei,(a,b) in enumerate(zip(p['land'],p['land'][1:]+p['land'][:1])):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);angle=math.atan2(dy,dx);count=math.ceil(length/4)
 for j in range(count):
  t=(j+.5)/count;x=a[0]+dx*t;y=a[1]+dy*t;ll=length/count
  if abs(x-16)<.1 and abs(y-144)<8 or abs(x-240)<.1 and abs(y-144)<8 or abs(y-18)<.1 and abs(x-128)<7 or abs(y-268)<.1 and abs(x-128)<9:continue
  before=set(c.objects);name=f'capital-wall-{ei}-{j}';o=k.box(name+'-wall',(0,0,1.8),(ll+.015,1.15,3.6),'wallStone');o['role']='solid'
  k.box(name+'-footing',(0,0,-.38),(ll+.025,1.5,.80),'stone');k.box(name+'-cap',(0,0,3.7),(ll+.04,1.55,.20),'wallCap')
  for zz in (.15,1.65,3.35):k.box(name+'-course-'+str(zz),(0,.59,zz),(ll,.10,.12),'wallCap',False)
  for q in (-ll*.30,ll*.30):k.box(name+'-merlon-'+str(q),(q,0,4.08),(.80,1.20,.58),'wallCap')
  k.box(name+'-buttress',(-ll/2,0,1.7),(.55,1.80,3.5),'stoneLight')
  if j%3==0:k.box(name+'-arrow-slit',(0,.585,2.6),(.12,.04,.63),'iron',False)
  for obj in set(c.objects)-before:
   for v in obj.data.vertices:v.co=Matrix.Rotation(angle,4,'Z')@v.co+Vector((x,y,0))
  wall_stations+=1
# New gates share civic material craft with the reused original transition gates.
def gate(name,center,angle,width=10):
 c=collection(name,'fortification');r=root(c,(*center,0),angle);k=kit(c,r)
 for side in (-1,1):
  x=side*(width/2+1.4);o=k.box(name+'-tower-'+str(side),(x,0,3.4),(2.8,3.5,6.8),'civicIvory');o['role']='solid'
  for zz in (.35,2.4,5.0,6.9):k.box(name+'-belt-'+str((side,zz)),(x,0,zz),(3.12,3.8,.25),'wallCap')
  for yy in (-1.9,1.9):k.box(name+'-lancet-'+str((side,yy)),(x,yy,4.65),(.48,.08,1.38),'civicShadow',False)
  vs=[(x-1.7,-2.0,7.15),(x+1.7,-2.0,7.15),(x+1.7,2.0,7.15),(x-1.7,2.0,7.15),(x,-2.0,9.45),(x,2.0,9.45)];o=k.mesh(name+'-crown-'+str(side),vs,[[0,3,5,4],[1,4,5,2],[0,4,1],[3,2,5]],'civicSlate');o['role']='overhead'
  k.box(name+'-banner-'+str(side),(x,1.82,2.0),(.85,.04,2.4),'clothBlue',False);k.beam(name+'-banner-pole-'+str(side),(x-.60,1.93,3.28),(x+.60,1.93,3.28),.075,'gold')
  k.beam(name+'-banner-star-a-'+str(side),(x-.25,1.89,2.08),(x+.25,1.89,2.08),.04,'gold');k.beam(name+'-banner-star-b-'+str(side),(x,1.89,1.7),(x,1.89,2.5),.04,'gold')
 for j in range(12):
  aa,bb=j*math.pi/12,(j+1)*math.pi/12;poly=[(-math.cos(q)*rad,3.65+math.sin(q)*rad*.28) for q,rad in [(aa,width/2),(bb,width/2),(bb,width/2+.36),(aa,width/2+.36)]]
  vs=[(xx,yy,zz) for yy in (-.7,.7) for xx,zz in poly];k.mesh(name+'-arch-'+str(j),vs,[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,3,7,6],[3,7,4,0]],'civicIvory')
 o=k.box(name+'-lintel',(0,0,5.4),(width+2.8,1.5,.55),'wallCap');o['role']='overhead'
 return c
gate('capital-south-gate',[128,268],0,14);gate('capital-east-gate',[240,144],math.pi/2,12)
# Bridge piers and dressed side walls descend to the real water surface.
c=collection('capital-bridge-foundations','fortification');k=kit(c)
for axis,center,length,width in [('x',[10,144],20,12),('x',[246,144],20,12),('y',[128,273],18,14),('y',[128,12],18,9)]:
 for side in (-1,1):
  x,y=center;x+=side*(width/2+.25) if axis=='y' else 0;y+=side*(width/2+.25) if axis=='x' else 0
  size=(.55,length,1.0) if axis=='y' else (length,.55,1.0);name=f'bridge-{axis}-{center}-{side}'
  o=k.box(name+'-parapet',(x,y,.45),size,'wallStone');o['role']='solid';k.box(name+'-cap',(x,y,1.02),(size[0]+.15,size[1]+.15,.16),'wallCap')
  for shift in (-length*.3,length*.3):k.box(name+'-pier-'+str(shift),(x+(shift if axis=='x' else 0),y+(shift if axis=='y' else 0),-3.35),(1.0,1.2,7.0),'stone')
# Lamps flank principal avenues and repeat civic gold without cluttering crossings.
c=collection('capital-street-furniture','civic');k=kit(c)
for x,y in [(x,y) for x in (120,136) for y in (100,116,176,200,224,244)]+[(x,y) for x in (50,206) for y in (96,128,168,200,232)]:
 name=f'capital-lamp-{x}-{y}';o=k.box(name+'-base',(x,y,.2),(.50,.50,.4),'stone');o['role']='solid'
 k.box(name+'-post',(x,y,1.9),(.13,.13,3.4),'iron');k.box(name+'-lantern',(x,y,3.6),(.5,.5,.64),'lanternLight',False);k.mesh(name+'-hood',[(x-.37,y-.37,3.97),(x+.37,y-.37,3.97),(x+.37,y+.37,3.97),(x-.37,y+.37,3.97),(x,y,4.24)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'iron')
# Preserve all ambient identities, with deliberate clear street circuits.
c=collection('capital-ambient-life','civic');routes=[[[30,144],[100,144],[100,146],[30,146]],[[128,84],[128,118],[130,118],[130,84]],[[80,120],[80,176],[82,176],[82,120]],[[176,152],[176,178],[178,178],[178,152]],[[104,192],[104,210],[106,210],[106,192]],[[152,192],[152,210],[154,210],[154,192]],[[128,164],[128,242],[130,242],[130,164]],[[208,152],[208,176],[210,176],[210,152]],[[48,152],[48,176],[50,176],[50,152]],[[188,152],[200,152],[200,154],[188,154]]]
walkers=[o for o in bpy.data.objects if o.get('kind')=='walker'];assert len(walkers)==10
for i,o in enumerate(walkers):
 o.parent=None;o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([[*a,0] for a in routes[i]])
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o)
scene['spawn_json']=json.dumps(p['spawn']);scene['safe_spawn_json']=json.dumps([128,164,0]);scene['layout_id']='wayfarer-regional-capital-v75';scene['world_bounds_json']=json.dumps(p['bounds']);scene['navigation_cell_size']=1.0
route=[('Arrival',[13.4,144]),('Gate avenue',[30,144]),('South avenue',[128,204]),('Plaza',[128,150]),('Hall',[128,59]),('Market',[188,153]),('Blacksmith',[65,176.6]),('Inn',[65,106.7]),('Residential',[128,230]),('Shrine',[194,107.5]),('Council',[68,77]),('Archive',[188,77]),('Exchange',[188,144]),('North gate',[128,25]),('East gate',[234,144]),('South gate',[128,263])]
scene['route_json']=json.dumps([{'name':n,'position':a} for n,a in route]);scene['districts_json']=json.dumps([{'name':n,'x':a[0],'y':a[1]} for n,a in [('Consortium Hall',[128,48]),('Wayfarer Square',[128,144]),('Lantern Market',[188,156]),('Bronze Anvil',[65,174]),('Seafarer Rest',[64,104]),('Luna Shrine',[194,98]),('Council Chambers',[68,60]),('Grand Archive',[188,60]),('Trade Exchange',[188,129]),('South Commons',[92,224]),('Willow Borough',[192,224])]])
scene['ground_shadow_resolution']=4096;scene['capital_version']=75;scene['capital_plan_json']=json.dumps(p,separators=(',',':'));scene['capital_stats_json']=json.dumps({'newHouses':len(new_houses),'existingHouses':p['existingHouses'],'totalHouses':len(p['lots']),'newTrees':len(tree_specs),'landArea':p['landArea'],'wallStations':wall_stations,'originalAssembliesReorganized':True})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('CAPITAL SAVED',scene['capital_stats_json'],flush=True)
