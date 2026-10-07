"""Put workshop tools on usable benches below their saved ground glazing."""
import ast, bpy, bmesh, json, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert s.get('capital_property_frontages')==1 and not s.get('capital_workbench_clearance')
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
tree=ast.parse((R/'tools/refine-capital-property-frontages-v76.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('remove_components','sign','workshop')]
ns={'bpy':bpy,'bmesh':bmesh}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<frontage-component-helpers>','exec'),ns)
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exporter['export'](s)
def invariant(data):
    return {'terrain':data['terrain'],'navigation':data['navigation'],'route':data['route'],
            'spawn':data['spawn'],'owners':[{k:v for k,v in o.items() if k!='parts'} for o in data['objects']],
            'solidsAndDoors':[(o['id'],p) for o in data['objects'] for p in o['parts']
                             if p['role']=='solid' or p['id'].endswith('-door-leaf')]}
saved=invariant(before);del before
out=R/'docs/review/wayfarer-capital-v76/property-frontages';report=json.loads((out/'authoring.json').read_text())
clearance=[]
for rec in report['properties']:
    c=bpy.data.collections[rec['id']];l=json.loads(c['building_preset_json'])
    if l['family']!='workshop':continue
    root=next(o for o in c.objects if o.type=='EMPTY' and not o.parent)
    k=Kit(c,root);k.prefix='capital-property-v76-'
    ns['remove_components'](c,('capital-property-v76-'+l['id'], '-shop-counter','-shop-goods-',
                             '-front-flowers-','-flower-bracket-','-craft-bench','-bench-leg-'))
    ns['workshop'](k,l)
    glass=[]
    for o in c.objects:
        if o.type!='MESH':continue
        for g in o.vertex_groups:
            if g.name.endswith('-ground-window-glass'):
                glass.extend(v.co.z for v in o.data.vertices if any(a.group==g.index for a in v.groups))
        if not o.get('component_count') and o.name.endswith('-ground-window-glass'):
            glass.extend(v.co.z for v in o.data.vertices)
    tooltop=max(v.co.z for o in c.objects if o.type=='MESH' and '-tool-' in o.name
                and o.name.startswith('capital-property-v76-') for v in o.data.vertices)
    assert glass and tooltop<min(glass)-.04,(l['id'],'Tools overlap glazing',tooltop,glass)
    clearance.append({'id':l['id'],'toolTop':round(tooltop,4),'glassBottom':round(min(glass),4)})
bpy.context.view_layer.update();after=exporter['export'](s)
assert invariant(after)==saved,'Workbench refinement changed navigation, public geometry or anchors'
report['afterStaticTriangles']=sum(len(f)-2 for o in after['objects'] for p in o['parts'] if p.get('visible',True) for f in p['faces'])
report['addedTriangles']=report['afterStaticTriangles']-report['beforeStaticTriangles']
assert report['addedTriangles']<report['triangleBudget']
report['workbenchClearance']=clearance
(out/'authoring.json').write_text(json.dumps(report,indent=2)+'\n')
# Existing glazing reflects the cooler sky; retain the exact original texture.
tone_path=out/'tone.json';tone=json.loads(tone_path.read_text());mat=bpy.data.materials['frontageGlazing']
if 'frontageGlazing' not in tone['materials']:
    rgb=(.34,.45,.59)
    tone['materials']['frontageGlazing']={'before':list(mat.diffuse_color[:3]),'after':list(rgb)}
    mat.diffuse_color=(*rgb,mat.diffuse_color[3])
    tone_path.write_text(json.dumps(tone,indent=2)+'\n')
s['capital_workbench_clearance']=1
del after,saved
runpy.run_path(str(R/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
print('Grounded workbenches; clear glazing:',len(clearance),flush=True)
