"""Independent full-scene part IDs distinguish visibility from shader differences."""
import bpy,json,math
import os
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('SPRITE_OUTPUT_ROOT', str(HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'))).resolve()
bpy.ops.wm.open_mainfile(filepath=str(OUT/'silver-scarf-modular-source.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['SilverScarfRig']
m=json.loads((OUT/'rig-manifest.json').read_text());parts=list(m['parts'])
for obj in scene.objects:
 if 'part_id' in obj:obj.pass_index=parts.index(obj['part_id'])+1
scene.view_layers[0].use_pass_object_index=True
nodes=scene.node_tree.nodes;rl=next(n for n in nodes if n.type=='R_LAYERS')
owner=nodes.new('CompositorNodeOutputFile');owner.format.file_format='OPEN_EXR';owner.format.color_depth='32'
scene.node_tree.links.new(rl.outputs['IndexOB'],owner.inputs[0])
depth=next(n for n in nodes if n.type=='OUTPUT_FILE' and n!=owner)
variants={'default':m['default'],'alternate':m['alternate'],'helmet':[p for p in m['default'] if p!='hair.silver']+['headgear.helm']}
times=[0,80,180,280,340,400,520,660]
for d,direction in enumerate(m['directions']):
 rig.rotation_euler=(0,0,d*math.pi/4)
 for i in [0,2,4,5]:
  scene.frame_set(times[i]+1);bpy.context.view_layer.update()
  for variant,chosen in variants.items():
   for obj in scene.objects:
    if 'part_id' in obj:obj.hide_render=obj['part_id'] not in chosen
   dest=OUT/'references'/variant/direction/f'{i:02}.png'
   scene.render.filepath=str(dest);depth.base_path=str(dest.parent);depth.file_slots[0].path=dest.stem+'-depth-'
   owner.base_path=str(dest.parent);owner.file_slots[0].path=dest.stem+'-owner-'
   bpy.ops.render.render(write_still=True)
print('OWNER_REFERENCES_COMPLETE',96,flush=True)
