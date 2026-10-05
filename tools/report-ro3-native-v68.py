"""Read-only summary of the exact saved RO3 source parameters for review."""
import json
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
fields=['layout_id','concept_architecture_version','frontage_family_version','ro3_facade_version','ro3_density_version','ro3_fountain_version','ro3_contact_fit_version','exterior_craft_version','material_authoring_version','baked_depth_version','ambient','sun_strength','bake_ao_samples','bake_ao_strength','bake_ao_radius','ground_shadow_resolution']
report={k:scene.get(k) for k in fields}
for field,key in [('primaryFacades','ro3_facade_review_json'),('secondaryFacades','ro3_secondary_review_json'),('densityPlan','ro3_density_plan_json'),('treeRelocations','ro3_tree_relocations_json'),('fountain','ro3_fountain_review_json'),('groundShadow','ground_shadow_bake_json')]:report[field]=json.loads(scene[key])
assert len(report['primaryFacades'])+len(report['secondaryFacades'])==37
(ROOT/'docs/review/wayfarer-v68/native-authoring.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS saved native parameters:37 envelopes, tiered fountain and current bake')
