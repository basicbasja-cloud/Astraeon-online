"""Paved city interior, planted tree courts and deeper editable facades.

Run once on the saved v47 source, then export. Navigation surfaces and service
anchors are retained. No building or player save is replaced.
"""
import bpy,bmesh,math,runpy
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('organic_town_version')==47 and not scene.get('paved_city_version')
owner=bpy.data.collections['court-terrain'];root=None
def mesh(name,vs,fs,mat,role='decorative',shadow=True):
    data=bpy.data.meshes.new('city-v48-'+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
    o=bpy.data.objects.new('city-v48-'+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow
    if root:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
    world=root.matrix_world if root else Matrix.Identity(4);size=3
    for f in data.polygons:
        n=(world.to_3x3()@f.normal).normalized()
        for li in f.loop_indices:
            p=world@data.vertices[data.loops[li].vertex_index].co
            data.uv_layers.active.data[li].uv=(p.x/size,p.y/size) if abs(n.z)>.65 else (p.x/size,p.z/size) if abs(n.y)>abs(n.x) else (p.y/size,p.z/size)
    return o
def box(name,c,size,mat,role='decorative',shadow=True):
    x,y,z=c;a,b,h=[v/2 for v in size]
    return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)
def beam(name,a,b,width,mat):
    a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,1,0))).normalized()*width/2;w=v.cross(u).normalized()*width/2
    return mesh(name,[tuple(p+i*u+j*w) for p in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
def ring(name,x,y,z,r,h,mat,sides=12,upper=None):
    upper=r if upper is None else upper
    vs=[(x+rr*math.cos(k*math.tau/sides),y+rr*math.sin(k*math.tau/sides),zz) for rr,zz in [(r,z),(upper,z+h)] for k in range(sides)]
    return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[k,(k+1)%sides,(k+1)%sides+sides,k+sides] for k in range(sides)],mat)

# Continuous paving inside the curtain wall, leaving a planted shoreline belt.
# The concept has stone streets and courts, rather than buildings on lawn pads.
m=bpy.data.materials.new('cityPaving');m.diffuse_color=(.68,.64,.55,1)
outline=[(14,54),(11,36),(17,19),(33,11),(48,11),(54,9),(60,11),(78,11),(99,19),(103,46),(103,78),(83,89),(58.6,89),(54,92),(49.4,89),(26,87),(15,73),(21,54)]
o=mesh('continuous-stone-interior',[(x,y,.025) for x,y in outline],[list(range(len(outline)))],'cityPaving',shadow=False);o['surface_role']='plaza';o['walkable']=True
# Narrow old streets now sit within a connected urban fabric. Their contacts
# remain authoritative while the base paving joins their frontages visually.
for o in owner.objects:
    if o.get('road_segment') and o.data.materials[0].name=='paving':
        o.data.materials[0]=m
    elif o.get('surface_role')=='plaza' and o.data.materials[0].name=='paving':o.data.materials[0]=m

# Individual tree pits are added by plant-paved-courts-v48.py after this pass.

# Distinct facade depth: splayed bay windows, corbels, shaded recesses, shutters,
# dressed stone at the foundations and chimneys with real stacks/caps.
for i,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
    owner=c;root=bpy.data.objects[c.name+'-placement'];walls=next(o for o in c.objects if o.name.endswith('-walls'));inv=root.matrix_world.inverted();vs=[inv@walls.matrix_world@v.co for v in walls.data.vertices]
    x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);x,y=(x0+x1)/2,(y0+y1)/2;w,d=x1-x0,y1-y0;h=max(v.z for v in vs)
    for side in (-1,1):
        xx=x+side*w*.29;zz=h*.77
        box(c.name+'-window-recess'+str(side),(xx,y1+.29,zz),(1.05,.20,1.39),'timber',shadow=False)
        box(c.name+'-window-glass'+str(side),(xx,y1+.405,zz),(.81,.035,1.12),'glass',shadow=False)
        for dx in (-.48,.48):box(c.name+'-window-jamb'+str((side,dx)),(xx+dx,y1+.47,zz),(.12,.18,1.44),'oak')
        for dz in (-.67,.67):box(c.name+'-window-lintel'+str((side,dz)),(xx,y1+.47,zz+dz),(1.08,.18,.14),'oak')
        box(c.name+'-window-mullion'+str(side),(xx,y1+.46,zz),(.055,.08,1.22),'stoneLight',shadow=False)
        box(c.name+'-window-transom'+str(side),(xx,y1+.46,zz-.09),(.87,.08,.055),'stoneLight',shadow=False)
        box(c.name+'-shutter'+str(side),(xx+side*.70,y1+.36,zz),(.34,.18,1.32),'oak')
        beam(c.name+'-jetty-corbels'+str(side),(xx,y1+.08,h*.47),(xx,y1+.48,h*.57),.16,'timber')
        # Diagonal framing is structurally attached to the upper storey.
        beam(c.name+'-upper-brace'+str(side),(x+side*w*.45,y1+.35,h*.58),(x+side*w*.24,y1+.35,h*.98),.12,'timber')
    box(c.name+'-foot-course',(x,y1+.10,.20),(w+.13,.23,.27),'stone')
    for j in range(max(3,int(w/.72))):
        xx=x0+.25+j*(w-.5)/(max(3,int(w/.72))-1)
        box(c.name+'-dressed-foot-'+str(j),(xx,y1+.23,.39),(.62,.12,.32),'stoneLight',shadow=False)
    # Slim, offset chimneys vary silhouettes without filling the walking route.
    xx=x+(-1 if i%2 else 1)*w*.26;yy=y-d*.17
    roof=max((inv@o.matrix_world@v.co).z for o in c.objects if o.type=='MESH' and o.get('render_visible',True) for v in o.data.vertices)
    box(c.name+'-chimney-stack',(xx,yy,roof-.10),(.61,.67,1.55),'stone')
    box(c.name+'-chimney-collar',(xx,yy,roof+.56),(.76,.81,.15),'stoneLight')
    box(c.name+'-chimney-dark',(xx,yy,roof+.64),(.51,.57,.04),'iron',shadow=False)
    for side in (-1,1):box(c.name+'-chimney-support'+str(side),(xx+side*.25,yy,roof+.82),(.09,.60,.30),'stoneLight')
    box(c.name+'-chimney-cap',(xx,yy,roof+1.0),(.85,.89,.16),'stoneLight')
    if i in (0,2,5,8):
        # An attached polygonal oriel: three glazing faces, deep sill and hood.
        xx=x+(.18*w if i%2 else -.18*w);zz=h*.64;front=y1+.72;back=y1+.26
        poly=[(xx-.64,back),(xx+.64,back),(xx+.64,front-.14),(xx+.43,front),(xx-.43,front),(xx-.64,front-.14)]
        vs=[(a,b,z) for z in (zz,zz+1.3) for a,b in poly]
        mesh(c.name+'-oriel',vs,[list(range(5,-1,-1)),list(range(6,12))]+[[k,(k+1)%6,(k+1)%6+6,k+6] for k in range(6)],'glass','overhead')
        for k,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
            beam(c.name+'-oriel-sill'+str(k),(*a,zz),(*b,zz),.16,'oak');beam(c.name+'-oriel-crown'+str(k),(*a,zz+1.3),(*b,zz+1.3),.16,'oak');beam(c.name+'-oriel-mullion'+str(k),(*a,zz),(*a,zz+1.3),.085,'timber')
        mesh(c.name+'-oriel-hood',[(a,b,zz+1.35) for a,b in poly]+[(xx,back,zz+1.8)],[[k,(k+1)%6,6] for k in range(6)],'slate','overhead')

# Hall roof gallery and crowned corner turrets strengthen the civic silhouette.
owner=bpy.data.collections['guild-hall'];root=None
for side in (-1,1):
    x=54+side*6.65;y=22.0
    ring('hall-corner-drum'+str(side),x,y,6.0,.66,2.4,'civicIvory')
    ring('hall-corner-cornice'+str(side),x,y,8.28,.79,.18,'civicGold')
    ring('hall-corner-roof'+str(side),x,y,8.46,.88,2.3,'civicSlate',upper=.05)
    ring('hall-corner-finial'+str(side),x,y,10.75,.10,.40,'civicGold',upper=.015)
    for j in range(5):
        yy=12.9+j*1.65
        box('hall-roof-gallery-post'+str((side,j)),(54+side*4.25,yy,10.80),(.20,.20,.76),'civicIvory')
    box('hall-roof-gallery-rail'+str(side),(54+side*4.25,16.2,11.18),(.25,7.0,.17),'civicGold')
scene['paved_city_version']=48;scene['layout_id']='wayfarer-paved-civic-town-v48'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved paved city, planted tree courts and facade/oriel/chimney depth')
