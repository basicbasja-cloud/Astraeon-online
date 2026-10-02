"""Refine the saved spatial town: architectural silhouette, thresholds, UVs.
Run against authoring/wayfarer-spatial.blend. Does not recreate town placement.
"""
import bpy,bmesh,json,math,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'))
kit['materials'].update({m.name:m for m in bpy.data.materials})
def box(c,id,p,size,mat,parent=None,role='decorative'):
 o=kit['box'](c,id,p,size,mat,role,True)
 if parent:o.parent=parent
 return o
def mesh(c,id,vs,fs,mat,parent=None,role='decorative'):
 o=kit['mesh'](c,id,vs,fs,mat,role,True)
 if parent:o.parent=parent
 return o
def prism(c,id,poly,z,h,mat,parent=None,role='decorative'):
 n=len(poly);return mesh(c,id,[(x,y,t) for t in (z,z+h) for x,y in poly],[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],mat,parent,role)
def beam(c,id,a,b,w,mat,parent):
 a,b=Vector(a),Vector(b);d=b-a;o=box(c,id,(0,0,0),(w,w,d.length),mat,parent);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def circle(x,y,r,n=16):return [(x+math.cos(i*math.tau/n)*r,y+math.sin(i*math.tau/n)*r) for i in range(n)]
def star(c,id,p,tangent,size,mat,parent):
 p,t=Vector(p),Vector(tangent).normalized();up=Vector((0,0,1));pts=[]
 for j in range(16):
  a=j*math.tau/16;r=size*(1 if j%2==0 else .30);pts.append(tuple(p+t*math.cos(a)*r+up*math.sin(a)*r))
 return mesh(c,id,[tuple(p)]+pts,[[0,j+1,(j+1)%16+1] for j in range(16)],mat,parent)
def arch(c,id,center,tangent,width,z,mat,parent):
 p,t=Vector(center),Vector(tangent).normalized();thickness=.10
 for j in range(12):
  a=j*math.pi/12;b=(j+1)*math.pi/12
  pts=[tuple(p+t*(math.cos(k)*r)+Vector((0,0,z+math.sin(k)*r))) for r,k in [(width,a),(width,b),(width+thickness,b),(width+thickness,a)]]
  mesh(c,id+f'-voussoir-{j}',pts,[[0,1,2,3]],mat,parent)

# Idempotent authored refinement nodes can be adjusted in Blender afterwards.
for o in list(bpy.data.objects):
 if o.get('golden_refinement'):bpy.data.objects.remove(o,do_unlink=True)
existing={o.name for o in bpy.data.objects}
terrain=bpy.data.collections['court-terrain'];hall=bpy.data.collections['guild-hall'];root=bpy.data.objects['guild-hall-placement'];root.location.z=.45
body=bpy.data.objects['guild-hall-walls'];poly=[tuple(v.co[:2]) for v in body.data.vertices[:4]];a,b=Vector(poly[2]),Vector(poly[3]);t=(b-a).normalized();n=Vector((t.y,-t.x));center=a.lerp(b,.63)
# A centered processional portal, blue gable and astronomical rose window.
portal=[tuple(center-t*.85),tuple(center+t*.85),tuple(center+t*.85+n*.58),tuple(center-t*.85+n*.58)]
prism(hall,'civic-portal-massing',portal,0,5.9,'cream',root,'solid')
vs=[(x,y,5.9) for x,y in portal]+[tuple(Vector((*center,0))+Vector((0,0,7.6))),tuple(Vector((*center,0))+Vector((*n,0))*.58+Vector((0,0,7.6)))]
mesh(hall,'civic-portal-roof',vs,[[0,3,5,4],[1,4,5,2]],'slate',root,'overhead');mesh(hall,'civic-portal-gable',vs,[[3,2,5]],'cream',root)
front=center+n*.61;arch(hall,'civic-door-arch',(*front,0),(*t,0),.57,2.0,'gold',root)
for j,side in enumerate([-1,1]):
 p=front+t*side*.75;beam(hall,f'civic-entry-column-{j}',(*p,.2),(*p,3.8),.18,'stoneLight',root)
star(hall,'civic-rose-star',(*front,4.8),(*t,0),.42,'gold',root)
# The civic entry and lantern are visible geometry on the gameplay-facing wall.
prism(hall,'civic-entry-door',[tuple(front-t*.47),tuple(front+t*.47),tuple(front+t*.47+n*.035),tuple(front-t*.47+n*.035)],.18,2.05,'timber',root)
beam(hall,'civic-door-center',(*front,.22),(*front,2.25),.055,'gold',root)
lantern=Vector((sum(p[0] for p in poly)/4,sum(p[1] for p in poly)/4))
prism(hall,'civic-lantern-drum',circle(lantern.x,lantern.y,1.0,8),6.8,2.4,'cream',root)
for j in range(8):
 phi=j*math.tau/8+.2;q=lantern+Vector((math.cos(phi),math.sin(phi)))*1.02;tan=Vector((-math.sin(phi),math.cos(phi)))
 pts=[tuple(q-tan*.22)+(7.25,),tuple(q+tan*.22)+(7.25,),tuple(q+tan*.22)+(8.35,),tuple(q)+(8.65,),tuple(q-tan*.22)+(8.35,)]
 mesh(hall,f'civic-lantern-window-{j}',pts,[[0,1,2,3,4]],'glass',root)
 beam(hall,f'civic-lantern-mullion-{j}',(*q,7.25),(*q,8.55),.045,'gold',root)
lantern_ring=circle(lantern.x,lantern.y,1.25,8)
mesh(hall,'civic-lantern-blue-crown',[(x,y,9.0) for x,y in lantern_ring]+[(lantern.x,lantern.y,11.0)],[[j,(j+1)%8,8] for j in range(8)],'slate',root,'overhead')
for j,(x,y) in enumerate(lantern_ring):beam(hall,f'civic-lantern-gold-rib-{j}',(x,y,9.03),(lantern.x,lantern.y,11.03),.05,'gold',root)
beam(hall,'civic-lantern-finial',(lantern.x,lantern.y,11),(lantern.x,lantern.y,11.8),.065,'gold',root)
for j in range(4):
 p=a.lerp(b,(j+.5)/4)+n*.055;arch(hall,f'civic-upper-window-{j}',(*p,0),(*t,0),.24,4.15,'stoneLight',root)
for j in range(2):
 tower=bpy.data.objects[f'guild-hall-tower-{j}'];old=[tuple(v.co[:2]) for v in tower.data.vertices[:4]]
 for suffix in ['', '-ridge']:
  o=bpy.data.objects.get(f'guild-hall-tower-roof-{j}'+suffix)
  if o:bpy.data.objects.remove(o,do_unlink=True)
 x=sum(p[0] for p in old)/4;y=sum(p[1] for p in old)/4
 mesh(hall,f'civic-tower-spire-{j}',[(px,py,7) for px,py in old]+[(x,y,10.0+j*.25)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'slate',root,'overhead')
 beam(hall,f'civic-spire-finial-{j}',(x,y,9.95+j*.25),(x,y,10.6+j*.25),.075,'gold',root)

# Civic heraldry, visible rose tracery and articulated portal trim.
rose_center=Vector((*front,4.8))+Vector((*n,0))*.02;up=Vector((0,0,1));horizontal=Vector((*t,0))
mesh(hall,'civic-rose-glass',[tuple(rose_center)]+[tuple(rose_center+horizontal*math.cos(j*math.tau/16)*.5+up*math.sin(j*math.tau/16)*.5) for j in range(16)],[[0,j+1,(j+1)%16+1] for j in range(16)],'glass',root)
star(hall,'civic-rose-tracery',tuple(rose_center+Vector((*n,0))*.02),(*t,0),.46,'gold',root)
for j,f in enumerate([.14,.86]):
 q=a.lerp(b,f)+n*.085;tan=(b-a).normalized();pts=[tuple(q-tan*.29)+(2.7,),tuple(q+tan*.29)+(2.7,),tuple(q+tan*.29)+(4.4,),tuple(q-tan*.29)+(4.4,)]
 mesh(hall,f'civic-processional-banner-{j}',pts,[[0,1,2,3]],'clothBlue',root)
 star(hall,f'civic-banner-compass-{j}',tuple(Vector((*q,3.65))+Vector((*n,0))*.025),(*tan,0),.21,'gold',root)

# The public terrace is raised, with steps and a separate authored navigation ramp.
terrace=bpy.data.objects['civic-terrace'];terrace.data.clear_geometry();pts=[(16.7,13.5),(25.7,13.5),(25.7,16),(16.7,16)]
terrace.data.from_pydata([(x,y,.45) for x,y in pts],[],[[0,1,2,3]])
for name in ['guild-hall-forecourt']:
 for v in bpy.data.objects[name].data.vertices:v.co.z=.005
for j in range(4):box(hall,f'civic-processional-step-{j}',(21.8,16.85-j*.23,.055*(j+1)),(4,.26,.11*(j+1)),'cream')
nav=mesh(terrain,'civic-stair-navigation',[(19.8,17.0,.018),(23.8,17.0,.018),(23.8,16.0,.45),(19.8,16.0,.45)],[[0,1,2,3]],'paving');nav['surface_role']='forecourt';nav['walkable']=True;nav['render_visible']=False
prism(hall,'civic-terrace-retaining',pts,0,.45,'cream')
for j,(x,w) in enumerate([(18.25,3.1),(24.75,1.9)]):box(hall,f'civic-terrace-front-edge-{j}',(x,16,.225),(w,.10,.45),'cream',role='solid')
for j,x in enumerate([16.7,25.7]):box(hall,f'civic-terrace-side-edge-{j}',(x,14.75,.225),(.10,2.5,.45),'cream',role='solid')

# Shrine stair contact profile is authored beside the visual treads.
nav=mesh(terrain,'shrine-stair-navigation',[(29.9,13.05,.018),(31.5,13.05,.018),(31.5,12.12,.42),(29.9,12.12,.42)],[[0,1,2,3]],'paving');nav['surface_role']='forecourt';nav['walkable']=True;nav['render_visible']=False
landing=mesh(terrain,'shrine-landing-navigation',[(29.9,12.12,.42),(31.5,12.12,.42),(31.5,11.65,.42),(29.9,11.65,.42)],[[0,1,2,3]],'paving');landing['surface_role']='forecourt';landing['walkable']=True;landing['render_visible']=False

# Larger orienting fountain, original celestial compass sculpture.
c=bpy.data.collections['astral-fountain'];p=bpy.data.objects['astral-fountain-placement']
for o in list(c.objects):
 if o.type=='MESH':bpy.data.objects.remove(o,do_unlink=True)
prism(c,'fountain-step',circle(0,0,1.35),0,.18,'cream',p,'solid')
prism(c,'fountain-basin',circle(0,0,1.23),.18,.26,'stoneLight',p,'solid')
prism(c,'fountain-water',circle(0,0,1.08,24),.45,.018,'water',p)
prism(c,'fountain-central-shaft',circle(0,0,.17,8),.45,1.5,'cream',p)
prism(c,'fountain-upper-bowl',circle(0,0,.42,16),1.45,.2,'stoneLight',p)
star(c,'fountain-celestial-star',(0,0,2.25),(1,0,0),.52,'gold',p)
for j,side in enumerate([-1,1]):
 mesh(c,f'fountain-wing-{j}',[(side*.1,0,1.8),(side*.9,0,2.65),(side*.78,0,1.95),(side*.43,0,1.55)],[[0,1,2,3]],'stoneLight',p)

# Shrine ceremonial silhouette and inn balcony remain distinct from houses.
c=bpy.data.collections['moon-shrine'];p=bpy.data.objects['moon-shrine-placement']
star(c,'shrine-astral-insignia',(-.1,.15,3.5),(1,0,0),.35,'gold',p)
c=bpy.data.collections['east-inn'];p=bpy.data.objects['east-inn-placement']
poly=[tuple(v.co[:2]) for v in bpy.data.objects['east-inn-walls'].data.vertices[:4]];a,b=Vector(poly[0]),Vector(poly[3]);t=(b-a).normalized();n=Vector((-t.y,t.x))
balcony=[tuple(a+n*.06),tuple(b+n*.06),tuple(b+n*.5),tuple(a+n*.5)];prism(c,'inn-traveler-balcony',balcony,2.55,.12,'oak',p)
for j in range(11):
 q=a.lerp(b,j/10)+n*.5;beam(c,f'inn-balcony-baluster-{j}',(*q,2.65),(*q,3.2),.06,'timber',p)
beam(c,'inn-balcony-rail',(*(a+n*.5),3.22),(*(b+n*.5),3.22),.08,'oak',p)
for id in ['residence','north-house']:
 c=bpy.data.collections[id];p=bpy.data.objects[id+'-placement'];part=bpy.data.objects[id+'-walls'];poly=[tuple(v.co[:2]) for v in part.data.vertices[:4]];center=Vector(poly[0]).lerp(Vector(poly[3]),.7)
 box(c,id+'-dormer',(*center,3.2 if id=='residence' else 2.65),(.6,.5,.75),'plaster',p)
 box(c,id+'-dormer-glass',(center.x,center.y+.26,3.25 if id=='residence' else 2.68),(.28,.03,.36),'glass',p)

# Authored eaves, expressive timber framing and family-specific frontages.
# Preserve original roof vertices so repeated refinement never grows the roofs.
commercial=bpy.data.collections['east-house']
for o in list(commercial.objects):
 if o.type!='MESH' or o.get('golden_refinement'):continue
 if o.name=='east-house-roof-gables':bpy.data.objects.remove(o,do_unlink=True);continue
 if o.name in ['east-house-walls','east-house-cornice','east-house-roof']:
  if not o.get('commercial_original'):o['commercial_original']=json.dumps(json.loads(o['original_vertices']) if o.get('original_vertices') else [list(v.co) for v in o.data.vertices])
  original=json.loads(o['commercial_original']);coords=[(v[0],v[1],v[2]-1.2 if v[2]>2.2 else v[2]) for v in original]
  if o.name=='east-house-roof':
   center=sum((Vector(v) for v in coords[:4]),Vector())/4
   for j in [4,5]:q=Vector(coords[j]);q.x+=(center.x-q.x)*.28;q.y+=(center.y-q.y)*.28;coords[j]=tuple(q)
   o.data.clear_geometry();o.data.from_pydata(coords,[],[[0,1,5,4],[2,3,4,5],[0,4,3],[1,2,5]]);o.data.update();o['original_vertices']=json.dumps(coords);o.data.materials.clear();o.data.materials.append(kit['materials']['slate'])
  else:
   for v,co in zip(o.data.vertices,coords):v.co=Vector(co)
 if o.name.startswith('east-house-timber-post-'):
  o.location.z=1.22
  for v in o.data.vertices:v.co.z=1 if v.co.z>0 else -1
 if o.name=='east-house-roof-ridge':
  if not o.get('commercial_location'):o['commercial_location']=json.dumps(list(o.location))
  original=json.loads(o['commercial_location']);o.location=(original[0],original[1],original[2]-1.2)
for c in bpy.data.collections:
 if c.get('family') not in ['civic','shrine','market','inn','workshop','residential']:continue
 body=bpy.data.objects.get(c.name+'-walls')
 if not body:continue
 p=bpy.data.objects[c.name+'-placement'];poly=[Vector(v.co[:2]) for v in body.data.vertices[:4]]
 height=max(v.co.z for v in body.data.vertices);a,b=poly[0],poly[3];t=(b-a).normalized();n=Vector((-t.y,t.x))
 for roof in [o for o in c.objects if o.type=='MESH' and o.name==c.name+'-roof']:
  if not roof.get('original_vertices'):roof['original_vertices']=json.dumps([list(v.co) for v in roof.data.vertices])
  original=json.loads(roof['original_vertices']);center=sum((Vector(v[:2]) for v in original[:4]),Vector((0,0)))/4
  for v,co in zip(roof.data.vertices,original):
   v.co=Vector(co)
   if v.index<4:
    d=Vector(co[:2])-center;v.co.x+=d.normalized().x*.18;v.co.y+=d.normalized().y*.18
  for j in range(4):beam(c,c.name+f'-eave-fascia-{j}',roof.data.vertices[j].co,roof.data.vertices[(j+1)%4].co,.10,'gold' if c['family']=='civic' else 'timber',p)
 if c['family'] in ['inn','residential','market']:
  for side in [2,3]:
   u,v=poly[side],poly[(side+1)%4];length=(v-u).length;normal=Vector((-(v-u).y,(v-u).x)).normalized()*-.07
   for j in range(max(1,int(length/1.4))):
    q=u.lerp(v,(j+.1)/max(1,int(length/1.4)))+normal;r=u.lerp(v,(j+.85)/max(1,int(length/1.4)))+normal
    beam(c,c.name+f'-front-brace-{side}-{j}',(*q,height*.56),(*r,height-.1),.07,'timber',p)
 if c['family']=='civic':
  for side in [2,3]:
   u,v=poly[side],poly[(side+1)%4];normal=Vector((-(v-u).y,(v-u).x)).normalized()*-.065
   for j in range(3):
    q=u.lerp(v,(j+.5)/3)+normal;tan=(v-u).normalized()
    # Tall recessed window, stone jambs and a pointed crown.
    pts=[tuple(q-tan*.28)+ (1.7,),tuple(q+tan*.28)+(1.7,),tuple(q+tan*.28)+(3.8,),tuple(q)+(4.2,),tuple(q-tan*.28)+(3.8,)]
    mesh(c,c.name+f'-lancet-glass-{side}-{j}',pts,[[0,1,2,3,4]],'glass',p)
    for k,sign in enumerate([-1,1]):beam(c,c.name+f'-lancet-jamb-{side}-{j}-{k}',(*(q+tan*.32*sign),1.7),(*(q+tan*.32*sign),3.8),.09,'stoneLight',p)
    beam(c,c.name+f'-lancet-mullion-{side}-{j}',(*q,1.7),(*q,4.05),.04,'gold',p)
    for k,sign in enumerate([-1,1]):beam(c,c.name+f'-lancet-crown-{side}-{j}-{k}',(*(q+tan*.32*sign),3.8),(*q,4.25),.085,'stoneLight',p)
 if c['family']=='workshop':
  # Open timber work shelter, distinct from the domestic and commercial roofs.
  u=a.lerp(b,.1)+n*.15;v=a.lerp(b,.85)+n*.15;corners=[u,v,v+n*.95,u+n*.95]
  mesh(c,'forge-work-shelter',[(q.x,q.y,2.2 if j<2 else 1.9) for j,q in enumerate(corners)],[[0,1,2,3]],'terracotta',p,'overhead')
  for j,q in enumerate(corners[2:]):beam(c,f'forge-yard-post-{j}',(*q,.05),(*q,1.9),.12,'timber',p)
  for j in range(5):
   q=a.lerp(b,.78)+n*.64;box(c,f'forge-stock-ingot-{j}',(q.x+(j%3)*.18,q.y,.28+(j//3)*.14),(.16,.35,.12),'iron',p)
 if c['family']=='residential':
  # Window boxes and entrance gardens change the lot composition and silhouette.
  for j,f in enumerate([.18,.8]):
   q=a.lerp(b,f)+n*.12;box(c,c.name+f'-domestic-windowbox-{j}',(*q,1.03),(.6,.25,.16),'oak',p)
   for k in range(5):
    r=q+t*(k-2)*.10;prism(c,c.name+f'-window-flower-{j}-{k}',circle(r.x,r.y,.065,5),1.1,.12,'flowers',p)

# Shrine has ceremonial lancets and white buttresses rather than cottage windows.
c=bpy.data.collections['moon-shrine'];p=bpy.data.objects['moon-shrine-placement'];body=bpy.data.objects['moon-shrine-walls'];poly=[Vector(v.co[:2]) for v in body.data.vertices[:4]]
for side in [2,3]:
 u,v=poly[side],poly[(side+1)%4];tan=(v-u).normalized();normal=Vector((tan.y,-tan.x));height=max(q.co.z for q in body.data.vertices)
 for j in range(2):
  q=u.lerp(v,(j+.5)/2)+normal*.045
  pts=[tuple(q-tan*.18)+(1.65,),tuple(q+tan*.18)+(1.65,),tuple(q+tan*.18)+(3.65,),tuple(q)+(4.05,),tuple(q-tan*.18)+(3.65,)]
  mesh(c,f'shrine-lancet-{side}-{j}',pts,[[0,1,2,3,4]],'glass',p)
  for sign in [-1,1]:beam(c,f'shrine-jamb-{side}-{j}-{sign}',(*(q+tan*.23*sign),1.55),(*(q+tan*.23*sign),3.7),.07,'stoneLight',p)
 for j in range(3):
  q=u.lerp(v,j/2)+normal*.1;box(c,f'shrine-buttress-{side}-{j}',(*q,height*.42),(.20,.22,height*.82),'stoneLight',p)
u,v=poly[2],poly[3];tan=(v-u).normalized();normal=Vector((tan.y,-tan.x));q=u.lerp(v,.72)+normal*.08
star(c,'shrine-facing-sun',(*q,4.3),(*tan,0),.31,'gold',p)

# A pointed sacred entrance distinguishes shrine massing from the civic hall.
u,v=poly[2],poly[3];tan=(v-u).normalized();normal=Vector((tan.y,-tan.x));q=u.lerp(v,.65);corners=[q-tan*.53,q+tan*.53,q+tan*.53+normal*.48,q-tan*.53+normal*.48]
prism(c,'shrine-sanctuary-portal',[tuple(r) for r in corners],.23,5.0,'stoneLight',p,'solid')
vs=[(r.x,r.y,5.23) for r in corners]+[(q.x,q.y,7.0),(q.x+normal.x*.48,q.y+normal.y*.48,7.0)]
mesh(c,'shrine-pointed-portal-roof',vs,[[0,4,5,3],[4,1,2,5]],'slate',p,'overhead');mesh(c,'shrine-pointed-portal-gable',vs,[[3,5,2]],'stoneLight',p)
front=q+normal*.52;arch(c,'shrine-ceremonial-arch',(*front,0),(*tan,0),.34,1.9,'gold',p)
prism(c,'shrine-sanctuary-door',[tuple(front-tan*.27),tuple(front+tan*.27),tuple(front+tan*.27+normal*.03),tuple(front-tan*.27+normal*.03)],.23,1.72,'timber',p)
star(c,'shrine-portal-star',(*front,4.45),(*tan,0),.28,'gold',p)
for j,sign in enumerate([-1,1]):
 r=q+tan*.55*sign+normal*.3;prism(c,f'shrine-ceremonial-pier-{j}',circle(r.x,r.y,.12,6),.23,5.3,'stoneLight',p)
 mesh(c,f'shrine-ceremonial-spire-{j}',[(x,y,5.55) for x,y in circle(r.x,r.y,.23,6)]+[(r.x,r.y,6.8)],[[k,(k+1)%6,6] for k in range(6)],'slate',p,'overhead')

# Clusters break the spherical canopy silhouette using the saved source mesh.
for o in bpy.data.objects:
 if o.type!='MESH' or '-canopy-' not in o.name:continue
 if not o.get('original_vertices'):o['original_vertices']=json.dumps([list(v.co) for v in o.data.vertices])
 seed=sum(map(ord,o.name))
 for v,co in zip(o.data.vertices,json.loads(o['original_vertices'])):
  original=Vector(co);factor=1+.12*math.sin(v.index*12.7+seed)
  v.co=original*factor

# Quiet northern domestic edge from the concept plan: two deliberately different
# small lots, rather than another copy of a civic/merchant facade.
for id,xy,width,depth,height,rise,angle in [('northwest-cottage',(7.7,10.2),2.2,1.7,1.65,1.1,-.12),('north-garden-house',(12.8,7.8),1.7,2.5,2.6,1.35,.14)]:
 c=bpy.data.collections.get(id)
 if not c:c=kit['family'](id,'residential')
 p=bpy.data.objects.get(id+'-placement')
 if not p:p=kit['empty'](c,id+'-placement',(*xy,0),'authoring-root')
 p.location=(*xy,0);p.rotation_euler.z=angle
 poly=[(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]
 prism(c,id+'-foundation',poly,0,.18,'cream',p)
 prism(c,id+'-walls',poly,.18,height,'plaster',p,'solid')
 # Crosswise ridge distinguishes the cottage from the longitudinal town houses.
 vs=[(x*1.12,y*1.12,height+.18) for x,y in poly]+[(0,-depth*.58,height+rise),(0,depth*.58,height+rise)]
 mesh(c,id+'-roof',vs,[[0,3,5,4],[1,4,5,2]],'terracotta' if id=='northwest-cottage' else 'slate',p,'overhead')
 mesh(c,id+'-gable',vs,[[0,4,1],[3,2,5]],'plaster',p)
 box(c,id+'-door',(-width*.12,depth/2+.035,.86),(.48,.06,1.3),'timber',p)
 for j,x in enumerate([-width*.32,width*.32]):
  box(c,id+f'-window-frame-{j}',(x,depth/2+.025,1.20),(.48,.08,.66),'oak',p)
  box(c,id+f'-window-glass-{j}',(x,depth/2+.074,1.20),(.32,.025,.48),'glass',p)
  if height>2:
   box(c,id+f'-upper-window-{j}',(x,depth/2+.035,2.25),(.36,.045,.52),'glass',p)
 box(c,id+'-hearth-chimney',(width*.36,-depth*.2,height+.3),(.28,.35,1.4),'cream',p)
 for j,x in enumerate([-width*.5,width*.5]):
  box(c,id+f'-garden-bed-{j}',(x,depth/2+.36,.12),(.35,.6,.24),'soil',p)
  for k in range(4):prism(c,id+f'-garden-flower-{j}-{k}',circle(x,(depth/2+.15)+k*.14,.065,5),.24,.15,'flowers',p)

# Sculpt the town into a defended raised bank; the gate has an actual bridge.
gate=bpy.data.collections['caravan-gate'];gate_root=bpy.data.objects['caravan-gate-placement'];span=bpy.data.objects.get('caravan-gate-arch-keystone')
if span:bpy.data.objects.remove(span,do_unlink=True)
center=6.95-gate_root.location.x
for j in range(16):
 a=j*math.pi/16;b=(j+1)*math.pi/16
 x1=center+math.cos(a)*1.4;x2=center+math.cos(b)*1.4;z1=2.65+math.sin(a)*1.4;z2=2.65+math.sin(b)*1.4
 vs=[(x,y,z) for y in [-1.45,-.55] for x,z in [(x1,z1),(x2,z2),(x2,5.05),(x1,5.05)]]
 mesh(gate,f'west-gate-arch-voussoir-{j}',vs,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],'stoneLight' if j==8 else 'cream',gate_root,'overhead')
# The southern boundary is a domestic-scale watchpost, not a second civic gate
# that hides the residential frontage in the fixed camera.
for o in bpy.data.collections['south-gate'].objects:
 if o.type!='MESH':continue
 if not o.get('watchpost_original'):o['watchpost_original']=json.dumps([list(v.co) for v in o.data.vertices])
 for v,co in zip(o.data.vertices,json.loads(o['watchpost_original'])):v.co=Vector((co[0],co[1],co[2]*.45))

outline=[(5,23.5),(3,15),(7,7),(16,4.5),(19.2,4.5),(21.0,3.5),(23.5,4.5),(28,4.5),(39.5,6),(40.3,22),(40.3,34.5),(28,36.7),(24,36.7),(21.5,38),(19.3,37.2),(11,36.5),(8.2,28.7),(9.8,23)]
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'));count=len(outline)
ground.data.clear_geometry();ground.data.from_pydata([(x,y,z) for z in [-3,0] for x,y in outline],[],[list(range(count,2*count))])
ground['outline_vertex_indices']=json.dumps(list(range(count,2*count)));bpy.context.scene['world_bounds_json']=json.dumps({'minX':0,'minY':0,'maxX':44,'maxY':40})
# Keep the old western tree on the authored land rather than over river water.
bpy.data.objects['east-garden-placement'].location=(9.8,31.4,0)
# Retaining faces use original masonry; the land's upper surface stays grass.
bank=mesh(bpy.data.collections['town-wall-0'],'town-bank-retaining',[(x,y,z) for z in [-3,0] for x,y in outline],[[i,(i+1)%count,(i+1)%count+count,i+count] for i in range(count)],'stone');bank['shadow']=False
ground.data.polygons.foreach_set('use_smooth',[False]*len(ground.data.polygons))
bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free()
water=bpy.data.objects['western-water'];water.data.clear_geometry();water.data.from_pydata([(-35,-35,-3.1),(80,-35,-3.1),(80,80,-3.1),(-35,80,-3.1)],[],[[0,1,2,3]])
bridge=[(5.85,22.7),(8.05,22.7),(8.05,29),(5.85,29)]
floor=mesh(terrain,'west-arrival-bridge-surface',[(x,y,.018) for x,y in bridge],[[0,1,2,3]],'paving');floor['surface_role']='primary';floor['walkable']=True
shore=[(-8,29),(3.5,29),(5,29.3),(8.05,29.0),(9.2,30.2),(9.8,33.4),(12,36.8),(12.6,44),(-8,44)]
fieldbank=mesh(terrain,'field-road-bank',[(x,y,.012) for x,y in shore],[list(range(len(shore)))],'grass');fieldbank['surface_role']='green';fieldbank['walkable']=True
bm=bmesh.new();bm.from_mesh(fieldbank.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(fieldbank.data);bm.free()
for j,(x,y) in enumerate(shore[:-1]):
 box(bpy.data.collections['caravan-gate'],f'field-shore-stone-{j}',(x,y,-.6),(.6+.2*(j%3),.75,1.25),'stone')
c=bpy.data.collections['caravan-gate'];prism(c,'west-arrival-bridge-deck',bridge,-.35,.35,'cream')
for j,x in enumerate([5.8,8.1]):
 box(c,f'west-arrival-bridge-parapet-{j}',(x,26,.34),(.22,5.8,.68),'cream',role='solid')
 for k,y in enumerate([24,26.1,28.1]):box(c,f'west-arrival-bridge-pier-{j}-{k}',(x,y,-1.7),(.50,.75,2.8),'cream')
for o in c.objects:
 if o.get('kind')=='walker' and o.name=='guard-2':
  root=bpy.data.objects['caravan-gate-placement'];world=[(6.9,25.1),(7.2,27.2),(6.8,28.0)]
  o['route_json']=json.dumps([[x-root.location.x,y-root.location.y,0] for x,y in world])
 if o.get('kind')=='walker' and o.name=='guard-1':
  root=bpy.data.objects['caravan-gate-placement'];world=[(11.1,21.4),(13.3,21.7),(12.8,23.0)]
  o['route_json']=json.dumps([[x-root.location.x,y-root.location.y,0] for x,y in world])
for c in bpy.data.collections:
 if not c.name.startswith('town-wall-'):continue
 o=next(o for o in c.objects if o.type=='MESH' and not o.get('golden_refinement'))
 for v in o.data.vertices:
  if v.co.z>.1:v.co.z=1.8
 poly=[tuple(v.co[:2]) for v in o.data.vertices[:4]];a=(Vector(poly[0])+Vector(poly[3]))/2;b=(Vector(poly[1])+Vector(poly[2]))/2;length=(b-a).length
 for j in range(max(1,int(length/1.0))):
  q=a.lerp(b,(j+.5)/max(1,int(length/1.0)));box(c,c.name+f'-merlon-{j}',(*q,2.0),(.38,.38,.4),'cream')
routes=json.loads(bpy.context.scene['route_json'])
for s in routes:
 if s['name']=='Blacksmith':s['position']=[14.4,29]
 if s['name']=='Inn':s['position']=[11.8,18.4]
bpy.context.scene['route_json']=json.dumps(routes)
for id in ['guild-board','planter-a','planter-b']:bpy.data.objects[id+'-placement'].location.z=.45
# The notice board's gameplay owner is its visible mesh, rather than the hall.
service=bpy.data.objects['quest-board'];world=service.matrix_world.copy()
for owner in list(service.users_collection):owner.objects.unlink(service)
bpy.data.collections['guild-board'].objects.link(service)
service.parent=bpy.data.objects['guild-board-placement'];service.matrix_world=world
# Author connected, rounded street junctions from the actual road meshes.
joins={}
for o in list(terrain.objects):
 if not o.get('road_segment') or o.get('legacy_role')=='field':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];a=(vs[0]+vs[3])/2;b=(vs[1]+vs[2])/2;width=(vs[0]-vs[3]).length
 for p in [a,b]:
  key=(round(p.x,4),round(p.y,4));entry=joins.setdefault(key,{'count':0,'width':0});entry['count']+=1;entry['width']=max(entry['width'],width)
for j,((x,y),entry) in enumerate(joins.items()):
 if entry['count']<2:continue
 points=circle(x,y,entry['width']/2,16);o=mesh(terrain,f'street-junction-{j}',[(px,py,.018) for px,py in points],[list(range(16))],'paving');o['surface_role']='residential';o['walkable']=True

# Keep the domestic service in a visible standing space beyond roof projection.
housing=bpy.data.objects['housing-keeper'];housing.location.y=33.5-bpy.data.objects['residence-placement'].location.y
gatekeeper=bpy.data.objects['gatekeeper'];gatekeeper.location=(14.5-bpy.data.objects['caravan-gate-placement'].location.x,21.1-bpy.data.objects['caravan-gate-placement'].location.y,0)

# New social/sacred services are authored children, not runtime XY constants.
for object_id,id,name,kind,xy in [('east-inn','inn-host',"The Seafarer's Host",'inn',(-.5,2.8)),('moon-shrine','luna-attendant','Luna Attendant','shrine',(-.4,3.0))]:
 c=bpy.data.collections[object_id];p=bpy.data.objects[object_id+'-placement'];o=kit['empty'](c,id,(*xy,0),'service');o.parent=p;o['data_json']=json.dumps({'name':name,'kind':kind,'symbol':'✧'})
# Traveler seating and a working forge explain their frontage functions.
c=bpy.data.collections['east-inn'];p=bpy.data.objects['east-inn-placement']
for j,(x,y) in enumerate([(-1.55,2.1),(1.65,2.25)]):
 prism(c,f'inn-courtyard-table-{j}',circle(x,y,.35,10),.63,.07,'oak',p,'solid');prism(c,f'inn-table-leg-{j}',circle(x,y,.07,6),0,.63,'timber',p)
 for k,dy in enumerate([-.55,.55]):
  box(c,f'inn-chair-seat-{j}-{k}',(x,y+dy,.35),(.38,.34,.07),'oak',p);box(c,f'inn-chair-back-{j}-{k}',(x,y+dy+(.14 if dy>0 else -.14),.62),(.38,.05,.48),'timber',p)
c=bpy.data.collections['artisan-workshop'];p=bpy.data.objects['artisan-workshop-placement']
prism(c,'forge-anvil-pedestal',circle(.65,1.2,.28,8),0,.42,'timber',p,'solid')
prism(c,'forge-anvil-waist',[(-.02,.98),(.97,.98),(.97,1.4),(-.02,1.4)],.42,.24,'iron',p)
mesh(c,'forge-anvil-horn',[(.9,1.0,.64),(1.35,1.16,.67),(.9,1.38,.64),(.9,1.0,.77),(1.35,1.16,.71),(.9,1.38,.77)],[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2]],'iron',p)
for j in range(3):
 x=-.55+j*.14;mesh(c,f'forge-hearth-flame-{j}',[(x,1.09,.28),(x+.15,1.09,.28),(x+.10,1.09,.68+.10*(j%2))],[[0,1,2]],'clothOchre',p)

# A clustered market uses different widths, cloth pitches and functional goods.
rose=bpy.data.materials.get('clothRose') or bpy.data.materials.new('clothRose');rose.diffuse_color=(.70,.34,.31,1);kit['materials']['clothRose']=rose
for id,xy,width,depth,angle,cloth in [('market-textiles',(28.2,23.8),1.65,.8,.13,'clothRose'),('market-spices',(34.4,23.6),2.05,.72,-.08,'clothOchre'),('market-supplies',(35.6,26.3),1.45,.9,.18,'clothBlue')]:
 c=bpy.data.collections.get(id) or kit['family'](id,'market');p=kit['empty'](c,id+'-placement',(*xy,0),'authoring-root');p.rotation_euler.z=angle
 box(c,id+'-counter',(0,0,.43),(width,depth,.86),'oak',p,'solid')
 for j,x in enumerate([-width*.46,width*.46]):beam(c,id+f'-awning-post-{j}',(x,.12,0),(x,.12,2.35),.07,'timber',p)
 corners=[(-width*.60,-depth*.8,2.08),(width*.60,-depth*.8,2.08),(width*.60,depth*.8,1.98),(-width*.60,depth*.8,1.98),(0,-depth*.8,2.38),(0,depth*.8,2.28)]
 mesh(c,id+'-canopy',corners,[[0,4,5,3],[4,1,2,5]],cloth,p,'overhead')
 for j in range(5):
  x=(j-2)*width/5;mesh(c,id+f'-scallop-{j}',[(x-width/10,depth*.8,1.98),(x+width/10,depth*.8,1.98),(x,depth*.8,1.80)],[[0,1,2]],cloth,p)
 for j in range(6):
  x=(j%3-1)*width*.24;y=(j//3-.5)*depth*.3
  box(c,id+f'-goods-{j}',(x,y,.95),(width*.18,.20,.18),'flowers' if cloth=='clothRose' else 'clothOchre' if cloth=='clothOchre' else 'plaster',p)
 prism(c,id+'-barrel',circle(width*.72,0,.22,10),0,.62,'oak',p,'solid')
 for j,z in enumerate([.12,.48]):prism(c,id+f'-barrel-band-{j}',circle(width*.72,0,.228,10),z,.04,'iron',p)

# Domestic and sacred planting frames lots while keeping the public routes open.
for id,centers in [('moon-shrine',[(26.9,9.2),(34.0,10.6),(33.5,13.4)]),('residence',[(14.8,34.8),(16.0,35.4)]),('willow-house',[(22.3,34.6),(24.5,34.5)]),('northwest-cottage',[(6.4,11.1),(8.7,11.5)])]:
 c=bpy.data.collections[id]
 for j,(x,y) in enumerate(centers):
  prism(c,id+f'-garden-border-{j}',circle(x,y,.52,10),.01,.13,'stoneLight')
  prism(c,id+f'-garden-soil-{j}',circle(x,y,.46,10),.145,.015,'soil')
  for k in range(4):
   phi=k*2.2+j;xx=x+math.cos(phi)*.22;yy=y+math.sin(phi)*.22
   prism(c,id+f'-garden-shrub-{j}-{k}',circle(xx,yy,.20,7),.15,.30+.09*(k%2),'leaf')
   for f in range(3):prism(c,id+f'-garden-blossom-{j}-{k}-{f}',circle(xx+(f-1)*.09,yy,.05,5),.47,.05,'flowers')

# Register exported lights to the actual authored lamp meshes.
for c in bpy.data.collections:
 lamps=[o for o in c.objects if o.type=='MESH' and '-lamp-bracket-' in o.name]
 lights=[o for o in c.objects if o.get('kind')=='light']
 for light,lamp in zip(lights,lamps):
  center=sum((v.co for v in lamp.data.vertices),Vector())/len(lamp.data.vertices);light.location=center+Vector((0,.12,-.14))

# Original painterly nature atlas is shared by authoring and browser surfaces.
for material_name,tile,size in [('grass',0,4.0),('soil',1,3.0),('leaf',2,2.5),('leafLight',2,2.5),('water',3,5.0)]:
 kit['materials'][material_name]['texture_json']=json.dumps({'file':'assets/wayfarer-nature-v1.webp','grid':[2,2],'tile':tile,'worldSize':size})

# Reuse original project paving as a material, alongside the original new atlas.
kit['materials']['paving']['texture_json']=json.dumps({'file':'assets/town-limestone-v1.webp','grid':[1,1],'tile':0,'worldSize':4.0})
# The Blender material view uses the same original atlas and UV tile mapping
# as the browser, so authoring review is not limited to flat blockout colors.
for material in kit['materials'].values():
 if not material.get('texture_json'):continue
 spec=json.loads(material['texture_json']);material.use_nodes=True;nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
 output=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled');shader.inputs['Roughness'].default_value=1;shader.inputs['Specular IOR Level'].default_value=0;links.new(shader.outputs['BSDF'],output.inputs['Surface'])
 uv=nodes.new('ShaderNodeTexCoord');fract=nodes.new('ShaderNodeVectorMath');fract.operation='FRACTION';links.new(uv.outputs['UV'],fract.inputs[0])
 scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';cols,rows=spec['grid'];scale.inputs[1].default_value=(1/cols,1/rows,1);links.new(fract.outputs['Vector'],scale.inputs[0])
 offset=nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=((spec['tile']%cols)/cols,(rows-1-spec['tile']//cols)/rows,0);links.new(scale.outputs['Vector'],offset.inputs[0])
 image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(ROOT/spec['file']),check_existing=True);image.image.filepath=bpy.path.relpath(str(ROOT/spec['file']));links.new(offset.outputs['Vector'],image.inputs['Vector']);links.new(image.outputs['Color'],shader.inputs['Base Color'])
for o in bpy.data.objects:
 if o.name not in existing:o['golden_refinement']=True
 if o.type!='MESH':continue
 if o.get('surface_role'):
  bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if f.normal.z<0];bmesh.ops.reverse_faces(bm,faces=faces);bm.to_mesh(o.data);bm.free()
 # Real Blender UVs follow wall horizontals and roof pitch; source transforms
 # and IDs are preserved through the same exporter as collision/navigation.
 if not o.data.uv_layers:o.data.uv_layers.new(name='Wayfarer-painterly')
 uv=o.data.uv_layers.active.data;worldsize=json.loads(o.data.materials[0].get('texture_json','{"worldSize":2.4}'))['worldSize']
 for face in o.data.polygons:
  normal=face.normal.normalized();up=Vector((0,0,1))
  if abs(normal.z)>.95:u=Vector((1,0,0));v=Vector((0,1,0))
  else:u=up.cross(normal).normalized();v=normal.cross(u).normalized()
  for index in face.loop_indices:
   co=o.data.vertices[o.data.loops[index].vertex_index].co;uv[index].uv=(co.dot(u)/worldsize,co.dot(v)/worldsize)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Refined spatial civic architecture, social balcony, fountain, stair profile and UVs')
