"""Match road-stone scale and planted private edges without new textures/casters."""
import bpy,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76';s=bpy.context.scene
assert s.get('capital_architecture_revision')==76 and not s.get('capital_beta_edges')
plan=json.loads((O/'beta-edge-plan.json').read_text());p=json.loads(s['capital_plan_json'])
mat=bpy.data.materials['publicTownStone'];spec=json.loads(mat['texture_json']);spec['worldSize']=plan['publicStoneWorldSize'];mat['texture_json']=json.dumps(spec)
updated=0
bpy.context.view_layer.update()
for o in bpy.data.collections['court-terrain'].objects:
    if o.type!='MESH' or o.get('export_reference_only') or not o.data.materials or o.data.materials[0]!=mat:continue
    layer=o.data.uv_layers.active or o.data.uv_layers.new(name='WorldUV')
    for face in o.data.polygons:
        for li in face.loop_indices:
            v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv=(v.x/spec['worldSize'],v.y/spec['worldSize'])
    updated+=1
c=bpy.data.collections.new('capital-beta-frontage-groundcover');s.collection.children.link(c);c['family']='vegetation'
for a in plan['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces']);d.materials.append(bpy.data.materials[a['material']]);d.uv_layers.new(name='WorldUV')
    scale=json.loads(d.materials[0]['texture_json'])['worldSize']
    for face in d.polygons:
        for li in face.loop_indices:
            v=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(v.x/scale,v.y/scale)
    o=bpy.data.objects.new(a['id'],d);c.objects.link(o);o['role']='decorative';o['shadow']=False
    # These surfaces are7mm above their unchanged private receivers and below
    # the existing15mm shadow overlay. They receive the original casts without
    # extra shadow rays, textures, solid obstacles or gameplay floor edits.
    o['owned_block']=a['block']
p['betaReferenceRefinement']={k:v for k,v in plan.items() if k!='pieces'}
p['betaReferenceRefinement']['pieces']=len(plan['pieces']);s['capital_plan_json']=json.dumps(p,separators=(',',':'));s['capital_beta_edges']=76
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));actual=exporter['export'](s)
assert actual['lighting'].get('groundShadow'),'Unchanged casters and floor geometry must retain their source-matched shadow bake'
assert runpy.run_path(str(R/'tools/capital-beta-edge-integrity-v76.py'))['preserved_digest'](actual)==plan['preservedSourceDigest'],'Only public UV scale and the planned groundcover may change'
del actual
for folder in ('wayfarer-capital-v75','wayfarer-capital-v76'):
    for name in ('plan.json','native-plan.json'):(R/'docs/review'/folder/name).write_text(json.dumps(p,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('PASS native beta frontage bands and continuous road UV scale;',updated,'public floor meshes',flush=True)
