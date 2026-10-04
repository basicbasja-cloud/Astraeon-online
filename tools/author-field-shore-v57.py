"""Ground the field approach above water with an original rounded shoreline.

The inherited field was a thin grass plane over the river. Its source-owned
contour now has rounded turns and a joined grass/earth/rock profile reaching
below the water. Bridge decks and district architecture stay in place.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;terrain=bpy.data.collections['court-terrain'];owner=bpy.data.collections['wayfarer-v44-detail'];PREFIX='field-shore-v57-'
field=bpy.data.objects['goldenfield-bank'];water=next(o for o in terrain.objects if o.get('surface_role')=='water');water_z=min((water.matrix_world@v.co).z for v in water.data.vertices)
if not field.get('original_field_outline_json'):field['original_field_outline_json']=json.dumps([list(field.matrix_world@v.co) for v in field.data.vertices])
outline=[Vector(p) for p in json.loads(field['original_field_outline_json'])];z=max(p.z for p in outline)
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
for d in list(bpy.data.meshes):
    if d.name.startswith(PREFIX) and d.users==0:bpy.data.meshes.remove(d)
points=[];corners=[]
for i,p in enumerate(outline):
    a=outline[i-1];b=outline[(i+1)%len(outline)];radius=min(1.8,(p-a).length*.18,(b-p).length*.18)
    corners.append((p+(a-p).normalized()*radius,p,p+(b-p).normalized()*radius))
for i,(entry,p,exit) in enumerate(corners):
    for j in range(6):
        t=j/6;points.append(entry*(1-t)**2+p*(2*t*(1-t))+exit*t*t)
    next_entry=corners[(i+1)%len(corners)][0];length=(next_entry-exit).length;n=max(1,math.ceil(length/1.8));tangent=(next_entry-exit).normalized();normal=Vector((tangent.y,-tangent.x,0))
    for j in range(n):
        t=j/n;point=exit.lerp(next_entry,t)+normal*(.28*math.sin(t*math.pi)*math.sin(i*.83+t*math.tau));point.z=z;points.append(point)
data=bpy.data.meshes.new('Rounded field approach floor v57');data.from_pydata([field.matrix_world.inverted()@p for p in points],[],[list(range(len(points)))])
bm=bmesh.new();bm.from_mesh(data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials['grass']);data.uv_layers.new(name='PhysicalUV')
for face in data.polygons:
    for li in face.loop_indices:
        p=points[data.loops[li].vertex_index];data.uv_layers.active.data[li].uv=(p.x/7,p.y/7)
field.data=data;field['shoreline_version']=57
signed=sum(p.x*q.y-q.x*p.y for p,q in zip(points,points[1:]+points[:1]));sign=1 if signed>0 else -1
rings=[]
for i,p in enumerate(points):
    tangent=(points[(i+1)%len(points)]-points[i-1]).normalized();normal=Vector((tangent.y,-tangent.x,0))*sign;wave=.15*math.sin(i*.47)+.09*math.sin(i*.17)
    rings.append([p,Vector((p.x+normal.x*.65,p.y+normal.y*.65,z-.42+wave*.25)),Vector((p.x+normal.x*(1.8+wave),p.y+normal.y*(1.8+wave),z-2.4+wave)),Vector((p.x+normal.x*(3.2+wave),p.y+normal.y*(3.2+wave),water_z+.4+wave)),Vector((p.x+normal.x*4.1,p.y+normal.y*4.1,water_z-.45))])
for i,ring in enumerate(rings):
    nxt=rings[(i+1)%len(rings)];d=bpy.data.meshes.new(PREFIX+str(i));d.from_pydata([tuple(p) for p in ring+nxt],[],[[k,k+1,k+6,k+5] for k in range(4)]);d.materials.clear()
    for mat in ('grass','soil','bankStone'):d.materials.append(bpy.data.materials[mat])
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();d.uv_layers.new(name='PhysicalUV')
    for j,face in enumerate(d.polygons):
        face.material_index=min(j,2)
        for li in face.loop_indices:
            p=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(p.x/4,p.z/4) if abs(face.normal.y)>abs(face.normal.x) else (p.y/4,p.z/4)
    # The current exporter uses one material per part, so retain a distinct
    # editable part for each physical grass/earth/rock course.
    for course,mat in enumerate(('grass','soil','bankStone','bankStone')):
        face=d.polygons[course];indices=list(face.vertices);vs=[tuple(d.vertices[j].co) for j in indices];part=bpy.data.meshes.new(PREFIX+str(i)+'-'+str(course));part.from_pydata(vs,[],[list(range(4))]);part.materials.append(bpy.data.materials[mat]);part.uv_layers.new(name='PhysicalUV')
        for li,old_li in enumerate(face.loop_indices):part.uv_layers.active.data[li].uv=d.uv_layers.active.data[old_li].uv
        o=bpy.data.objects.new(PREFIX+str(i)+'-'+str(course),part);owner.objects.link(o);o['role']='decorative';o['shadow']=False
    bpy.data.meshes.remove(d)
scene['field_shore_version']=57
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
import runpy
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Grounded field approach:',len(points),'joined shoreline sections to',water_z-.45,flush=True)
