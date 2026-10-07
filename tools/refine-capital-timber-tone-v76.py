"""Keep timber warm and legible after removing its legacy renderer override."""
import bpy, json, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene;assert s.get('capital_natural_landscape') and not s.get('capital_timber_tone_revision')
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exporter['export'](s)
mat=bpy.data.materials['timber'];old=list(mat.diffuse_color[:3]);target=[.24,.13,.06];mat.diffuse_color=(*target,1)
after=exporter['export'](s)
for k in before:
    if k!='materials':assert before[k]==after[k],k
for name,material in before['materials'].items():
    if name!='timber':assert material==after['materials'][name],name
assert after['lighting'].get('groundShadow')==before['lighting']['groundShadow']
tone=json.loads((O/'tone.json').read_text());tone.setdefault('iterations',[]).append({'material':'timber','before':old,'after':target,'basis':'Source-matched 910x512 gameplay showed the unmasked native color too pale and gray beside RO3 01:40/03:35 timber.'})
tone['materials']['timber']['after']=target;(O/'tone.json').write_text(json.dumps(tone,indent=2)+'\n')
s['capital_timber_tone_revision']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Warm timber; all geometry, UVs, anchors and current shadow bake retained',flush=True)
