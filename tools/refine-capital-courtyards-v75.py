"""Author inward-facing neighborhoods and shared features in the native city."""
import bpy,json,hashlib,math,runpy,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;p=json.loads((R/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());assert s.get('capital_ro3_street_scale')==75
if not s.get('capital_inward_courts'):
 assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['courtyardRefinement']['beforeSourceSHA256']
 terrain=bpy.data.collections['court-terrain']
 for m in p['courtyardRefinement']['moves']:
  c=bpy.data.collections[m['id']];members=set(c.objects);t=Matrix.Translation(Vector((*m['after'],0)))@Matrix.Rotation(m['rotation'],4,'Z')@Matrix.Translation(Vector((-m['before'][0],-m['before'][1],0)))
  for o in c.objects:
   par=o.parent
   while par and par not in members:par=par.parent
   if par is None:o.matrix_world=t@o.matrix_world
  for o in terrain.objects:
   if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):o.matrix_world=t@o.matrix_world
  if c.get('building_preset_json'):c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))
 os.environ['ASTRAEON_DEFER_NATIVE_SAVE']='1'
 runpy.run_path(str(R/'tools/refine-capital-gardens-v75.py'),run_name='__main__')
 del os.environ['ASTRAEON_DEFER_NATIVE_SAVE']
 Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
 for court in p['courtyards']:
  c=bpy.data.collections.new('capital-'+court['id']);s.collection.children.link(c);c['family']='civic';c['capital_courtyard_json']=json.dumps(court)
  r=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(r);r.location=(*court['center'],.04);k=Kit(c,r);k.prefix='capital-v75-'
  # Closed stone well ring, water below the coping, timber winding structure.
  points=[(radius*math.cos(j*math.tau/16),radius*math.sin(j*math.tau/16),z) for radius,z in [(.86,0),(.86,.88),(.61,0),(.61,.88)] for j in range(16)]
  faces=[]
  for j in range(16):
   q=(j+1)%16;faces.extend([[j,q,q+16,j+16],[j+32,j+48,q+48,q+32],[j+16,q+16,q+48,j+48],[j,j+32,q+32,q]])
  o=k.mesh(court['id']+'-well-stone',points,faces,'stoneLight');o['role']='solid'
  k.mesh(court['id']+'-well-water',[(.60*math.cos(j*math.tau/16),.60*math.sin(j*math.tau/16),.38) for j in range(16)],[list(range(16))],'water',False)
  for x in (-1.02,1.02):k.box(court['id']+'-well-post-'+str(x),(x,0,1.32),(.20,.20,2.64),'timber')
  k.beam(court['id']+'-well-winder',(-1.15,0,1.65),(1.15,0,1.65),.14,'oak');k.beam(court['id']+'-well-rope',(0,0,1.65),(0,0,.48),.055,'oak')
  k.mesh(court['id']+'-well-roof',[(-1.24,-.98,2.58),(1.24,-.98,2.58),(1.24,0,3.16),(-1.24,0,3.16),(-1.24,.98,2.58),(1.24,.98,2.58)],[[0,1,2,3],[3,2,5,4]],'roofClayWarm')
  def bench(name,x,y):
   o=k.box(name+'-seat',(x,y,.58),(2.4,.55,.14),'gardenBenchGreen');o['role']='solid'
   k.box(name+'-back',(x,y+.22,.94),(2.4,.10,.70),'gardenBenchGreen')
   for dx in (-.90,.90):k.box(name+'-leg-'+str(dx),(x+dx,y,.27),(.16,.44,.54),'iron')
  def planter(name,x,y):
   o=k.box(name+'-stone',(x,y,.24),(1,.65,.48),'stoneLight');o['role']='solid';k.box(name+'-soil',(x,y,.49),(.88,.53,.04),'soil',False)
   for j in range(5):
    xx=x-.32+j*.16;k.box(name+'-green-'+str(j),(xx,y,.63),(.20,.37,.23),'leaf',False);k.box(name+'-bloom-'+str(j),(xx,y,.79),(.10,.10,.08),'flowerRose' if j%2 else 'flowerIvory',False)
  if court['id']=='artisan-court':
   bench('artisan-court-north-seat',0,-2.4);bench('artisan-court-south-seat',0,4.8);planter('artisan-court-planter',-2.8,3.8)
   for y in (-1.5,1.5):
    o=k.box('artisan-court-worktable-'+str(y),(4.4,y,.93),(2.1,.95,.15),'oak');o['role']='solid'
    for x in (3.65,5.15):k.box('artisan-court-table-leg-'+str((x,y)),(x,y,.43),(.16,.70,.86),'timber')
    for j in range(3):k.box('artisan-court-workpiece-'+str((j,y)),(3.9+j*.40,y,1.08),(.30,.45,.15),'oak')
   k.box('artisan-court-noticeboard',(-3,0,1.56),(1.42,.12,1.1),'oak');k.box('artisan-court-notice-inset',(-3,-.08,1.56),(1.20,.03,.88),'questParchment',False)
   for x in (-3.6,-2.4):k.box('artisan-court-notice-post-'+str(x),(x,0,1.01),(.12,.14,2.02),'timber')
  else:
   bench('willow-court-west-seat',-3.8,.9);bench('willow-court-east-seat',4.9,.9);planter('willow-court-west-planter',-3.8,-.7);planter('willow-court-east-planter',4.9,-.7)
 for i,route in [(6,[[101.5,164.8],[105.3,164.8],[105.3,167],[101.5,167]]),(10,[[154,199.5],[155.3,199.5],[155.3,201],[154,201]])]:
  o=bpy.data.objects[f'capital-resident-{i:02}'];assert o.get('kind')=='walker';o.parent=None;o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([[*v,0] for v in route])
 routes=json.loads(s['route_json']);routes.extend([{'name':'Artisans’ Court','position':[104.8,165.2]},{'name':'Willow Court','position':[154.5,200]}]);s['route_json']=json.dumps(routes)
 districts=json.loads(s['districts_json']);districts.extend([{'name':court['name'],'x':court['center'][0],'y':court['center'][1]} for court in p['courtyards']]);s['districts_json']=json.dumps(districts)
 s['capital_inward_courts']=75
 stats=json.loads(s['capital_stats_json']);stats['inwardCourts']=2;stats['inwardFacingHomes']=len(p['courtyardRefinement']['moves']);s['capital_stats_json']=json.dumps(stats)
 s['capital_plan_json']=json.dumps(p,separators=(',',':'));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('NATIVE INWARD COURTS',s.get('capital_inward_courts'),flush=True)
