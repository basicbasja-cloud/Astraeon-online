"""Prove only eight declared resident records changed in the full city source.

Removing those records reconstructs the preceding verified export byte for
byte. Existing route sampling independently checks all original/new patrols.
"""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
plan=json.loads((O/'plaza-life-plan.json').read_text());author=json.loads((O/'plaza-life-authoring.json').read_text())
prior=json.loads((O/'before-plaza-life-verified-source.json').read_text())
assert prior['sourceSHA256']==plan['beforeSourceSHA256']==author['beforeSourceSHA256']
assert len(prior['steps'])==14 and all(a['exitCode']==0 for a in prior['steps'])
ids={a['id'] for a in plan['walkers']};assert len(ids)==8
all_walkers=[a for o in s['objects'] for a in o.get('walkers',[])]
new=[a for a in all_walkers if a['id'] in ids];assert len(new)==8
assert len(all_walkers)==36 and len([a for a in all_walkers if a['id'] not in ids])==28
assert new==author['walkers']
coordinate_error=0
for a,expected in zip(new,plan['walkers']):
    for key in expected:
        if key!='route':assert a[key]==expected[key]
    assert len(a['route'])==len(expected['route'])
    coordinate_error=max(coordinate_error,max(abs(x-y) for p,q in zip(a['route'],expected['route']) for x,y in zip(p,q)))
assert coordinate_error<.00002
restored={**s,'objects':[{**o,'walkers':[a for a in o['walkers'] if a['id'] not in ids]} if o['id']==plan['owner'] else o for o in s['objects']]}
restored_raw=(json.dumps(restored,separators=(',',':'))+'\n').encode()
restored_hash=hashlib.sha256(restored_raw).hexdigest()
assert restored_hash==prior['sourceSHA256'],'An unapproved mesh, field, material, original resident or light changed'
ground=s['lighting']['groundShadow'];ground_hash=hashlib.sha256((R/ground['file']).read_bytes()).hexdigest()
assert ground_hash==author['originalGroundBakeSHA256']
prior_views=json.loads((O/'ro3-polish-final/views.json').read_text())
assert len(prior_views)==7 and all(a['sourceSHA256']==restored_hash and a['groundShadowSHA256']==ground_hash for a in prior_views)
traversal=json.loads((O/'traversal.json').read_text())
assert traversal['sourceSHA256']==hashlib.sha256(raw).hexdigest() and traversal['pass']
assert len(traversal['patrolChecks'])==36 and all(a['blockedSamples']==0 for a in traversal['patrolChecks'])
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'reconstructedPreviousSourceSHA256':restored_hash,
    'previousSourceByteForBytePreservedExceptDeclaredNewResidents':True,'allOriginalResidentRecordsPreserved':28,
    'newOriginalWayfarerResidents':8,'totalResidents':36,'allPatrolsClear':True,'maximumNativeRouteCoordinateError':coordinate_error,
    'allOriginalArtLightingNavigationAndGameplayFieldsExactlyPreserved':True,'originalGroundBakeSHA256':ground_hash,
    'lightingReuseJustified':True,'newImages':0,'newStaticTriangles':0,'newCollisionObjects':0,'pass':True,
    'visualAcceptance':'Requires source-matched gameplay review'}
(O/'plaza-life-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
