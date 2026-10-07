"""Move authored dormer assemblies to physically exposed roof-slope positions."""
import bpy,json,runpy,gc,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';s=bpy.context.scene;assert s.get('capital_unique_neighborhoods_v80') and not s.get('capital_dormer_contact_correction_v80');p=json.loads((O/'plan.json').read_text());changes=[]
for a in p['houses']:
 if a['design'] not in ('garden-cottage','dormered-gambrel'):continue
 c=bpy.data.collections[a['id']];old=a['depth']*(.24 if a['design']=='garden-cottage' else .23);new=a['depth']/2-.25;parts=[]
 for o in c.objects:
  if o.type!='MESH' or not o.name.startswith('capital-v80-') or 'dormer' not in o.name:continue
  assert o.get('role')!='solid'
  for v in o.data.vertices:v.co.y+=new-old
  light=o.data.color_attributes.get('BakedTownLight')
  if light:o.data.color_attributes.remove(light)
  o.data.update();parts.append(o.name)
 assert len(parts)>15,a['id'];changes.append({'id':a['id'],'parts':parts,'oldFrontY':old,'newFrontY':new,'shift':new-old,'reason':'Window front sits ahead of the high roof break, exposed above the main slope; entire native dormer assembly moved together.'})
assert len(changes)==6
s['capital_dormer_contact_correction_v80']=1;s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v80-neighborhoods.png';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__');(O/'dormer-contact-correction.json').write_text(json.dumps({'changes':changes,'originalCollisionTerrainGameplayUnchanged':True,'rebakeRequired':True},indent=2)+'\n');print('PASS six physically exposed original dormer assemblies',flush=True)
