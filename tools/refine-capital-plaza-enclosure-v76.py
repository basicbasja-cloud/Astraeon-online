"""Apply the reviewed four-property enclosure plan to the editable native city."""
import bpy, json, hashlib, runpy
from pathlib import Path
from mathutils import Matrix, Vector

R=Path(__file__).resolve().parents[1]
O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene
assert s.get('capital_natural_landscape')
data=json.loads((O/'plaza-enclosure-plan.json').read_text())
p,revision,lawns=data['plan'],data['revision'],data['lawns']
assert s.get('capital_plaza_enclosure',0)==revision.get('iteration',1)-1,'Apply each inset once'
previous_authoring=json.loads((O/'plaza-enclosure-authoring.json').read_text()) if revision.get('iteration',1)>1 else None
if previous_authoring:assert previous_authoring.get('iteration',1)==revision['iteration']-1
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==revision['beforeSourceSHA256']
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'))
before=exporter['export'](s)
def triangles(d):
    return sum(len(f)-2 for o in d['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces'])
for m in revision.get('iterationMoves',revision['moves']):
    c=bpy.data.collections[m['id']];members=set(c.objects)
    t=Matrix.Translation(Vector(m['delta']))
    for o in c.objects:
        par=o.parent
        while par and par not in members:par=par.parent
        if par is None:o.matrix_world=t@o.matrix_world
    for o in bpy.data.collections['court-terrain'].objects:
        if o.get('object_id')==m['id'] and ('-entry-contact-' in o.name or '-entry-tread-' in o.name):
            o.matrix_world=t@o.matrix_world
    c['building_preset_json']=json.dumps(next(l for l in p['lots'] if l['id']==m['id']))

terrain=bpy.data.collections['court-terrain']
def floor(a):
    old=bpy.data.objects.get(a['id'])
    d=bpy.data.meshes.new(a['id']+'-plaza-edge')
    d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']])
    d.uv_layers.new(name='WorldUV')
    size=json.loads(d.materials[0].get('texture_json','{}')).get('worldSize',2.4)
    for f in d.polygons:
        for li in f.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/size,v.y/size)
    if old:old.data=d;old.matrix_world=Matrix.Identity(4)
    else:old=bpy.data.objects.new(a['id'],d);terrain.objects.link(old)
    old['export_reference_only']=False;old['surface_role']=a['role'];old['walkable']=True;old['render_visible']=True
old_plan=json.loads(s['capital_plan_json'])
new_ids={a['id'] for a in p['floors']}
for a in old_plan['floors']:
    if a['id'] not in new_ids:bpy.data.objects[a['id']]['export_reference_only']=True
for a in p['floors']:
    if a['id'] in revision['editedPublicFloors'] or a['id'].startswith(('capital-private-plaza-edge-','capital-owned-curb-')):floor(a)
c=bpy.data.collections['capital-owned-block-boundaries']
root=next(o for o in c.objects if o.type=='EMPTY')
bpy.data.batch_remove(ids=[o for o in c.objects if o.type=='MESH'])
FacadeKit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
k=FacadeKit(c,root);k.prefix='capital-v75-'
for i,loop in enumerate(p['privateLoops']):
    for j,(a,b) in enumerate(zip(loop,loop[1:]+loop[:1])):
        if Vector((b[0]-a[0],b[1]-a[1])).length<.0001:continue
        k.mesh(f'owned-curb-{i}-{j}',[(x,y,z) for z in (.025,.20) for x,y in (a,b)],
               [[0,1,3,2]],'roadCurbFace',False,recalculate_normals=False)
c=bpy.data.collections['capital-beta-frontage-groundcover']
for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
for a in lawns['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces'])
    d.materials.append(bpy.data.materials['grass']);d.uv_layers.new(name='WorldUV')
    if a.get('vertexOpacity'):
        layer=d.attributes.new('SurfaceOpacity','FLOAT','POINT')
        for i,value in enumerate(a['vertexOpacity']):layer.data[i].value=value
    for f in d.polygons:
        for li in f.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/7,v.y/7)
    o=bpy.data.objects.new(a['id'],d);c.objects.link(o)
    o['role']='decorative';o['shadow']=False;o['owned_block']=a['block']
walker=bpy.data.objects[revision['walker']['id']]
walker['route_json']=json.dumps([[*q,0] for q in revision['walker']['after']['route']])
s['capital_plan_json']=json.dumps(p,separators=(',',':'))
s['capital_plaza_enclosure']=revision.get('iteration',1)
bpy.context.view_layer.update()
after=exporter['export'](s)
for key in before:
    if key not in ('objects','terrain','lighting'):assert after[key]==before[key],key
old={o['id']:o for o in before['objects']};new={o['id']:o for o in after['objects']}
allowed={m['id'] for m in revision['moves']}|{'capital-owned-block-boundaries','capital-beta-frontage-groundcover'}
for name,a in old.items():
    if name in allowed:continue
    b=new[name]
    if any(w['id']==revision['walker']['id'] for w in a.get('walkers',[])):
        a=json.loads(json.dumps(a))
        for w in a['walkers']:
            if w['id']==revision['walker']['id']:w.update(revision['walker']['after'])
    assert a==b,name
assert len([w for o in after['objects'] for w in o.get('walkers',[])])==28
old_lawn_tris=sum(len(f)-2 for a in old['capital-beta-frontage-groundcover']['parts'] for f in a['faces'])
new_lawn_tris=sum(len(f)-2 for a in new['capital-beta-frontage-groundcover']['parts'] for f in a['faces'])
delta=triangles(after)-triangles(before)
curb_delta=delta-(new_lawn_tris-old_lawn_tris)
assert abs(curb_delta)<2000,curb_delta
landscape=json.loads((O/'landscape-authoring.json').read_text())
landscape['addedTriangles']+=new_lawn_tris-old_lawn_tris
assert 0<landscape['addedTriangles']<landscape['triangleBudget']
landscape['plazaEnclosureLawnRevision']={'oldTriangles':old_lawn_tris,'newTriangles':new_lawn_tris}
if lawns.get('nativeEdgeOpacity'):landscape['grassEdgeBlend']=lawns['edgeBlending']
(O/'landscape-authoring.json').write_text(json.dumps(landscape,indent=2)+'\n')
archive='natural-lawns-before-plaza-2.json' if revision.get('iteration',1)==2 else 'natural-lawns-before-plaza.json'
(O/archive).write_text((O/'natural-lawns-plan.json').read_text())
if data.get('preFeatherLawns'):
    (O/'natural-lawns-before-feather.json').write_text(json.dumps(data['preFeatherLawns'],indent=2)+'\n')
    (O/'grass-feather-plan.json').write_text(json.dumps(lawns,separators=(',',':'))+'\n')
(O/'natural-lawns-plan.json').write_text(json.dumps(lawns,indent=2)+'\n')
for name in ('native-plan.json','plan.json'):
    (O.parent/name).write_text(json.dumps(p,indent=2)+'\n')
revision.update(additionalTriangles=curb_delta+(previous_authoring['additionalTriangles'] if previous_authoring else 0),grassTriangleChange=new_lawn_tris-old_lawn_tris,
                triangleBudget=2000,unchangedObjectsVerified=len(old)-len(allowed),residentCount=28)
(O/'plaza-enclosure-authoring.json').write_text(json.dumps(revision,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Plaza enclosure saved: four complete fronts, continuous terraces and curbs;',delta,'triangle change',flush=True)
