import bpy
from mathutils import Vector
# Bind older building families as well as the current named frontage kit.
for c in bpy.data.collections:
    r=bpy.data.objects.get(c.name+'-placement')
    if not r or not any(o.type=='MESH' and o.get('role')=='solid' for o in c.objects):continue
    owned=[o for o in c.objects if o!=r]+[o for o in bpy.data.collections['court-terrain'].objects if o.get('object_id')==c.name]
    for o in owned:
        if o.parent==r:continue
        before=o.matrix_world.copy();o.parent=r;o.matrix_parent_inverse=r.matrix_world.inverted();o.matrix_world=before
bpy.context.view_layer.update()
r=bpy.data.objects['avenue-cottage-east-placement'];m=r.matrix_world.copy();m.translation.x+=1.5;r.matrix_world=m;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Bound older building families; moved cottage geometry clear of the Weaver')
