"""A restrained RO3-informed tone using Wayfarer's own material palette.

Changes color parameters only; no borrowed texture, camera, geometry or light
direction. Clay/ivory/timber remain domestic; blue/gold remain civic accents.
"""
import bpy, json, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
assert s.get('capital_property_frontages')==1
assert not s.get('capital_tone_revision')
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'))
before=exporter['export'](s)
colors={'roofClayWarm':(.56,.25,.14), 'roofClayOchre':(.54,.30,.17),
        'roofClayRose':(.48,.215,.125), 'timber':(.24,.13,.06),
        'publicTownStone':(.47,.47,.415),'frontageGlazing':(.34,.45,.59)}
receipt={'materials':{},'lighting':{}}
for name,rgb in colors.items():
    mat=bpy.data.materials[name]
    receipt['materials'][name]={'before':list(mat.diffuse_color[:3]),'after':list(rgb)}
    mat.diffuse_color=(*rgb,mat.diffuse_color[3])
for key,value in {'sun_color_json':json.dumps([1.10,1.02,.87]),
                  'ambient_color_json':json.dumps([1.00,1.015,1.03]),
                  'shadow_color':'#555766'}.items():
    receipt['lighting'][key]={'before':s[key],'after':value};s[key]=value
after=exporter['export'](s)
for key in before:
    if key not in ('materials','lighting'):assert before[key]==after[key],key
assert before['lighting']['sun']['cast']==after['lighting']['sun']['cast']
assert before['lighting']['sun']['strength']==after['lighting']['sun']['strength']
assert before['lighting']['ambient']==after['lighting']['ambient']
for name,mat in before['materials'].items():
    if name not in colors:assert after['materials'][name]==mat,name
    else:assert {k:v for k,v in mat.items() if k!='color'}=={k:v for k,v in after['materials'][name].items() if k!='color'}
receipt.update(noTexturesOrGeometryChanged=True,cameraUnchanged=True,
               visualAcceptance='Pending gameplay comparison; palette is an authored choice, not a measured RO3 value')
out=R/'docs/review/wayfarer-capital-v76/property-frontages'
(out/'tone.json').write_text(json.dumps(receipt,indent=2)+'\n')
s['capital_tone_revision']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
