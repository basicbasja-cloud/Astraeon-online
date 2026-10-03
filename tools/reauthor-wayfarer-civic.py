"""Targeted civic architecture pass on the current saved scene; never rebuild the town.

Original parts remain hidden references. Services and authored floor contacts survive.
Run through run-bpy-task.py, then export-world-v3.py.
"""
import math
import json
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene['world_id'] == 'wayfarer-spatial'
owner = bpy.data.collections['guild-hall']
parent = bpy.data.objects['guild-hall-placement']
inverse = parent.matrix_world.inverted()
prefix = 'civic-v4-'
for o in list(owner.objects):
    if o.name.startswith(prefix):
        bpy.data.objects.remove(o, do_unlink=True)
    elif o.type == 'MESH':
        o['render_visible'] = o.name.startswith('civic-processional-step-')
        o['role'] = 'decorative'
        o['shadow'] = False

for name, color in {
    'civicIvory': (.91, .85, .70, 1), 'civicShadow': (.60, .64, .64, 1),
    'civicSlate': (.14, .28, .43, 1), 'civicSlateLight': (.23, .39, .52, 1),
    'civicGlass': (.13, .28, .38, 1), 'civicGlassLight': (.43, .70, .73, 1),
    'civicGold': (.93, .70, .32, 1), 'civicDoor': (.20, .13, .085, 1),
}.items():
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = color

def mesh(name, vs, fs, material, role='decorative', shadow=False):
    data = bpy.data.meshes.new(prefix + name)
    data.from_pydata([inverse @ Vector(v) for v in vs], [], fs)
    bm = bmesh.new(); bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces)); bm.to_mesh(data); bm.free()
    data.materials.append(bpy.data.materials[material])
    obj = bpy.data.objects.new(prefix + name, data); owner.objects.link(obj)
    obj.parent = parent; obj['role'] = role; obj['shadow'] = shadow
    return obj

def box(name, c, size, material='civicIvory', role='decorative', shadow=False):
    x,y,z=c; a,b,h=[s/2 for s in size]
    vs=[(x+u*a,y+v*b,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(name, vs, [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],material,role,shadow)

def beam(name,a,b,r=.035,material='civicGold',sides=6):
    a,b=Vector(a),Vector(b); axis=(b-a).normalized()
    u=axis.cross(Vector((0,0,1)))
    if u.length<.001:u=Vector((1,0,0))
    u.normalize(); v=axis.cross(u).normalized()
    vs=[tuple(p+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))) for p in (a,b) for i in range(sides)]
    return mesh(name,vs,[list(reversed(range(sides))),list(range(sides,2*sides))]+[[i,(i+1)%sides,(i+1)%sides+sides,i+sides] for i in range(sides)],material)

def roof(name,cx,y0,y1,width,eave,ridge):
    mesh(name+'-gable',[(cx-width/2,y1,eave),(cx+width/2,y1,eave),(cx,y1,ridge)],[[0,1,2]],'civicIvory')
    for side in (-1,1):
        x=cx+side*width/2
        mesh(name+f'-slope-{side}',[(x,y0,eave),(x,y1,eave),(cx,y1,ridge),(cx,y0,ridge)],[[0,1,2,3]],'civicSlate' if side<0 else 'civicSlateLight','overhead',True)
        beam(name+f'-verge-{side}',(x,y1+.015,eave),(cx,y1+.015,ridge),.045)
        beam(name+f'-eave-{side}',(x,y0,eave),(x,y1,eave),.06,'civicIvory')
        # Authored blue slate courses and narrow raised ribs, readable at distance.
        for k in range(1,7):
            t=k/7
            beam(name+f'-course-{side}-{k}',(x+(cx-x)*t,y0,eave+(ridge-eave)*t),(x+(cx-x)*t,y1,eave+(ridge-eave)*t),.018,'civicSlate')
        for k in range(1,5):
            yy=y0+(y1-y0)*k/5
            beam(name+f'-rib-{side}-{k}',(x,yy,eave+.015),(cx,yy,ridge+.015),.025)
    beam(name+'-ridge',(cx,y0,ridge+.035),(cx,y1,ridge+.035),.065)

def spire(name,x,y,z,width,height):
    # Octagonal slate crown with gold hips; each tower has its own silhouette.
    vs=[(x+math.cos(i*math.tau/8)*width/2,y+math.sin(i*math.tau/8)*width/2,z) for i in range(8)]+[(x,y,z+height)]
    mesh(name,vs,[[i,(i+1)%8,8] for i in range(8)],'civicSlate','overhead',True)
    for i in range(8):beam(name+f'-hip-{i}',vs[i],vs[8],.027)
    beam(name+'-finial',(x,y,z+height),(x,y,z+height+.65),.045)
    beam(name+'-crossbar',(x-.20,y,z+height+.42),(x+.20,y,z+height+.42),.025)

def arch(name,x,y,bottom,width,height,material='civicGlass',side=False):
    # Pointed lancet, including its inset surround; no rectangular window sticker.
    def p(u,z):return (x,y+u,z) if side else (x+u,y,z)
    r=width/2; shoulder=bottom+height*.66
    pts=[p(-r,bottom),p(r,bottom),p(r,shoulder),p(r*.78,shoulder+height*.12),p(0,bottom+height),p(-r*.78,shoulder+height*.12),p(-r,shoulder)]
    mesh(name+'-glass',pts,[list(range(7))],material)
    for i in range(7):beam(name+f'-stone-{i}',pts[i],pts[(i+1)%7],.06,'civicIvory')
    beam(name+'-mullion',p(0,bottom),p(0,bottom+height),.025)
    beam(name+'-transom',p(-r,shoulder-.25),p(r,shoulder-.25),.025)

# Nave, unequal aisle masses, and an open public terrace in front.
box('nave',(27,7.0,3.75),(6.4,8.0,6.6),'civicIvory','solid',True)
roof('nave',27,2.72,11.28,7.0,7.1,10.2)
for side in (-1,1):
    x=27+side*4.5
    box(f'aisle-{side}',(x,7.8,2.45),(2.8,6.4,4.0),'civicShadow','solid',True)
    roof(f'aisle-{side}',x,4.35,11.15,3.3,4.6,6.2)
    box(f'aisle-cornice-{side}',(x,11.035,4.35),(2.9,.18,.24))
    for i,yy in enumerate((5.2,7.5,9.8)):
        xx=27+side*6.05
        box(f'buttress-{side}-{i}',(xx,yy,2.5),(.42,.62,4.1))
        box(f'buttress-foot-{side}-{i}',(xx,yy,.75),(.62,.85,.6),'civicShadow')
        spire(f'buttress-pinnacle-{side}-{i}',xx,yy,4.65,.55,1.0)
        arch(f'aisle-side-window-{side}-{i}',xx+side*.035,yy-.72,1.6,.8,2.3,side=True)
    for i,xx in enumerate((x-.65,x+.65)):
        arch(f'aisle-front-window-{side}-{i}',xx,11.045,1.3,.78,2.5)

# South facade: recessed paired doors, deep archivolt and rose compass above.
box('entry-recess',(27,11.018,2.0),(2.08,.07,3.1),'civicDoor')
arch('portal',27,11.065,.5,2.1,3.8,'civicDoor')
for i,xx in enumerate((26.55,27.45)):
    box(f'door-leaf-{i}',(xx,11.08,1.70),(.84,.04,2.35),'civicDoor')
    for z in (.75,1.8,2.6):box(f'door-hinge-{i}-{z}',(xx,11.11,z),(.77,.035,.06),'civicGold')
    box(f'door-pull-{i}',(xx+( .25 if i==0 else -.25),11.13,1.6),(.05,.05,.22),'civicGold')
for side in (-1,1):
    x=27+side*1.7
    box(f'front-pier-{side}',(x,11.14,3.8),(.52,.48,6.7))
    box(f'front-pier-base-{side}',(x,11.14,.74),(.76,.76,.6),'civicShadow')
    spire(f'front-pier-spire-{side}',x,11.14,7.2,.65,1.6)
    box(f'blue-banner-{side}',(x+side*.50,11.15,3.8),(.58,.025,2.3),'clothBlue')
    for j in range(8):
        a=j*math.tau/8
        beam(f'banner-star-{side}-{j}',(x+side*.50,11.19,4.05),(x+side*.50+math.cos(a)*(.23 if j%2==0 else .12),11.19,4.05+math.sin(a)*(.35 if j%2==0 else .17)),.02)
rose=[(27+math.cos(i*math.tau/32)*1.12,11.055,5.65+math.sin(i*math.tau/32)*1.12) for i in range(32)]
mesh('rose-glass',rose,[list(range(32))],'civicGlassLight')
for i in range(32):beam(f'rose-frame-{i}',rose[i],rose[(i+1)%32],.07,'civicIvory')
for i in range(12):
    a=i*math.tau/12
    beam(f'rose-ray-{i}',(27,11.11,5.65),(27+math.cos(a)*1.02,11.11,5.65+math.sin(a)*1.02),.025)
beam('rose-vertical',(27,11.14,4.95),(27,11.14,6.35),.05)
beam('rose-horizontal',(26.3,11.14,5.65),(27.7,11.14,5.65),.05)
arch('gable-lancet',27,11.29,7.75,.72,1.55)

# Towers frame the nave without hiding the front public stair.
for i,(x,y,size,height) in enumerate(((21.8,9.7,1.8,7.7),(32.1,9.1,1.6,6.8))):
    box(f'tower-{i}',(x,y,(height+.45)/2),(size,size,height-.45),'civicIvory','solid',True)
    for j,z in enumerate((.7,3.0,5.25,height-.25)):
        box(f'tower-belt-{i}-{j}',(x,y,z),(size+.20,size+.20,.18),'civicShadow')
    for j,z in enumerate((1.6,4.0,height-2.1)):
        arch(f'tower-front-lancet-{i}-{j}',x,y+size/2+.015,z,.60,1.45)
        arch(f'tower-side-lancet-{i}-{j}',x+size/2+.015,y,z,.60,1.45,side=True)
    spire(f'tower-crown-{i}',x,y,height,size+ .48,3.0 if i==0 else 2.6)

# A rear bell lantern adds a third height and keeps the Hall dominant on the skyline.
box('lantern',(27,5.1,9.2),(1.6,1.6,2.2),'civicIvory')
arch('lantern-front',27,5.91,8.45,.85,1.45,'civicDoor')
spire('lantern-crown',27,5.1,10.45,2.1,3.25)
scene['ambient']=.64
scene['sun_strength']=.40
scene['sun_cast_x']=.55
scene['sun_cast_y']=.32
route=json.loads(scene['route_json'])
for checkpoint in route:
    if checkpoint.get('name')=='Residential':
        checkpoint['position']=[38,39]
        checkpoint.pop('point',None)
scene['route_json']=json.dumps(route)
scene['civic_authoring_version']=4
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved reauthored Hall: nave, aisles, lancets, rose, bell lantern and unequal towers')
