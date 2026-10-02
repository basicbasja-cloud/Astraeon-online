"""Add leaf-cluster geometry to the saved scene; never recreate town objects.
Retains existing canopy meshes as invisible shadow proxies and editing references.
Uses the already completed original artwork, without generating new images.
"""
import bpy,json,math,runpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert bpy.context.scene['world_id']=='wayfarer-spatial'
material=bpy.data.materials.get('foliageCutout') or bpy.data.materials.new('foliageCutout')
material.diffuse_color=(.42,.57,.28,1)
material['texture_json']=json.dumps({'file':'assets/wayfarer-foliage-v1.webp','grid':[1,1],'tile':0,'worldSize':2.4,'alphaCutoff':.35})
material.use_nodes=True;nodes=material.node_tree.nodes
if not nodes.get('Wayfarer leaf artwork'):
 nodes.clear();links=material.node_tree.links
 output=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfPrincipled');shader.inputs['Roughness'].default_value=1;shader.inputs['Specular IOR Level'].default_value=0
 image=nodes.new('ShaderNodeTexImage');image.name='Wayfarer leaf artwork';image.image=bpy.data.images.load(str(ROOT/'assets/wayfarer-foliage-v1.webp'),check_existing=True);image.image.filepath=bpy.path.relpath(str(ROOT/'assets/wayfarer-foliage-v1.webp'));image.extension='CLIP'
 links.new(image.outputs['Color'],shader.inputs['Base Color']);links.new(image.outputs['Alpha'],shader.inputs['Alpha']);links.new(shader.outputs['BSDF'],output.inputs['Surface'])
 material.surface_render_method='DITHERED'
count=0
for source in list(bpy.data.objects):
 if source.type!='MESH' or '-canopy-' not in source.name or source.get('authored_cutout_uv'):continue
 collection=next(c for c in source.users_collection if c.get('family'))
 if collection.get('family')!='vegetation':continue
 # Original canopy continues to author the inexpensive sun shadow volume.
 source['render_visible']=False;source.hide_render=True;source.hide_set(True)
 radius=max(v.co.length for v in source.data.vertices)
 seed=sum(map(ord,source.name))
 for side in range(2):
  name=source.name+f'-leafcard-{side}'
  if bpy.data.objects.get(name):continue
  # Crossed spatial branches: not camera-following whole-tree imagery. The
  # fixed-angle view sees both leaf planes, and traversal retains real depth.
  angle=.35+(seed%7)*.06+side*math.pi/2
  axis=Vector((math.cos(angle),math.sin(angle),0))*radius*.98
  up=Vector((0,0,radius*1.04));tilt=Vector((0,0,0)) if side==0 else Vector((.04,-.06,.08))
  vs=[tuple(-axis-up+tilt),tuple(axis-up+tilt),tuple(axis+up+tilt),tuple(-axis+up+tilt)]
  data=bpy.data.meshes.new(name);data.from_pydata(vs,[],[[0,1,2,3]]);data.materials.append(material);data.uv_layers.new(name='Wayfarer-leaf-cluster')
  for loop,uv in zip(data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):data.uv_layers.active.data[loop].uv=uv
  obj=bpy.data.objects.new(name,data);collection.objects.link(obj);obj.parent=source;obj['role']='overhead';obj['shadow']=False;obj['authored_cutout_uv']=True;count+=1
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Added',count,'leaf-cluster planes; retained every original canopy and town object')
