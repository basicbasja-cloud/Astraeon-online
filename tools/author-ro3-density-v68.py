"""Finish ordinary house envelopes and original RO3 street infill in native Blender.

Run on saved primary facade68 with the reviewed density plan. Existing lot
identities/services survive; new occupied ground is explicit source geometry.
"""
import json, math, runpy, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
plan=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
vs,fs=[],[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role') and not o.get('walkable',o.get('surface_role')!='water'):continue
 base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles()
 fs.extend(tuple(base+i for i in f.vertices) for f in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def floor(x,y):
 hit=tree.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))[0]
 return max(0,hit.z if hit else 0)
def frame(owner,record):
 name='ro3-v68-'+owner.name+'-model-frame'
 old=bpy.data.objects.get(name)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 placement=bpy.data.objects.get(owner.name+'-placement')
 if not placement:
  placement=bpy.data.objects.new(owner.name+'-placement',None);owner.objects.link(placement)
 obj=bpy.data.objects.new(name,None);owner.objects.link(obj);obj.parent=placement
 t,n=record['tangent'],record['normal'];x,y=record['center'];z=floor(x,y)
 obj.matrix_world=Matrix(((t[0],n[0],0,x),(t[1],n[1],0,y),(0,0,1,z),(0,0,0,1)))
 bpy.context.view_layer.update();return obj
records=[]
for record in plan['existingEnvelopes']+plan['infill']:
 name=record['owner'];owner=bpy.data.collections.get(name)
 if not owner:owner=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(owner);owner['family']=record['family']
 bpy.data.batch_remove(ids=[o for o in owner.objects if o.name.startswith('ro3-v68-')])
 root=frame(owner,record);kit=Kit(owner,root);inv=root.matrix_world.inverted();w,d=record['width'],record['depth']
 family='market' if record['family']=='market' else 'workshop' if record['family']=='workshop' else 'residential'
 floor_top={'residential':3.65,'market':3.8,'workshop':3.55}[family]
 wall=bpy.data.objects.get(record.get('wall',''))
 wings=[]
 for o in list(owner.objects):
  if o.type!='MESH' or o.name.startswith('ro3-v68-'):continue
  n=o.name
  if 'wing' in n:
   wings.append(o)
   if o.data.materials and ('roof' in n or 'gable' in n):
    if 'roof' in n:o.data.materials[0]=bpy.data.materials['roofClayWarm']
   continue
  # Keep outdoor workshop/courtyard furniture; replace the obsolete envelope.
  keep=any(t in n for t in ('bench','barrel','crate','-forge-','anvil','-fence','-yard-','lantern','-lamp','flower','planter','-cart','chimney-smoke'))
  if o.get('role')=='solid':
   o['render_visible']=False;o['shadow']=False
   if o==wall:
    if 'ro3_v68_original_vertices' not in o:o['ro3_v68_original_vertices']=json.dumps([list(v.co) for v in o.data.vertices])
    original=json.loads(o['ro3_v68_original_vertices']);old_base=record['oldBase'];old_top=record['oldTop']
    for vertex,point in zip(o.data.vertices,original):
     p=o.matrix_world@Vector(point);p.z=old_base+(p.z-old_base)*(floor_top-.44)/(old_top-old_base)
     vertex.co=o.matrix_world.inverted()@p
   continue
  if keep:continue
  bpy.data.objects.remove(o,do_unlink=True)
 if wall and record['physicalMode'].startswith('retain'):
  poly=[inv@Vector((x,y,root.matrix_world.translation.z)) for x,y in record['originalPolygon']]
  points=[(p.x,p.y,z) for z in (.05,floor_top) for p in poly];count=len(poly)
  core=kit.mesh(name+'-ground-core',points,[list(range(count-1,-1,-1)),list(range(count,2*count))]+[[i,(i+1)%count,(i+1)%count+count,i+count] for i in range(count)],'stoneLight')
 else:
  core=kit.box(name+'-ground-core',(0,0,(floor_top+.05)/2),(w,d,floor_top-.05),'stoneLight')
 core['role']='solid'
 if not wall or record['physicalMode'].startswith('expanded'):
  foot=kit.box(name+'-foundation',(0,0,.22),(w+.22,d+.22,.44),'cream');foot['role']='solid'
 for o in wings:
  if o.get('role')!='solid':continue
  points=[inv@o.matrix_world@v.co for v in o.data.vertices];cx=sum(p.x for p in points)/len(points)
  if abs(cx)>w*.35:kit.side_windows[-1 if cx<0 else 1]=[]
 if wall and record['physicalMode'].startswith('retain'):
  front_points=[p.x for p in poly if abs(p.y-d/2)<.001]
  assert len(front_points)==2
  kit.ground_front=((min(front_points)+max(front_points))/2,max(front_points)-min(front_points))
 if family=='market':
  gx,gw=kit.ground_front or (0,w)
  probes=[root.matrix_world@Vector((gx+gw*.22+side*1.21,d/2+1.24,0)) for side in (-1,1)]
  kit.awning_rise=max(0,max(floor(p.x,p.y) for p in probes)-root.matrix_world.translation.z+2.38-2.88)
 result=kit.build(-w/2,w/2,-d/2,d/2,family,record['index'],oldtop=record.get('oldTop',0))
 result.update(physicalMode=record['physicalMode'],center=record['center'],originalFamily=record['family'])
 records.append(result);print('RO3 full envelope',name,record['physicalMode'],flush=True)
# Relocate rooted tree groups overlapping newly occupied ground, as complete groups.
geo=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'))
saved_world=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
polys=[r['polygon'] for r in plan['existingEnvelopes']+plan['infill'] if not r['physicalMode'].startswith('retain')]
moved=[]
for owner in bpy.data.collections:
 if owner.get('family')!='vegetation':continue
 for trunk in list(owner.objects):
  if trunk.type!='MESH' or trunk.get('role')!='solid' or not trunk.name.endswith('-root'):continue
  points=[trunk.matrix_world@v.co for v in trunk.data.vertices];poly=geo['hull'](points)
  if not any(geo['overlap'](poly,p,.35) for p in polys):continue
  cx=sum(p.x for p in points)/len(points);cy=sum(p.y for p in points)/len(points)
  chosen=None
  for radius in (3,5,7,9):
   for k in range(16):
    dx,dy=radius*math.cos(k*math.tau/16),radius*math.sin(k*math.tau/16);shift=[(x+dx,y+dy) for x,y in poly]
    if not all(geo['inside'](p,saved_world['terrain']['walkablePolygon']) for p in shift):continue
    if any(geo['overlap'](shift,p,1) for p in polys):continue
    if any(geo['overlap'](shift,geo['hull'](road['vertices']),.3) for road in saved_world['terrain']['surfaces'] if road.get('centerline')):continue
    # Keep moved trunks outside saved roads and all other building solids.
    occupied=[]
    for c in bpy.data.collections:
     if c.get('family') in ('vegetation','terrain'):continue
     for ob in c.objects:
      if ob.type=='MESH' and ob.get('role')=='solid':occupied.append(geo['hull']([ob.matrix_world@v.co for v in ob.data.vertices]))
    if any(geo['overlap'](shift,p,.6) for p in occupied):continue
    chosen=(dx,dy,floor(cx+dx,cy+dy)-floor(cx,cy));break
   if chosen:break
  assert chosen, 'No grounded relocation for '+trunk.name
  prefix=trunk.name[:-5]
  group=[o for o in owner.objects if o.name.startswith(prefix)]
  for o in group:o.matrix_world=Matrix.Translation(Vector(chosen))@o.matrix_world
  moved.append({'tree':prefix,'delta':chosen,'parts':len(group)})
bpy.context.view_layer.update()
scene=bpy.context.scene;scene['ro3_density_version']=68;scene['ro3_density_plan_json']=json.dumps(plan);scene['ro3_secondary_review_json']=json.dumps(records);scene['ro3_tree_relocations_json']=json.dumps(moved)
bpy.data.batch_remove(ids=[d for d in bpy.data.meshes if not d.users])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved',len(records),'RO3 envelopes;',len(moved),'complete tree relocations; rebake required',flush=True)
