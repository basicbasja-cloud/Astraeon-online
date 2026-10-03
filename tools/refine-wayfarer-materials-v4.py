"""Apply original painted swatches to the authored civic stone and slate."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name,reference in {'civicIvory':'stoneLight','civicShadow':'stone','civicSlate':'slate','civicSlateLight':'slate','streetIvory':'stoneLight','streetSlate':'slate'}.items():
    if name in bpy.data.materials:bpy.data.materials[name]['texture_json']=bpy.data.materials[reference]['texture_json']
rock=ROOT/'assets/wayfarer-rock-v4.webp'
if rock.exists():
    spec={'file':'assets/wayfarer-rock-v4.webp','grid':[1,1],'tile':0,'worldSize':1.7}
    for name in ['bankStone','bankStoneLight']:bpy.data.materials[name]['texture_json']=json.dumps(spec)
bpy.context.scene['material_authoring_version']=4
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved painted civic swatches and available original river-rock material')
