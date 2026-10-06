"""Author the reviewed square, road cross and closed district curbs into Blender.

Input is an offline plan from plan-ro3-blueprint-v72.py; geometry, materials,
placements and continuous lowered entrances are saved in the native authority.
"""
import bpy,json,runpy,sys,math,random
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_public_planting_version')==71 and not scene.get('ro3_blueprint_version')
plan=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));before=exporter['export'](scene)
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];kit=Kit(terrain,None);kit.prefix='blueprint72-'
def uv(o):
 scale=json.loads(o.data.materials[0].get('texture_json','{}')).get('worldSize',2.4)
 if not o.data.uv_layers.active:o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;n=f.normal
   o.data.uv_layers.active.data[li].uv=(p.x/scale,p.y/scale) if abs(n.z)>.65 else (p.y/scale,p.z/scale) if abs(n.x)>abs(n.y) else (p.x/scale,p.z/scale)
def floor_tree(data):
 vs=[];fs=[]
 # Continuous land is a physical floor too, including outer wall margins.
 for s in [data['terrain'],*[a for a in data['terrain']['surfaces'] if a['walkable']]]:
  off=len(vs);vs.extend(s['vertices'])
  for f in s['faces']:
   for i in range(1,len(f)-1):fs.append(tuple(off+f[k] for k in (0,i,i+1)))
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
oldfloor=floor_tree(before)
def ground(tree,p):
 hit=tree.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),150)[0]
 return hit.z if hit else .025
# Preserve complete house hierarchies; articulated facade detail and scale survive.
for name,d in plan['houseMoves'].items():
 root=bpy.data.objects[name+'-placement'];root.matrix_world=Matrix.Translation(Vector(d))@root.matrix_world
bpy.context.view_layer.update()
# Fountain's figure, native pools, water, planters and seating share its placement.
fountain=bpy.data.collections['astral-fountain'];basin=bpy.data.objects['fountain-basin'];pts=[basin.matrix_world@v.co for v in basin.data.vertices];old=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2,0));fd=Vector((*plan['center'],0))-old
root=bpy.data.objects['astral-fountain-placement'];root.matrix_world=Matrix.Translation(fd)@root.matrix_world
composition=json.loads(scene['ro3_town_composition_review_json']);treeRecords={a['root']:a for a in composition['evergreens']};treeParts={};treeMoves=[]
for name,d in plan['treeMoves'].items():
 trunk=bpy.data.objects[name];owner=trunk.users_collection[0];prefix=name[:-5] if name.endswith('-root') else name[:-6];extra=set(treeRecords.get(name,{}).get('parts',[]));parts=[o for o in owner.objects if o.type=='MESH' and (o.name.startswith(prefix+'-') or o.name.startswith('tree69-crown-'+prefix+'-') or o.name in extra)]
 assert trunk in parts,(name,'tree group');delta=Vector(d);p=trunk.matrix_world.translation;points=[trunk.matrix_world@v.co for v in trunk.data.vertices];cx=sum(v.x for v in points)/len(points);cy=sum(v.y for v in points)/len(points);delta.z=ground(oldfloor,(cx+delta.x,cy+delta.y))-ground(oldfloor,(cx,cy))
 for o in parts:o.matrix_world=Matrix.Translation(delta)@o.matrix_world
 treeParts[name]=[o.name for o in parts];treeMoves.append({'root':name,'parts':treeParts[name],'offset':list(delta)})
 if name in treeRecords:treeRecords[name]['center']=[treeRecords[name]['center'][i]+delta[i] for i in range(3)]
 # Owned original-alpha tree-bed artwork follows the trunk.
 for b in composition['ownedTreeBeds']:
  if b['root']==name:
   o=bpy.data.objects[b['id']];o.matrix_world=Matrix.Translation(delta)@o.matrix_world;b['polygon']=[[x+delta.x,y+delta.y] for x,y in b['polygon']]
scene['ro3_town_composition_review_json']=json.dumps(composition)
# Retire all independent strip ends and legacy apron rims.
retired=[]
for o in terrain.objects:
 if o.type=='MESH' and (o.get('road_curb_v69') or o.get('curb_fascia_v70') or (o.name.startswith('lot69-') and '-rim-' in o.name) or o.get('curb_grass_v69') or o.name.startswith('composition70-verge-')):
  o['render_visible']=False;o['walkable']=False;retired.append(o.name)
def replace_mesh(o,triangles,z):
 if not triangles:o['render_visible']=False;o['walkable']=False;return
 verts=[];faces=[];lookup={}
 for t in triangles:
  face=[]
  for x,y in t:
   key=(round(x,7),round(y,7))
   if key not in lookup:lookup[key]=len(verts);verts.append((x,y,z(x,y) if callable(z) else z))
   face.append(lookup[key])
  # Native upward faces independent of polygon winding.
  a,b,c=[Vector(verts[i]) for i in face]
  if (b-a).cross(c-a).z<0:face.reverse()
  faces.append(face)
 mesh=bpy.data.meshes.new(o.name+'-native72');mesh.from_pydata(verts,[],faces);mesh.materials.append(o.data.materials[0]);o.data=mesh;o.matrix_world=Matrix.Identity(4);uv(o)
for r in plan['roads']:
 o=bpy.data.objects[r['id']];replace_mesh(o,r['triangles'],r['z']);o['centerline_json']=json.dumps(r['centerline']);o['road_width']=min(r['widths'])
replace_mesh(bpy.data.objects['organic-v47-civic-court'],plan['plaza']['triangles'],.025)
for name,r in plan['approaches'].items():
 verts=[(x,y,.026) for t in r['triangles'] for x,y in t];o=kit.mesh('cross-'+name,verts,[list(range(i,i+3)) for i in range(0,len(verts),3)],'publicSquareStone',False);del o['role'];o['surface_role']='primary';o['walkable']=True
for r in plan['aprons']:
 replace_mesh(bpy.data.objects[r['id']],r['triangles'],r['z'])
bpy.context.view_layer.update();base=exporter['export'](scene);floor=floor_tree(base)
def g(p):return ground(floor,p)
# Read native entrances, not gaps in an arbitrary road strip.
entries=[a['approach'][:2] for o in base['objects'] for a in o.get('portals',[])]+[a['position'][:2] for o in base['objects'] for a in o.get('services',[])]
# Ordinary front doors also receive a continuous lowered curb crossing.
for c in bpy.data.collections:
 doors=[o for o in c.objects if o.type=='MESH' and 'door' in o.name and o.get('render_visible',True) and not any(k in o.name for k in ('jamb','lintel','surround','arch','hood','handle','hinge','bolt'))]
 if doors:
  points=[o.matrix_world@v.co for o in doors for v in o.data.vertices];entries.append([sum(p.x for p in points)/len(points),sum(p.y for p in points)/len(points)])
curbs=[];grass=[];rng=random.Random(7207);solidPolys=[h['hull'](p['vertices']) for obj in base['objects'] for p in obj['parts'] if p['role']=='solid']
for z in plan['zones']:
 rings=[r for a in z['outline'] for r in [a['outer'],*a['holes']]];segments=[(a,b) for r in rings for a,b in zip(r,r[1:]+r[:1])]
 def dist(p):return z.get('curbDistances',{}).get(f'{p[0]:.7f},{p[1]:.7f}',0) if z.get('curbDistances') else min(h['distance'](p,a,b) for a,b in segments)
 # Project each entrance onto this closed boundary only if it is a local crossing.
 drops=[]
 for p in entries:
  nearest=None
  for a,b in segments:
   dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)));q=(a[0]+t*dx,a[1]+t*dy);d=math.dist(p,q)
   if nearest is None or d<nearest[0]:nearest=(d,q)
  if nearest and nearest[0]<4:drops.append(nearest[1])
 def rise(p):
  d=min((math.dist(p,a) for a in drops),default=100);t=max(0,min(1,(d-.95)/.5));return .20*t*t*(3-2*t)
 def height(x,y):
  d=dist((x,y));bevel=.75+.25*min(1,max(0,min(d,.36-d))/.035);return g((x,y))+rise((x,y))*bevel
 triangles=[t for b in z['curbBands'] for t in b['triangles']];o=kit.mesh('curb-'+z['id'],[(x,y,height(x,y)) for t in triangles for x,y in t],[list(range(i,i+3)) for i in range(0,len(triangles)*3,3)],'roadCurbStone',False);del o['role'];o['surface_role']='forecourt';o['walkable']=True;o['closed_curb_v72']=True;replace_mesh(o,triangles,height)
 fasciaVerts=[];fasciaFaces=[]
 for bounds in [z['outline'],z['curbInner']]:
  for a in bounds:
   for ring in [a['outer'],*a['holes']]:
    for p,q in zip(ring,ring[1:]+ring[:1]):
     i=len(fasciaVerts);fasciaVerts.extend([(p[0],p[1],g(p)+.003),(q[0],q[1],g(q)+.003),(q[0],q[1],height(*q)),(p[0],p[1],height(*p))]);fasciaFaces.append([i,i+1,i+2,i+3])
 f=kit.mesh('fascia-'+z['id'],fasciaVerts,fasciaFaces,'roadCurbFace',False);del f['role'];f['surface_role']='forecourt';f['walkable']=False
 curbs.append({'id':o.name,'fascia':f.name,'zone':z['id'],'owners':z['owners'],'loops':rings,'loweredCrossings':drops,'width':.36,'rise':.20})
 # Soft original-alpha planting is tied to the plot's inside curb margin.
 # Choose short straight courses; don't span grade changes or an entrance.
 for a,b in segments:
  length=math.dist(a,b)
  if length<1.8 or rng.random()>.30:continue
  tx,ty=(b[0]-a[0])/length,(b[1]-a[1])/length;mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
  # Find the building side by the actual closed plot outline (holes included).
  def inside(p):return any(h['inside'](p,k['outer']) and not any(h['inside'](p,r) for r in k['holes']) for k in z['outline'])
  nx,ny=-ty,tx
  if not inside((mid[0]+nx*.5,mid[1]+ny*.5)):nx,ny=-nx,-ny
  span=min(length-.2,2.6);pts=[(mid[0]+tx*t+nx*d,mid[1]+ty*t+ny*d) for t,d in [(-span/2,.44),(span/2,.44),(span/2,.95),(-span/2,.95)]]
  if not all(inside(p) for p in pts) or any(math.dist(mid,p)<1.4 for p in drops):continue
  if any(h['overlap'](pts,p,.05) for p in solidPolys):continue
  heights=[g((pts[0][0]+(pts[1][0]-pts[0][0])*u/4+(pts[3][0]-pts[0][0])*v/4,pts[0][1]+(pts[1][1]-pts[0][1])*u/4+(pts[3][1]-pts[0][1])*v/4)) for u in range(5) for v in range(5)]
  if max(heights)-min(heights)>.025:continue
  verts=[(x,y,g((x,y))+.017) for x,y in pts];o=kit.mesh('green-'+str(len(grass)),verts,[[0,1,2],[0,2,3]],'plantingEdgeGrass',False);del o['role'];o['surface_role']='forecourt';o['walkable']=False
  for face in o.data.polygons:
   for li in face.loop_indices:o.data.uv_layers.active.data[li].uv=[(0,0),(1,0),(1,1),(0,1)][o.data.loops[li].vertex_index]
  grass.append({'id':o.name,'zone':z['id'],'vertices':verts})
scene['ro3_blueprint_version']=72;scene['ro3_blueprint_review_json']=json.dumps({'plaza':{k:v for k,v in plan['plaza'].items() if k!='triangles'},'center':plan['center'],'houseMoves':plan['houseMoves'],'treeMoves':treeMoves,'fountainOffset':list(fd),'zones':[{k:v for k,v in z.items() if k not in ('triangles','curbBands')} for z in plan['zones']],'curbs':curbs,'closedBoundaryLoops':sum(len(r['loops']) for r in curbs),'retiredLegacyMeshes':retired,'curbGreen':grass,'rule':plan['rule']})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS native larger square and closed district boundaries',len(curbs),'curb meshes',len(grass),'soft planting courses')
