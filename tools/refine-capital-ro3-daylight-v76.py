"""Native daylight, planted-edge grain and small paving-joint grass candidate.

Guarded one-shot authoring; all pre-existing meshes and gameplay semantics
remain exact. Full image assets are reused without resampling or replacement.
"""
import bpy, json, hashlib, runpy, gc
from pathlib import Path

R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene
assert s.get('capital_plaza_enclosure')==2
assert not s.get('capital_ro3_daylight'),'Daylight candidate already authored'
plan=json.loads((O/'grass-ingress-plan.json').read_text())
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==plan['beforeSourceSHA256']
assert hashlib.sha256((R/plan['jointTexture']['file']).read_bytes()).hexdigest()==plan['jointTextureSHA256']
assert hashlib.sha256((R/'assets/wayfarer-lawn-v44.webp').read_bytes()).hexdigest()==plan['grassTextureSHA256']
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'))
before=exporter['export'](s)
assert before['lighting']['sun']['cast']==[-.42,.55]
colors={'publicTownStone':[.44,.415,.355],'houseApronPaving':[.47,.445,.375],'grass':[.16,.245,.085]}
tone=json.loads((O/'tone.json').read_text())
for name,color in colors.items():
    old=list(bpy.data.materials[name].diffuse_color[:3])
    tone['materials'].setdefault(name,{'before':old})['after']=color
    bpy.data.materials[name].diffuse_color=(*color,1)
grass=bpy.data.materials['grass'];spec=json.loads(grass['texture_json'])
spec.update(paletteNative=True,paletteDetail=.72,meanLinearRGB=plan['grassTextureMeanLinearRGB'],anisotropy=4)
grass['texture_json']=json.dumps(spec)
settings={'sun_strength':.63,'ambient':.46,'ambient_color_json':json.dumps([1.015,1.015,1.015]),
          'shadow_color':'#454843','sun_angular_radius':.04}
native_settings={name:{'before':s.get(name),'after':value} for name,value in settings.items()}
for name,value in settings.items():
    s[name]=value
    if name in tone['lighting']:tone['lighting'][name]['after']=value
s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v76-ro3-polish.png'
owner=bpy.data.collections.new(plan['owner']);owner['family']='vegetation';s.collection.children.link(owner)
for name,color in {'capitalGrassBladeLight':[.20,.29,.095],'capitalGrassBladeShade':[.09,.155,.035]}.items():
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1)
    # Existing lawn grain, native palette: no texture fetch or image duplicate.
    m['texture_json']=json.dumps({**spec,'paletteDetail':.30})
for a in plan['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces'])
    d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV')
    for f in d.polygons:
        for li in f.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/7,v.y/7)
    o=bpy.data.objects.new(a['id'],d);owner.objects.link(o);o['role']='decorative';o['shadow']=False
s['capital_ro3_daylight']=1
bpy.context.view_layer.update();after=exporter['export'](s)
for key in before:
    if key not in ('objects','lighting','materials'):assert before[key]==after[key],key
old={o['id']:o for o in before['objects']};new={o['id']:o for o in after['objects']}
assert new.keys()-old.keys()=={plan['owner']}
for name,o in old.items():assert new[name]==o,name
assert not new[plan['owner']]['portals'] and not new[plan['owner']]['lights']
assert all(a['role']=='decorative' and not a['shadow'] for a in new[plan['owner']]['parts'])
for name,m in before['materials'].items():
    if name not in colors:assert after['materials'][name]==m,name
    elif name!='grass':assert after['materials'][name]['texture']==m['texture'],name
count=sum(len(f)-2 for a in new[plan['owner']]['parts'] for f in a['faces'])
assert count==plan['triangles']<plan['triangleBudget']
receipt={'beforeSourceSHA256':plan['beforeSourceSHA256'],'lightingBefore':before['lighting'],
    'lightingAfter':after['lighting'],'nativeSettings':native_settings,
    'materialsBefore':{n:before['materials'][n] for n in colors},
    'materialsAfter':{n:after['materials'][n] for n in colors},
    'newMaterials':{n:after['materials'][n] for n in after['materials'].keys()-before['materials'].keys()},
    'grassOwner':plan['owner'],'grassTriangles':count,'triangleBudget':plan['triangleBudget'],
    'allExistingOwnersExactlyPreserved':True,'existingOwnerCount':len(old),
    'terrainAndGameplayExactlyPreserved':True,'originalTextureBytesExactlyPreserved':True,
    'visualAcceptance':'Candidate requires source-matched RO3 comparison'}
(O/'ro3-daylight-authoring.json').write_text(json.dumps(receipt,indent=2)+'\n')
tone['noTexturesOrGeometryChanged']=False
tone['originalTextureBytesUnchanged']=True
tone['iterations'].append({'materials':colors,'basis':'Warmer stone, neutral shadows and muted planted edges guided by RO3 street 00:50; gameplay acceptance pending.'})
(O/'tone.json').write_text(json.dumps(tone,indent=2)+'\n')
del before,after,old,new
gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
assert (R/'world/v3/wayfarer-spatial.json').stat().st_size<100*1024*1024
print('RO3 daylight candidate saved;',len(old),'existing owners unchanged;',count,'small grass triangles',flush=True)
