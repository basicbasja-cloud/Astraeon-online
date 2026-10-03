"""Source-owned garden courts, door contacts and editable civic grouping."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
assert scene['town_plan_version']==44
for c in list(bpy.data.collections):
    if c.name=='wayfarer-v44-gardens':
        for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
gardens=bpy.data.collections.new('wayfarer-v44-gardens');scene.collection.children.link(gardens);gardens['family']='vegetation'
# Trees are reusable vegetation components. Each grove has designed spacing,
# clear routes, varied size and rotation, rather than arbitrary prop scatter.
prototype=bpy.data.collections['plaza-oak-west']
points=[(44,65),(43,71),(44,77),(63,65),(64,71),(63,77),
        (41,37),(42,42),(65,37),(65,42),(33,54),(36,57),
        (73,60),(72,64),(84,35),(80,35),(26,37),(30,37),
        (38,83),(45,86),(58,85),(77,84),(94,60),(95,70),
        (20,52),(19,57),(34,17),(39,17),(68,17),(74,18)]
anchor=Vector((36,61,0))
for i,(x,y) in enumerate(points):
    scale=.8+(i%4)*.065;angle=(i%5)*.63;rot=Matrix.Rotation(angle,4,'Z')
    for p in prototype.objects:
        if p.type!='MESH':continue
        o=bpy.data.objects.new(f'grove-v44-{i}-{p.name}',p.data.copy());gardens.objects.link(o)
        for v in o.data.vertices:v.co=Vector((x,y,0))+rot@((p.matrix_world@v.co-anchor)*scale)
        o['role']=p['role'];o['shadow']=p['shadow'];o['render_visible']=p.get('render_visible',True)
# Grass must have quiet surface variation instead of a flat empty green slab.
grass=bpy.data.materials['grass'];grass.diffuse_color=(.42,.51,.32,1)
grass['texture_json']=json.dumps({'file':'assets/wayfarer-lawn-v44.webp','grid':[1,1],'tile':0,'worldSize':7})
for o in bpy.data.collections['court-terrain'].objects:
    if o.get('road_segment'):o['legacy_role']='avenue' if o.name.startswith(('plan-v44-arrival-avenue','plan-v44-consortium')) else 'street'
# Retain source transform ownership after the expansion, so later Blender edits
# move meshes, contacts and gameplay anchors as one object again.
root=bpy.data.objects['guild-hall-placement'];root.location=(54,20,.6075);bpy.context.view_layer.update()
owned=list(bpy.data.collections['guild-hall'].objects)
for name in ['guild-board','planter-a','planter-b']:owned+=list(bpy.data.collections[name].objects)
owned += [o for o in bpy.data.collections['court-terrain'].objects if o.get('object_id')=='guild-hall' or o.name.startswith(('civic-terrace','civic-stair'))]
for o in owned:
    if o==root:continue
    before=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=before
# Contact Z is the actual raised landing, not an old approximate nominal height.
landing=next(o for o in bpy.data.collections['court-terrain'].objects if o.name=='civic-terrace')
top=max((landing.matrix_world@v.co).z for v in landing.data.vertices)
for o in owned:
    if o.get('kind') in ('portal','approach','service','presentation'):
        p=o.matrix_world.translation;p.z=top;o.matrix_world.translation=p
gatekeeper=bpy.data.objects['gatekeeper'];gatekeeper.matrix_world.translation=Vector((52.2,91.2,0))
# Remove crossbars where a curb would obstruct a crossing visually. The paving
# remains a continuous single-level surface through each neighbourhood junction.
street_collection=bpy.data.collections['wayfarer-v44-streets']
for o in street_collection.objects:
    if '-curb-' in o.name:
        o['render_visible']=False;o['role']='decorative';o['shadow']=False
scene['garden_authoring_version']=44
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved',len(points),'planned grove trees and restored civic parent/contact ownership')
