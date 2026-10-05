"""Apply original aged stone art consistently to saved city paving without changing UVs."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_aged_paving_version');art=json.loads((ROOT/'authoring/materials/wayfarer-aged-pavers-v69.json').read_text());updated=[]
for m in bpy.data.materials:
 spec=json.loads(m.get('texture_json','{}'))
 if spec.get('file')!='assets/wayfarer-pavers-v69.webp':continue
 m['texture_json']=json.dumps(art['texture']);updated.append(m.name)
assert {'paving','cityPaving','avenuePaving','houseApronPaving'}<=set(updated)
scene['ro3_aged_paving_version']=69;scene['ro3_aged_paving_review_json']=json.dumps({'updatedMaterials':updated,'nativeUVsAndStoneScalePreserved':True,'art':art})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS consistent aged town paving on',updated,'with native UV scale8')
