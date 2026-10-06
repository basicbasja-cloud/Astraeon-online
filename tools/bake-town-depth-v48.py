"""Bake directional overhang shade and contact depth into source color corners.

Uses Blender's documented BVHTree. Stored AO/sun factors ship as vertex colors;
there is no new per-frame raycast or screen-space effect in gameplay.
"""
import bpy,math,runpy,json,time,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('paved_city_version')==48
# New Hall pieces share its editable root just like the existing landmark.
root=bpy.data.objects['guild-hall-placement']
for o in bpy.data.collections['guild-hall'].objects:
    if o.name.startswith('city-v48-') and not o.parent:
        before=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=before
# The paved outline is concave at the arrival neck. Triangulate it in the DCC,
# rather than trusting a triangle fan to fill that boundary correctly.
o=bpy.data.objects['city-v48-continuous-stone-interior']
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
meshes=[];occluders=[]
for c in bpy.data.collections:
    if not c.get('family') or c['family'] in ('terrain','vegetation'):continue
    for o in c.objects:
        if o.type!='MESH' or o.get('export_reference_only') or not o.get('render_visible',True):continue
        mat=o.data.materials[0].name.lower()
        if any(k in mat for k in ('leaf','foliage','flower','glass','cloth','silk','water')):continue
        meshes.append(o)
        if o.get('role') in ('solid','overhead') or o.get('shadow'):occluders.append(o)
vertices=[];faces=[]
for o in occluders:
    base=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
    o.data.calc_loop_triangles();faces.extend(tuple(base+i for i in t.vertices) for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
sun=Vector((-scene['sun_cast_x'],-scene['sun_cast_y'],1)).normalized()
sample_count=int(scene.get('bake_ao_samples',8));ao_strength=float(scene.get('bake_ao_strength',.35));ao_radius=float(scene.get('bake_ao_radius',1.5))
assert 1<=sample_count<=64 and 0<=ao_strength<=1 and 0<ao_radius<=10
samples=[(math.sqrt((i+.5)/sample_count)*math.cos(i*2.399963),math.sqrt((i+.5)/sample_count)*math.sin(i*2.399963),math.sqrt(1-(i+.5)/sample_count)) for i in range(sample_count)]
selected_collections=set(filter(None,os.environ.get('ASTRAEON_BAKE_COLLECTIONS','').split(',')))
if selected_collections:meshes=[o for o in meshes if any(c.name in selected_collections for c in o.users_collection)]
count=0;start=time.monotonic()
for index,o in enumerate(meshes):
    data=o.data;old=data.color_attributes.get('BakedTownLight')
    if old:data.color_attributes.remove(old)
    layer=data.color_attributes.new(name='BakedTownLight',type='FLOAT_COLOR',domain='CORNER')
    for face in data.polygons:
        normal=(o.matrix_world.to_3x3()@face.normal).normalized();center=o.matrix_world@face.center
        tangent=normal.cross(Vector((0,0,1)))
        if tangent.length<.1:tangent=normal.cross(Vector((0,1,0)))
        tangent.normalize();other=normal.cross(tangent).normalized()
        for li in face.loop_indices:
            point=o.matrix_world@data.vertices[data.loops[li].vertex_index].co
            point=point.lerp(center,.025)+normal*.04
            occ=0
            for x,y,z in samples:
                hit=tree.ray_cast(point,tangent*x+other*y+normal*z,ao_radius)
                if hit[0] is not None:occ+=max(0,1-hit[3]/ao_radius)
            ao=1-ao_strength*occ/len(samples)
            visible=1.0 if normal.dot(sun)<=0 or tree.ray_cast(point,sun,100)[0] is None else .12
            layer.data[li].color=(ao,visible,0,1);count+=1
    if index%700==0:print('BAKE',index,'/',len(meshes),'corners',count,flush=True)
scene['baked_depth_version']=scene.get('concept_architecture_version',48)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Baked',count,'corners on',len(meshes),'meshes in',round(time.monotonic()-start,1),'seconds')
