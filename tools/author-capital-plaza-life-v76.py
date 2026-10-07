"""Add original plaza activity without changing art, collision or lighting."""
import bpy,json,hashlib,runpy,gc
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene;assert s.get('capital_ro3_daylight')==1 and not s.get('capital_plaza_life')
plan=json.loads((O/'plaza-life-plan.json').read_text())
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==plan['beforeSourceSHA256']
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exporter['export'](s)
owner=bpy.data.collections[plan['owner']]
for a in plan['walkers']:
    assert a['id'] not in bpy.data.objects
    o=bpy.data.objects.new(a['id'],None);owner.objects.link(o)
    o['kind']='walker';o['data_json']=json.dumps({k:v for k,v in a.items() if k not in ('id','route')})
    o['route_json']=json.dumps([[*q,0] for q in a['route']])
s['capital_plaza_life']=1;bpy.context.view_layer.update();after=exporter['export'](s)
for key in before:
    if key!='objects':assert before[key]==after[key],key
old={o['id']:o for o in before['objects']};new={o['id']:o for o in after['objects']};assert old.keys()==new.keys()
for name,a in old.items():
    if name!=plan['owner']:assert new[name]==a,name
    else:
        for key in a:
            if key!='walkers':assert new[name][key]==a[key],key
        assert new[name]['walkers'][:len(a['walkers'])]==a['walkers']
        for actual,expected in zip(new[name]['walkers'][len(a['walkers']):],plan['walkers']):
            for key in expected:
                if key!='route':assert actual[key]==expected[key]
            assert len(actual['route'])==len(expected['route'])
            assert max(abs(x-y) for p,q in zip(actual['route'],expected['route']) for x,y in zip(p,q))<.00002
assert exporter['shadow_geometry_digest'](before)==exporter['shadow_geometry_digest'](after)==after['lighting']['groundShadow']['geometryDigest']
receipt={k:v for k,v in plan.items() if k!='walkers'}
receipt.update(allOriginalMeshesFloorsAndMaterialsExactlyPreserved=True,allOriginalLightingExactlyPreserved=True,
    originalGroundBakeSHA256=hashlib.sha256((R/after['lighting']['groundShadow']['file']).read_bytes()).hexdigest(),
    groundGeometryDigest=after['lighting']['groundShadow']['geometryDigest'],lightingReuseJustified=True,
    originalWalkerRecordsExactlyPreserved=plan['beforeWalkerCount'],newWalkerRecords=len(plan['walkers']),
    visualAcceptance='Requires source-matched gameplay review')
receipt['walkers']=new[plan['owner']]['walkers'][len(old[plan['owner']]['walkers']):]
(O/'plaza-life-authoring.json').write_text(json.dumps(receipt,indent=2)+'\n')
p=json.loads(s['capital_plan_json']);assert p['ambientPopulation']==plan['beforeWalkerCount']
p['ambientPopulation']=plan['afterWalkerCount']
p['plazaLifeRefinement']={'additionalResidents':len(plan['walkers']),'existingResidentsPreserved':plan['beforeWalkerCount'],
    'roles':[a['id'] for a in plan['walkers']],'existingArtworkReused':True}
s['capital_plan_json']=json.dumps(p,separators=(',',':'))
for name in ('native-plan.json','plan.json'):(O.parent/name).write_text(json.dumps(p,indent=2)+'\n')
del before,after,old,new;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Saved plaza activity:',plan['afterWalkerCount'],'walkers; original28, all meshes, navigation and baked lighting preserved',flush=True)
