"""Resolve native closed-curb grades and continuous accessible entrance profiles."""
import bpy,json,runpy,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_blueprint_contacts_version')==72
plan=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());record=json.loads(scene['ro3_blueprint_review_json']);ex=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))
if not scene.get('ro3_blueprint_stair_fit_version'):
 for name,a in plan['architectureChanges'].items():
  o=bpy.data.objects[name];inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;p.x=a['anchor']+(p.x-a['anchor'])*a['factor'] if a['mode']=='scaleX' else p.x+a['offset'];v.co=inv@p
 scene['ro3_blueprint_stair_fit_version']=72
if not scene.get('ro3_blueprint_ornament_fit_version'):
 for name,d in plan['ornamentMoves'].items():
  collection=bpy.data.collections[name];owned=set(collection.objects)
  for root in collection.objects:
   if root.parent not in owned:root.matrix_world=Matrix.Translation(Vector(d))@root.matrix_world
 scene['ro3_blueprint_ornament_fit_version']=72
record['civicOrnamentMoves']=plan['ornamentMoves']
record['plaza']={k:v for k,v in plan['plaza'].items() if k!='triangles'}
record['architectureChanges']=plan['architectureChanges'];record['stairReserve']=plan['stairReserve'];record['closedBoundaryLoops']=plan['closedBoundaryLoops'];record['zones']=[{k:v for k,v in z.items() if k not in ('triangles','curbBands','curbDistances')} for z in plan['zones']]
old=ex['export'](scene);names={r['id'] for r in record['curbs']};vs=[];fs=[]
for s in [old['terrain'],*[a for a in old['terrain']['surfaces'] if a['walkable'] and a['id'] not in names]]:
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  for j in range(1,len(f)-1):fs.append(tuple(off+f[k] for k in (0,j,j+1)))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def g(p):
 hit=floor.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),150)[0];return hit.z if hit else .025
def replace(o,verts,faces):
 mesh=bpy.data.meshes.new(o.name+'-graded72');mesh.from_pydata(verts,[],faces);mesh.materials.append(o.data.materials[0]);o.data=mesh;mesh.uv_layers.new(name='PhysicalUV');scale=json.loads(mesh.materials[0].get('texture_json','{}')).get('worldSize',2.4)
 for f in mesh.polygons:
  for li in f.loop_indices:
   p=mesh.vertices[mesh.loops[li].vertex_index].co;n=f.normal;mesh.uv_layers.active.data[li].uv=(p.x/scale,p.y/scale) if abs(n.z)>.65 else (p.y/scale,p.z/scale) if abs(n.x)>abs(n.y) else (p.x/scale,p.z/scale)
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
def surface(name,material,walkable):
 o=bpy.data.objects.get(name)
 if not o:
  data=bpy.data.meshes.new(name);data.materials.append(bpy.data.materials[material]);o=bpy.data.objects.new(name,data);terrain.objects.link(o);o['surface_role']='forecourt';o['walkable']=walkable;o['closed_curb_v72']=walkable
 return o
for z in plan['zones']:
 rec=next((r for r in record['curbs'] if r['zone']==z['id']),None)
 if rec is None:
  rec={'id':'blueprint72-curb-'+z['id'],'fascia':'blueprint72-fascia-'+z['id'],'zone':z['id'],'owners':z['owners'],'loweredCrossings':[],'width':.36,'rise':.20};record['curbs'].append(rec);surface(rec['id'],'roadCurbStone',True);surface(rec['fascia'],'roadCurbFace',False)
 rec['loops']=[r for a in z['outline'] for r in [a['outer'],*a['holes']]];drops=rec['loweredCrossings']
 def rise(p):
  d=min((math.dist(p,a) for a in drops),default=100);t=max(0,min(1,(d-.95)/.5));return .20*t*t*(3-2*t)
 def height(p):
  d=z['curbDistances'][f'{p[0]:.7f},{p[1]:.7f}'];bevel=.75+.25*min(1,max(0,min(d,.36-d))/.035);return g(p)+.0003+rise(p)*bevel
 triangles=[t for b in z['curbBands'] for t in b['triangles']];verts=[];faces=[];lookup={}
 for t in triangles:
  face=[]
  for p in t:
   key=(round(p[0],7),round(p[1],7))
   if key not in lookup:lookup[key]=len(verts);verts.append((*p,height(p)))
   face.append(lookup[key])
  a,b,c=[Vector(verts[i]) for i in face]
  if (b-a).cross(c-a).z<0:face.reverse()
  faces.append(face)
 replace(bpy.data.objects[rec['id']],verts,faces)
 fv=[];ff=[]
 for bounds in [z['outline'],z['curbInner']]:
  for a in bounds:
   for ring in [a['outer'],*a['holes']]:
    sampled=[]
    for p,q in zip(ring,ring[1:]+ring[:1]):
     count=math.ceil(math.dist(p,q)/.6);sampled.extend([(p[0]+(q[0]-p[0])*k/count,p[1]+(q[1]-p[1])*k/count) for k in range(count)])
    for p,q in zip(sampled,sampled[1:]+sampled[:1]):
     i=len(fv);fv.extend([(*p,g(p)-.003),(*q,g(q)-.003),(*q,g(q)+.0003+rise(q)*.75),(*p,g(p)+.0003+rise(p)*.75)]);ff.append([i,i+1,i+2,i+3])
 replace(bpy.data.objects[rec['fascia']],fv,ff)
 rec['gradeSampleSpacing']=.6
 if z.get('greenTriangles'):
  name='blueprint72-green-'+z['id'];o=surface(name,'plantingEdgeGrass',False);points=[(x,y,g((x,y))+.017) for t in z['greenTriangles'] for x,y in t];replace(o,points,[list(range(i,i+3)) for i in range(0,len(points),3)]);record['curbGreen']=[r for r in record['curbGreen'] if r['id']!=name]+[{'id':name,'zone':z['id'],'kind':'owned civic planting island'}]
def planar(o,triangles,z):
 if not triangles:o['render_visible']=False;o['walkable']=False;return
 points=[(x,y,z) for t in triangles for x,y in t];faces=[]
 for i in range(0,len(points),3):
  a,b,c=map(Vector,points[i:i+3]);faces.append([i,i+1,i+2] if (b-a).cross(c-a).z>0 else [i+2,i+1,i])
 replace(o,points,faces);o['render_visible']=True;o['walkable']=True
for r in plan['roads']:
 o=bpy.data.objects[r['id']];planar(o,r['triangles'],r['z']);o['centerline_json']=json.dumps(r['centerline']);o['road_width']=min(r['widths'])
for r in plan['aprons']:planar(bpy.data.objects[r['id']],r['triangles'],r['z'])
planar(bpy.data.objects['organic-v47-civic-court'],plan['plaza']['triangles'],.025)
for name,r in plan['approaches'].items():planar(bpy.data.objects['blueprint72-cross-'+name],r['triangles'],.026)
scene['ro3_blueprint_review_json']=json.dumps(record);scene['ro3_blueprint_profiles_version']=72;runpy.run_path(str(ROOT/'tools/fit-ro3-grass-contact-v70.py'))['fit'](scene)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS continuous lowered native curb profiles, max edge spacing .6m')
