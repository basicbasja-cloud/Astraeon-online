"""Irregular rooted grass creeps onto the building-side floor beyond street curbs."""
import bpy,json,random,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_road_curb_version')==69;assert not scene.get('ro3_curb_grass_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def contact(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];return Vector((p.x,p.y,hit.z+.017)) if hit else None
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];approaches=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])];groups=[]
for record in json.loads(scene['ro3_road_curb_review_json'])['curbBlocks']:
 o=bpy.data.objects[record['id']];p=[o.matrix_world@v.co for v in o.data.vertices];a,b=p[0],p[6];t=b-a;t.z=0;t.normalize();n=p[1]-p[0];n.z=0;n.normalize();a=a+n*.275;b=b+n*.275
 if groups and groups[-1]['road']==record['road'] and groups[-1]['normal'].dot(n)>.99 and (groups[-1]['end'].xy-a.xy).length<.035:groups[-1]['end']=b
 else:groups.append({'road':record['road'],'start':a,'end':b,'normal':n,'tangent':t})
kit=Kit(terrain,None);kit.prefix='curbgrass69-';r=random.Random(694539);records=[]
for g in groups:
 if (g['end']-g['start']).length<.7 or r.random()>.68:continue
 a,b,n=g['start'],g['end'],g['normal'];width=r.uniform(.36,.70)
 for depth in [width,width*.7,width*.45]:
  pts=[a,b,b+n*depth,a+n*depth];q=[tuple(p[:2]) for p in pts]
  if any(h['overlap'](q,p,.02) for p in solids):continue
  if any(h['inside'](p,q) or min(h['distance'](p,x,y) for x,y in zip(q,q[1:]+q[:1]))<.75 for p in approaches):continue
  verts=[contact(p) for p in pts]
  if not all(p is not None for p in verts) or max(p.z for p in verts)-min(p.z for p in verts)>.13:continue
  # Clockwise horizontal outline: reverse triangles so plants face the sun.
  cross=(verts[1]-verts[0]).cross(verts[3]-verts[0]).z;faces=[[0,1,2],[0,2,3]] if cross>0 else [[0,2,1],[0,3,2]]
  o=kit.mesh('strip-'+str(len(records)),[tuple(p) for p in verts],faces,'vergeGroundcover' if r.random()>.25 else 'vergeGroundcoverShade',False);del o['role'];o['surface_role']='forecourt';o['walkable']=False;o['curb_grass_v69']=True
  uv=[(0,0),(1,0),(1,1),(0,1)]
  for f in o.data.polygons:
   for li in f.loop_indices:o.data.uv_layers.active.data[li].uv=uv[o.data.loops[li].vertex_index]
  records.append({'id':o.name,'road':g['road'],'width':depth,'vertices':[list(p) for p in verts]});break
scene['ro3_curb_grass_version']=69;scene['ro3_curb_grass_review_json']=json.dumps({'strips':records,'nativeGroundOffset':.017,'shadowCastersChanged':False,'floorChanged':False,'placement':'Outside stone road curb, on building-side paving; approaches and solids protected'})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Living roadside floor:',len(records),'soft native strips outside street curbs; no floor/caster change')
