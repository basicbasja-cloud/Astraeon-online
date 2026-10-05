"""Coherent rectangular street paving with local aged stones and rooted joint grass."""
import bpy,json,random,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_road_curb_version')==69 and not scene.get('ro3_path_wear_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());art=json.loads((ROOT/'authoring/materials/wayfarer-path-wear-v69.json').read_text());r=random.Random(694545)
# Roads and building-side zones share the same stone scale/world UV alignment.
# Their native palette and physical curb distinguish the public street.
paving=json.loads(bpy.data.materials['paving']['texture_json']);paving['anisotropy']=4
bpy.data.materials['avenuePaving']['texture_json']=json.dumps(paving)
bpy.data.materials['avenuePaving'].diffuse_color=(.405,.395,.325,1)
m=bpy.data.materials.new('agedPathPatch');m.diffuse_color=(.43,.42,.35,1);m['texture_json']=json.dumps(art['texture'])
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];return hit.z if hit else None
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];approaches=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])]
roads={s['id']:s for s in w['terrain']['surfaces'] if s.get('centerline')};groups=[]
for record in json.loads(scene['ro3_road_curb_review_json'])['curbBlocks']:
 o=bpy.data.objects[record['id']];p=[o.matrix_world@v.co for v in o.data.vertices];a,b=p[0],p[6];t=b-a;t.z=0;t.normalize();n=p[1]-p[0];n.z=0;n.normalize()
 if groups and groups[-1]['road']==record['road'] and groups[-1]['normal'].dot(n)>.99 and (groups[-1]['end'].xy-a.xy).length<.035:groups[-1]['end']=b
 else:groups.append({'road':record['road'],'start':a,'end':b,'normal':n,'tangent':t})
print('Curbedge groups',len(groups),'long enough',sum((g['end']-g['start']).length>=1.3 for g in groups),'max length',max((g['end']-g['start']).length for g in groups));kit=Kit(terrain,None);kit.prefix='walkwear69-';patches=[];clumps=0;rejected={'bounds':0,'solids':0,'approaches':0,'ground':0}
for g in groups:
 length=(g['end']-g['start']).length
 if length<1.3 or r.random()>.60:continue
 for fraction in ([.30,.72] if length>16 else [.5]):
  t,n=g['tangent'],g['normal'];a=g['start'];size=r.uniform(2.6,3.2);depth=r.uniform(2.4,2.8)
  roadside=roads[g['road']]['width']>=7.5 and r.random()<.55
  center=a+t*(length*fraction)+n*((-depth/2-.16) if roadside else depth/2+.40)
  q=[center-t*size/2-n*depth/2,center+t*size/2-n*depth/2,center+t*size/2+n*depth/2,center-t*size/2+n*depth/2];poly=[tuple(p[:2]) for p in q]
  if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in poly):rejected['bounds']+=1;continue
  if any(h['overlap'](poly,p,.03) for p in solids):rejected['solids']+=1;continue
  if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<.8 for p in approaches):rejected['approaches']+=1;continue
  heights=[ground(p) for p in q];samples=[ground(q[0]+t*size*u/4+n*depth*v/4) for u in range(5) for v in range(5)]
  if any(z is None for z in samples) or max(samples)-min(samples)>.035:rejected['ground']+=1;continue
  verts=[tuple(Vector((p.x,p.y,z+.021))) for p,z in zip(q,heights)];uv=[(0,0),(1,0),(1,1),(0,1)];cross=t.cross(n).z;faces=[[0,1,2],[0,2,3]] if cross>0 else [[0,2,1],[0,3,2]]
  o=kit.mesh('patch-'+str(len(patches)),verts,faces,'agedPathPatch',False);del o['role'];o['surface_role']='forecourt';o['walkable']=False;o['path_wear_v69']=True
  # Alternate orientation without changing stone sizes or underlying native UVs.
  turn=len(patches)%4
  def rotate(u,v):
   for _ in range(turn):u,v=1-v,u
   return u,v
  for f in o.data.polygons:
   for li in f.loop_indices:o.data.uv_layers.active.data[li].uv=rotate(*uv[o.data.loops[li].vertex_index])
  roots=[]
  candidates=art['grassJointUVs'][:];r.shuffle(candidates)
  for tex_u,tex_v in candidates[:8]:
   u,v=tex_u,tex_v
   for _ in range((4-turn)%4):u,v=1-v,u
   p=q[0]+t*size*u+n*depth*v;z=ground(p);assert z is not None;p.z=z+.021;points=[];faces=[]
   for blade in range(3):
    angle=r.random()*math.tau;side=Vector((math.cos(angle),math.sin(angle),0))*.018;lean=Vector((r.uniform(-.035,.035),r.uniform(-.035,.035),r.uniform(.08,.16)));off=len(points);points.extend([tuple(p-side),tuple(p+side),tuple(p+lean)]);faces.append([off,off+1,off+2])
   ob=kit.mesh('joint-grass-'+str(clumps),points,faces,'grass',False);del ob['role'];ob['surface_role']='forecourt';ob['walkable']=False;ob['path_wear_grass_v69']=True;ob['path_wear_root']=list(p);roots.append(list(p));clumps+=1
  patches.append({'id':o.name,'road':g['road'],'location':'road shoulder' if roadside else 'building-side walk','size':[size,depth],'roots':roots,'turn':turn})
print('Wear patch skips',rejected);assert len(patches)>=12,(len(patches),'insufficient dispersed safe patches')
scene['ro3_path_wear_version']=69;scene['ro3_path_wear_review_json']=json.dumps({'patches':patches,'jointGrassClumps':clumps,'bladesPerClump':3,'nativeGroundOffset':.021,'collisionAndWalkableFloorChanged':False,'roadPaving':'shared rectangular flagstones, native world UV scale8; hexagon-like cobble repeat removed','protected':'existing solids, service/portal approaches, steps and road center','art':art})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Lived-in path:',len(patches),'aged misaligned stone patches;',clumps,'rooted joint grass clumps; roads share rectangular paving')
