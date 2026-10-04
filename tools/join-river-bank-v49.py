"""Replace disconnected shoreline strips with shared continuous rock strata.

Repeatable, source-owned presentation pass. Keeps navigation and bridge decks
unchanged. Each strip uses identical vertices at the neighbour's boundary and
continues below the authored water surface rather than ending in mid-air.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('terraced_city_version')==49
PREFIX='bank-v49-';owner=bpy.data.collections['wayfarer-v44-detail']
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith('detail-v44-bank-'):o['render_visible']=False
for d in list(bpy.data.meshes):
 if d.name.startswith(PREFIX) and not d.users:bpy.data.meshes.remove(d)
terrain=bpy.data.collections['court-terrain']
ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
outline=[ground.matrix_world@ground.data.vertices[i].co for i in json.loads(ground['outline_vertex_indices'])]
water=next(o for o in terrain.objects if o.get('surface_role')=='water')
water_z=min((water.matrix_world@v.co).z for v in water.data.vertices)
points=[]
for a,b in zip(outline,outline[1:]+outline[:1]):
 n=max(2,math.ceil((b-a).length/1.8))
 points.extend(a.lerp(b,j/n) for j in range(n))
# Shared rings interpolate a broad rock profile without breaking at segment
# corners. The lower ring stays submerged even at the most exposed facets.
rings=[]
for i,p in enumerate(points):
 prev=points[i-1];nxt=points[(i+1)%len(points)]
 incoming=(p-prev).normalized();outgoing=(nxt-p).normalized()
 normal=Vector((incoming.y+outgoing.y,-incoming.x-outgoing.x,0)).normalized()
 wave=.12*math.sin(i*.51)+.08*math.sin(i*.19)
 rings.append([Vector((p.x,p.y,0)),
  Vector((p.x+normal.x*.3,p.y+normal.y*.3,-.48+wave)),
  Vector((p.x+normal.x*(.9+wave),p.y+normal.y*(.9+wave),-2.7+wave*.8)),
  Vector((p.x+normal.x*(1.55+wave),p.y+normal.y*(1.55+wave),-4.8+wave)),
  Vector((p.x+normal.x*2.1,p.y+normal.y*2.1,water_z-.45))])
for i,ring in enumerate(rings):
 nxt=rings[(i+1)%len(rings)];vs=[tuple(p) for p in ring+nxt]
 fs=[[k,k+1,k+6,k+5] for k in range(4)]
 data=bpy.data.meshes.new(PREFIX+str(i));data.from_pydata(vs,[],fs)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 data.materials.append(bpy.data.materials['bankStone'])
 data.uv_layers.new(name='PhysicalUV')
 for f in data.polygons:
  for li in f.loop_indices:
   p=data.vertices[data.loops[li].vertex_index].co
   data.uv_layers.active.data[li].uv=(p.x/4,p.z/4) if abs(f.normal.y)>abs(f.normal.x) else (p.y/4,p.z/4)
 o=bpy.data.objects.new(PREFIX+str(i),data);owner.objects.link(o)
 o['role']='decorative';o['shadow']=False;o['river_bank_version']=49
scene['continuous_bank_version']=49
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved continuous river strata:',len(rings),'shared sections; bottom',water_z-.45)
