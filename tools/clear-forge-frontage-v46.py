import bpy
from mathutils import Vector
from pathlib import Path
# Clear the blacksmith's door/yard sight line rather than relying on invisible trees.
for o in bpy.data.collections['west-garden'].objects:
 if o.type=='MESH':
  m=o.matrix_world.copy();m.translation+=Vector((-4.7,-1.3,0));o.matrix_world=m
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('Moved forge tree to the planted western verge, outside the service frontage')
