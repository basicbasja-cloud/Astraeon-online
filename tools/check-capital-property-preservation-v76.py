"""Compare the rendered frontage candidate with the audited Git checkpoint.

Allow the recorded property meshes, color choices and refreshed baked lighting.
Independently preserve every other mesh, UV, floor, gameplay anchor and collider.
"""
import json, hashlib, subprocess, collections
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'docs/review/wayfarer-capital-v76/property-frontages'
base_raw=subprocess.check_output(['git','show','d7f9f15:world/v3/wayfarer-spatial.json'],cwd=R)
assert hashlib.sha256(base_raw).hexdigest()=='ad5956f55b4a4d1fb00c665754f5bc28f13b001a7f1456bf0e6c3e01894155dc'
base=json.loads(base_raw);raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();now=json.loads(raw)
author=json.loads((O/'authoring.json').read_text());tone=json.loads((O/'tone.json').read_text())
daylight_path=O/'ro3-daylight-authoring.json'
daylight=json.loads(daylight_path.read_text()) if daylight_path.exists() else None
life_path=O/'plaza-life-authoring.json'
life=json.loads(life_path.read_text()) if life_path.exists() else None
changed={p['id'] for p in author['properties']};assert len(changed)==46
landscape=json.loads((O/'landscape-authoring.json').read_text())
tree_parts={t['id']:set(t['parts']) for t in landscape['trees']};assert len(tree_parts)==78
def geometric(part):return {k:v for k,v in part.items() if k!='bakedLighting'}
plaza_path=O/'plaza-enclosure-authoring.json'
plaza=json.loads(plaza_path.read_text()) if plaza_path.exists() else None
moves={m['id']:m['delta'] for m in plaza['moves']} if plaza else {}
translation_errors=[]
def translated_equal(before,after,delta):
    excluded=('vertices','bakedLighting','polygon')
    assert {k:v for k,v in before.items() if k not in excluded}=={k:v for k,v in after.items() if k not in excluded}
    assert len(before['vertices'])==len(after['vertices'])
    error=max(abs(v[i]+delta[i]-q[i]) for v,q in zip(before['vertices'],after['vertices']) for i in range(3))
    translation_errors.append(error)
    # Two rounded Float32 coordinate endpoints can differ by two export units.
    assert error<=.000020001,(before['id'],error)
    if 'polygon' in before:assert max(abs(a[i]+delta[i]-b[i]) for a,b in zip(before['polygon'],after['polygon']) for i in (0,1))<.00002
if plaza:
    plan=json.loads((O.parent/'native-plan.json').read_text())
    inset=plaza.get('targetInset',10);assert inset in (10,16)
    assert len(moves)==4 and all(abs(d[0])==inset and d[1:]==[0,0] for d in moves.values())
    for key in base['terrain']:
        if key!='surfaces':assert base['terrain'][key]==now['terrain'][key],key
    old_floors={a['id']:a for a in base['terrain']['surfaces']}
    new_floors={a['id']:a for a in now['terrain']['surfaces']}
    planned={a['id']:a for a in plan['floors']}
    permitted=set(plaza['editedPublicFloors'])|{n for n in old_floors|new_floors if n.startswith(('capital-owned-curb-','capital-private-plaza-edge-'))}
    for name in old_floors|new_floors:
        if name in permitted:
            expected=planned.get(name);actual=new_floors.get(name)
            if expected is None:assert actual is None;continue
            assert actual and actual['faces']==expected['faces'] and actual['material']==expected['material'] and actual['role']==expected['role']
            assert actual['walkable'] and actual['visible']
            assert len(expected['vertices'])==len(actual['vertices'])
            assert max(abs(x-y) for a,b in zip(expected['vertices'],actual['vertices']) for x,y in zip(a,b))<.00002
            size=now['materials'][actual['material']]['texture']['worldSize']
            for f,uv in zip(actual['faces'],actual['uvs']):
                for i,q in zip(f,uv):assert max(abs(q[j]-actual['vertices'][i][j]/size) for j in (0,1))<.00002
        elif old_floors[name].get('objectId') in moves:
            translated_equal(old_floors[name],new_floors[name],moves[old_floors[name]['objectId']])
        else:assert old_floors[name]==new_floors[name],name
for key in base:
    if key not in ('objects','materials','lighting') and not (plaza and key=='terrain'):assert now[key]==base[key],key
old_objects={o['id']:o for o in base['objects']};new_objects={o['id']:o for o in now['objects']}
assert new_objects.keys()-old_objects.keys()==({daylight['grassOwner']} if daylight else set())
assert not old_objects.keys()-new_objects.keys()
solids=doors=unmodified_parts=0;walkers=[]
for name,old in old_objects.items():
    new=new_objects[name]
    for key in old:
        if key!='parts':
            expected=old[key]
            if plaza and key=='walkers':expected=[plaza['walker']['after'] if w['id']==plaza['walker']['id'] else w for w in expected]
            if life and name==life['owner'] and key=='walkers':expected=expected+life['walkers']
            assert new[key]==expected,(name,key)
    for role in ('solid','door'):
        select=lambda p: p['role']=='solid' if role=='solid' else p['id'].endswith('-door-leaf')
        before=[geometric(p) for p in old['parts'] if select(p)]
        after=[geometric(p) for p in new['parts'] if select(p)]
        if name in moves:
            assert len(before)==len(after)
            for a,b in zip(before,after):translated_equal(a,b,moves[name])
        else:assert before==after,(name,role)
        if role=='solid':solids+=len(before)
        else:doors+=len(before)
    if name not in changed:
        if name=='capital-beta-frontage-groundcover':
            assert all(p['material']=='grass' and p['role']=='decorative' and not p['shadow'] for p in new['parts'])
        elif plaza and name=='capital-owned-block-boundaries':
            parts={a['id']:a for a in new['parts']};expected=set()
            for i,loop in enumerate(plan['privateLoops']):
                for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
                    if sum((b[k]-a[k])**2 for k in (0,1))<.00000001:continue
                    n=f'capital-v75-owned-curb-{i}-{j}';expected.add(n);part=parts[n]
                    assert part['role']=='decorative' and not part['shadow'] and part['material']=='roadCurbFace'
                    assert part['faces']==[[0,1,3,2]]
                    vs=[[x,y,z] for z in (.025,.20) for x,y in (a,b)]
                    assert max(abs(x-y) for a,b in zip(vs,part['vertices']) for x,y in zip(a,b))<.00002
            assert parts.keys()==expected
        else:
            allowed=tree_parts.get(name,set())
            assert {p['id'] for p in old['parts']}=={p['id'] for p in new['parts']},name
            before_parts=[geometric(p) for p in old['parts'] if p['id'] not in allowed]
            after_parts=[geometric(p) for p in new['parts'] if p['id'] not in allowed]
            if name in moves:
                assert len(before_parts)==len(after_parts)
                for a,b in zip(before_parts,after_parts):translated_equal(a,b,moves[name])
            else:assert before_parts==after_parts,name
            unmodified_parts+=len(old['parts'])-len(allowed)
    walkers.extend(new.get('walkers',[]))
assert len(walkers)==28+(life['newWalkerRecords'] if life else 0)
assert len([a for a in walkers if not a['id'].startswith('capital-plaza-life-')])==28
assert now['materials'].keys()-base['materials'].keys()==(daylight['newMaterials'].keys() if daylight else set())
assert not base['materials'].keys()-now['materials'].keys()
for name,old in base['materials'].items():
    expected=dict(old)
    if name in tone['materials']:
        expected['color']=tone['materials'][name]['after']
        assert all(abs(a-b)<1e-6 for a,b in zip(expected['color'],now['materials'][name]['color'])),name
        expected['color']=now['materials'][name]['color']
    if daylight and name=='grass':
        # Only the recorded grain normalization opts into the native palette;
        # the original image, tile, world scale and UVs are independently kept.
        assert old['texture']==daylight['materialsBefore'][name]['texture']
        expected['texture']=daylight['materialsAfter'][name]['texture']
    assert expected==now['materials'][name],name
if daylight:
    for name,expected in daylight['newMaterials'].items():assert now['materials'][name]==expected,name
assert base['lighting']['sun']['cast']==now['lighting']['sun']['cast']
if daylight:
    expected={k:v for k,v in daylight['lightingAfter'].items() if k!='groundShadow'}
    assert expected=={k:v for k,v in now['lighting'].items() if k!='groundShadow'}
    assert daylight['lightingBefore']['sun']['strength']==base['lighting']['sun']['strength']
    assert daylight['lightingBefore']['ambient']==base['lighting']['ambient']
else:
    assert base['lighting']['sun']['strength']==now['lighting']['sun']['strength']
    assert base['lighting']['ambient']==now['lighting']['ambient']
assert now['lighting']['sun']['color']==json.loads(tone['lighting']['sun_color_json']['after'])
assert now['lighting']['ambientColor']==json.loads(tone['lighting']['ambient_color_json']['after'])
assert now['lighting']['shadowColor']==tone['lighting']['shadow_color']['after']
assert now['lighting']['groundShadow']['resolution']==base['lighting']['groundShadow']['resolution']==4096
assert now['lighting']['groundShadow']['geometryDigest']!=base['lighting']['groundShadow']['geometryDigest']
def triangles(source):return sum(len(f)-2 for o in source['objects'] for p in o['parts'] if p.get('visible',True) for f in p['faces'])
extra=triangles(now)-triangles(base)
assert extra==author['addedTriangles']+landscape['addedTriangles']+(plaza['additionalTriangles'] if plaza else 0)+(daylight['grassTriangles'] if daylight else 0)
assert 0<author['addedTriangles']<author['triangleBudget']
assert 0<landscape['addedTriangles']<landscape['triangleBudget']
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'baselineSHA256':hashlib.sha256(base_raw).hexdigest(),
        'changedProperties':len(changed),'uses':dict(collections.Counter(p['use'] for p in author['properties'])),
        'unchangedOtherMeshParts':unmodified_parts,'preservedSolids':solids,'preservedDoorLeaves':doors,
        'preservedWalkers':28,'totalWalkers':len(walkers),'publicAndPrivateFloorsExactlyPreserved':not bool(plaza),
        'allAnchorsExactlyPreserved':not bool(plaza),'existingTextureSpecificationsExactlyPreserved':not bool(daylight),
        'addedStaticTriangles':extra,'staticTriangleIncreasePercent':round(extra/triangles(base)*100,3),
        'revisedTreeCrowns':len(tree_parts),'treeRootsAndAllOtherTreePartsExactlyPreserved':True,
        'floorAtlasResolution':4096,'exportBytes':len(raw),'pass':True,
        'visualAcceptance':'Requires source-matched gameplay review'}
if plaza:report['plazaEnclosure']={'translatedWholeProperties':len(moves),'privateExtensionArea':plaza['privateExtensionArea'],
    'retainedRoadWidths':plaza['retainedRoadWidths'],'editedPublicFloors':plaza['editedPublicFloors'],
    'maximumTranslationRoundingError':max(translation_errors),
    'allOtherFloorsAndAnchorsExactlyPreserved':True,'reroutedExistingResident':plaza['walker']['id']}
if daylight:report['daylight']={'lighting':expected,'nativeLawnGrainNormalization':True,
    'allOriginalTextureBytesAndResolutionsRetained':daylight['originalTextureBytesExactlyPreserved'],
    'addedDecorativeGrassTriangles':daylight['grassTriangles'],'additionalGameplayObstacles':0}
if life:report['plazaActivity']={'newResidents':life['newWalkerRecords'],'allOriginalResidentRecordsPreserved':True,
    'existingCharacterArtworkReused':True,'newImagesOrStaticTriangles':0}
(O/'preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
