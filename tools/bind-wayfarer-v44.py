"""Keep new frontage lots and existing landmarks individually editable in Blender."""
import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;assert scene['town_plan_version']==44
lots=[('baker',37,44),('apothecary',40,60),('cobbler',34,73),('weaver',65,73),('bookbinder',70,46),('market-arcade',80,44),('garden-home',38,23),('scribe',64,24),('willow-east',80,73),('riverside',70,86),('joiner',20,62),('copper-shop',35,66)]
for name,x,y in lots:
    cid='frontage-'+name;c=bpy.data.collections.get(cid)
    if c is None:c=bpy.data.collections.new(cid);scene.collection.children.link(c)
    c['family']='residential' if name in ('garden-home','willow-east','riverside') else 'market'
    for o in list(bpy.data.collections['wayfarer-v44-streets'].objects):
        if o.name.startswith('plan-v44-'+name+'-'):c.objects.link(o);bpy.data.collections['wayfarer-v44-streets'].objects.unlink(o)
    root=bpy.data.objects.get(cid+'-placement')
    if root is None:root=bpy.data.objects.new(cid+'-placement',None);c.objects.link(root);root.location=(x,y,0)
    bpy.context.view_layer.update()
    for o in list(c.objects)+[o for o in bpy.data.collections['court-terrain'].objects if o.name=='plan-v44-'+name+'-threshold']:
        if o==root:continue
        world=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=world
        if o.get('surface_role'):o['object_id']=cid
families={'residential','workshop','market','inn','shrine','civic'}
for c in bpy.data.collections:
    if c.get('family') not in families or c.name.startswith(('wayfarer-','frontage-')):continue
    anchor=next((o for o in c.objects if o.get('kind')=='presentation'),None)
    if anchor is None:continue
    root=bpy.data.objects.get(c.name+'-placement')
    if root is None:root=bpy.data.objects.new(c.name+'-placement',None);c.objects.link(root);root.location=anchor.matrix_world.translation
    if c.name!='guild-hall':
        children={o:o.matrix_world.copy() for o in c.objects if o!=root}
        root.matrix_world.translation=anchor.matrix_world.translation.copy()
        bpy.context.view_layer.update()
        for o,world in children.items():o.matrix_world=world
    bpy.context.view_layer.update()
    owned=list(c.objects)+[o for o in bpy.data.collections['court-terrain'].objects if o.get('object_id')==c.name]
    for o in list(bpy.data.collections['wayfarer-street-details'].objects):
        if o.name.startswith('street-v4-'+c.name+'-') or c.name=='astral-fountain' and o.name.startswith('street-v4-statue-'):c.objects.link(o);bpy.data.collections['wayfarer-street-details'].objects.unlink(o);owned.append(o)
    for o in owned:
        if o==root:continue
        world=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=world
for cid in ('guild-board','planter-a','planter-b'):
    root=bpy.data.objects.get(cid+'-placement')
    if root:
        world=root.matrix_world.copy();root.parent=bpy.data.objects['guild-hall-placement'];root.matrix_parent_inverse=root.parent.matrix_world.inverted();root.matrix_world=world
# Physical texel density on facade, roof slopes and lawns. Cutout leaf cards and
# heraldic panels retain their deliberately registered UVs.
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.materials:continue
    mat=o.data.materials[0]
    if not mat.get('texture_json') or mat.name=='bannerSilk':continue
    spec=json.loads(mat['texture_json'])
    if spec.get('alphaCutoff'):continue
    size=spec.get('worldSize',2.4)
    if not o.data.uv_layers.active:o.data.uv_layers.new(name='PhysicalUV')
    roof=any(s in mat.name.lower() for s in ('slate','terracotta','roof'))
    for face in o.data.polygons:
        normal=(o.matrix_world.to_3x3()@face.normal).normalized()
        if roof and abs(normal.z)>.1:
            u=Vector((0,1,0));u=(u-normal*u.dot(normal)).normalized();v=normal.cross(u).normalized()
        elif abs(normal.z)>.65:u,v=Vector((1,0,0)),Vector((0,1,0))
        elif abs(normal.y)>abs(normal.x):u,v=Vector((1,0,0)),Vector((0,0,1))
        else:u,v=Vector((0,1,0)),Vector((0,0,1))
        for li in face.loop_indices:
            p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(p.dot(u)/size,p.dot(v)/size)
scene['placement_ownership_version']=44;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved individual editable frontage collections and source roots')
