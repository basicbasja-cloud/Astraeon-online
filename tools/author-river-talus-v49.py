"""Original rounded cliff-foot boulders, grounded below the river surface."""
import bpy,bmesh,json,math,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('continuous_bank_version')==49
PREFIX='talus-v49-';owner=bpy.data.collections['wayfarer-v44-detail'];rng=random.Random(4921)
for o in list(bpy.data.objects):
 if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for d in list(bpy.data.meshes):
 if d.name.startswith(PREFIX) and not d.users:bpy.data.meshes.remove(d)
terrain=bpy.data.collections['court-terrain'];ground=next(o for o in terrain.objects if o.type=='MESH' and not o.get('surface_role'))
outline=[ground.matrix_world@ground.data.vertices[i].co for i in json.loads(ground['outline_vertex_indices'])]
water=next(o for o in terrain.objects if o.get('surface_role')=='water');water_z=min((water.matrix_world@v.co).z for v in water.data.vertices)
count=0
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
 tangent=(b-a).normalized();normal=Vector((tangent.y,-tangent.x,0))
 # Match the existing bank's outward direction using polygon winding.
 signed=sum(p.x*q.y-q.x*p.y for p,q in zip(outline,outline[1:]+outline[:1]))
 if signed<0:normal=-normal
 for j in range(max(1,int((b-a).length/9))):
  t=(j+.5)/max(1,int((b-a).length/9));center=a.lerp(b,t)+normal*(2.2+rng.random()*1.4)
  for k in range(3):
   r=.65+rng.random()*.9;sx=r*(.85+rng.random()*.50);sy=r*(.75+rng.random()*.45);sz=r*(.60+rng.random()*.65)
   # Lowest point is submerged; clusters meet the sloping bank rather than
   # floating beside it. Broad variations replace a straight cliff-water edge.
   c=center+tangent*((k-1)*r*.9)+normal*(.2 if k==1 else -.25)
   c.z=water_z+sz*.35
   data=bpy.data.meshes.new(PREFIX+str(count));bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
   angle=rng.random()*math.tau;ca,sa=math.cos(angle),math.sin(angle)
   for v in bm.verts:
    x,y,z=v.co;v.co=c+Vector((ca*x*sx-sa*y*sy,sa*x*sx+ca*y*sy,z*sz))
   bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials['bankStoneLight' if count%4==0 else 'bankStone']);data.uv_layers.new(name='PhysicalUV')
   for f in data.polygons:
    for li in f.loop_indices:
     p=data.vertices[data.loops[li].vertex_index].co;n=f.normal;data.uv_layers.active.data[li].uv=(p.x/3,p.z/3) if abs(n.y)>.5 else (p.y/3,p.z/3)
   o=bpy.data.objects.new(PREFIX+str(count),data);owner.objects.link(o);o['role']='decorative';o['shadow']=False;count+=1
scene['river_talus_version']=49
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
print('Saved',count,'rounded submerged shoreline boulders')
