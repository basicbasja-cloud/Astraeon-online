"""Read-only source69 paving, facade weathering and accessory provenance."""
import json
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
fields=['ro3_house_apron_version','ro3_lot_grass_fit_version','ro3_grass_life_version','ro3_verge_fit_version','ro3_roof_fitting_version','ro3_wing_detail_version','ro3_street_version','ro3_house_life_version','layout_id','concept_architecture_version','frontage_family_version','ro3_facade_version','ro3_density_version','ro3_fountain_version','ro3_contact_fit_version','exterior_craft_version','material_authoring_version','baked_depth_version','ambient','sun_strength','bake_ao_samples','bake_ao_strength','bake_ao_radius','ground_shadow_resolution']
report={k:scene.get(k) for k in fields}
for field,key in [('houseAprons','ro3_house_apron_review_json'),('lotGrassFit','ro3_lot_grass_fit_review_json'),('livingFoundationGrass','ro3_grass_life_review_json'),('foundationGrassFit','ro3_verge_fit_review_json'),('junctionOmissions','ro3_junction_omissions_json'),('roofFittings','ro3_roof_fitting_review_json'),('attachedWings','ro3_wing_detail_review_json'),('street','ro3_street_review_json'),('houseLife','ro3_house_life_review_json'),('primaryFacades','ro3_facade_review_json'),('secondaryFacades','ro3_secondary_review_json'),('densityPlan','ro3_density_plan_json'),('treeRelocations','ro3_tree_relocations_json'),('fountain','ro3_fountain_review_json'),('groundShadow','ground_shadow_bake_json')]:report[field]=json.loads(scene[key])
assert len(report['primaryFacades'])+len(report['secondaryFacades'])==37
for field,key in [('lotGrassContact','ro3_lot_grass_contact_review_json'),('goodsFloorFit','ro3_goods_floor_fit_review_json'),('fullGrass','ro3_full_grass_review_json')]:report[field]=json.loads(scene[key])
for field,key in [('roadCurbs','ro3_road_curb_review_json'),('treeTextures','ro3_tree_texture_review_json'),('roadsideGrass','ro3_curb_grass_review_json'),('treeCrowns','ro3_tree_crown_review_json')]:
 if scene.get(key):report[field]=json.loads(scene[key])
(ROOT/'docs/review/wayfarer-v69/native-authoring.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS saved native parameters:source69 native street, dressed houses and current bake')
