"""Add circulation inlays and celestial fountain details to the saved town.
All original town objects, IDs, geometry and street-facing homes are retained.
"""
import bpy,math,json,runpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert bpy.context.scene['world_id']=='wayfarer-spatial'
terrain=bpy.data.collections['court-terrain'];collection=bpy.data.collections['astral-fountain'];root=bpy.data.objects['astral-fountain-placement']
def mesh(name,vs,faces,material,parent=root,owner=collection,surface=False):
 if bpy.data.objects.get(name):return bpy.data.objects[name]
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],faces);data.materials.append(bpy.data.materials[material]);data.uv_layers.new(name='Wayfarer-painterly')
 for polygon in data.polygons:
  for loop in polygon.loop_indices:
   p=data.vertices[data.loops[loop].vertex_index].co;data.uv_layers.active.data[loop].uv=(p.x/2.4,p.y/2.4)
 obj=bpy.data.objects.new(name,data);owner.objects.link(obj);obj.parent=parent;obj['role']='decorative';obj['shadow']=False
 if surface:obj['surface_role']='plaza';obj['walkable']=True;obj['object_id']='astral-fountain'
 return obj
def ring(name,inner,outer,material):
 n=64;vs=[(math.cos(j*math.tau/n)*r,math.sin(j*math.tau/n)*r,.024) for r in [inner,outer] for j in range(n)]
 return mesh(name,vs,[[j,j+n,(j+1)%n+n,(j+1)%n] for j in range(n)],material,owner=terrain,surface=True)
def prism(name,r,z,h,material='stoneLight'):
 n=8;vs=[(math.cos(j*math.tau/n)*r,math.sin(j*math.tau/n)*r,k) for k in [z,z+h] for j in range(n)]
 return mesh(name,vs,[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)],material)
def beam(name,a,b,r,material):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u).normalized();n=6
 vs=[tuple(p+(u*math.cos(j*math.tau/n)+v*math.sin(j*math.tau/n))*r) for p in [a,b] for j in range(n)]
 return mesh(name,vs,[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)],material)
ring('plaza-fountain-apron',1.36,1.73,'stoneLight');ring('plaza-circulation-inlay',2.95,3.08,'stoneLight');ring('plaza-inner-compass-line',1.96,2.015,'gold')
for j in range(8):
 angle=j*math.tau/8;t=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-t.y,t.x,0));a=t*2.77;b=t*(2.27 if j%2==0 else 2.45)
 mesh(f'plaza-compass-ray-{j}',[tuple(a+Vector((0,0,.025))),tuple(b+side*.10+Vector((0,0,.025))),tuple(b-side*.10+Vector((0,0,.025)))],[[0,1,2]],'stoneLight',owner=terrain,surface=True)
# Original abstract winged celestial sculpture, not a gameplay actor model.
prism('fountain-sculpture-body',.14,1.78,.72);prism('fountain-sculpture-collar',.17,2.44,.09,'gold');prism('fountain-sculpture-neck',.085,2.5,.14)
head=mesh('fountain-sculpture-head',[(math.sin(phi)*math.cos(theta)*.16,math.sin(phi)*math.sin(theta)*.16,2.78+math.cos(phi)*.18) for phi in [math.pi/6,math.pi/2,5*math.pi/6] for theta in [j*math.tau/8 for j in range(8)]],[[j,(j+1)%8,(j+1)%8+8,j+8] for j in range(8)]+[[j+8,(j+1)%8+8,(j+1)%8+16,j+16] for j in range(8)]+[list(range(7,-1,-1)),list(range(16,24))],'stoneLight')
for sign in [-1,1]:
 beam(f'fountain-sculpture-arm-{sign}',(sign*.12,0,2.35),(sign*.28,.08,2.72),.065,'stoneLight')
 for j in range(5):
  k=(j+1)/6;beam(f'fountain-wing-feather-{sign}-{j}',(sign*(.12+.28*k),-.025,1.82+.12*k),(sign*(.36+.50*k),-.025,2.1+.48*k),.023,'cream')
# Keep the earlier emblem as an editing reference; the focal emblem floats above
# the crown instead of intersecting the sculpture's body.
old=bpy.data.objects['fountain-celestial-star'];old['render_visible']=False;old.hide_render=True;old.hide_set(True)
vs=[(0,-.035,3.3)]+[(math.cos(j*math.tau/16)*(.36 if j%2==0 else .12),-.035,3.3+math.sin(j*math.tau/16)*(.36 if j%2==0 else .12)) for j in range(16)]
mesh('fountain-crown-compass',vs,[[0,j+1,(j+1)%16+1] for j in range(16)],'gold')
material=bpy.data.materials.get('waterLight') or bpy.data.materials.new('waterLight');material.diffuse_color=(.42,.78,.80,1)
for j in range(8):
 a=j*math.tau/8;points=[(.17+u*.67,1.59+u*.08-.92*u*u) for u in [k/8 for k in range(9)]]
 for k,((r,z),(r2,z2)) in enumerate(zip(points,points[1:])):beam(f'fountain-jet-{j}-{k}',(math.cos(a)*r,math.sin(a)*r,z),(math.cos(a)*r2,math.sin(a)*r2,z2),.012,'waterLight')
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Added authored fountain sculpture, water arcs and walkable plaza circulation inlays')
