"""Planted civic courts using the existing original foliage artwork and mesh contract."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];prefix='garden-v4-';scene=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
owner=bpy.data.collections.get('wayfarer-civic-gardens')
if owner is None:owner=bpy.data.collections.new('wayfarer-civic-gardens');scene.collection.children.link(owner)
owner['family']='vegetation'
def mesh(name,vs,fs,mat,role='decorative',shadow=False,uvs=None):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='GardenUV')
    for p in data.polygons:
        for j,li in enumerate(p.loop_indices):
            point=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=uvs[j] if uvs else (point.x/2,point.z/2)
    o=bpy.data.objects.new(prefix+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow;return o
def box(name,c,s,mat):
    x,y,z=c;a,b,h=[v/2 for v in s];vs=[(x+u*a,y+v*b,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(name,vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat)
def beam(name,a,b,r,role='decorative'):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.001:u=Vector((1,0,0))
    u.normalize();v=axis.cross(u).normalized();n=7
    vs=[tuple(p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))) for p in (a,b) for i in range(n)]
    return mesh(name,vs,[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],'timber',role,True)
for i,(x,y) in enumerate(((22.2,17.5),(32.1,17.5),(20.8,20.5),(36.8,21.5),(19.7,32.4),(35.1,31.7),(38.5,42.2),(13.5,18.0))):
    beam(f'tree-{i}-trunk',(x,y,.05),(x+.04,y-.06,2.9),.11,'solid')
    for j in range(4):
        a=(j+i*.37)*math.tau/4;dx,dy=math.cos(a)*.72,math.sin(a)*.72
        beam(f'tree-{i}-branch-{j}',(x,y,2.0),(x+dx,y+dy,3.25),.037)
    for j,(cx,cy,z,r) in enumerate(((x,y,3.62,1.04),(x-.48,y+.24,3.05,.76),(x+.48,y-.25,3.03,.80))):
        for side in range(2):
            a=.3+i*.13+side*math.pi/2;axis=Vector((math.cos(a)*r,math.sin(a)*r,0));up=Vector((0,0,r*.9));c=Vector((cx,cy,z))
            mesh(f'tree-{i}-leaf-{j}-{side}',[tuple(c-axis-up),tuple(c+axis-up),tuple(c+axis+up),tuple(c-axis+up)],[[0,1,2,3]],'foliageCutout','overhead',False,[(0,0),(1,0),(1,1),(0,1)])
    # Small planted foot rings make the tree/ground join deliberate.
    n=18;vs=[(x+math.cos(j*math.tau/n)*r,y+math.sin(j*math.tau/n)*r,.055) for r in (.16,.43) for j in range(n)]
    mesh(f'tree-{i}-ground-ring',vs,[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)],'soil')
for i,(x,y,w,d) in enumerate(((22.1,15.7,1.1,2.0),(32.0,15.8,1.1,2.0),(20.8,27.5,1.3,2.4),(34.8,27.4,1.3,2.4),(36.9,40.9,2.0,.65))):
    box(f'flowerbed-{i}',(x,y,.12),(w,d,.20),'soil')
    for j in (-1,1):
        box(f'flowerbed-{i}-long-edge-{j}',(x+j*w/2,y,.18),(.09,d+.12,.22),'stoneLight')
        box(f'flowerbed-{i}-short-edge-{j}',(x,y+j*d/2,.18),(w+.12,.09,.22),'stoneLight')
    for j in range(20):
        xx=x-w*.38+(j%4)*w*.76/3;yy=y-d*.4+(j//4)*d*.8/4
        box(f'flowerbed-{i}-leaves-{j}',(xx,yy,.28),(.19,.20,.16),'leafLight')
        box(f'flowerbed-{i}-bloom-{j}',(xx+.035,yy,.41),(.09,.09,.11),'flowers' if j%4 else 'clothOchre')
scene['garden_authoring_version']=4
# The same visibility intent should be legible in the saved Blender viewport.
for o in bpy.data.objects:
    if o.type=='MESH':o.hide_render=not bool(o.get('render_visible',True));o.hide_set(o.hide_render)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved eight planted civic trees and five flowering courts')
