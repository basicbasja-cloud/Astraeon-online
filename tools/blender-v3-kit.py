"""Shared procedural authoring primitives; no runtime or map-specific data."""
import bpy,bmesh
scene=bpy.context.scene
materials={}
for name,color in {'stone':(0.66,0.59,0.45,1),'stoneLight':(.85,.77,.58,1),'blue':(.10,.27,.42,1),'gold':(.83,.60,.22,1),'wood':(.29,.18,.10,1),'leaf':(.19,.38,.21,1),'grass':(.34,.43,.24,1),'paving':(.60,.53,.40,1)}.items():
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color;materials[name]=m
def family(id,name):
 c=bpy.data.collections.new(id);scene.collection.children.link(c);c['family']=name;return c
def mesh(c,id,vertices,faces,material,role='decorative',shadow=True):
 m=bpy.data.meshes.new(id);m.from_pydata(vertices,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free();o=bpy.data.objects.new(id,m);c.objects.link(o);o.data.materials.append(materials[material]);o['role']=role;o['shadow']=shadow;return o
def box(c,id,center,size,material,role='solid',shadow=True):
 x,y,z=center;a,b,h=[v/2 for v in size]
 verts=[(x+sx*a,y+sy*b,z+sz*h) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
 return mesh(c,id,verts,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],material,role,shadow)
def empty(c,id,position,kind):
 o=bpy.data.objects.new(id,None);c.objects.link(o);o.location=position;o.empty_display_type='SPHERE';o.empty_display_size=.15;o['kind']=kind;return o
