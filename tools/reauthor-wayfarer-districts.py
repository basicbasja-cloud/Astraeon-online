"""Fortified banks and individually composed district buildings in the existing town."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
prefix='district-v4-'
for o in list(bpy.data.objects):
    if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
for name,color in {'bankStone':(.55,.57,.54,1),'bankStoneLight':(.73,.73,.64,1),'wallStone':(.74,.71,.62,1),'wallCap':(.86,.81,.69,1),'roofMoss':(.19,.34,.30,1),'roofClay':(.59,.28,.15,1),'roofBlue':(.18,.35,.49,1)}.items():
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color
for name,reference in {'wallStone':'stone','wallCap':'stoneLight','roofClay':'terracotta','roofBlue':'slate','roofMoss':'slate'}.items():
    bpy.data.materials[name]['texture_json']=bpy.data.materials[reference]['texture_json']
owner=None
def collection(name,family):
    c=bpy.data.collections.get(name)
    if c is None:c=bpy.data.collections.new(name);scene.collection.children.link(c)
    c['family']=family;return c
def mesh(name,vs,fs,mat,role='decorative',shadow=False):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials[mat])
    data.uv_layers.new(name='WorldUV')
    for face in data.polygons:
        n=face.normal;axes=(0,1) if abs(n.z)>.6 else (0,2) if abs(n.y)>abs(n.x) else (1,2)
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p[axes[0]]/2.0,p[axes[1]]/2.0)
    o=bpy.data.objects.new(prefix+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow;return o
def box(name,c,size,mat,role='decorative',shadow=False,angle=0):
    x,y,z=c;a,b,h=[v/2 for v in size];co,si=math.cos(angle),math.sin(angle)
    vs=[(x+u*a*co-v*b*si,y+u*a*si+v*b*co,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(name,vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)
def beam(name,a,b,r,mat,sides=6):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.001:u=Vector((1,0,0))
    u.normalize();v=axis.cross(u).normalized()
    vs=[tuple(p+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))) for p in (a,b) for i in range(sides)]
    return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[i,(i+1)%sides,(i+1)%sides+sides,i+sides] for i in range(sides)],mat)
def roof(name,x,y,w,d,eave,ridge,mat):
    mesh(name+'-south-gable',[(x-w/2,y+d/2,eave),(x+w/2,y+d/2,eave),(x,y+d/2,ridge)],[[0,1,2]],'plaster')
    mesh(name+'-north-gable',[(x-w/2,y-d/2,eave),(x+w/2,y-d/2,eave),(x,y-d/2,ridge)],[[0,1,2]],'plaster')
    for side in (-1,1):
        xx=x+side*w/2
        mesh(name+f'-roof-{side}',[(xx,y-d/2,eave),(xx,y+d/2,eave),(x,y+d/2,ridge),(x,y-d/2,ridge)],[[0,1,2,3]],mat,'overhead',True)
        beam(name+f'-barge-{side}',(xx,y+d/2+.01,eave),(x,y+d/2+.01,ridge),.055,'timber')
    beam(name+'-ridge',(x,y-d/2,ridge),(x,y+d/2,ridge),.04,'oak')

# Keep original short wall meshes as references, but retain their collision contract.
for c in bpy.data.collections:
    if c.name.startswith('town-wall-'):
        for o in c.objects:
            if o.type=='MESH':o['render_visible']=False;o['shadow']=False
owner=collection('wayfarer-river-fortifications','fortification')
terrain=bpy.data.collections['court-terrain']
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
vs=[tuple(ground.matrix_world@v.co) for v in ground.data.vertices]
outline=[vs[i] for i in json.loads(ground['outline_vertex_indices'])]
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
    # Leave the north passage and the south gate/bridge throat open.
    if (a[1]<=4.1 and b[1]<=4.1 and min(a[0],b[0])>=23.9 and max(a[0],b[0])<=30.1) or (a[1]>=46 and b[1]>=46 and min(a[0],b[0])>=24.6 and max(a[0],b[0])<=29.4):continue
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);angle=math.atan2(dy,dx)
    if length<.5:continue
    mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
    box(f'curtain-{i}',(mx,my,1.35),(length,.62,2.7),'wallStone','solid',True,angle)
    box(f'curtain-cap-{i}',(mx,my,2.75),(length+.04,.83,.20),'wallCap',angle=angle)
    n=max(1,round(length/1.45))
    for j in range(n+1):
        t=j/n;x=a[0]+dx*t;y=a[1]+dy*t
        box(f'crenel-{i}-{j}',(x,y,3.03),(.57,.78,.50),'wallCap',shadow=True,angle=angle)
    # Faceted rocky support below the wall, with varied mineral planes.
    nx,ny=dy/length,-dx/length
    n=max(2,round(length/2))
    for j in range(n):
        t0=j/n;t1=(j+1)/n
        p=(a[0]+dx*t0,a[1]+dy*t0);q=(a[0]+dx*t1,a[1]+dy*t1)
        mid=((p[0]+q[0])/2+nx*.38,(p[1]+q[1])/2+ny*.38,-1.5-(j%3)*.2)
        mesh(f'rock-bank-{i}-{j}',[(p[0],p[1],0),(q[0],q[1],0),mid,(q[0]+nx*.7,q[1]+ny*.7,-3.05),(p[0]+nx*.6,p[1]+ny*.6,-3.05)],[[0,1,2],[1,3,2],[3,4,2],[4,0,2]],'bankStone' if j%2 else 'bankStoneLight')

for i,(x,y) in enumerate(((12,45),(42,46),(53,40),(53,23),(51,8),(39,4),(16,4),(7,8),(4,18),(6,37))):
    box(f'watchtower-base-{i}',(x,y,1.65),(1.65,1.65,3.3),'wallStone','solid',True)
    box(f'watchtower-belt-{i}',(x,y,3.25),(1.94,1.94,.25),'wallCap')
    for u in (-1,0,1):
        for v in (-1,0,1):
            if u==0 and v==0:continue
            box(f'watchtower-merlon-{i}-{u}-{v}',(x+u*.64,y+v*.64,3.65),(.44,.44,.65),'wallCap',shadow=True)
    box(f'watchtower-slit-{i}',(x,y+.831,2.1),(.12,.018,.65),'iron')
    box(f'watchtower-banner-{i}',(x,y+.843,1.55),(.60,.022,1.9),'clothBlue')
    beam(f'watchtower-banner-star-{i}-a',(x,y+.87,.98),(x,y+.87,2.05),.022,'gold')
    beam(f'watchtower-banner-star-{i}-b',(x-.22,y+.87,1.5),(x+.22,y+.87,1.5),.022,'gold')

# Distinct buildings are composed from common architectural elements, never house copies.
# Location, height, wing, roof and facade combinations are authored per lot.
lots=[('northwest-lodge',14.4,14,3.6,3.0,3.8,'roofClay',0),('garden-row-house',16.5,9,3.4,3.2,4.5,'roofMoss',1),('west-courtyard-home',9.0,28.5,3.0,3.0,3.7,'roofClay',2),('northern-townhouse',36,8.2,3.0,3.3,4.7,'roofClay',3),('east-market-warehouse',48.5,25.2,4.2,3.8,4.2,'roofMoss',4),('east-market-tower-house',46.9,13.8,3.1,3.0,4.8,'roofClay',5),('southeast-courtyard-house',43,42.3,3.0,2.4,3.5,'roofClay',6),('southwest-lodge',19.0,41.0,3.2,3.0,4.2,'roofBlue',7)]
for name,x,y,w,d,h,roofmat,variant in lots:
    owner=collection('district-'+name,'market' if 'market' in name else 'residential')
    box(name+'-foundation',(x,y,.16),(w+.22,d+.22,.32),'stone','solid')
    box(name+'-walls',(x,y,h/2+.25),(w,d,h),'plaster','solid',True)
    roof(name,x,y,w+.42,d+.40,h+.28,h+1.80+(variant%2)*.35,roofmat)
    front=y+d/2+.018
    for j,xx in enumerate((x-w/2+.08,x+w/2-.08)):
        box(name+f'-corner-post-{j}',(xx,front,h/2+.25),(.12,.13,h),'timber')
    for j,z in enumerate((.52,h*.48,h+.15)):
        box(name+f'-cross-beam-{j}',(x,front,z),(w,.14,.12),'timber')
    box(name+'-door',(x+(-.35 if variant%2 else .35),front+.015,1.12),(.70,.035,1.75),'timber')
    for j,xx in enumerate((x-w*.28,x+w*.28)):
        box(name+f'-window-{j}',(xx,front+.03,h*.72),(.65,.04,.82),'glass')
        for side in (-1,1):box(name+f'-shutter-{j}-{side}',(xx+side*.40,front+.045,h*.72),(.16,.055,.9),'oak')
        box(name+f'-window-sill-{j}',(xx,front+.06,h*.72-.46),(.91,.18,.09),'wallCap')
    beam(name+'-gable-tie',(x-w/2,front+.08,h+.38),(x+w/2,front+.08,h+.38),.065,'timber')
    beam(name+'-gable-upright',(x,front+.08,h+.35),(x,front+.08,h+1.75),.065,'timber')
    for side in (-1,1):beam(name+f'-gable-brace-{side}',(x+side*w*.38,front+.08,h+.38),(x,front+.08,h+1.55),.045,'timber')
    if variant%3==0:
        box(name+'-porch-floor',(x,front+.6,.16),(w*.70,1.1,.25),'paving')
        roof(name+'-porch',x,front+.60,w*.8,1.3,2.20,2.65,roofmat)
        for j,xx in enumerate((x-w*.30,x+w*.30)):beam(name+f'-porch-post-{j}',(xx,front+1.1,.2),(xx,front+1.1,2.2),.07,'timber')
    elif variant%3==1:
        roof(name+'-side-wing',x+w*.58,y+.25,w*.58,d*.72,h*.62,h*.62+.95,roofmat)
        box(name+'-side-wing-wall',(x+w*.58,y+.25,h*.31+.15),(w*.5,d*.64,h*.62),'plaster','solid',True)
    else:
        box(name+'-upper-balcony',(x,front+.35,h*.49),(w*.7,.72,.12),'oak')
        box(name+'-balcony-rail',(x,front+.71,h*.49+.62),(w*.7,.07,.08),'timber')
        for j in range(7):box(name+f'-balcony-post-{j}',(x-w*.3+j*w*.6/6,front+.71,h*.49+.31),(.05,.05,.62),'timber')
    box(name+'-chimney',(x-w*.3,y-.3,h+1.15),(.4,.45,1.8),'stone')
    box(name+'-chimney-cap',(x-w*.3,y-.3,h+2.10),(.54,.59,.13),'wallCap')

# Market sheds form a compact browsing court; aisles stay open to the Merchant.
owner=collection('district-market-court','market')
for i,(x,y,w,cloth) in enumerate(((38.5,23.8,2.2,'clothRose'),(41.5,30.3,2.3,'clothOchre'),(45.2,26.0,1.9,'clothBlue'))):
    for j,xx in enumerate((x-w/2,x+w/2)):
        beam(f'stall-{i}-post-{j}',(xx,y,.10),(xx,y,2.25),.07,'timber')
        beam(f'stall-{i}-front-post-{j}',(xx,y+1.3,.10),(xx,y+1.3,2.10),.055,'timber')
    for j in range(8):
        xa=x-w/2+j*w/8;xb=xa+w/8
        mesh(f'stall-{i}-canopy-{j}',[(xa,y,2.3),(xb,y,2.3),(xb,y+1.4,2.05),(xa,y+1.4,2.05)],[[0,1,2,3]],cloth if j%2 else 'wallCap','overhead',True)
    box(f'stall-{i}-counter',(x,y+.85,.7),(w, .62,1.10),'oak','solid')
    for j in range(7):
        box(f'stall-{i}-goods-{j}',(x-w*.40+j*w*.8/6,y+.82,1.37),(.18,.25,.22),'marketAmber' if i==1 else 'flowers' if i==0 else 'shrineAzure')

for o in bpy.data.collections['guild-hall'].objects:
    if o.name.startswith('civic-processional-step-'):o['render_visible']=True
bpy.context.view_layer.update()
scene['district_authoring_version']=4
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved fortified rocky banks, eight varied buildings and three market stalls')
