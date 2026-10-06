"""Place local residents along the actual walking streets of native neighborhoods."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_continuous_neighborhoods')==75
if not s.get('capital_neighborhood_street_life'):
 # Keep the original ten identities, all 18 new residents and draw budgets.
 # Longitudinal street circuits make residential frontage activity visible.
 for i,x,ya,yb in [(1,80,194,208),(3,80,164,177),(4,80,222,233),(5,176,194,208),(8,176,222,233),(13,80,86,105)]:
  o=bpy.data.objects[f'capital-resident-{i:02}'];assert o.get('kind')=='walker';o.parent=None;o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([[x,ya,0],[x,yb,0],[x+.9,yb,0],[x+.9,ya,0]])
 s['capital_neighborhood_street_life']=75
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
 runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Native longitudinal neighborhood resident routes saved',flush=True)
