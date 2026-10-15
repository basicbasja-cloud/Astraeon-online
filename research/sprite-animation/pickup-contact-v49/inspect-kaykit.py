import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(P/'references/Rig_Medium_General.glb'))
print('OBJECTS',[(o.name,o.type) for o in bpy.context.scene.objects]);print('ACTIONS',[(a.name,list(a.frame_range)) for a in bpy.data.actions])
for o in bpy.context.scene.objects:
 if o.type=='ARMATURE':print('BONES',o.name,[b.name for b in o.pose.bones])
