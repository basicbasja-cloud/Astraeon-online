"""Editable concept-led Hall and attached town wings on the saved city.

Keeps authored stairs, services, portals and placement roots. Existing Hall
meshes remain hidden references. This pass is repeatable, never a town rebuild.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('paved_city_version')==48
PREFIX='concept-v49-';owner=None;root=None;world_input=True
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for data in list(bpy.data.meshes):
 if data.name.startswith(PREFIX) and data.users==0:bpy.data.meshes.remove(data)
def mesh(name,vs,fs,mat,role='decorative',shadow=True,bevel=0):
 # Monumental civic scale is geometry in the authoring source, not a runtime
 # enlargement of sprites. Keep the public stair elevation and entrance axis.
 if owner.name=='guild-hall' and world_input:
  vs=[(54+(x-54)*1.8,21.35+(y-21.35)*1.12,.6075+(z-.6075)*2.0) for x,y,z in vs]
 if world_input and owner.get('concept_terrace_height'):
  vs=[(x,y,z+owner['concept_terrace_height']) for x,y,z in vs]
 inverse=root.matrix_world.inverted() if root and world_input else Matrix.Identity(4)
 data=bpy.data.meshes.new(PREFIX+name);data.from_pydata([inverse@Vector(v) for v in vs],[],fs)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=bevel,segments=2,profile=.5,affect='EDGES',clamp_overlap=True)
 bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(data);bm.free()
 data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
 o=bpy.data.objects.new(PREFIX+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow
 if root:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
 size=3
 for f in data.polygons:
  for li in f.loop_indices:
   p=data.vertices[data.loops[li].vertex_index].co;n=f.normal
   data.uv_layers.active.data[li].uv=(p.x/size,p.y/size) if abs(n.z)>.65 else (p.x/size,p.z/size) if abs(n.y)>abs(n.x) else (p.y/size,p.z/size)
 return o
def box(name,c,size,mat='civicIvory',role='decorative',shadow=True):
 x,y,z=c;a,b,h=[v/2 for v in size]
 bevel=min(.065,min(size)*.12) if mat in ('civicIvory','civicShadow','stone','stoneLight') and min(size)>.14 else 0
 return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow,bevel)
def beam(name,a,b,r,mat='civicIvory',sides=8):
 a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();w=v.cross(u).normalized()
 vs=[tuple(p+r*(math.cos(k*math.tau/sides)*u+math.sin(k*math.tau/sides)*w)) for p in (a,b) for k in range(sides)]
 return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[k,(k+1)%sides,(k+1)%sides+sides,k+sides] for k in range(sides)],mat)
def prism(name,poly,y0,y1,mat,role='decorative'):
 n=len(poly);vs=[(x,y,z) for y in (y0,y1) for x,z in poly]
 return mesh(name,vs,[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[k,(k+1)%n,(k+1)%n+n,k+n] for k in range(n)],mat,role)
def arch(name,x,y,bottom,width,spring,rise,thick=.18,depth=.28,mat='civicIvory'):
 # Individually dressed, curved voussoirs; true hole with a shaded reveal.
 for k in range(16):
  a,b=math.pi*k/16,math.pi*(k+1)/16
  poly=[(x-math.cos(t)*r,bottom+spring+math.sin(t)*h) for t,r,h in [(a,width/2,rise),(b,width/2,rise),(b,width/2+thick,rise+thick),(a,width/2+thick,rise+thick)]]
  prism(name+'-voussoir-'+str(k),poly,y-depth/2,y+depth/2,mat)
 for side in (-1,1):box(name+'-jamb-'+str(side),(x+side*(width/2+thick/2),y,bottom+spring/2),(thick,depth,spring),mat)
def lancet(name,x,y,z,w,h):
 # The window belongs to a real recessed bay, bounded by stone side piers.
 r=w/2;spring=h*.58;rise=h*.42
 poly=[(x-r,z),(x+r,z)]+[(x+math.cos(k*math.pi/12)*r,z+spring+math.sin(k*math.pi/12)*rise) for k in range(13)]
 prism(name+'-inset',poly,y-.42,y-.37,'civicGlass')
 arch(name,x,y,z,w,spring,rise,.14,.42)
 for side in (-1,1):beam(name+'-reveal-'+str(side),(x+side*r,y-.39,z),(x+side*r,y+.18,z),.07,'civicShadow')
 beam(name+'-mullion',(x,y-.12,z),(x,y-.12,z+h-.12),.045,'civicGold')
 beam(name+'-transom',(x-r,y-.10,z+spring*.65),(x+r,y-.10,z+spring*.65),.035,'civicIvory')
 # Subdivided glazing carries broad colored panes, no noisy texture decals.
 for side in (-1,1):box(name+'-pane-'+str(side),(x+side*w*.20,y-.34,z+h*.32),(w*.32,.035,h*.46),'civicGlassLight',shadow=False)
 box(name+'-sill',(x,y+.10,z-.12),(w+.42,.64,.20))
def roof(name,x,y0,y1,w,eave,peak,mat='civicSlate',hip=.0):
 mesh(name+'-gable',[(x-w/2,y1-.05,eave),(x+w/2,y1-.05,eave),(x,y1-.05,peak)],[[0,1,2]],'civicIvory' if mat=='civicSlate' else 'plaster')
 for side in (-1,1):
  xx=x+side*w/2
  mesh(name+'-slope-'+str(side),[(xx,y0,eave),(xx,y1,eave),(x,y1-hip,peak),(x,y0+hip,peak)],[[0,1,2,3]],mat,'overhead')
  beam(name+'-eave-'+str(side),(xx,y0,eave),(xx,y1,eave),.10,'civicShadow' if mat=='civicSlate' else 'timber')
  beam(name+'-verge-'+str(side),(xx,y1+.06,eave),(x,y1-hip+.06,peak),.085,'civicGold' if mat=='civicSlate' else 'timber')
 beam(name+'-ridge',(x,y0+hip,peak),(x,y1-hip,peak),.09,'civicGold' if mat=='civicSlate' else 'timber')
def tower(name,x,y,r,z,h):
 # Octagonal drums avoid the rectangular toy tower family.
 for suffix,zz,hh,rr,mat in [('base',.6,.55,r+.24,'civicShadow'),('shaft',1.15,z-1.15,r,'civicIvory'),('belt',z-.42,.20,r+.16,'civicGold'),('crown',z-.15,.30,r+.24,'civicIvory')]:
  vs=[(x+rr*math.cos(k*math.tau/8+math.pi/8),y+rr*math.sin(k*math.tau/8+math.pi/8),q) for q in (zz,zz+hh) for k in range(8)]
  mesh(name+'-'+suffix,vs,[list(range(7,-1,-1)),list(range(8,16))]+[[k,(k+1)%8,(k+1)%8+8,k+8] for k in range(8)],mat,'solid' if suffix=='shaft' else 'decorative')
 if r>.65:
  for zz in (2.0,z-2.6):
   yy=y+r*.93+.05
   box(name+'-shadow-bay-'+str(zz),(x,yy,zz+.9),(.75,.12,1.92),'civicShadow',shadow=False)
   lancet(name+'-window-'+str(zz),x,yy+.42,zz,.60,1.75)
 vs=[(x+(r+.35)*math.cos(k*math.tau/8+math.pi/8),y+(r+.35)*math.sin(k*math.tau/8+math.pi/8),z+.15) for k in range(8)]+[(x,y,z+h)]
 mesh(name+'-spire',vs,[[k,(k+1)%8,8] for k in range(8)],'civicSlate','overhead')
 for k in range(8):beam(name+'-hip-'+str(k),vs[k],vs[-1],.035,'civicGold')
 beam(name+'-finial',(x,y,z+h),(x,y,z+h+.75),.075,'civicGold')
 beam(name+'-star-cross',(x-.20,y,z+h+.55),(x+.20,y,z+h+.55),.035,'civicGold')

owner=bpy.data.collections['guild-hall'];root=bpy.data.objects['guild-hall-placement'];world_input=True
for o in owner.objects:
 if o.type=='MESH' and not o.name.startswith(PREFIX) and not o.name.startswith('civic-processional-step-'):
  o['render_visible']=False;o['shadow']=False;o['role']='decorative'
# Rebuild front as real openings, rather than placing glass on a filled wall.
x0,x1,y0,y1=49.6,58.4,10.6,21.35
box('nave-back',(54,y0+.20,4.95),(8.8,.4,8.7),role='solid')
for side in (-1,1):box('nave-side-'+str(side),(54+side*4.2,16,4.95),(.4,10.8,8.7),role='solid')
for a,b in [(49.6,52.25),(55.75,58.4)]:box('portal-wall-'+str(a),((a+b)/2,y1,2.75),(b-a,.50,4.3),role='solid')
box('portal-overwall',(54,y1,4.77),(3.5,.5,.45))
arch('portal',54,y1+.14,.61,3.5,2.65,1.25,.27,.70)
# Curved arch spandrels close the upper wall, while the lower doorway is open.
for k in range(16):
 a,b=k*math.pi/16,(k+1)*math.pi/16
 poly=[(54-1.75*math.cos(a),3.26+1.25*math.sin(a)),(54-1.75*math.cos(b),3.26+1.25*math.sin(b)),(54-1.75*math.cos(b),4.6),(54-1.75*math.cos(a),4.6)]
 prism('portal-spandrel-'+str(k),poly,y1-.25,y1+.25,'civicIvory')
box('door-recess',(54,20.82,2.05),(3.2,.1,2.9),'civicDoor')
for side in (-1,1):
 box('door-leaf-'+str(side),(54+side*.78,20.90,1.99),(1.48,.08,2.70),'civicDoor')
 for z in (1.0,2.8):box('door-brace-'+str((side,z)),(54+side*.78,20.96,z),(1.42,.06,.12),'civicGold',shadow=False)
 box('door-handle-'+str(side),(54+side*.25,21.01,1.85),(.09,.09,.37),'civicGold')
# Rose opening in an upper stone bay. Square-to-circle spandrels are volume.
for a,b in [(49.6,52.35),(55.65,58.4)]:box('rose-wall-'+str(a),((a+b)/2,y1,7.02),(b-a,.5,4.05))
box('rose-base-band',(54,y1,5.10),(3.3,.5,.32));box('rose-top-band',(54,y1,8.90),(3.3,.5,.40))
cx,cz,r=54,7.05,1.39
for k in range(32):
 angles=[k*math.tau/32,(k+1)*math.tau/32];poly=[]
 for a in angles:poly.append((cx+r*math.cos(a),cz+r*math.sin(a)))
 for a in reversed(angles):
  q=min(1.65/max(abs(math.cos(a)),.001),1.85/max(abs(math.sin(a)),.001));poly.append((cx+q*math.cos(a),cz+q*math.sin(a)))
 prism('rose-spandrel-'+str(k),poly,21.10,21.60,'civicIvory')
 p=(cx+r*math.cos(angles[0]),21.64,cz+r*math.sin(angles[0]));q=(cx+r*math.cos(angles[1]),21.64,cz+r*math.sin(angles[1]));beam('rose-rim-'+str(k),p,q,.10)
 poly=[(cx+math.cos(k*math.tau/32)*r,cz+math.sin(k*math.tau/32)*r) for k in range(32)]
prism('rose-glass',poly,20.92,20.96,'civicGlass')
for k in range(12):
 a=k*math.tau/12;beam('rose-tracery-'+str(k),(cx,21.03,cz),(cx+math.cos(a)*r*.94,21.03,cz+math.sin(a)*r*.94),.06,'civicGold')
for side in (-1,1):lancet('nave-high-bay-'+str(side),54+side*2.88,22.06,5.55,1.06,2.95)
for z in (5.07,9.12):box('nave-carved-belt-'+str(z),(54,21.77,z),(8.95,.48,.23),'civicShadow')
for side in (-1,1):
 x=54+side*4.2
 box('front-buttress-'+str(side),(x,21.70,4.2),(.64,1.2,7.2))
 for z in (1.0,4.8,7.55):box('buttress-course-'+str((side,z)),(x,21.73,z),(.85,1.32,.22),'civicShadow')
 tower('front-pinnacle-'+str(side),x,21.78,.34,9.2,1.6)
 # Deep lower aisles carry recessed windows; roof is a distinct smaller mass.
 xx=54+side*6.35;w=3.35
 box('aisle-back-'+str(side),(xx,13,3.25),(w,.40,5.3),'civicShadow','solid')
 box('aisle-outer-'+str(side),(xx+side*w/2,17.6,3.25),(.40,9.6,5.3),'civicShadow','solid')
 for dx in (-1.30,0,1.30):box('aisle-front-pier-'+str((side,dx)),(xx+dx,22.20,3.25),(.38,.60,5.3))
 box('aisle-front-base-'+str(side),(xx,22.20,1.01),(w,.60,.8))
 box('aisle-front-crown-'+str(side),(xx,22.20,5.55),(w,.60,.7))
 for j,dx in enumerate((-.65,.65)):lancet('aisle-front-'+str((side,j)),xx+dx,22.50,1.45,.91,3.72)
 roof('aisle-roof-'+str(side),xx,12.6,22.85,4.1,6.15,8.45)
 for j,yy in enumerate((12.65,15.75,18.85)):
  box('side-buttress-'+str((side,j)),(xx+side*1.8,yy,2.8),(.8,.62,4.4))
  a,b=xx+side*1.8,54+side*4.35
  for k in range(8):
   t0,t1=k/8,(k+1)/8;points=[]
   for t in (t0,t1):points.append((a+(b-a)*t,5.0+3.85*math.sin(t*math.pi/2)))
   points.extend((px,pz+.38) for px,pz in reversed(points[:]))
   prism('flying-arch-'+str((side,j,k)),points,yy-.24,yy+.24,'civicIvory')
roof('nave-roof',54,10.0,22.15,9.4,9.55,12.75)
lancet('nave-gable-lancet',54,22.78,10.08,.90,1.65)
for side in (-1,1):beam('gable-tracery-'+str(side),(54+side*3.68,22.23,10.02),(54,22.23,12.31),.055,'civicIvory')
# Three unequal crowned towers create the landmark hierarchy in the concept.
tower('west-bell',46.9,19.9,1.10,10.7,4.5)
tower('east-bell',61.0,18.7,.93,9.7,3.5)
tower('rear-lantern',54,13.7,.94,13.45,3.65)
# The broad drum and dome belong to the same scaled source geometry as the
# nave. Retain older parts as hidden references rather than rescaling them on
# every run. The open entry and lower aisles stay beneath this major crown.
for o in owner.objects:
 if o.name.startswith(PREFIX+'rear-lantern'):o['render_visible']=False;o['shadow']=False;o['role']='decorative'
 if o.name.startswith(('quality-v46-hall-dome-','quality-v46-dome-rib-')):
  o['render_visible']=False;o['shadow']=False
profile=[(12.75,1.55),(13.0,2.05),(14.7,2.05),(14.94,2.22),(15.28,2.34),(15.95,2.25),(16.7,1.85),(17.4,1.20),(17.75,.73),(18.6,.73),(18.80,.98),(19.15,.70),(19.75,.10)]
cx,cy=54,14.5
for k,((z0,r0),(z1,r1)) in enumerate(zip(profile,profile[1:])):
 vs=[(cx+r*math.cos(i*math.tau/8+math.pi/8),cy+r*math.sin(i*math.tau/8+math.pi/8),z) for z,r in [(z0,r0),(z1,r1)] for i in range(8)]
 mesh('crown-drum-'+str(k),vs,[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)],'civicIvory' if k==1 else 'civicGold' if k in (0,2,3,8,10) else 'civicSlate','overhead')
 if k not in (0,1,2,3,8,10):
  for i in range(8):beam('crown-rib-'+str((k,i)),vs[i],vs[i+8],.045,'civicGold')
for side in (-1,1):lancet('crown-drum-lancet-'+str(side),cx+side*.66,cy+2.39,13.15,.65,1.30)
beam('crown-finial',(54,cy,19.75),(54,cy,20.55),.055,'civicGold')
# Open Gothic canopy: a high arch, deep vault, thin steep roof and side shafts.
for side in (-1,1):
 x=54+side*2.35
 box('canopy-pier-'+str(side),(x,23.13,2.22),(.42,.60,3.22))
 box('canopy-base-'+str(side),(x,23.13,.90),(.72,.85,.58),'civicShadow')
 tower('canopy-pinnacle-'+str(side),x,23.15,.20,4.6,1.1)
arch('canopy-front',54,23.15,.61,4.3,2.55,1.12,.28,.62)
arch('canopy-inner',54,21.90,.61,4.3,2.55,1.12,.22,.34)
roof('canopy-roof',54,21.2,23.65,5.45,4.55,5.72)
# Keep the canopy tympanum open: roof()'s generic solid gable is hidden.
bpy.data.objects[PREFIX+'canopy-roof-gable']['render_visible']=False
for side in (-1,1):
 x=54+side*3.2
 poly=[(x-.34,3.3),(x+.34,3.3),(x+.34,5.8),(x-.34,5.8)]
 prism('guild-banner-'+str(side),poly,21.80,21.84,'clothBlue')
 for k in range(8):
  a=k*math.tau/8;beam('guild-star-'+str((side,k)),(x,21.9,4.9),(x+math.cos(a)*(.26 if k%2==0 else .13),21.9,4.9+math.sin(a)*(.44 if k%2==0 else .22)),.024,'civicGold')

# Ground the aisle and rear volumes at terrain level: their raised stone
# walls previously ended above the paving outside the central stair landing.
for side in (-1,1):box('aisle-foundation-'+str(side),(54+side*6.35,17.45,.31),(3.62,10.0,.62),'civicShadow','solid')
box('nave-foundation',(54,15.6,.31),(8.8,10.0,.62),'civicShadow','solid')

# The Hall now occupies a genuinely larger civic lot. Preserve each adjoining
# house as an editable root and move the entire family once, with a baseline
# saved in the source so this pass remains repeatable.
for name,dx,dy in [('frontage-garden-home',-4,4),('frontage-scribe',4,3)]:
 placement=bpy.data.objects[name+'-placement']
 if 'concept_v49_original_location' not in placement:placement['concept_v49_original_location']=list(placement.location)
 before=list(placement['concept_v49_original_location']);placement.location=(before[0]+dx,before[1]+dy,before[2]+scene.get('civic_terrace_height_v49',0))
bpy.context.view_layer.update()

# Attached rear wings and gabled dormers fill gaps within each existing lot.
# Ground additions are actual solids; A* derives their contacts from the source.
world_input=False
for i,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
 owner=c;root=bpy.data.objects[c.name+'-placement'];inv=root.matrix_world.inverted();o=next(o for o in c.objects if o.name.endswith('-walls'));vs=[inv@o.matrix_world@v.co for v in o.data.vertices]
 x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);h=max(v.z for v in vs);x,y=(x0+x1)/2,(y0+y1)/2;w=x1-x0
 # This short wing attaches behind the street facade, away from door approach.
 side=-1 if i%2 else 1;xx=x+side*w*.26;yy=y0-.68;ww=w*.72;hh=h*.68
 # Constrained lots use dormers and jetties; a rear wing would cross their
 # neighbour or street. Other lots have an actual source-owned setback.
 if c.name not in ('frontage-cobbler','frontage-joiner','frontage-willow-east','frontage-market-arcade','frontage-copper-shop'):
  box(c.name+'-attached-wing',(xx,yy,hh/2+.20),(ww,2.15,hh),'plaster','solid')
  roof(c.name+'-wing-roof',xx,yy-1.40,yy+1.40,ww+.70,hh+.37,hh+1.8,'terracotta' if i%3 else 'slate',.35)
  for dx in (-ww*.39,ww*.39):box(c.name+'-wing-frame-'+str(dx),(xx+dx,yy+1.1,hh*.6),(.14,.16,hh*.78),'timber')
 # Dormer breaks the main roof, with a recessed front and real cheeks.
 dx=x+(-.18 if i%2 else .19)*w;roof_z=h+.72;dy=y1-.65
 box(c.name+'-dormer',(dx,dy,roof_z+.40),(1.15,1.6,1.06),'plaster','overhead')
 box(c.name+'-dormer-inset',(dx,dy+.83,roof_z+.42),(.72,.10,.70),'timber',shadow=False)
 box(c.name+'-dormer-glass',(dx,dy+.89,roof_z+.42),(.52,.04,.54),'glass',shadow=False)
 roof(c.name+'-dormer-roof',dx,dy-.92,dy+1.02,1.5,roof_z+.97,roof_z+1.65,'slate' if i%3==0 else 'terracotta')
 box(c.name+'-dormer-sill',(dx,dy+.96,roof_z+.05),(1.1,.34,.14),'oak')
 # Forecourt shop canopy has angled supports and coherent shop/home scale.
 if i in (0,1,2,4,6,7):
  mesh(c.name+'-shop-awning',[(x-w*.38,y1+.39,2.55),(x+w*.38,y1+.39,2.55),(x+w*.38,y1+1.15,2.05),(x-w*.38,y1+1.15,2.05)],[[0,1,2,3]],'clothOchre' if i%2 else 'clothRose','overhead')
  for side in (-1,1):beam(c.name+'-awning-brace-'+str(side),(x+side*w*.37,y1+.31,1.65),(x+side*w*.37,y1+1.05,2.04),.06,'timber')
# Older service buildings and perimeter homes need the same construction depth.
for i,c in enumerate(sorted([c for c in bpy.data.collections if c.get('family') in ('inn','workshop','residential','market') and not c.name.startswith('frontage-')],key=lambda c:c.name)):
 wall=next((o for o in c.objects if o.type=='MESH' and o.name.endswith('-walls') and o.get('render_visible',True)),None)
 if not wall:continue
 owner=c;root=bpy.data.objects.get(c.name+'-placement')
 if not root:continue
 inv=root.matrix_world.inverted();vs=[inv@wall.matrix_world@v.co for v in wall.data.vertices]
 x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);h=max(v.z for v in vs);base=min(v.z for v in vs);x,y=(x0+x1)/2,(y0+y1)/2;w=x1-x0;d=y1-y0
 # Stone undercroft and corner quoins ground timber/plaster upper floors.
 box(c.name+'-stone-sock',(x,y1+.07,base+.42),(w+.06,.20,.84),'stone')
 for side in (-1,1):
  xx=x+side*(w/2-.1)
  for j in range(max(3,int(h/.56))):
   z=base+.35+j*.56
   box(c.name+'-quoin-'+str((side,j)),(xx,y1+.13,z),(.34 if j%2 else .51,.26,.39),'stoneLight',shadow=False)
  beam(c.name+'-corner-brace-'+str(side),(xx,y1+.25,h*.54),(xx-side*w*.20,y1+.25,h*.88),.07,'timber')
 # Varied upper-storey window bays, with actual projecting framing and hoods.
 count=3 if w>7 else 2
 for j in range(count):
  xx=x+(j-(count-1)/2)*w*.31;z=base+(h-base)*.69;ww=min(1.05,w*.18);hh=min(1.42,(h-base)*.33)
  box(c.name+'-window-shade-'+str(j),(xx,y1+.18,z),(ww+.30,.20,hh+.28),'timber',shadow=False)
  box(c.name+'-window-pane-'+str(j),(xx,y1+.305,z),(ww,.05,hh),'glass',shadow=False)
  for side in (-1,1):
   box(c.name+'-window-jamb-'+str((j,side)),(xx+side*(ww/2+.075),y1+.40,z),(.13,.22,hh+.3),'oak')
   box(c.name+'-window-shutter-'+str((j,side)),(xx+side*(ww/2+.30),y1+.23,z),(.28,.19,hh+.11),'oak')
  box(c.name+'-window-mullion-'+str(j),(xx,y1+.38,z),(.06,.08,hh),'stoneLight',shadow=False)
  box(c.name+'-window-sill-'+str(j),(xx,y1+.38,z-hh/2-.12),(ww+.45,.48,.17),'stoneLight')
  box(c.name+'-window-hood-'+str(j),(xx,y1+.30,z+hh/2+.18),(ww+.48,.55,.17),'timber')
 if c['family']=='inn':
  # A larger projecting gable and entrance porch distinguish the tavern.
  roof(c.name+'-cross-gable',x+w*.23,y1-.9,y1+.75,w*.62,h-.55,h+1.8,'terracotta')
  for j in range(5):box(c.name+'-balcony-bracket-'+str(j),(x-w*.35+j*w*.175,y1+.4,h*.47),(.12,.72,.23),'timber')
  box(c.name+'-balcony-ledger',(x,y1+.42,h*.48),(w*.77,.90,.19),'oak')

# Market stalls carry goods, aprons and supports rather than empty brown cubes.
owner=bpy.data.collections['east-inn'];root=bpy.data.objects['east-inn-placement'];world_input=True
box('inn-east-wing',(20.2,38.0,2.52),(4.8,5.7,4.44),'plaster','solid')
box('inn-east-undercroft',(20.2,38.0,.66),(4.94,5.8,.72),'stone')
roof('inn-east-wing-roof',20.2,34.8,41.2,5.5,4.85,7.05,'terracotta')
for xx in (18.1,20.2,22.3):box('inn-wing-framing-'+str(xx),(xx,40.92,2.77),(.19,.24,3.8),'timber')
for z in (1.13,2.55,4.63):box('inn-wing-belt-'+str(z),(20.2,40.95,z),(4.9,.25,.17),'timber')
for j,xx in enumerate((19.0,21.45)):
 box('inn-wing-window-dark-'+str(j),(xx,41.00,3.44),(1.30,.12,1.42),'timber',shadow=False)
 box('inn-wing-window-glass-'+str(j),(xx,41.08,3.44),(1.02,.04,1.20),'glass',shadow=False)
 box('inn-wing-window-mullion-'+str(j),(xx,41.14,3.44),(.08,.07,1.25),'oak')
 box('inn-wing-window-sill-'+str(j),(xx,41.11,2.73),(1.48,.4,.15),'stoneLight')
 for side in (-1,1):box('inn-wing-shutter-'+str((j,side)),(xx+side*.76,41.04,3.44),(.27,.17,1.33),'oak')
beam('inn-wing-gable-brace-left',(18.0,41.27,4.95),(20.2,41.27,6.80),.08,'timber')
beam('inn-wing-gable-brace-right',(22.4,41.27,4.95),(20.2,41.27,6.80),.08,'timber')
beam('inn-wing-gable-post',(20.2,41.27,4.9),(20.2,41.27,6.86),.10,'timber')
owner=bpy.data.collections['moon-shrine'];root=bpy.data.objects['moon-shrine-placement'];world_input=True
for side in (-1,1):
 x=86+side*3.20
 tower('luna-apse-'+str(side),x,21.0,.92,5.20,3.1)
 roof('luna-connecting-roof-'+str(side),86+side*1.9,19.2,23.5,2.5,4.85,6.90)
 box('luna-front-pier-'+str(side),(86+side*1.65,23.50,3.18),(.31,.70,5.30))
 tower('luna-front-pinnacle-'+str(side),86+side*1.65,23.60,.20,6.1,1.65)
 # Small paired lamps emphasize the actual sanctuary approach.
 box('luna-lamp-bracket-'+str(side),(86+side*1.18,23.86,2.3),(.22,.30,.14),'civicGold')
 box('luna-lamp-glass-'+str(side),(86+side*1.18,23.86,2.55),(.18,.20,.34),'civicGlassLight',shadow=False)
arch('luna-portal',86,23.68,.43,1.34,1.85,.82,.20,.46,'civicIvory')
arch('luna-portal-gold',86,23.80,.43,1.30,1.82,.80,.065,.07,'civicGold')
owner=bpy.data.collections['artisan-workshop'];root=bpy.data.objects['artisan-workshop-placement']
# Covered working yard and stepped masonry chimney give the forge its own family.
roof('forge-yard-roof',22.10,67.0,71.95,3.65,2.85,4.25,'terracotta')
for yy in (67.6,71.35):
 box('forge-yard-post-'+str(yy),(23.56,yy,1.4),(.22,.22,2.8),'timber','solid')
 box('forge-yard-foot-'+str(yy),(23.56,yy,.25),(.43,.43,.5),'stone')
 beam('forge-yard-brace-'+str(yy),(23.56,yy,2.0),(22.95,yy,2.80),.075,'timber')
box('forge-master-stack',(17.4,68.3,5.75),(1.03,1.15,2.70),'stone')
for z in (4.80,6.75,7.18):box('forge-stack-course-'+str(z),(17.4,68.3,z),(1.27,1.38,.17),'stoneLight')
box('forge-stack-mouth',(17.4,68.3,7.29),(.79,.92,.04),'iron',shadow=False)
for side in (-1,1):box('forge-stack-cap-post-'+str(side),(17.4+side*.43,68.3,7.46),(.12,.92,.36),'stone')
box('forge-stack-cap',(17.4,68.3,7.72),(1.38,1.43,.18),'stoneLight')
world_input=False
for i,c in enumerate(sorted([c for c in bpy.data.collections if c.name in ('market-textiles','market-spices','market-supplies')],key=lambda c:c.name)):
 owner=c;root=bpy.data.objects.get(c.name+'-placement');world_input=False
 counter=next(o for o in c.objects if o.name.endswith('-counter'));inv=root.matrix_world.inverted();vs=[inv@counter.matrix_world@v.co for v in counter.data.vertices]
 x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);z=max(v.z for v in vs);x,y=(x0+x1)/2,(y0+y1)/2;w=x1-x0
 box(c.name+'-front-apron',(x,y1+.055,z*.57),(w,.10,z*.54),'clothBlue' if i==0 else 'clothOchre')
 for j in range(5):
  xx=x-w*.38+j*w*.19
  box(c.name+'-goods-tray-'+str(j),(xx,y,z+.08),(w*.16,.48,.14),'oak')
  for k in range(3):
   if c.name=='market-textiles':box(c.name+'-folded-cloth-'+str((j,k)),(xx,y-.14+k*.13,z+.18),(.29,.14,.14),['clothBlue','clothRose','clothOchre'][(j+k)%3],shadow=False)
   else:
    beam(c.name+'-jar-'+str((j,k)),(xx+.10*(k-1),y+.08*(k%2),z+.15),(xx+.10*(k-1),y+.08*(k%2),z+.39),.10,'terracotta' if i%2 else 'teal')
 for side in (-1,1):beam(c.name+'-canopy-support-'+str(side),(x+side*w*.45,y1-.25,z+.5),(x+side*w*.45,y1+.25,z+1.25),.05,'oak')
scene['concept_architecture_version']=49;scene['layout_id']='wayfarer-concept-civic-town-v49'
scene['concept_hall_scale']='width 1.8; depth 1.12; height 2.0 about raised entrance datum'
# Stronger sun and cooler shaded volume, keeping warm plaster and quiet stone.
scene['ambient']=.57;scene['sun_strength']=.48
scene['sun_cast_x']=.62;scene['sun_cast_y']=-.40
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved concept Hall with open archivolts, rose recess, stone bays, flying buttresses, unequal towers; twelve attached town wings/dormers')
