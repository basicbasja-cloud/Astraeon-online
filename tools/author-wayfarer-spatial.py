"""Evolve the saved Golden layout into actual authored spatial architecture.

Run once against authoring/wayfarer-court.blend; thereafter edit/save the spatial
scene and export it. Painted buildings stay in the court as migration references.
All runtime geometry, navigation, services and materials originate in this scene.
"""
import bpy, math, json, runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
kit=runpy.run_path(str(ROOT/'tools/blender-v3-kit.py'))
scene=bpy.context.scene
scene['world_id']='wayfarer-spatial';scene['layout_id']='wayfarer-spatial-v1'
colors={'cream':(.79,.70,.51,1),'plaster':(.91,.80,.60,1),'slate':(.12,.31,.47,1),'terracotta':(.62,.25,.12,1),'teal':(.12,.38,.37,1),'timber':(.28,.16,.08,1),'oak':(.49,.30,.13,1),'iron':(.18,.21,.20,1),'glass':(.19,.35,.39,1),'clothBlue':(.16,.39,.62,1),'clothOchre':(.85,.56,.22,1),'water':(.15,.54,.57,1),'flowers':(.78,.40,.44,1),'leafLight':(.30,.48,.17,1),'soil':(.47,.38,.22,1)}
for name,color in colors.items():
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color;kit['materials'][name]=m
for name,tile in [('cream',0),('stone',0),('stoneLight',0),('slate',1),('blue',1),('terracotta',2),('plaster',3)]:
 kit['materials'][name]['texture_json']=json.dumps({'file':'assets/wayfarer-materials-v1.webp','grid':[2,2],'tile':tile,'worldSize':2.4})
def mesh(c,id,vs,fs,mat,role='decorative',shadow=True,parent=None):
 o=kit['mesh'](c,id,vs,fs,mat,role,shadow)
 if parent:o.parent=parent
 return o
def box(c,id,p,size,mat,role='decorative',parent=None):
 o=kit['box'](c,id,p,size,mat,role,True)
 if parent:o.parent=parent
 return o
def prism(c,id,poly,z,h,mat,role='decorative',parent=None):
 n=len(poly);return mesh(c,id,[(x,y,t) for t in (z,z+h) for x,y in poly],[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],mat,role,parent=parent)
def circle(x,y,r,n=12):return [(x+math.cos(i*math.tau/n)*r,y+math.sin(i*math.tau/n)*r) for i in range(n)]
def roof(c,id,poly,z,rise,mat,parent,hip=False):
 # Roof follows the actual ground footprint, rather than a perspective image.
 a,b,d,e=[Vector((x,y,z)) for x,y in poly];u=(a+e)/2;v=(b+d)/2
 if hip:u=u.lerp(v,.18);v=v.lerp((a+e)/2,.18)
 u.z+=rise;v.z+=rise
 vs=[tuple(p) for p in [a,b,d,e,u,v]]
 faces=[[0,1,5,4],[2,3,4,5]]+([[0,4,3],[1,2,5]] if hip else [])
 mesh(c,id,vs,faces,mat,'overhead',parent=parent)
 if not hip:mesh(c,id+'-gables',vs,[[0,4,3],[1,2,5]],'plaster',parent=parent)
 beam(c,id+'-ridge',u,v,.10,'gold' if mat in ('slate','teal') else 'timber',parent)
def beam(c,id,a,b,width,mat,parent):
 a,b=Vector(a),Vector(b);delta=b-a;o=box(c,id,(0,0,0),(width,width,delta.length),mat,parent=parent);o.location=(a+b)/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
def front_detail(c,id,a,b,z,w,h,mat,parent,offset=.035):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();n=Vector((-t.y,t.x));p=(a+b)/2+n*offset
 poly=[tuple(p-t*w/2-n*.025),tuple(p+t*w/2-n*.025),tuple(p+t*w/2+n*.025),tuple(p-t*w/2+n*.025)]
 return prism(c,id,poly,z,h,mat,parent=parent)
def lamp(c,root,p,i):
 x,y,z=p;box(c,root.name+f'-lamp-bracket-{i}',(x,y,z),(.16,.20,.07),'iron',parent=root);box(c,root.name+f'-lamp-{i}',(x,y+.12,z-.14),(.18,.16,.25),'gold',parent=root)
def plant(c,root,x,y,r,seed):
 prism(c,root.name+f'-flowerbox-{seed}',circle(x,y,r,8),0,.22,'cream',parent=root)
 for j in range(5):
  px=x+math.cos(j*2.4)*r*.6;py=y+math.sin(j*2.4)*r*.6
  prism(c,root.name+f'-leaf-{seed}-{j}',circle(px,py,.11,6),.22,.12,'leaf',parent=root)
  prism(c,root.name+f'-bloom-{seed}-{j}',circle(px,py,.07,6),.34,.07,'flowers',parent=root)

# Latest concept: forge lower-left, inn upper-left, commercial and sacred east.
forge=bpy.data.objects['artisan-workshop-placement'];inn=bpy.data.objects['east-inn-placement']
forge.location=(13.5,26.3,0);inn.location=(10.8,14.8,0)
bpy.data.objects['west-house-placement'].location=(35.5,28.5,0)
bpy.data.collections['west-house']['family']='residential'
routes=json.loads(scene['route_json'])
for s in routes:
 if s['name']=='Blacksmith':s['position']=[13.5,28.5]
 if s['name']=='Inn':s['position']=[10.8,17]
scene['route_json']=json.dumps(routes)
districts=json.loads(scene['districts_json'])
for d in districts:
 if d['name']=='Bronze Anvil':d.update(x=13.5,y=27.8)
 if d['name']=='Seafarer Rest':d.update(x=10.8,y=16.8)
scene['districts_json']=json.dumps(districts)
terrain=bpy.data.collections['court-terrain']
for name,points,mat in [('forge-workyard',[(10.5,26.9),(17,26.9),(17,29.5),(10.5,29.5)],'soil'),('inn-courtyard',[(8.5,15.8),(13.5,15.8),(13.5,18.4),(8.5,18.4)],'paving')]:
 o=bpy.data.objects[name];o.data.clear_geometry();o.data.from_pydata([(x,y,.018) for x,y in points],[],[[0,1,2,3]]);o.data.materials.clear();o.data.materials.append(kit['materials'][mat]);o['surface_role']='yard' if mat=='soil' else 'forecourt'

for c in list(bpy.data.collections):
 if c.get('family') in (None,'terrain'):continue
 root=next((o for o in c.objects if o.get('kind')=='presentation'),None)
 if not root:continue
 sprite=json.loads(root['data_json']);id=c.name
 oldparts=[o for o in c.objects if o.type=='MESH']
 body=next((o for o in oldparts if o.get('role')=='solid'),None)
 poly=[tuple(v.co[:2]) for v in body.data.vertices[:len(body.data.vertices)//2]] if body else None
 for o in oldparts:bpy.data.objects.remove(o,do_unlink=True)
 # Presentation information remains a classified migration/reference asset.
 root['footprint_review']='spatial geometry authored with the same object ID and service parent'
 if sprite.get('building') and sprite['art']!='gate':
  family=c['family'];height={'civic':5.4,'shrine':4.8,'market':3.2,'inn':3.9,'workshop':2.8,'residential':2.5}[family]
  if id=='willow-house':height=3.2
  if id=='north-house':height=2.1
  mat='cream' if family in ('civic','shrine') else 'plaster'
  prism(c,id+'-foundation',poly,0,.22,'cream',parent=root)
  prism(c,id+'-walls',poly,.22,height,mat,'solid',root)
  prism(c,id+'-cornice',poly,height+.16,.14,'cream',parent=root)
  roofmat={'civic':'slate','shrine':'slate','market':'slate' if id=='west-house' else 'terracotta','inn':'terracotta','workshop':'terracotta','residential':'teal' if id=='willow-house' else 'terracotta' if id=='north-house' else 'slate'}[family]
  roof(c,id+'-roof',poly,height+.30,2.3 if family=='civic' else 2 if family=='shrine' else 1.35 if id!='north-house' else .9,roofmat,root,hip=family=='shrine' or id=='willow-house')
  a,b=Vector(poly[0]),Vector(poly[3]);edge=b-a;n=Vector((-edge.y,edge.x)).normalized()
  door=a.lerp(b,.63 if family=='civic' else .48 if family!='residential' else {'residence':.27,'willow-house':.68,'north-house':.5}.get(id,.38));dw=.9 if family=='civic' else .6
  front_detail(c,id+'-door-frame',door-edge.normalized()*.01,door+edge.normalized()*.01,.22,dw+.22,1.8,'cream',root,.05)
  front_detail(c,id+'-door',door-edge.normalized()*.01,door+edge.normalized()*.01,.24,dw,1.55,'timber',root,.11)
  box(c,id+'-threshold',(*door,.12),(1.05,.46,.24),'cream',parent=root)
  for side in range(4):
   p,q=Vector(poly[side]),Vector(poly[(side+1)%4]);length=(q-p).length
   for j in range(max(1,int(length/1.1))):
    pos=p.lerp(q,(j+.5)/max(1,int(length/1.1)))
    for floor in range(2 if height>3.4 else 1):
     z=1.15+floor*1.8
     if side==3 and (pos-door).length<.7 and floor==0:continue
     prefix=id+f'-window-{side}-{j}-{floor}';t=(q-p).normalized()
     front_detail(c,prefix+'-frame',pos+t*.01,pos-t*.01,z,.53,.85,'timber' if family not in ('civic','shrine') else 'cream',root)
     front_detail(c,prefix+'-glass',pos+t*.01,pos-t*.01,z+.07,.36,.67,'glass',root,.065)
     front_detail(c,prefix+'-mullion',pos+t*.01,pos-t*.01,z+.07,.045,.67,'gold' if family=='civic' else 'oak',root,.10)
  if family in ('inn','residential','market','workshop'):
   for j,p in enumerate(poly):beam(c,id+f'-timber-post-{j}',(*p,.22),(*p,height+.2),.12,'timber',root)
   for j in (0,2,3):beam(c,id+f'-timber-beam-{j}',(*poly[j],height*.56),(*poly[(j+1)%4],height*.56),.12,'timber',root)
  if family=='civic':
   for j,p in enumerate([a.lerp(b,.10),a.lerp(b,.90)]):
    square=[(p.x+x,p.y+y) for x,y in [(-.55,-.55),(.55,-.55),(.55,.55),(-.55,.55)]]
    prism(c,id+f'-tower-{j}',square,0,7,'cream','solid',root);roof(c,id+f'-tower-roof-{j}',square,7,2.8,'slate',root,True)
    prism(c,id+f'-tower-collar-{j}',square,5.8,.18,'gold',parent=root)
    front_detail(c,id+f'-banner-{j}',p-Vector((.2,0)),p+Vector((.2,0)),3.1,.42,2,'clothBlue',root,.65)
    front_detail(c,id+f'-banner-star-{j}',p-Vector((.02,0)),p+Vector((.02,0)),3.5,.12,.75,'gold',root,.71)
   # Original astronomical insignia and broad processional entrance.
   prism(c,id+'-door-crown',circle(door.x,door.y,1.0,12),3.2,.16,'gold',parent=root)
  elif family=='shrine':
   p=Vector(poly[2]);square=[(p.x+x,p.y+y) for x,y in [(-.42,-.42),(.42,-.42),(.42,.42),(-.42,.42)]]
   prism(c,id+'-bell-tower',square,0,7.2,'cream','solid',root);roof(c,id+'-spire',square,7.2,2.9,'slate',root,True)
   beam(c,id+'-star-axis',(*p,9.7),(*p,10.4),.07,'gold',root);plant(c,root,door.x+1.3,door.y+.7,.35,0)
  elif family=='inn':
   # Porch, balcony and hanging traveler sign create a social silhouette.
   for j,f in enumerate([.08,.9]):
    p=a.lerp(b,f)+n*.55;beam(c,id+f'-porch-post-{j}',(*p,0),(*p,2.2),.13,'timber',root)
   porch=[tuple(a+n*.15),tuple(b+n*.15),tuple(b+n*1.0),tuple(a+n*1.0)]
   prism(c,id+'-porch',porch,0,.12,'oak',parent=root);roof(c,id+'-porch-roof',porch,2.3,.25,'terracotta',root,True)
   p=a.lerp(b,.12)+n*.85;front_detail(c,id+'-seafarer-sign',p-Vector((.01,0)),p+Vector((.01,0)),1.3,.62,.8,'clothOchre',root)
   for j in range(3):plant(c,root,*(a.lerp(b,(j+.3)/3)+n*.45),.2,j)
  elif family=='workshop':
   p=Vector(poly[1]);box(c,id+'-chimney',(*p,2.8),(.55,.55,5.6),'cream',parent=root);box(c,id+'-chimney-cap',(*p,5.65),(.75,.75,.22),'iron',parent=root)
   p=door+n*.8;box(c,id+'-forge-hearth',(*p,.38),(.78,.66,.76),'iron',parent=root);box(c,id+'-ember-mouth',(p.x,p.y+.34,.36),(.45,.045,.3),'clothOchre',parent=root)
   p=a.lerp(b,.1)+n*.9;box(c,id+'-anvil-foot',(*p,.3),(.3,.4,.6),'iron',parent=root);box(c,id+'-anvil',(*p,.68),(.6,.25,.17),'iron',parent=root)
   box(c,id+'-workbench',(*(a.lerp(b,.8)+n*.8),.48),(1,.45,.16),'oak',parent=root)
  elif family=='market':
   awning=[tuple(a+n*.08),tuple(b+n*.08),tuple(b+n*.9),tuple(a+n*.9)]
   mesh(c,id+'-awning',[(x,y,2.2 if i<2 else 1.9) for i,(x,y) in enumerate(awning)],[[0,1,2,3]],'clothBlue' if id=='east-house' else 'clothOchre','overhead',parent=root)
   for j,p in enumerate([a+n*.8,b+n*.8]):beam(c,id+f'-awning-pole-{j}',(*p,0),(*p,1.95),.07,'timber',root)
   box(c,id+'-display',(*(a.lerp(b,.2)+n*.6),.35),(.65,.45,.7),'oak',parent=root)
  else:
   plant(c,root,*(a.lerp(b,.9)+n*.5),.23,0)
   if id=='willow-house':
    for j in range(6):
     p=a.lerp(b,j/5)+n*.8;box(c,id+f'-garden-picket-{j}',(*p,.32),(.07,.07,.64),'oak',parent=root)
   if id=='north-house':
    p=Vector(poly[1]);box(c,id+'-chimney',(*p,2.5),(.35,.35,2.3),'cream',parent=root)
  lamp(c,root,(*door,1.9),0)
 elif sprite['art']=='gate':
  # Existing actual pillar footprints define the passage. No visual card remains.
  old=json.loads(root['structure_json']);width=2.8 if id=='caravan-gate' else 1.2
  center=Vector((-.9,-.8));h=5.2 if id=='caravan-gate' else 3.9
  # Build around the already authored clear arrival centerline.
  localx=6.95-root.location.x if id=='caravan-gate' else 20.94-root.location.x if id=='north-gate' else 21.32-root.location.x
  for j,x in enumerate([localx-width/2-.43,localx+width/2+.43]):
   p=(x,-1.0);q=[(x-.43,-1.65),(x+.43,-1.65),(x+.43,-.35),(x-.43,-.35)]
   prism(c,id+f'-pillar-{j}',q,0,h,'cream','solid',root);roof(c,id+f'-blue-tower-{j}',q,h,1.8,'slate',root,True)
   for k in range(3):box(c,id+f'-pillar-band-{j}-{k}',(x,-1,1+k*1.5),(1.0,1.4,.12),'stoneLight',parent=root)
   front_detail(c,id+f'-banner-{j}',Vector((x-.1,-.25)),Vector((x+.1,-.25)),1.7,.45,2.1,'clothBlue',root)
  box(c,id+'-arch-keystone',(localx,-1,h-.6),(width,.9,1.1),'cream','overhead',root)
  for j in range(7):
   x=localx-width/2+j*width/6;box(c,id+f'-parapet-{j}',(x,-1,h+.1),(.2,1.0,.32),'cream',parent=root)
 elif sprite.get('tree'):
  prism(c,id+'-root',circle(0,0,.18,8),0,1.6,'timber','solid',root)
  for j in range(3):
   a=Vector((0,0,1));b=Vector((math.cos(j*2.2)*.6,math.sin(j*2.2)*.6,2.8));beam(c,id+f'-branch-{j}',a,b,.13,'timber',root)
  # Rounded low-poly canopy clusters, reused material with varied authored size.
  seed=sum(map(ord,id));r=.72+(seed%5)*.07
  for j in range(5):
   x=math.cos(j*2.4)*r*.45;y=math.sin(j*2.4)*r*.45;z=2.0+(j%3)*.36
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=r,location=(x,y,z));o=bpy.context.object;o.name=id+f'-canopy-{j}';o.scale=(1,.85,1.15)
   for owner in list(o.users_collection):owner.objects.unlink(o)
   c.objects.link(o);o.parent=root;o.data.materials.append(kit['materials']['leafLight' if j%2 else 'leaf']);o['role']='overhead';o['shadow']=True
 elif sprite['art']=='fountain':
  prism(c,id+'-basin',circle(0,0,.94,16),0,.38,'cream','solid',root)
  prism(c,id+'-water',circle(0,0,.78,20),.385,.025,'water',parent=root)
  prism(c,id+'-shaft',circle(0,0,.13,8),.4,1.3,'cream',parent=root)
  prism(c,id+'-bowl',circle(0,0,.38,12),1.1,.20,'gold',parent=root)
  prism(c,id+'-star',circle(0,0,.14,6),1.75,.22,'gold',parent=root)
 elif sprite['art']=='bench':
  box(c,id+'-seat',(0,0,.42),(1.15,.35,.12),'oak',parent=root);box(c,id+'-back',(0,-.16,.75),(1.15,.10,.55),'oak',parent=root)
  for j,x in enumerate([-.42,.42]):box(c,id+f'-leg-{j}',(x,0,.21),(.10,.25,.42),'iron',parent=root)
 elif id.startswith('planter'):plant(c,root,0,0,.38,0)
 elif id=='guild-board':
  box(c,id+'-board',(0,0,1.15),(1.15,.14,1.0),'timber',parent=root);box(c,id+'-notice',(0,.081,1.16),(.78,.02,.68),'plaster',parent=root)
  for j,x in enumerate([-.5,.5]):box(c,id+f'-post-{j}',(x,0,.6),(.12,.12,1.2),'oak',parent=root)
 elif id=='food-market':
  box(c,id+'-counter',(0,0,.45),(1.55,.8,.9),'oak',parent=root)
  for j,x in enumerate([-.72,.72]):box(c,id+f'-pole-{j}',(x,0,1.2),(.08,.08,2.4),'timber',parent=root)
  roof(c,id+'-striped-canopy',[(-.95,-.6),(.95,-.6),(.95,.6),(-.95,.6)],2.1,.30,'clothBlue',root)
  for j in range(9):prism(c,id+f'-produce-{j}',circle((j%3-.9)*.35,(j//3-.9)*.2,.10,6),.9,.15,'clothOchre' if j%2 else 'flowers',parent=root)
 else:
  for j in range(3):box(c,id+f'-storage-{j}',((j%2-.5)*.65,(j//2)*.55,.35),(.6,.5,.7),'oak',parent=root)

# Spatial ground: all existing surface vertices remain authorable in Blender.
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
for o in terrain.objects:
 if o.type!='MESH':continue
 o['render_visible']=True
 if o.get('surface_role'):
  mat='soil' if o['surface_role'] in ('field','yard','service') else 'grass' if o['surface_role'] in ('garden','green') else 'paving'
  o.data.materials.clear();o.data.materials.append(kit['materials'][mat])
  for v in o.data.vertices:v.co.z=.018
# A raised sacred threshold with actual steps and a smooth navigation profile.
c=bpy.data.collections['moon-shrine'];root=bpy.data.objects['moon-shrine-placement']
for j in range(3):box(c,f'shrine-step-{j}',(-.1,1.5-j*.24,.07*(j+1)),(1.6,.28,.14*(j+1)),'cream',parent=root)
# Quiet original water edge outside the walkable town and retaining boundary.
water=mesh(terrain,'western-water',[(-9,-5,-.35),(1.8,-5,-.35),(1.8,45,-.35),(-9,45,-.35)],[[0,1,2,3]],'water',shadow=False)
water['surface_role']='water'
scene['environment_architecture']='spatial-meshes-painterly-2d-actors'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved spatial Wayfarer with seven original architectural families')
