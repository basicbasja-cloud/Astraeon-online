"""Resolve vegetation/building conflicts and author continuous wall gardens."""
import bpy,json,runpy,math,os
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75
p=json.loads((ROOT/'docs/review/wayfarer-capital-v75/native-plan.json').read_text());terrain=bpy.data.collections['court-terrain']
FacadeKit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def floor(a):
 old=bpy.data.objects.get(a['id']);d=bpy.data.meshes.new(a['id']+'-refined');d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV');scale=8 if a['material'] in ('publicTownStone','houseApronPaving') else json.loads(bpy.data.materials[a['material']].get('texture_json','{}')).get('worldSize',2.4)
 for f in d.polygons:
  for li in f.loop_indices:
   v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale)
 if old:old.data=d;old.matrix_world=Matrix.Identity(4)
 else:old=bpy.data.objects.new(a['id'],d);terrain.objects.link(old)
 old['export_reference_only']=False;old['surface_role']=a['role'];old['walkable']=True;old['render_visible']=True;return old
# Replace actual indexed paving after clipping it clear of formal planted beds.
old_plan=json.loads(s['capital_plan_json']);new_ids={a['id'] for a in p['floors']}
for a in old_plan['floors']:
 if a['id'] not in new_ids:bpy.data.objects[a['id']]['export_reference_only']=True
for a in p['floors']:floor(a)
# Rebuild matching vertical curb faces, preserving the closed native top bands.
c=bpy.data.collections['capital-owned-block-boundaries'];r=next(o for o in c.objects if o.type=='EMPTY');bpy.data.batch_remove(ids=[o for o in c.objects if o.type=='MESH']);k=FacadeKit(c,r);k.prefix='capital-v75-'
for i,loop in enumerate(p['privateLoops']):
 for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):k.mesh(f'owned-curb-{i}-{j}',[(x,y,z) for z in (.025,.20) for x,y in (a,b)],[[0,1,3,2]],'roadCurbFace',False,recalculate_normals=False)
if not s.get('capital_garden_clearance'):
 # The east ceremonial garden now occupies the clear market-side courtyard.
 for i,pos in [(12,[183.5,176.2]),(13,[183.5,178.2]),(14,[201.5,176.2]),(15,[201.5,178.2])]:
  o=bpy.data.objects[f'capital-tree-{i:03}-placement'];o.location.x,o.location.y=pos
 # Outer rows are beside the walls, clear of every house's actual ground mass.
 for i in range(52,76):
  o=bpy.data.objects[f'capital-tree-{i:03}-placement'];o.location.x=18 if i%2==0 else 238;o.location.z=.020
 c=bpy.data.collections['capital-civic-gardens'];r=next(o for o in c.objects if o.type=='EMPTY');k=FacadeKit(c,r);k.prefix='capital-v75-'
 dy=(min(v[1] for v in p['parks'][3]['polygon'])+max(v[1] for v in p['parks'][3]['polygon'])-min(v[1] for v in old_plan['parks'][3]['polygon'])-max(v[1] for v in old_plan['parks'][3]['polygon']))/2
 edges=[]
 for o in c.objects:
  if not o.name.startswith('capital-v75-park-3-'):continue
  if '-stone-edging-' in o.name:edges.append(o)
  else:
   for v in o.data.vertices:v.co.y+=dy
 bpy.data.batch_remove(ids=edges)
 park=next(a for a in p['parks'] if a['name']=='East Coronation Garden');loop=park['polygon']
 for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):k.beam(f'park-3-stone-edging-{j}',(*a,.16),(*b,.16),.20,'stoneLight')
 floor({'id':'capital-parterre-path-3','vertices':[[191.9,175,.05],[193.1,175,.05],[193.1,180,.05],[191.9,180,.05]],'faces':[[0,1,2,3]],'material':'houseApronPaving','role':'garden'})
 s['capital_garden_clearance']=75
if not s.get('capital_parterre_streets'):
 for i in range(8):
  o=bpy.data.objects[f'capital-tree-{i:03}-placement'];o.location.y=87.5 if i%2==0 else 91.5
 for i in (64,65):bpy.data.objects[f'capital-tree-{i:03}-placement'].location.y=156
 c=bpy.data.collections['capital-civic-gardens'];r=next(o for o in c.objects if o.type=='EMPTY');k=FacadeKit(c,r);k.prefix='capital-v75-'
 for pi in (0,1,4,5):
  dy=(min(v[1] for v in p['parks'][pi]['polygon'])+max(v[1] for v in p['parks'][pi]['polygon'])-min(v[1] for v in old_plan['parks'][pi]['polygon'])-max(v[1] for v in old_plan['parks'][pi]['polygon']))/2
  edges=[]
  for o in c.objects:
   if not o.name.startswith(f'capital-v75-park-{pi}-'):continue
   if '-stone-edging-' in o.name:edges.append(o)
   else:
    for v in o.data.vertices:v.co.y+=dy
  bpy.data.batch_remove(ids=edges);park=p['parks'][pi];loop=park['polygon']
  for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):k.beam(f'park-{pi}-stone-edging-{j}',(*a,.16),(*b,.16),.20,'stoneLight')
  xs=[v[0] for v in loop];ys=[v[1] for v in loop];x=(min(xs)+max(xs))/2;ya,yb=min(ys),max(ys)
  floor({'id':f'capital-parterre-path-{pi}','vertices':[[x-.6,ya,.05],[x+.6,ya,.05],[x+.6,yb,.05],[x-.6,yb,.05]],'faces':[[0,1,2,3]],'material':'houseApronPaving','role':'garden'})
 s['capital_parterre_streets']=75
if not s.get('capital_market_garden_clearance'):
 bpy.data.objects['capital-tree-012-placement'].location.x=182
 c=bpy.data.collections['capital-civic-gardens'];r=next(o for o in c.objects if o.type=='EMPTY');k=FacadeKit(c,r);k.prefix='capital-v75-'
 bpy.data.batch_remove(ids=[o for o in c.objects if o.name.startswith('capital-v75-park-3-stone-edging-')])
 loop=p['parks'][3]['polygon']
 for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):k.beam(f'park-3-stone-edging-{j}',(*a,.16),(*b,.16),.20,'stoneLight')
 s['capital_market_garden_clearance']=75
if p.get('ro3StreetScaleRefinement') and not s.get('capital_garden_circuit_clearance'):
 # Widening the perimeter circuit trims two gardens, including their real
 # stone borders. Keep benches and paths centered in the reduced planted area.
 c=bpy.data.collections['capital-civic-gardens'];r=next(o for o in c.objects if o.type=='EMPTY');k=FacadeKit(c,r);k.prefix='capital-v75-'
 for pi in (2,3):
  old_x=[v[0] for v in old_plan['parks'][pi]['polygon']];new_x=[v[0] for v in p['parks'][pi]['polygon']];dx=(min(new_x)+max(new_x)-min(old_x)-max(old_x))/2
  edges=[]
  for o in c.objects:
   if not o.name.startswith(f'capital-v75-park-{pi}-'):continue
   if '-stone-edging-' in o.name:edges.append(o)
   else:
    for v in o.data.vertices:v.co.x+=dx
  bpy.data.batch_remove(ids=edges);loop=p['parks'][pi]['polygon']
  for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):k.beam(f'park-{pi}-stone-edging-{j}',(*a,.16),(*b,.16),.20,'stoneLight')
  path=bpy.data.objects[f'capital-parterre-path-{pi}']
  for v in path.data.vertices:v.co.x+=dx
 s['capital_garden_circuit_clearance']=75
if p.get('ro3StreetScaleRefinement') and s.get('capital_tree_junction_clearance')!='wide-cross-north':
 # These two formal-axis trees met the newly widened north cross street.
 # Keep the original full assemblies and move them to verified clear ground.
 for i in (25,31):
  o=bpy.data.objects[f'capital-tree-{i:03}-placement'];o.location.y=116.8;o.location.z=.025
 s['capital_tree_junction_clearance']='wide-cross-north'
if not s.get('capital_plaza_oaks'):
 for name,target in [('plaza-oak-west',[111,144]),('plaza-oak-east',[145,144])]:
  c=bpy.data.collections[name];c['family']=c['capital_reference_family'];c.hide_render=False;c.hide_viewport=False
  trunk=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid');vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];center=Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,min(v.z for v in vs)))
  mat=Matrix.Translation(Vector((*target,.010))-center);members=set(c.objects)
  for o in c.objects:
   parent=o.parent;child=False
   while parent:
    if parent in members:child=True;break
    parent=parent.parent
   if not child:o.matrix_world=mat@o.matrix_world
 stats=json.loads(s['capital_stats_json']);stats['restoredBroadleafAccents']=2;s['capital_stats_json']=json.dumps(stats);s['capital_plaza_oaks']=75
if not s.get('capital_tree_roots_final'):
 # Evaluate after parent changes, then place the complete broadleaf assemblies
 # using their actual world-space trunk feet, without inherited parent offsets.
 bpy.context.view_layer.update()
 for name,target in [('plaza-oak-west',[111,144]),('plaza-oak-east',[145,144])]:
  c=bpy.data.collections[name];meshes=[o for o in c.objects if o.type=='MESH'];world={o:o.matrix_world.copy() for o in meshes}
  trunk=next(o for o in meshes if o.get('role')=='solid');vs=[world[trunk]@v.co for v in trunk.data.vertices];center=Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,min(v.z for v in vs)))
  delta=Matrix.Translation(Vector((*target,.010))-center)
  for o in meshes:o.parent=None;o.matrix_world=delta@world[o]
 for i in (25,26,29,31,32,35):
  o=bpy.data.objects[f'capital-tree-{i:03}-placement'];o.location.z=.010
  if i in (29,35):o.location.y=232;o.location.z=.025
 s['capital_tree_roots_final']=75
if not s.get('capital_south_tree_roots'):
 for i in (29,35):bpy.data.objects[f'capital-tree-{i:03}-placement'].location.z=.025
 s['capital_south_tree_roots']=75
s['capital_plan_json']=json.dumps(p,separators=(',',':'));bpy.context.view_layer.update()
if not os.environ.get('ASTRAEON_DEFER_NATIVE_SAVE'):
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Native wall gardens and tree clearance refined',flush=True)
