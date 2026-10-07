"""Align crown highlight sectors with the city's actual authored sunlight."""
import bpy, math, json, runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene;assert s.get('capital_natural_landscape') and not s.get('capital_crown_sun_aligned')
sun_angle=math.atan2(-s['sun_cast_y'],-s['sun_cast_x']);delta=sun_angle-2.45
a,b=math.cos(delta),math.sin(delta);count=0
for c in bpy.data.collections:
    if c.get('family')!='vegetation' or c.name=='capital-beta-frontage-groundcover':continue
    stem=next(o for o in c.objects if o.type=='MESH' and o.get('role')=='solid')
    roots=[stem.matrix_world@v.co for v in stem.data.vertices]
    cx=(min(v.x for v in roots)+max(v.x for v in roots))/2;cy=(min(v.y for v in roots)+max(v.y for v in roots))/2
    for obj in c.objects:
        if not obj.get('landscape_v76'):continue
        inverse=obj.matrix_world.inverted()
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co;x,y=p.x-cx,p.y-cy
            v.co=inverse@Vector((cx+a*x-b*y,cy+b*x+a*y,p.z))
        obj.data.update();count+=1
assert count==234,count
report=json.loads((O/'landscape-authoring.json').read_text());report['crownSunAlignment']={'sunAzimuthRadians':sun_angle,'rotatedCrownMeshes':count,'trunksAndRootsUnchanged':True}
(O/'landscape-authoring.json').write_text(json.dumps(report,indent=2)+'\n');s['capital_crown_sun_aligned']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Aligned original-alpha crowns with saved city sun:',count,flush=True)
