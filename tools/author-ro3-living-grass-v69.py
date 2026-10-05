"""Soft living foundation strips with native short grass clumps; no floor edits."""
import bpy,json,random,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_verge_fit_version')==69
assert not scene.get('ro3_grass_life_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];r=random.Random(690453)
art=json.loads((ROOT/'authoring/materials/wayfarer-street-v69.json').read_text())['materials']['groundcover']['texture']
for name in ('vergeGroundcover','vergeGroundcoverShade'):bpy.data.materials[name]['texture_json']=json.dumps(art)
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def root_point(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
 return Vector((p.x,p.y,hit.z+.017)) if hit else None
strips=[];clumps=0;quads=0
for c in bpy.data.collections:
 for o in list(c.objects):
  if not o.get('street_v69_patch'):continue
  assert not o.get('shadow')
  root=o.parent;inv=root.matrix_world.inverted();old=[v.co.copy() for v in o.data.vertices];t=old[-1]-old[0];t.z=0;t.normalize();n=Vector((t.y,-t.x,0));center=(old[0]+old[-1])/2;half=max(abs((p-center).dot(t)) for p in old);depth=max((p-center).dot(n) for p in old)
  corners=[center-t*half,center+t*half,center+t*half+n*depth,center-t*half+n*depth];world=[root_point(root.matrix_world@p) for p in corners]
  if all(p is not None for p in world) and max(p.z for p in world)-min(p.z for p in world)<=.13:
   data=o.data;mat=data.materials[0];data.clear_geometry();data.from_pydata([tuple(inv@p) for p in world],[],[[0,2,1],[0,3,2]]);data.update()
   uv=data.uv_layers.active or data.uv_layers.new(name='PhysicalUV');coords=[(0,0),(1,0),(1,1),(0,1)]
   for f in data.polygons:
    for li in f.loop_indices:uv.data[li].uv=coords[data.loops[li].vertex_index]
   quads+=1
  # All plant vertices stay on a low, rooted physical growth profile.
  kit=Kit(c,root);kit.prefix='grass69-'+str(clumps)+'-'
  for k in range(8):
   local=center+t*r.uniform(-half*.82,half*.82)+n*r.uniform(depth*.08,depth*.55);p=root_point(root.matrix_world@local)
   if p is None:continue
   q=inv@p;points=[];faces=[]
   for blade in range(3):
    angle=r.random()*math.tau;side=Vector((math.cos(angle),math.sin(angle),0))*.021;lean=Vector((r.uniform(-.07,.07),r.uniform(-.07,.07),r.uniform(.12,.23)))
    off=len(points);points.extend([tuple(q-side),tuple(q+side),tuple(q+lean)]);faces.append([off,off+1,off+2])
   ob=kit.mesh('clump-'+str(k),points,faces,'grass' if k%3 else 'leafLight',False);ob['street_v69_clump']=True;ob['street_v69_root_world']=list(p)
   clumps+=1
  strips.append({'id':o.name,'owner':c.name,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices]})
review=json.loads(scene['ro3_street_review_json']);review['patches']=strips;scene['ro3_street_review_json']=json.dumps(review)
scene['ro3_grass_life_version']=69;scene['ro3_grass_life_review_json']=json.dumps({'foundationStrips':len(strips),'alphaPaddedQuads':quads,'rootedClumps':clumps,'bladesPerClump':3,'shadowCastersChanged':False,'floorChanged':False})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Living grass:',len(strips),'soft strips;',quads,'alpha-padded quads;',clumps,'rooted 3-blade clumps; lighting geometry preserved')
