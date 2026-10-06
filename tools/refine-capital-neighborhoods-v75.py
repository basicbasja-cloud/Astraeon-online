"""Apply continuous native street-facing neighborhoods from a reviewed plan."""
import bpy,json,math,runpy,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75 and s.get('capital_close_set_frontages')==75
p=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());assert p.get('neighborhoodRefinement');terrain=bpy.data.collections['court-terrain']
FacadeKit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def collection(name,family):
 c=bpy.data.collections.new(name);s.collection.children.link(c);c['family']=family;return c
def root(c,position=(0,0,0),angle=0):
 o=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(o);o.location=position;o.rotation_euler.z=angle;return o
def kit(c,r):
 k=FacadeKit(c,r);k.prefix='capital-v75-';return k
def floor(a):
 d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV')
 for f in d.polygons:
  for li in f.loop_indices:
   v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/8,v.y/8)
 o=bpy.data.objects.new(a['id'],d);terrain.objects.link(o);o['surface_role']=a['role'];o['walkable']=True;o['object_id']=a['objectId'];o['render_visible']=False
 return o
if not s.get('capital_continuous_neighborhoods'):
 assert hashlib.sha256((ROOT/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['neighborhoodRefinement']['beforeSourceSHA256'],'Native relocation requires its recorded baseline export'
 for m in p['neighborhoodRefinement']['moves']:
  c=bpy.data.collections[m['id']];assert c.get('family') in ('residential','market','workshop','inn')
  transform=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
  members=set(c.objects)
  for o in c.objects:
   par=o.parent
   while par and par not in members:par=par.parent
   if par is None:o.matrix_world=transform@o.matrix_world
  for o in terrain.objects:
   if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=transform@o.matrix_world
  if c.get('building_preset_json'):c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 build=runpy.run_path(str(ROOT/'tools/capital-house-kit-v75.py'))['build_house']
 for i,l in enumerate(l for l in p['lots'] if l.get('neighborhoodInfill')):
  assert l['id'] not in bpy.data.collections
  build(l,200+i,collection,root,kit,floor);print('NEIGHBORHOOD HOME',l['id'],l['center'],flush=True)
 s['capital_continuous_neighborhoods']=75
 runpy.run_path(str(ROOT/'tools/refine-capital-gardens-v75.py'),run_name='__main__')
 bpy.context.view_layer.update()
 # New owned block paving changes height beneath a few retained tree roots.
 floors=[]
 for a in p['floors']:
  for face in a['faces']:
   vs=[a['vertices'][i] for i in face];floors.append(([(v[0],v[1]) for v in vs],max(v[2] for v in vs)))
 def inside(x,y,poly):
  hit=False
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
  return hit
 for c in bpy.data.collections:
  if c.get('family')!='vegetation':continue
  trunk=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid');vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];x=(min(v.x for v in vs)+max(v.x for v in vs))/2;y=(min(v.y for v in vs)+max(v.y for v in vs))/2;z=min(v.z for v in vs)
  ground=max([0]+[zz for poly,zz in floors if inside(x,y,poly)]);delta=ground-.015-z
  members=set(c.objects)
  for o in c.objects:
   if o.parent not in members:o.matrix_world=Matrix.Translation(Vector((0,0,delta)))@o.matrix_world

 stats=json.loads(s['capital_stats_json']);stats.update(newHouses=p['newHouses'],totalHouses=len(p['lots']),continuousNeighborhoods=True);s['capital_stats_json']=json.dumps(stats);s['capital_plan_json']=json.dumps(p,separators=(',',':'))
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
 runpy.run_path(str(ROOT/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
print('Native neighborhoods',s['capital_stats_json'],flush=True)
