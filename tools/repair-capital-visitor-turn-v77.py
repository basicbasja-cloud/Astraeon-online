"""One declared visitor turn around the new seat; no geometry or bake changes."""
import bpy,json,runpy,hashlib,gc
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v77/street-depth';s=bpy.context.scene
assert not s.get('capital_visitor_turn_v77')
exp=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exp['export'](s)
old=next(a for o in before['objects'] for a in o.get('walkers',[]) if a['id']=='capital-plaza-life-herbalist-visitor')
route=json.loads((O/'traversal-before-visitor-turn.json').read_text())['repairs'][old['id']]
o=bpy.data.objects[old['id']];inv=o.matrix_world.inverted()
o['route_json']=json.dumps([list(inv@Vector((x,y,0))) for x,y in route])
bpy.context.view_layer.update();after=exp['export'](s)
new=next(a for owner in after['objects'] for a in owner.get('walkers',[]) if a['id']==old['id'])
assert {k:v for k,v in new.items() if k!='route'}=={k:v for k,v in old.items() if k!='route'}
for k in before.keys()-{'objects'}:assert before[k]==after[k],k
for a,b in zip(before['objects'],after['objects']):
    if a['id']!='astral-fountain':assert a==b,a['id']
    else:
        expected={**a,'walkers':[new if w['id']==old['id'] else w for w in a['walkers']]};assert expected==b
record={'owner':'astral-fountain','before':old,'after':new,'reason':'Avoid the new southwest seat on the closed-loop return leg','allDrawGeometryMaterialsAndGroundBakeExact':True}
(O/'visitor-turn.json').write_text(json.dumps(record,indent=2)+'\n')
p=json.loads((O/'plan.json').read_text());p['walkerRouteChanges']=[record];(O/'plan.json').write_text(json.dumps(p,indent=2)+'\n')
r=json.loads((O/'authoring.json').read_text());r['allOriginalSolidGeometryAndGameplayExact']=False;r['allOriginalSolidGeometryAndGameplayExactExceptDeclaredVisitorTurn']=True;r['walkerRouteChanges']=[record];(O/'authoring.json').write_text(json.dumps(r,indent=2)+'\n')
s['capital_visitor_turn_v77']=1;del before,after;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('One source-authored closed-loop visitor turn; original static art and bake exact',flush=True)
