"""Weathered native facades and house-owned fittings on completed street69.

All ground goods have explicit native collision proxies. Elevated window boxes,
lamps and drains share each house's editable frame. Reuses palette/materials;
no dynamic lights or per-frame procedural dressing.
"""
import json,math,random,runpy
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_street_version')==69
assert not scene.get('ro3_house_life_version'),'Migration already applied'
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
# Fit each green island's single cutout swatch to its native wedge. Source
# geometry remains rooted; the alpha perimeter supplies an organic edge.
for o in bpy.data.objects:
 if o.get('street_v69_patch'):
  points=[v.co for v in o.data.vertices];t=(points[-1]-points[0]).normalized();n=Vector((-t.y,t.x,0))
  us=[v.dot(t) for v in points];vs=[v.dot(n) for v in points]
  for f in o.data.polygons:
   for li in f.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co
    o.data.uv_layers.active.data[li].uv=((q.dot(t)-min(us))/(max(us)-min(us)),(q.dot(n)-min(vs))/(max(vs)-min(vs)))
art=json.loads((ROOT/'authoring/materials/wayfarer-house-weather-v69.json').read_text())['materials']
for name in ('homeLimewash','merchantLimewash','workshopLimewash','plaster'):
 bpy.data.materials[name]['texture_json']=json.dumps(art['limewash']['texture'])
# Old UV registrations used a four-unit repeat. Preserve physical density.
for o in bpy.data.objects:
 if o.type=='MESH' and o.data.materials and o.data.materials[0].name in ('homeLimewash','merchantLimewash','workshopLimewash','plaster') and o.data.uv_layers.active:
  for uv in o.data.uv_layers.active.data:uv.uv*=4/3.2
patina=bpy.data.materials.new('foundationPatina');patina.diffuse_color=(.16,.17,.08,1);patina['texture_json']=json.dumps(art['patina']['texture'])
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def height(x,y):
 hit=floor.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),150)[0]
 assert hit is not None,(x,y)
 return hit.z

def hull(points):
 p=sorted(set((round(v.x,5),round(v.y,5)) for v in points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 def chain(seq):
  out=[]
  for v in seq:
   while len(out)>1 and cross(out[-2],out[-1],v)<=0:out.pop()
   out.append(v)
  return out
 return chain(p)[:-1]+chain(reversed(p))[:-1]

records=[];r=random.Random(694539)
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 core=next((o for o in c.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls'))),None)
 if core is None:continue
 root=core.parent;inv=root.matrix_world.inverted();kit=Kit(c,root);kit.prefix='life69-'+c.name[:22]+'-'
 points=[inv@core.matrix_world@v.co for v in core.data.vertices];poly=hull(points);top=max(v.z for v in points)
 front=max(zip(poly,poly[1:]+poly[:1]),key=lambda e:e[1][0]-e[0][0])
 a,b=Vector((*front[0],0)),Vector((*front[1],0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));length=(b-a).length
 # Rooted damp strip is mapped vertically once, with irregular cutout coverage.
 for j,(aa,bb) in enumerate(zip(poly,poly[1:]+poly[:1])):
  aa,bb=Vector((*aa,0)),Vector((*bb,0));tt=(bb-aa).normalized();nn=Vector((tt.y,-tt.x,0));ll=(bb-aa).length
  pp=[aa+nn*.008+Vector((0,0,.46)),bb+nn*.008+Vector((0,0,.46)),bb+nn*.008+Vector((0,0,.98)),aa+nn*.008+Vector((0,0,.98))]
  ob=kit.mesh('base-wear-'+str(j),[tuple(p) for p in pp],[[0,1,2,3]],'foundationPatina',False)
  for f in ob.data.polygons:
   for k,li in enumerate(f.loop_indices):ob.data.uv_layers.active.data[li].uv=[(0,1),(ll/2.4,1),(ll/2.4,0),(0,0)][k]
 # Lantern brackets and the downpipe lie under the jetty, away from glazing.
 px=a+t*.32+n*.105
 kit.beam('drain',tuple(px+Vector((0,0,.54))),tuple(px+Vector((0,0,top-.32))),.075,'iron')
 for z in (.80,1.9,top-.45):kit.box('drain-clip-'+str(z),tuple(px+Vector((0,0,z))),(.13,.05,.045),'iron',False)
 lamp=a+t*(length-.42)+n*.25+Vector((0,0,top-.35))
 kit.beam('lantern-bracket',tuple(lamp-n*.22),tuple(lamp+Vector((0,0,.19))),.05,'iron')
 kit.box('lantern-glass',tuple(lamp),(.19,.17,.27),'stoneLight',False)
 for zz in (-.17,.17):kit.box('lantern-cap-'+str(zz),tuple(lamp+Vector((0,0,zz))),(.27,.23,.065),'iron')
 for dx in (-.11,.11):kit.box('lantern-bar-'+str(dx),tuple(lamp+t*dx),(.035,.20,.31),'iron')
 # One or two upper flower boxes; bottoms clear the full-height moving actor.
 windows=[o for o in c.objects if o.name.startswith('ro3-v68-') and '-front-window-' in o.name and o.name.endswith('-glass')]
 for j,o in enumerate(windows[::2]):
  pp=[inv@o.matrix_world@v.co for v in o.data.vertices];center=sum(pp,Vector())/len(pp);width=max(v.x for v in pp)-min(v.x for v in pp)
  base=min(v.z for v in pp)-.25;cy=max(v.y for v in pp)+.43;cx=center.x
  kit.box('flowerbox-'+str(j),(cx,cy,base+.06),(width+.20,.32,.20),'oak')
  kit.box('soil-'+str(j),(cx,cy,base+.172),(width+.11,.25,.025),'soil',False)
  for end in (-1,1):kit.box('box-band-'+str(j)+'-'+str(end),(cx+end*width*.33,cy+.165,base+.06),(.045,.018,.20),'iron',False)
  for leaf in range(7):
   xx=cx-width*.43+leaf*width*.86/6;yy=cy+r.uniform(-.065,.065);zz=base+.20
   kit.mesh('box-leaf-'+str(j)+'-'+str(leaf),[(xx-.12,yy,zz),(xx,yy+.08,zz+.12),(xx+.12,yy,zz),(xx,yy-.08,zz+.04)],[[0,1,2],[0,2,3]],'leafLight',False)
   if leaf%2==j%2:kit.box('box-flower-'+str(j)+'-'+str(leaf),(xx,yy,zz+.12),(.085,.075,.07),'flowers',False)
 records.append({'owner':c.name,'upperFlowerBoxes':len(windows[::2]),'lanterns':1,'drains':1,'weatheredBaseFaces':len(poly)})
# Ground stations planned against exact native footprints and protected routes.
props=json.loads((ROOT/'authoring/ro3-house-props-v69.json').read_text())['props'];placed=[]
for j,p in enumerate(props):
 c=bpy.data.collections[p['owner']];core=next(o for o in c.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls')))
 root=core.parent;inv=root.matrix_world.inverted();kit=Kit(c,root);kit.prefix='goods69-'+str(j)+'-'
 x,y=p['center'];ground=height(x,y);heights=[height(*q) for q in p['polygon']]
 if max(heights)-min(heights)>.035:continue
 # Build in a local prop frame, then fit into the house-owned model frame.
 before=set(c.objects);kind=p['kind'];z=0
 if kind=='barrel':
  segments=10;rr=.29;hh=.78
  ring=[(rr*math.cos(k*math.tau/segments),rr*math.sin(k*math.tau/segments),zz) for zz in (.02,hh) for k in range(segments)]
  kit.mesh('barrel',ring,[list(range(segments-1,-1,-1)),list(range(segments,segments*2))]+[[k,(k+1)%segments,(k+1)%segments+segments,k+segments] for k in range(segments)],'oak')
  for zz in (.13,.65):
   pts=[((rr+.009)*math.cos(k*math.tau/segments),(rr+.009)*math.sin(k*math.tau/segments),zz+dz) for dz in (-.035,.035) for k in range(segments)]
   kit.mesh('hoop-'+str(zz),pts,[[k,(k+1)%segments,(k+1)%segments+segments,k+segments] for k in range(segments)],'iron')
 elif kind=='crate':
  kit.box('crate',(0,0,.34),(.73,.57,.64),'oak')
  for xx in (-.31,.31):kit.box('crate-edge-'+str(xx),(xx,.297,.34),(.07,.035,.64),'timber')
  kit.beam('crate-brace',(-.30,.30,.06),(.30,.30,.61),.065,'timber')
  for z in (.16,.34,.52):kit.box('board-joint-'+str(z),(0,.292,z),(.62,.014,.022),'timber',False)
 else:
  kit.box('planter',(0,0,.28),(.73,.57,.52),'stoneLight')
  kit.box('planter-rim',(0,0,.55),(.80,.64,.09),'stone')
  kit.box('planter-soil',(0,0,.60),(.66,.51,.025),'soil',False)
  for k in range(9):
   xx=r.uniform(-.28,.28);yy=r.uniform(-.21,.21)
   kit.mesh('herb-'+str(k),[(xx-.12,yy,.61),(xx,yy+.10,.87),(xx+.12,yy,.61),(xx,yy-.10,.73)],[[0,1,2],[0,2,3]],'leafLight',False)
   if k%3==0:kit.box('petal-'+str(k),(xx,yy,.84),(.08,.08,.055),'flowers',False)
 collider=kit.box('collision',(0,0,.45),(.82,.68,.90),'oak',False);collider['role']='solid';collider['render_visible']=False
 t=Vector((*p['tangent'],0));n=Vector((*p['normal'],0))
 for o in set(c.objects)-before:
  for v in o.data.vertices:
   q=v.co.copy();v.co=inv@(Vector((x,y,ground+.012))+t*q.x+n*q.y+Vector((0,0,q.z)))
  o['house_life_v69_station']=j
  o['house_life_v69_ground']=ground
 placed.append({**p,'ground':ground,'collider':collider.name})
scene['ro3_house_life_version']=69;scene['ro3_house_life_review_json']=json.dumps({'buildings':records,'groundStations':placed,'plannedCount':len(props)})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Source69 house life:',len(records),'weathered houses,',len(placed),'ground stations; rebake both lighting passes')
