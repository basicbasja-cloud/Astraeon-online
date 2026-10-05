"""Keep saved texture provenance aligned after the organic-edge art iteration."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
art=json.loads((ROOT/'authoring/materials/wayfarer-street-v69.json').read_text())['materials']
for names,key in [(('paving','cityPaving','avenuePaving'),'paving'),(('streetBrickLime',),'brick'),(('vergeGroundcover','vergeGroundcoverShade'),'groundcover')]:
 for name in names:bpy.data.materials[name]['texture_json']=json.dumps(art[key]['texture'])
weather=json.loads((ROOT/'authoring/materials/wayfarer-house-weather-v69.json').read_text())['materials']
bpy.data.materials['foundationPatina']['texture_json']=json.dumps(weather['patina']['texture'])
bpy.context.scene['material_authoring_version']=69
bpy.context.scene['exterior_craft_version']=69
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
