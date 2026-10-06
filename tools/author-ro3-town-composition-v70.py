"""Saved-source migration: layered evergreens, owned green verges and facade relief.

Retains every original solid, editable placement, aperture and route. Original
foliage remains hidden in the file; the new curved boughs use original artwork.
"""
import bpy,bmesh,json,math,random,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_spatial_hierarchy_version')==70
assert not scene.get('ro3_town_composition_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'))
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene)
runpy.run_path(str(ROOT/'tools/fit-ro3-grass-contact-v70.py'))['fit'](scene)
art=json.loads((ROOT/'authoring/materials/wayfarer-conifer-v70.json').read_text())
for name,color in [('conifer70',(.22,.33,.12)),('conifer70Light',(.33,.445,.17)),('conifer70Shade',(.125,.23,.075))]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m['texture_json']=json.dumps(art['texture'])
bpy.data.materials['timber'].diffuse_color=(.31,.195,.105,1)
bpy.data.materials['roofClayWarm'].diffuse_color=(.47,.17,.085,1)
bpy.data.materials['roofClayOchre'].diffuse_color=(.55,.285,.13,1)
bpy.data.materials['stoneLight'].diffuse_color=(.79,.745,.62,1)
rose=bpy.data.materials['roofClayWarm'].copy();rose.name='roofClayRose';rose.diffuse_color=(.40,.14,.175,1)
rose_owners=['frontage-garden-home','frontage-riverside','north-garden-house','civic-home-west','willow-house','district-northern-townhouse'];rose_parts=0
for name in rose_owners:
 for obj in bpy.data.collections[name].objects:
  if obj.type=='MESH' and obj.data.materials and obj.data.materials[0].name=='roofClayWarm':obj.data.materials[0]=rose;rose_parts+=1
bpy.data.materials['gardenBenchGreen'].diffuse_color=(.105,.22,.155,1)
bpy.data.materials['plantingEdgeGrass'].diffuse_color=(.37,.47,.19,1)
for name in ('vergeGroundcover','vergeGroundcoverShade'):
 bpy.data.materials[name].diffuse_color=(.36,.455,.18,1)

terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
vs=[];fs=[]
for s in w['terrain']['surfaces']:
 if not s['walkable']:continue
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  fs.extend(tuple(off+f[k] for k in (0,j,j+1)) for j in range(1,len(f)-1))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),150)[0]
 return hit.z if hit else None
roads=[h['hull'](s['vertices']) for s in w['terrain']['surfaces'] if s.get('centerline') and s.get('width',0)>=1.8]
solids=[(o['id'],h['hull'](p['vertices'])) for o in w['objects'] for p in o['parts'] if p['role']=='solid']
approaches=[s['position'][:2] for o in w['objects'] for s in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])]
def safe(poly,owner=None):
 if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in poly):return False
 if any(h['overlap'](poly,p,.06) for p in roads):return False
 if any(oid!=owner and h['overlap'](poly,p,.06) for oid,p in solids):return False
 if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<.80 for p in approaches):return False
 return True

rng=random.Random(70083);trees=[];hidden=[];beds=[];verges=[];ornaments=[];shutters=[]
tk=Kit(terrain,None);tk.prefix='green70-'
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 if c.get('family')!='vegetation':continue
 roots=[o for o in c.objects if o.type=='MESH' and o.name.endswith('-root') and o.get('role')=='solid']
 for index,root in enumerate(roots):
  prefix=root.name[:-5]
  # Keep two civic broadleaf accents; the street/garden trees become evergreens.
  if prefix in ('hall-oak-west','shrine-oak-west'):continue
  leaves=[o for o in c.objects if o.type=='MESH' and o.get('render_visible',True) and o.data.materials and o.data.materials[0].name=='foliageCutout' and (o.name.startswith(prefix+'-') or o.name.startswith('tree69-crown-'+prefix+'-'))]
  if not leaves:continue
  bounds=[o.matrix_world@v.co for o in leaves for v in o.data.vertices]
  rp=[root.matrix_world@v.co for v in root.data.vertices]
  cx=(min(p.x for p in rp)+max(p.x for p in rp))/2;cy=(min(p.y for p in rp)+max(p.y for p in rp))/2;base=min(p.z for p in rp)
  radius=max(max(p.x for p in bounds)-min(p.x for p in bounds),max(p.y for p in bounds)-min(p.y for p in bounds))*.46
  height=(max(p.z for p in bounds)-base)*1.28
  assert .4<radius<4 and 2<height<12,(prefix,radius,height)
  for o in leaves:o['render_visible']=False;o['shadow']=False;hidden.append(o.name)
  # Original sideways branches would protrude outside a tapered evergreen.
  for o in c.objects:
   if o.name.startswith(prefix+'-branch-'):o['render_visible']=False;o['shadow']=False;hidden.append(o.name)
  kit=Kit(c,None);kit.prefix='conifer70-'+prefix+'-'
  groups={n:([],[],[]) for n in ('conifer70','conifer70Light','conifer70Shade')}
  for tier in range(8):
   t=tier/7;rad=radius*(.08+.92*(1-t)**.82);z=base+height*(.34+.66*t)
   for fan in range(8):
    angle=fan*math.tau/8+tier*.39+rng.uniform(-.08,.08)
    rr=rad*rng.uniform(.89,1.05);drop=height*(.085-.025*t)
    mat='conifer70Light' if fan in (0,1,7) and tier>2 else 'conifer70Shade' if fan in (3,4,5) else 'conifer70'
    vertices,faces,uvs=groups[mat];off=len(vertices)
    for j in range(3):
     v=j/2;distance=rr*(.12+.88*v)
     for i in range(3):
      u=i/2;a=angle+(u-.5)*(1.12-.18*v)
      zz=z-drop*v**1.4+.09*rr*math.sin(math.pi*u)*math.sin(math.pi*v)
      vertices.append((cx+distance*math.cos(a),cy+distance*math.sin(a),zz));uvs.append((u,1-v))
    for j in range(2):
     for i in range(2):
      k=off+j*3+i;faces.append([k,k+1,k+4,k+3])
  added=[]
  for mat,(vertices,faces,uvs) in groups.items():
   obj=kit.mesh(mat,vertices,faces,mat,True);obj['role']='overhead';obj['conifer_v70']=True
   bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0]);bm.to_mesh(obj.data);bm.free();obj.data.update()
   matrix=obj.matrix_world.copy();obj.parent=root.parent;obj.matrix_world=matrix
   for f in obj.data.polygons:
    for li in f.loop_indices:obj.data.uv_layers.active.data[li].uv=uvs[obj.data.loops[li].vertex_index]
   added.append(obj.name)
  trees.append({'root':root.name,'center':[cx,cy,base],'radius':radius,'height':height,'tiers':8,'boughs':64,'parts':added,'retainedRootAndCollision':True})
  # A chamfered owned grass bed grows around the trunk, on building-side paving.
  chosen=None
  for rx,ry in ((1.8,1.65),(1.6,1.45),(1.4,1.3),(1.2,1.1)):
   cut=.28;poly=[(cx-rx+cut,cy-ry),(cx+rx-cut,cy-ry),(cx+rx,cy-ry+cut),(cx+rx,cy+ry-cut),(cx+rx-cut,cy+ry),(cx-rx+cut,cy+ry),(cx-rx,cy+ry-cut),(cx-rx,cy-ry+cut)]
   heights=[ground(p) for p in poly]+[ground((cx,cy))]
   if safe(poly,c.name) and all(z is not None for z in heights) and max(heights)-min(heights)<.035:chosen=poly,heights;break
  if chosen:
   poly,heights=chosen;z=heights[-1]+.017
   obj=tk.mesh('tree-bed-'+prefix,[(cx,cy,z)]+[(p[0],p[1],heights[i]+.017) for i,p in enumerate(poly)],[[0,i+1,(i+1)%8+1] for i in range(8)],'plantingEdgeGrass',False)
   del obj['role'];obj['surface_role']='forecourt';obj['walkable']=False;obj['green_bed_v70']=True
   for f in obj.data.polygons:
    for li in f.loop_indices:
     p=obj.data.vertices[obj.data.loops[li].vertex_index].co;obj.data.uv_layers.active.data[li].uv=((p.x-(cx-rx))/(rx*2),(p.y-(cy-ry))/(ry*2))
   # Existing tree soil/stone ring remains visible as the trunk's inner edging.
   beds.append({'id':obj.name,'owner':c.name,'root':root.name,'polygon':poly,'contacts':9,'floorOffset':.017})

# Broaden coherent verge strips outward into safe building zones, never the road.
review=json.loads(scene['ro3_curb_grass_review_json'])
for rec in review['strips']:
 obj=bpy.data.objects[rec['id']];pts=[obj.matrix_world@v.co for v in obj.data.vertices];normal=pts[3]-pts[0];normal.z=0;old=normal.length;normal.normalize()
 for depth in (1.7,1.4,1.1,.9):
  if depth<old+.2:continue
  q=[pts[0],pts[1],pts[1]+normal*depth,pts[0]+normal*depth];poly=[tuple(p[:2]) for p in q]
  samples=[q[0]+(q[1]-q[0])*u/4+(q[3]-q[0])*v/4 for u in range(5) for v in range(5)]
  zs=[ground(p) for p in samples]
  if not safe(poly) or any(z is None for z in zs) or max(zs)-min(zs)>.035:continue
  inv=obj.matrix_world.inverted()
  for vertex,p in zip(obj.data.vertices,q):p.z=ground(p)+.017;vertex.co=inv@p
  rec['vertices']=[list(obj.matrix_world@v.co) for v in obj.data.vertices];rec['greenDepthV70']=depth
  verges.append({'id':obj.name,'oldDepth':old,'newDepth':depth,'contacts':4});break
scene['ro3_curb_grass_review_json']=json.dumps(review)

# Carved lower window bands and open shutters create real facade relief.
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 if c.get('family') not in ('residential','market','workshop','inn'):continue
 windows=[o for o in c.objects if o.type=='MESH' and o.name.startswith('ro3-v68-') and '-front-window-' in o.name and o.name.endswith('-glass')]
 for index,window in enumerate(windows):
  root=window.parent;kit=Kit(c,root);kit.prefix='facade70-'+c.name+'-'+str(index)+'-'
  p=[v.co.copy() for v in window.data.vertices];center=sum(p,Vector())/len(p);width=max(v.x for v in p)-min(v.x for v in p);height=max(v.z for v in p)-min(v.z for v in p)
  bottom=center.z-height/2;front=center.y+.40
  # Strip and diamonds sit below the sill, leaving every light unobstructed.
  band=kit.box('carved-band',(center.x,front,bottom-.39),(width+.19,.085,.17),'timber');ornaments.append(band.name)
  for k in (-1,0,1):
   x=center.x+k*width*.29;z=bottom-.39;r=.063
   obj=kit.mesh('diamond-'+str(k),[(x-r,front+.048,z),(x,front+.070,z+r),(x+r,front+.048,z),(x,front+.070,z-r),(x,front+.09,z)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'stoneLight',True);ornaments.append(obj.name)
  if index%2 or c.get('family')=='workshop':continue
  for side in (-1,1):
   x=center.x+side*(width/2+.22);panelwidth=.24
   obj=kit.box('open-shutter-'+str(side),(x,front+.04,center.z),(panelwidth,.075,height*.97),'timber');shutters.append(obj.name)
   for z in (center.z-height*.34,center.z+height*.34):kit.box('shutter-strap-'+str((side,z)),(x,front+.084,z),(panelwidth,.025,.047),'iron',False)
   for k in (-1,0,1):kit.box('shutter-board-'+str((side,k)),(x+k*(.10*2/3),front+.083,center.z),(.05,.022,height*.87),'timber',False)

scene['ro3_town_composition_version']=70
scene['ro3_town_composition_review_json']=json.dumps({'shutterWidth':.24,'shutterClearance':'Narrow leaves fitted between neighboring window bays','roseRoofOwners':rose_owners,'roseRoofParts':rose_parts,'benchPalette':'weathered sage green','evergreens':trees,'hiddenOriginalDecorations':hidden,'ownedTreeBeds':beds,'broadenedBuildingVergeStrips':verges,'carvedFacadeParts':ornaments,'openShutters':shutters,'fountain':'Retained planted tiered pools, four benches, four raised flower beds and cascades; public court now has irregular street stone','placement':'Tree beds and broadened verges tested outside through-roads, solids and service approaches; all original house envelopes and collision retained','texture':art,'lighting':'Native warm sunlight, neutral warm fill and eight-ray gray-green ground casts, with corner contact shading'})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('PASS native source70 composition:',len(trees),'evergreens;',len(beds),'owned tree beds;',len(verges),'broader green verges;',len(ornaments),'carved facade parts;',len(shutters),'open shutters')
