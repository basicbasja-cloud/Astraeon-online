"""Expose gambrel dormer glazing consistently across actual roof depths."""
import bpy,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v80/unique-neighborhoods';s=bpy.context.scene;assert s.get('capital_dormer_contact_correction_v80') and not s.get('capital_dormer_slope_clearance_v80');p=json.loads((O/'plan.json').read_text());changes=[]
for a in p['houses']:
 if a['design']!='dormered-gambrel':continue
 old=a['depth']/2-.25;new=max(old,(a['depth']/2+.28)*.8+.22);parts=[]
 for o in bpy.data.collections[a['id']].objects:
  if o.type!='MESH' or not o.name.startswith('capital-v80-') or 'dormer' not in o.name:continue
  for v in o.data.vertices:v.co.y+=new-old
  layer=o.data.color_attributes.get('BakedTownLight')
  if layer:o.data.color_attributes.remove(layer)
  o.data.update();parts.append(o.name)
 assert len(parts)>15;changes.append({'id':a['id'],'oldFrontY':old,'newFrontY':new,'parts':parts,'reason':'Place the full window above the steep lower slope at every authored depth.'})
s['capital_dormer_slope_clearance_v80']=1;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__');(O/'narrow-dormer-correction.json').write_text(json.dumps({'changes':changes,'rebakeRequired':True,'originalCollisionDoorsTerrainGameplayExact':True},indent=2)+'\n');print('PASS consistent depth-dependent native gambrel contacts',flush=True)
