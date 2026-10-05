"""Relocate orphan flowers to grounded building-side planting edges; retain containers."""
import bpy,json,math,re,runpy
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_planting_edge_version');Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());art=json.loads((ROOT/'authoring/materials/wayfarer-planting-grass-v69.json').read_text());m=bpy.data.materials.new('plantingEdgeGrass');m.diffuse_color=(.29,.46,.14,1);m['texture_json']=json.dumps(art['texture'])
for name in ('vergeGroundcover','vergeGroundcoverShade'):bpy.data.materials[name]['texture_json']=json.dumps(art['texture'])
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];return hit.z if hit else None
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];approaches=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])];edges=[]
for record in json.loads(scene['ro3_road_curb_review_json'])['curbBlocks']:
 o=bpy.data.objects[record['id']];p=[o.matrix_world@v.co for v in o.data.vertices];t=p[6]-p[0];t.z=0;t.normalize();n=p[1]-p[0];n.z=0;n.normalize();edges.append({'road':record['road'],'point':(p[0]+p[6])/2,'t':t,'n':n})
occupied=[];kit=Kit(terrain,None);kit.prefix='plantedge69-';records=[];small=[]
def safe(center,t,n,length,width):
 q=[center+t*u*length/2+n*v*width/2 for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]];poly=[tuple(p[:2]) for p in q]
 if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in poly):return None
 if any(h['overlap'](poly,p,.10) for p in solids+occupied):return None
 if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<.95 for p in approaches):return None
 heights=[ground(q[0]+t*length*u/4+n*width*v/4) for u in range(5) for v in range(5)]
 if any(z is None for z in heights) or max(heights)-min(heights)>.035:return None
 return q,poly,ground(center)
def choose(old,length,width):
 candidates=[]
 for e in edges:
  center=e['point']+e['n']*(.325+width/2+.12);candidate=safe(center,e['t'],e['n'],length,width)
  if candidate:candidates.append(((center.xy-old.xy).length,e,center,candidate))
 assert candidates,tuple(old)
 _,e,center,candidate=min(candidates,key=lambda v:v[0]);return e,center,candidate

def grass_patch(q,poly,z,name):
 verts=[tuple(Vector((p.x,p.y,z+.017))) for p in q];faces=[[0,1,2],[0,2,3]] if (q[1]-q[0]).cross(q[3]-q[0]).z>0 else [[0,2,1],[0,3,2]]
 ob=kit.mesh('grass-'+name,verts,faces,'plantingEdgeGrass',False);del ob['role'];ob['surface_role']='forecourt';ob['walkable']=False;ob['planting_edge_grass_v69']=True
 uv=[(0,0),(1,0),(1,1),(0,1)]
 for f in ob.data.polygons:
  for li in f.loop_indices:ob.data.uv_layers.active.data[li].uv=uv[ob.data.loops[li].vertex_index]
 return ob.name
owner=bpy.data.collections['wayfarer-civic-gardens']
for i in range(5):
 soil=bpy.data.objects['organic-v47-bed-'+str(i)];parts=[o for o in owner.objects if o==soil or o.name.startswith('organic-v47-bed-shrub-'+str(i)+'-') or o.name.startswith('organic-v47-bed-petal-'+str(i)+'-')]
 points=[soil.matrix_world@v.co for v in soil.data.vertices];old=sum(points,Vector())/len(points);scale=.58;width=(max(p.x for p in points)-min(p.x for p in points))*scale;length=(max(p.y for p in points)-min(p.y for p in points))*scale
 # Flowers' leaf/petal extents fit the padded planted island.
 length+=.20;width+=.20;e,center,(q,poly,z)=choose(old,length,width);angle=math.atan2(e['t'].y,e['t'].x)-math.pi/2
 transform=Matrix.Translation(Vector((center.x,center.y,z+.020)))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal(Vector((scale,scale,1,1)))@Matrix.Translation(-old)
 for o in parts:o.matrix_world=transform@o.matrix_world;o['planting_edge_v69']=True
 patch=grass_patch(q,poly,z,'bed-'+str(i));occupied.append(poly);records.append({'group':i,'parts':[o.name for o in parts],'before':list(old),'after':[center.x,center.y,z+.020],'xyScale':scale,'road':e['road'],'grassPatch':patch,'plantingPolygon':poly,'floor':z})
# Preserve flower boxes, fountain beds, owned doorway planting and close building-edge rows.
# Rehome the inherited ground groups that were stranded far from any physical edge.
owner=bpy.data.collections['wayfarer-v44-detail'];orphans=[]
for o in owner.objects:
 if o.type!='MESH' or not o.get('render_visible',True) or not re.match(r'flora-v64-\d+-soil$',o.name):continue
 p=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 distance=min(min(h['distance'](p[:2],a,b) for a,b in zip(poly,poly[1:]+poly[:1])) if not h['inside'](p[:2],poly) else 0 for poly in solids)
 if distance>2.8:orphans.append((int(o.name.split('-')[2]),p))
for k,old in sorted(orphans):
 parts=[o for o in owner.objects if o.type=='MESH' and (o.name.startswith('detail-v44-flower-'+str(k)+'-') or o.name.startswith('flora-v64-'+str(k)+'-'))];assert parts
 e,center,(q,poly,z)=choose(old,.70,.70);old_floor=ground(old);assert old_floor is not None;offset=Vector((center.x-old.x,center.y-old.y,z-old_floor))
 for o in parts:o.matrix_world=Matrix.Translation(offset)@o.matrix_world;o['planting_edge_v69']=True
 patch=grass_patch(q,poly,z,'flower-'+str(k));occupied.append(poly);small.append({'group':k,'parts':[o.name for o in parts],'before':list(old),'after':[center.x,center.y,z+old.z-old_floor],'road':e['road'],'grassPatch':patch,'plantingPolygon':poly,'floor':z})
assert len(records)==5 and len(small)>0
scene['ro3_planting_edge_version']=69;scene['ro3_planting_edge_review_json']=json.dumps({'beds':records,'orphanGroundFlowerGroups':small,'grassPatches':len(records)+len(small),'preserved':'raised flower boxes, formal fountain beds, owned entrances and near-building ground flowers; all original solids and walkable floors','placement':'grounded grass islands on building-side curb edges; solids, approaches, steps protected','art':art})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS planting edges:',len(records),'relocated beds;',len(small),'relocated orphan flower groups; grounded grass islands')
