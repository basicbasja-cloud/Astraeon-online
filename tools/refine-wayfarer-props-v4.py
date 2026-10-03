"""Street lamps, seating and planted edges placed around the reviewed routes."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];prefix='props-v4-';scene=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
owner=bpy.data.collections.get('wayfarer-street-furniture')
if owner is None:owner=bpy.data.collections.new('wayfarer-street-furniture');scene.collection.children.link(owner)
owner['family']='civic'
m=bpy.data.materials.get('lanternLight') or bpy.data.materials.new('lanternLight');m.diffuse_color=(1,.68,.30,1)
def mesh(name,vs,fs,mat,role='decorative',shadow=False):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='FurnitureUV')
    for p in data.polygons:
        axis=(0,1) if abs(p.normal.z)>.6 else (0,2) if abs(p.normal.y)>abs(p.normal.x) else (1,2)
        for li in p.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(v[axis[0]],v[axis[1]])
    o=bpy.data.objects.new(prefix+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow;return o
def box(name,x,y,z,w,d,h,mat,role='decorative',shadow=False):
    vs=[(x+u*w/2,y+v*d/2,z+t*h/2) for t in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(name,vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)
def beam(name,a,b,r,mat):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.001:u=Vector((1,0,0))
    u.normalize();v=axis.cross(u).normalized();n=8
    vs=[tuple(p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))) for p in (a,b) for i in range(n)]
    return mesh(name,vs,[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],mat,shadow=True)
lamps=[(23,18.8),(31,18.8),(20.6,24.2),(33.5,24.2),(24.65,33.8),(29.35,33.8),(24.65,39.8),(29.35,39.8),(15.5,23.7),(11.4,35.6),(39,29.2),(45.8,28.9),(40.6,16.6),(46,17.4),(36.8,39.4)]
for i,(x,y) in enumerate(lamps):
    box(f'lamp-{i}-plinth',x,y,.12,.35,.35,.24,'stoneLight')
    beam(f'lamp-{i}-stem',(x,y,.22),(x,y,2.3),.057,'iron')
    for z in (.35,1.92,2.13):beam(f'lamp-{i}-collar-{z}',(x,y,z),(x,y,z+.07),.085,'gold')
    box(f'lamp-{i}-glass',x,y,2.43,.23,.23,.37,'lanternLight')
    for j,(u,v) in enumerate(((-1,-1),(1,-1),(1,1),(-1,1))):beam(f'lamp-{i}-cage-{j}',(x+u*.145,y+v*.145,2.20),(x+u*.12,y+v*.12,2.66),.025,'iron')
    box(f'lamp-{i}-foot',x,y,2.19,.34,.34,.07,'iron')
    mesh(f'lamp-{i}-cap',[(x-.22,y-.22,2.67),(x+.22,y-.22,2.67),(x+.22,y+.22,2.67),(x-.22,y+.22,2.67),(x,y,2.91)],[[0,1,4],[1,2,4],[2,3,4],[3,0,4],[3,2,1,0]],'iron')
    beam(f'lamp-{i}-finial',(x,y,2.9),(x,y,3.06),.035,'gold')
for i,(x,y,w) in enumerate(((21.1,25.7,1.5),(33.8,25.7,1.5),(21.9,19,1.4),(32.4,19,1.4),(39,40.8,1.6),(12.5,24.9,1.4))):
    for j in range(4):box(f'bench-{i}-seat-{j}',x,y-.20+j*.13,.47,w,.105,.095,'oak',shadow=True)
    for j,z in enumerate((.82,1.02)):box(f'bench-{i}-back-{j}',x,y-.27,z,w,.07,.15,'oak',shadow=True)
    for j,xx in enumerate((x-w*.38,x+w*.38)):
        beam(f'bench-{i}-front-leg-{j}',(xx,y+.15,.04),(xx,y+.15,.5),.047,'iron')
        beam(f'bench-{i}-back-leg-{j}',(xx,y-.27,.04),(xx,y-.27,1.13),.047,'iron')
        beam(f'bench-{i}-arm-{j}',(xx,y-.27,.73),(xx,y+.2,.73),.04,'iron')
# Organic clusters at outer garden edges, clear of the stairs and services.
clusters=[(20.6,17.8),(33.5,17.9),(18.3,22),(36.5,23.4),(18.8,28.7),(35.7,28.9),(18.9,34),(34.2,33.5),(37.2,41.3),(42,18.8),(46,18.6),(15.6,21.1)]
for i,(x,y) in enumerate(clusters):
    for j,(dx,dy,r) in enumerate(((-.3,0,.37),(.27,.15,.42),(0,-.28,.31))):
        bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
        for v in bm.verts:v.co=Vector((x+dx+v.co.x*r,y+dy+v.co.y*r,.28+v.co.z*r*.8))
        data=bpy.data.meshes.new(prefix+f'plant-{i}-{j}');bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials['leafLight'])
        o=bpy.data.objects.new(prefix+f'plant-{i}-{j}',data);owner.objects.link(o);o['role']='decorative';o['shadow']=True
# Earlier layout moved the walkable bridge surface but left its visual deck,
# parapets and piers at the obsolete western gate. Relocate that source geometry
# to the existing southern bridge; keep its public contact surface unchanged.
for o in bpy.data.objects:
    if o.name.startswith('west-arrival-bridge-') and o.type=='MESH' and not o.get('surface_role') and not o.get('bridge_relocated_v4'):
        o.matrix_world=Matrix.Translation((20,21,0))@o.matrix_world;o['bridge_relocated_v4']=True
    if o.name in ['field-shore-stone-0','field-shore-stone-1','field-shore-stone-2']:
        o['render_visible']=False;o['role']='decorative';o['shadow']=False;o.hide_render=True;o.hide_set(True)
    if o.name=='west-arrival-bridge-deck' and not o.get('bridge_extended_v4'):
        inverse=o.matrix_world.inverted()
        for v in o.data.vertices:
            world=o.matrix_world@v.co
            if world.y>49.95:world.y=52.3
            v.co=inverse@world
        o['bridge_extended_v4']=True
    if o.name.startswith('west-arrival-bridge-parapet-') and not o.get('bridge_extended_v4'):
        inverse=o.matrix_world.inverted()
        for v in o.data.vertices:
            world=o.matrix_world@v.co
            if world.y>49.8:world.y=52.2
            v.co=inverse@world
        o['bridge_extended_v4']=True
    if o.name in ['west-arrival-bridge-pier-0-2','west-arrival-bridge-pier-1-2'] and not o.get('bridge_extended_v4'):
        o.matrix_world=Matrix.Translation((0,2,0))@o.matrix_world;o['bridge_extended_v4']=True
# The old broad forecourt otherwise draws an unsupported paving rectangle
# over the river beside the narrow crossing. Match its existing bridge width.
o=bpy.data.objects['arrival-forecourt'];inverse=o.matrix_world.inverted()
for v in o.data.vertices:
    world=o.matrix_world@v.co;world.x=max(25.9,min(28.1,world.x));v.co=inverse@world
scene['furniture_authoring_version']=4
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved 15 lanterns, six benches and twelve planted edges')
