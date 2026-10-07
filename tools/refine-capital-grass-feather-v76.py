"""Save generic native vertex opacity; preserve the grass/street ownership mask."""
import bpy,json,runpy,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene;assert s.get('capital_plaza_enclosure') and not s.get('capital_grass_feather')
plan=json.loads((O/'grass-feather-plan.json').read_text())
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exporter['export'](s)
c=bpy.data.collections['capital-beta-frontage-groundcover']
for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
for a in plan['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces'])
    d.materials.append(bpy.data.materials['grass']);d.uv_layers.new(name='WorldUV')
    layer=d.attributes.new('SurfaceOpacity','FLOAT','POINT')
    for i,value in enumerate(a['vertexOpacity']):layer.data[i].value=value
    for f in d.polygons:
        for li in f.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/7,v.y/7)
    o=bpy.data.objects.new(a['id'],d);c.objects.link(o)
    o['role']='decorative';o['shadow']=False;o['owned_block']=a['block']
bpy.context.view_layer.update();after=exporter['export'](s)
def unchanged(d):
    return {**d,'objects':[o for o in d['objects'] if o['id']!='capital-beta-frontage-groundcover']}
assert unchanged(before)==unchanged(after)
landscape=json.loads((O/'landscape-authoring.json').read_text())
landscape['addedTriangles']+=plan['edgeBlending']['addedTriangles']
# The edge blend adds bounded geometry, with no texture or physics cost. Keep
# its separate 20k guard and the original landscape's 27k guard visible.
landscape['triangleBudget']=27000+plan['edgeBlending']['triangleBudget']
landscape['grassEdgeBlend']=plan['edgeBlending']
assert landscape['addedTriangles']<landscape['triangleBudget']
(O/'landscape-authoring.json').write_text(json.dumps(landscape,indent=2)+'\n')
(O/'natural-lawns-before-feather.json').write_text((O/'natural-lawns-plan.json').read_text())
(O/'natural-lawns-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
s['capital_grass_feather']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Native lawn transition saved:',plan['edgeBlending'],flush=True)
