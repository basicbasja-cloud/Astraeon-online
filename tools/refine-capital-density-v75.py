"""Apply reviewed close-set capital frontages without rebuilding original art."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75
p=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());terrain=bpy.data.collections['court-terrain']
assert p.get('densityRefinement'), 'Prepare an explicit density plan first'
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
if not s.get('capital_close_set_frontages'):
 for m in p['densityRefinement']['moves']:
  c=bpy.data.collections[m['id']];assert c.get('building_preset_json'),'Only newly authored modules move'
  transform=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
  members=set(c.objects)
  for o in c.objects:
   par=o.parent
   while par and par not in members:par=par.parent
   if par is None:o.matrix_world=transform@o.matrix_world
  for o in terrain.objects:
   if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=transform@o.matrix_world
  c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 build=runpy.run_path(str(ROOT/'tools/capital-house-kit-v75.py'))['build_house']
 for i,l in enumerate(l for l in p['lots'] if l.get('densityInfill')):
  assert l['id'] not in bpy.data.collections
  build(l,100+i,collection,root,kit,floor);print('DENSITY INFILL',l['id'],l['center'],flush=True)
 s['capital_close_set_frontages']=75
 # Update authored road contacts/minimap centerlines to neighborhood widths.
 for road in p['roads']:
  for j,(a,b) in enumerate(zip(road['centerline'],road['centerline'][1:])):
   o=bpy.data.objects[road['id']+'-'+str(j)];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*road['width']/2,dx/length*road['width']/2
   vs=[[a[0]+nx,a[1]+ny,.025],[b[0]+nx,b[1]+ny,.025],[b[0]-nx,b[1]-ny,.025],[a[0]-nx,a[1]-ny,.025]]
   for v,q in zip(o.data.vertices,vs):v.co=q
   o['road_width']=road['width'];o['legacy_role']='avenue' if road['width']>=8 else 'street'
 # Short local resident routes give inhabited blocks activity. Frame actor
 # budgets and the original ten identities remain unchanged.
 residents=[(60,216),(90,216),(112,216),(140,216),(160,216),(187,216),(60,184),(90,184),(112,184),(140,184),(160,184),(192,184),(90,112),(112,112),(140,112),(160,112),(64,80),(188,80)]
 c=bpy.data.collections['astral-fountain']
 for i,(x,y) in enumerate(residents):
  o=bpy.data.objects.new(f'capital-resident-{i:02}',None);c.objects.link(o);o['kind']='walker';o['data_json']=json.dumps({'pace':.38+(i%4)*.06,'tint':(i*23)%360,'kind':'travel' if i%3 else 'market','archetype':['mage','ranger','warrior'][i%3]});o['route_json']=json.dumps([[x-2,y,0],[x+2,y,0],[x+2,y+.9,0],[x-2,y+.9,0]])
 p['ambientPopulation']=28
 # Rebuild actual indexed floor unions and owned block edges from this plan.
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
 stats=json.loads(s['capital_stats_json']);stats.update(newHouses=p['newHouses'],totalHouses=len(p['lots']),densityRefined=True);s['capital_stats_json']=json.dumps(stats)
 s['capital_plan_json']=json.dumps(p,separators=(',',':'))
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
 runpy.run_path(str(ROOT/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
print('Close-set native capital',s['capital_stats_json'],flush=True)
