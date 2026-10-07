"""Clear new porch volumes from the two existing projecting oriel bays."""
import ast, bpy, bmesh, json, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert s.get('capital_property_frontages')==1
tree=ast.parse((R/'tools/refine-capital-property-frontages-v76.py').read_text())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='remove_components')
namespace={'bpy':bpy,'bmesh':bmesh}
exec(compile(ast.Module(body=[node],type_ignores=[]),'<frontage-component-helper>','exec'),namespace)
report_path=R/'docs/review/wayfarer-capital-v76/property-frontages/authoring.json'
report=json.loads(report_path.read_text());fixed=[]
for record in report['properties']:
    c=bpy.data.collections[record['id']];l=json.loads(c['building_preset_json'])
    if l['architectureType']!='oriel-house' or l['family']!='residential':continue
    prefix='capital-property-v76-'+l['id']
    namespace['remove_components'](c,(prefix+'-entry-shed',prefix+'-porch-'))
    record.update(use='shuttered-oriel',projection=.47)
    c['property_frontage_json']=json.dumps({k:v for k,v in record.items() if k not in ('id','district')})
    fixed.append(l['id'])
bpy.context.view_layer.update()
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));data=exporter['export'](s)
report['afterStaticTriangles']=sum(len(f)-2 for o in data['objects'] for p in o['parts'] if p.get('visible',True) for f in p['faces'])
report['addedTriangles']=report['afterStaticTriangles']-report['beforeStaticTriangles']
report['orielSoffitsCleared']=fixed
report_path.write_text(json.dumps(report,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Cleared redundant porch volumes',fixed)
