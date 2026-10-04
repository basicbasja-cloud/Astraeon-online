"""Concept-led masonry spillways and falling water, in the saved source.

Water emerges below the walkable city floor, follows the bank slope and ends
in the river. No actor route, shore collider or bridge is overridden.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('continuous_bank_version')==49
PREFIX='falls-v49-';owner=bpy.data.collections['wayfarer-v44-detail']
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for d in list(bpy.data.meshes):
 if d.name.startswith(PREFIX) and not d.users:bpy.data.meshes.remove(d)
mat=bpy.data.materials.get('riverCascade') or bpy.data.materials.new('riverCascade')
mat.diffuse_color=(.59,.82,.84,1)
mat['texture_json']=json.dumps({'file':'assets/wayfarer-cascade-v1.svg','grid':[1,1],'tile':0,'worldSize':2.4,'alphaCutoff':.05})
foam=bpy.data.materials.get('riverFoam') or bpy.data.materials.new('riverFoam')
foam.diffuse_color=(.79,.91,.87,1)
foam['texture_json']=json.dumps({'file':'assets/wayfarer-river-foam-v1.svg','grid':[1,1],'tile':0,'worldSize':2.4})
terrain=bpy.data.collections['court-terrain']
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
outline=[ground.matrix_world@ground.data.vertices[i].co for i in json.loads(ground['outline_vertex_indices'])]
water=next(o for o in terrain.objects if o.get('surface_role')=='water')
water_z=min((water.matrix_world@v.co).z for v in water.data.vertices)
def mesh(name,vs,fs,material,uvs=None):
 d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(vs,[],fs)
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
 d.materials.append(bpy.data.materials[material]);d.uv_layers.new(name='PhysicalUV')
 for f in d.polygons:
  for li in f.loop_indices:
   i=d.loops[li].vertex_index;p=d.vertices[i].co
   d.uv_layers.active.data[li].uv=uvs[i] if uvs else (p.x/3,p.z/3)
 o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o['role']='decorative';o['shadow']=False
 return o
for number,xy in enumerate([(39,91.2),(72,92),(12,65)]):
 desired=Vector((*xy,0));best=None
 for a,b in zip(outline,outline[1:]+outline[:1]):
  tangent=(b-a).normalized();p=a+(b-a)*max(0,min(1,(desired-a).dot(b-a)/(b-a).length_squared))
  distance=(p-desired).length
  if best is None or distance<best[0]:best=(distance,p,tangent)
 _,p,t=best;n=Vector((t.y,-t.x,0));width=1.35 if number==2 else 1.85
 def point(side,offset,z):
  q=p+t*side+n*offset;return(q.x,q.y,z)
 # Stone voussoirs surround a recessed culvert mouth underneath the city.
 center=-1.12;r=width*.5;inner=r*.88
 mesh(str(number)+'-throat',[point(-inner,.7,center-.52),point(inner,.7,center-.52),point(inner,.7,center),point(-inner,.7,center)],[[0,1,2,3]],'civicDoor')
 for j in range(9):
  a=j*math.pi/9;b=(j+1)*math.pi/9
  vs=[point(math.cos(angle)*radius,offset,center+math.sin(angle)*radius) for offset in (.50,.88) for radius in (inner,r+.25) for angle in (a,b)]
  mesh(str(number)+'-arch-'+str(j),vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],'wallCap' if j%3 else 'stone')
 # A small, stepped stream bends out past the rock before reaching the river.
 profile=[(-1.1,.92,.92),(-1.55,1.05,1.0),(-2.8,1.34,.9),(-4.3,1.72,.96),(-5.6,2.08,1.05),(water_z+.035,2.47,1.25)]
 vs=[];uv=[]
 for z,offset,span in profile:
  for side in (-1,1):vs.append(point(side*width*.5*span,offset,z));uv.append(((side+1)/2,z/2.4))
 mesh(str(number)+'-stream',vs,[[j*2,j*2+1,j*2+3,j*2+2] for j in range(len(profile)-1)],'riverCascade',uv)
 # Broad foam patches sit on the river, with scalloped rather than square edges.
 for j in range(3):
  c=p+n*(2.5+j*.55);radius=width*(.68+j*.13);vs=[(c.x,c.y,water_z+.05+j*.002)];uv=[(.5,.5)]
  for k in range(12):
   a=k*math.tau/12;r0=radius*(.84+.12*math.sin(k*2.7+j));q=c+t*(math.cos(a)*r0)+n*(math.sin(a)*r0*.46)
   vs.append((q.x,q.y,water_z+.05+j*.002))
   uv.append((.5+math.cos(a)*r0/radius*.5,.5+math.sin(a)*r0/radius*.5))
  mesh(str(number)+'-foam-'+str(j),vs,[[0,k+1,(k+1)%12+1] for k in range(12)],'riverFoam',uv)
scene['river_falls_version']=49
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved three masonry spillways, bank-following cascades and river foam')
