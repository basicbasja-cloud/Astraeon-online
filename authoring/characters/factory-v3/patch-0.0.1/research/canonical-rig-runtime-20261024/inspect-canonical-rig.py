import bpy,json
from pathlib import Path
scene=bpy.context.scene
print('CANONICAL_READ_ONLY',json.dumps({'blender':bpy.app.version_string,'actions':len(bpy.data.actions),'objects':[{'name':o.name,'type':o.type,'bones':len(o.data.bones)if o.type=='ARMATURE'else 0,'vertices':len(o.data.vertices)if o.type=='MESH'else 0,'module':o.get('spriteModule'),'dimensions':list(o.dimensions)}for o in scene.objects if o.type in ['MESH','ARMATURE']],'scene_keys':list(scene.keys())}))
