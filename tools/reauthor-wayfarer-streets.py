"""Connect civic spaces and add individually composed building details in the saved town."""
import bpy, bmesh, math, json
from mathutils import Vector, Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
assert scene['civic_authoring_version']==4
prefix='street-v4-'
for o in list(bpy.data.objects):
    if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
terrain=bpy.data.collections['court-terrain']
owner=bpy.data.collections.get('wayfarer-street-details')
if owner is None:
    owner=bpy.data.collections.new('wayfarer-street-details');scene.collection.children.link(owner)
owner['family']='civic'
for name,color in {'gardenGrass':(.48,.56,.32,1),'streetIvory':(.89,.82,.66,1),'streetSlate':(.24,.39,.51,1),'streetOchre':(.82,.53,.25,1),'statueIvory':(.94,.88,.74,1)}.items():
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color

def mesh(name,vs,fs,mat,collection=owner,role='decorative',shadow=False,surface=None):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='World-scale-UV')
    for face in data.polygons:
        n=face.normal;axes=(0,1) if abs(n.z)>.65 else (0,2) if abs(n.y)>abs(n.x) else (1,2)
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p[axes[0]]/3,p[axes[1]]/3)
    obj=bpy.data.objects.new(prefix+name,data);collection.objects.link(obj);obj['role']=role;obj['shadow']=shadow
    if surface:obj['surface_role']=surface;obj['walkable']=True
    return obj
def box(name,c,s,mat='streetIvory',role='decorative',shadow=False):
    x,y,z=c;a,b,h=[v/2 for v in s]
    return mesh(name,[(x+u*a,y+v*b,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role=role,shadow=shadow)
def beam(name,a,b,r,mat='streetIvory',sides=6):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.001:u=Vector((1,0,0))
    u.normalize();v=axis.cross(u).normalized()
    vs=[tuple(p+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))) for p in (a,b) for i in range(sides)]
    return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[i,(i+1)%sides,(i+1)%sides+sides,i+sides] for i in range(sides)],mat)
def surface(name,points,mat='paving',z=.045):
    return mesh(name,[(x,y,z) for x,y in points],[list(range(len(points)))],mat,terrain,surface='plaza')
def paving(name,x0,y0,x1,y1):return surface(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)])

# Continuous generous public space, framed by planted courts rather than grass seams.
surface('civic-square',[(27+math.cos(i*math.tau/48)*7.3,25.5+math.sin(i*math.tau/48)*6.7) for i in range(48)])
paving('hall-processional-lane',23.7,14.28,30.3,21.9)
paving('west-shopping-street',10.0,22.0,23.8,25.8)
paving('east-shopping-street',32.0,25.0,45.0,29.1)
paving('inn-forge-connection',11.8,25.0,15.4,32.0)
paving('south-residential-street',28.8,38.2,46.3,41.2)
paving('east-residential-connection',43.9,29,47.2,41.0)
paving('west-residential-lane',16,29,19.5,40.2)

# Calm ground colour reduces large noisy grass patches at the gameplay camera.
grass=bpy.data.materials['grass']
if grass.get('texture_json'):del grass['texture_json']
grass.diffuse_color=(.48,.56,.32,1)

# Low borders divide garden courts, and form proper masonry banks for canal edges.
for i,(x0,y0,x1,y1) in enumerate(((23.35,14.8,23.35,21.1),(30.65,14.8,30.65,21.1),(19.9,21.9,23.4,21.9),(31.7,22.0,35.2,22.0),(21.85,30.0,21.85,34.3),(32.15,30,32.15,36.1))):
    box(f'garden-edge-{i}',((x0+x1)/2,(y0+y1)/2,.17),(max(.22,abs(x1-x0)),max(.22,abs(y1-y0)),.30),'streetIvory')
    box(f'garden-edge-cap-{i}',((x0+x1)/2,(y0+y1)/2,.34),(max(.3,abs(x1-x0)+.1),max(.3,abs(y1-y0)+.1),.09),'stoneLight')

# Authored variants: bay windows, balconies, dormers and different commercial awnings.
# Existing complete houses are neither cloned nor displaced.
blocks=[('east-inn',2,'clothOchre'),('artisan-workshop',0,'clothRose'),('market-shop',1,'clothBlue'),('willow-house',3,'clothRose'),('residence',4,'clothOchre'),('civic-home-west',5,'clothBlue'),('civic-shop-east',6,'clothOchre'),('east-row-home',7,'clothRose'),('inn-side-home',8,'clothBlue')]
for block,variant,cloth in blocks:
    col=bpy.data.collections.get(block)
    if not col:continue
    walls=[o for o in col.objects if o.type=='MESH' and o['role']=='solid' and 'wall' in o.name and o.get('render_visible',True)]
    if not walls:continue
    wall=max(walls,key=lambda o:len(o.data.vertices))
    vs=[wall.matrix_world@v.co for v in wall.data.vertices]
    x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs)
    top=max(v.z for v in vs);cx=(x0+x1)/2;cy=(y0+y1)/2;ww=x1-x0
    # South-facing storefront. Awnings vary by business; residentials get timber balconies.
    if block in ('east-inn','artisan-workshop','market-shop','civic-shop-east'):
        aw=ww*.76;y=y1+.03;h=top*.52
        for stripe in range(9):
            xa=cx-aw/2+stripe*aw/9;xb=xa+aw/9
            mesh(f'{block}-awning-{stripe}',[(xa,y,h+.35),(xb,y,h+.35),(xb,y+.9,h),(xa,y+.9,h)],[[0,1,2,3]],cloth if stripe%2==0 else 'streetIvory')
            box(f'{block}-valance-{stripe}',((xa+xb)/2,y+.9,h-.08),(aw/9,.025,.16),cloth if stripe%2==0 else 'streetIvory')
        for j,xx in enumerate((cx-aw/2,cx+aw/2)):
            beam(f'{block}-awning-post-{j}',(xx,y+.85,.15),(xx,y+.85,h+.08),.045,'timber')
        if block=='east-inn':
            box('inn-balcony-floor',(cx,y1+.46,top*.63),(ww*.65,1.0,.16),'oak')
            for j in range(9):box(f'inn-balcony-baluster-{j}',(cx-ww*.3+j*ww*.6/8,y1+.91,top*.63+.39),(.055,.06,.70),'timber')
            box('inn-balcony-rail',(cx,y1+.91,top*.63+.78),(ww*.66,.09,.10),'oak')
    else:
        x=cx+(-.25 if variant%2 else .25)
        box(f'{block}-bay',(x,y1+.23,top*.52),(ww*.50,.50,top*.48),'plaster')
        for j,xx in enumerate((x-ww*.16,x+ww*.16)):
            box(f'{block}-bay-glass-{j}',(xx,y1+.495,top*.56),(ww*.20,.02,.72),'glass')
            for sign in (-1,1):box(f'{block}-shutter-{j}-{sign}',(xx+sign*ww*.12,y1+.52,top*.56),(.10,.03,.82),'oak')
        box(f'{block}-bay-sill',(x,y1+.52,top*.56-.40),(ww*.53,.14,.10),'streetIvory')
        box(f'{block}-flower-box',(x,y1+.63,top*.56-.54),(ww*.48,.20,.17),'timber')
        for j in range(7):
            xx=x-ww*.20+j*ww*.4/6
            box(f'{block}-flowers-{j}',(xx,y1+.63,top*.56-.38),(.14,.17,.17),'flowers' if j%3 else 'leafLight')
    # Different chimney height, ridge position and caps avoid repeated roof silhouette.
    x=x0+.45 if variant%2 else x1-.45
    box(f'{block}-chimney',(x,cy-.35,top+.7+(variant%3)*.15),(.38,.43,1.7),'stone')
    box(f'{block}-chimney-cap',(x,cy-.35,top+1.60+(variant%3)*.15),(.52,.57,.14),'streetIvory')

# Celestial fountain: replace the tiny pole figure with a readable winged monument.
f=bpy.data.collections['astral-fountain']
for o in f.objects:
    if o.type=='MESH' and any(s in o.name for s in ('sculpture','wing-feather','crown-compass')):
        o['render_visible']=False;o['shadow']=False;o['role']='decorative'
x,y=27,25.5
beam('statue-plinth',(x,y,.5),(x,y,1.9),.29,'statueIvory',8)
# A flowing bell-shaped robe, shoulders, head and raised arms.
vs=[(x+math.cos(i*math.tau/12)*r,y+math.sin(i*math.tau/12)*r,z) for r,z in ((.38,1.78),(.14,2.8),(.23,3.16)) for i in range(12)]
mesh('statue-robes',vs,[[i+k*12,(i+1)%12+k*12,(i+1)%12+(k+1)*12,i+(k+1)*12] for k in range(2) for i in range(12)],'statueIvory')
beam('statue-neck',(x,y,3.12),(x,y,3.36),.10,'statueIvory')
beam('statue-head',(x,y,3.36),(x,y,3.69),.18,'statueIvory',12)
for side in (-1,1):
    beam(f'statue-arm-{side}',(x+side*.2,y,3.08),(x+side*.58,y,3.40),.09,'statueIvory')
    beam(f'statue-hand-{side}',(x+side*.58,y,3.40),(x+side*.65,y,3.65),.07,'statueIvory')
    wing=[(x+side*.18,y-.16,2.85),(x+side*.65,y-.18,3.5),(x+side*1.45,y-.18,4.3),(x+side*1.15,y-.18,3.2),(x+side*.62,y-.18,2.7)]
    mesh(f'statue-wing-{side}',wing,[[0,1,2,3,4]],'statueIvory')
    for j in range(7):
        t=j/7
        beam(f'statue-feather-{side}-{j}',(x+side*(.24+t*.45),y-.205,2.91+t*.45),(x+side*(.68+t*.75),y-.205,3.05+t*1.13),.035,'streetIvory')

route=json.loads(scene['route_json'])
for point in route:
    if point['name']=='Residential':point['position']=[38,39];point.pop('point',None)
scene['route_json']=json.dumps(route)
scene['street_authoring_version']=4
entry=bpy.data.objects['guild-hall-entrance']
for o in (entry,bpy.data.objects[entry['approach_id']]):
    world=o.matrix_world.translation.copy();world.z=.455
    o.location=o.parent.matrix_world.inverted()@world if o.parent else world
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved connected streets, garden banks, business awnings and unique residential details')
