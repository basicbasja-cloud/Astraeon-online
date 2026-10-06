"""Read-only inventory of the saved source70 town and its reference decisions."""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
w=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))['export'](scene)
parts=[p for o in w['objects'] for p in o['parts']];surfaces=w['terrain']['surfaces']
report={'sourcePass':70,'cacheVersion':77,'source':w['source'],'layout':scene['layout_id'],'collections':len(w['objects']),'bounds':w['terrain']['bounds'],'lighting':w['lighting'],'cost':{'allParts':len(parts),'visibleParts':sum(p.get('visible',True) for p in parts),'visibleTriangles':sum(sum(len(f)-2 for f in p['faces']) for p in parts if p.get('visible',True)),'terrainSurfaces':len(surfaces),'walkableSurfaces':sum(s['walkable'] for s in surfaces)},'materials':w['materials']}
for name,key in [('hierarchy','ro3_spatial_hierarchy_review_json'),('composition','ro3_town_composition_review_json'),('primaryFacades','ro3_facade_review_json'),('secondaryFacades','ro3_secondary_review_json'),('density','ro3_density_plan_json'),('fountain','ro3_fountain_review_json'),('houseAprons','ro3_house_apron_review_json'),('foundationGrass','ro3_grass_life_review_json'),('roadsideGrass','ro3_curb_grass_review_json'),('pathGrass','ro3_path_wear_review_json'),('plantingEdges','ro3_planting_edge_review_json')]:
 report[name]=json.loads(scene[key])
assert len(report['primaryFacades'])+len(report['secondaryFacades'])==37
report['foundationContactRefit']=json.loads(scene['ro3_grass_contact_v70_json'])
if scene.get('ro3_foliage_light_v70_json'):report['foliageLighting']=json.loads(scene['ro3_foliage_light_v70_json'])
(ROOT/'docs/review/wayfarer-v70/native-authoring.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS saved source70 inventory',json.dumps(report['cost']))
