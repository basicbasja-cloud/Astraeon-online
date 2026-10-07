"""Native, guarded street-depth candidate. Original images stay full resolution."""
import bpy, json, math, runpy, hashlib, gc
from pathlib import Path
from mathutils import Matrix, Vector
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v77/street-depth';s=bpy.context.scene
plan=json.loads((O/'plan.json').read_text())
assert not s.get('capital_street_depth_v77'),'Already applied'
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==plan['beforeSourceSHA256']
exp=runpy.run_path(str(R/'tools/export-world-v3.py'));before=exp['export'](s)
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
changes={}
def material_change(name,color=None,**settings):
    m=bpy.data.materials[name];changes[name]={'before':before['materials'][name]}
    if color:m.diffuse_color=(*color,1)
    spec=json.loads(m.get('texture_json','{}'));spec.update(settings);m['texture_json']=json.dumps(spec)
material_change('publicTownStone',worldSize=5.76,paletteDetail=.58)
material_change('frontageGlazing',color=[.055,.12,.16],paletteDetail=.18)
for name in ('homeLimewash','merchantLimewash','workshopLimewash','roofClayWarm','roofClayRose','roofClayOchre'):
    if name not in before['materials']:continue
    spec=before['materials'][name].get('texture',{})
    if spec:material_change(name,paletteDetail=min(spec.get('paletteDetail',.8),.56))
# Increase the physical tile repeat size in native UVs, rather than swapping in
# lower-resolution art or silently modifying only the renderer.
uv_meshes=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.materials or o.data.materials[0].name!='publicTownStone':continue
    assert o.data.uv_layers.active,o.name
    for f in o.data.polygons:
        for li in f.loop_indices:
            q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            o.data.uv_layers.active.data[li].uv=(q.x/5.76,q.y/5.76)
    uv_meshes.append(o.name)
# Each old tuft occupies nine consecutive vertex indices in its spatial-cell
# mesh. Preserve blade dimensions; move only declared painted-joint roots.
old=json.loads((R/'docs/review/wayfarer-capital-v76/property-frontages/grass-ingress-plan.json').read_text())
shift={a['root']:a for a in plan['grassRootShifts']};offsets={};remove={}
for index,a in enumerate(old['roots']):
    x,y,z=a['position'];cell=(int(x//32),int(y//32))
    for blade in range(3):
        mat='capitalGrassBladeLight' if (index+blade)%3 else 'capitalGrassBladeShade'
        name=f'capital-grass-{cell[0]}-{cell[1]}-{mat}';off=offsets.get(name,0);offsets[name]=off+3
        if index not in shift:continue
        q=shift[index];o=bpy.data.objects[name]
        if q['after'] is None:remove.setdefault(name,set()).update(range(off,off+3));continue
        delta=Vector(q['after'])-Vector(q['before'])
        for j in range(off,off+3):o.data.vertices[j].co+=delta
for name,indices in remove.items():
    import bmesh
    o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[j] for j in indices],context='VERTS');bm.to_mesh(o.data);bm.free()
for name in offsets:
    o=bpy.data.objects[name]
    for f in o.data.polygons:
        for li in f.loop_indices:
            q=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(q.x/7,q.y/7)
sun_settings={'sun_cast_x':-.63,'sun_cast_y':.825,'sun_strength':.82,'ambient':.38,'shadow_color':'#62645e'}
for n,v in sun_settings.items():s[n]=v
s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v77-street-depth.png'

new_ids=[];source=bpy.data.collections['capital-tree-000']
visible=[o for o in source.objects if o.type=='MESH' and o.get('render_visible',True)]
stem=next(o for o in visible if o.get('role')=='solid')
pts=[stem.matrix_world@v.co for v in stem.data.vertices]
center=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)))
height=max((o.matrix_world@v.co).z-center.z for o in visible for v in o.data.vertices)
furniture=bpy.data.collections.new('capital-street-parklets-v77');furniture['family']='civic';s.collection.children.link(furniture);new_ids.append(furniture.name)
for a in plan['parklets']:
    name='capital-street-tree-v77-'+a['id'];c=bpy.data.collections.new(name);c['family']='vegetation';s.collection.children.link(c);new_ids.append(name)
    q=Vector(a['position']);q.z-=.015;scale=a['height']/height
    transform=Matrix.Translation(q)@Matrix.Rotation(a['treeRotation'],4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-center)
    for index,original in enumerate(visible):
        o=original.copy();o.data=original.data.copy();o.name=name+'-'+str(index);o.parent=None
        o.matrix_world=Matrix.Identity(4)
        for v in o.data.vertices:v.co=transform@(original.matrix_world@v.co)
        light=o.data.color_attributes.get('BakedTownLight')
        if light:o.data.color_attributes.remove(light)
        c.objects.link(o)
    root=bpy.data.objects.new(name+'-furniture-frame',None);c.objects.link(root)
    root.location=a['position'];k=Kit(c,root);k.prefix='capital-v77-'
    # A small planted stone surround gives each street tree a owned contact.
    r=.52;verts=[]
    for z,radius in [(0,r),(.28,r),(.28,r-.09)]:
        verts += [(radius*math.cos(j*math.tau/12),radius*math.sin(j*math.tau/12),z) for j in range(12)]
    faces=[[j,(j+1)%12,12+(j+1)%12,12+j] for j in range(12)]
    faces += [[12+j,12+(j+1)%12,24+(j+1)%12,24+j] for j in range(12)]
    rim=k.mesh(name+'-stone-surround',verts,faces,'stoneLight');rim['role']='solid'
    k.mesh(name+'-soil',[(0,0,.255)]+verts[24:],[[0,j+1,(j+1)%12+1] for j in range(12)],'soil',False)
    frame=bpy.data.objects.new(name+'-bench-frame',None);furniture.objects.link(frame);frame.location=a['benchPosition'];frame.rotation_euler.z=a['benchAngle']
    b=Kit(furniture,frame);b.prefix='capital-v77-'
    for j in range(4):b.box(name+'-seat-slat-'+str(j),(0,-.21+j*.14,.48),(1.8,.11,.08),'oak')
    for j in range(3):b.box(name+'-back-slat-'+str(j),(0,.31,.69+j*.14),(1.8,.08,.11),'oak')
    for side in (-1,1):
        b.box(name+'-leg-'+str(side),(side*.70,0,.24),(.12,.58,.48),'iron')
        b.beam(name+'-back-support-'+str(side),(side*.7,.26,.35),(side*.7,.31,1.08),.09,'iron')
    # One conservative hidden proxy covers the seat and feet; the back is
    # decorative. This avoids walk-through props without a detailed collider.
    proxy=b.box(name+'-bench-proxy',(0,.02,.52),(1.86,.68,1.04),'oak',False);proxy['role']='solid';proxy['render_visible']=False

p=json.loads(s['capital_plan_json']);p['betaReferenceRefinement']['publicStoneWorldSize']=5.76
p['streetDepthRefinement']={'revision':77,'parklets':plan['parklets'],'publicStoneWorldSize':5.76,'newOwners':new_ids}
s['capital_plan_json']=json.dumps(p);s['capital_street_depth_v77']=1
for name in ('plan.json','native-plan.json'):(O.parent/name).write_text(json.dumps(p,indent=2)+'\n')
bpy.context.view_layer.update();after=exp['export'](s)
for n in changes:changes[n]['after']=after['materials'][n]
old_objects={o['id']:o for o in before['objects']};new_objects={o['id']:o for o in after['objects']}
assert set(new_objects)-set(old_objects)==set(new_ids)
for n,o in old_objects.items():
    for key in ('family','portals','services','lights','walkers','presentation'):assert o.get(key)==new_objects[n].get(key),(n,key)
    assert [a for a in o['parts'] if a['role']=='solid']==[a for a in new_objects[n]['parts'] if a['role']=='solid'],n
added=sum(len(f)-2 for n in new_ids for a in new_objects[n]['parts'] if a.get('visible',True) for f in a['faces'])
assert added<plan['triangleBudget'],added
receipt={'beforeSourceSHA256':plan['beforeSourceSHA256'],'newOwners':new_ids,'addedTriangles':added,
    'materialChanges':changes,'lightingBefore':before['lighting'],'lightingAfter':after['lighting'],
    'nativeSunSettings':sun_settings,'publicUVMeshes':uv_meshes,'allOriginalSolidGeometryAndGameplayExact':True,
    'pavingImageBytesRetained':True,'originalResolutionRetained':True,'visualAcceptance':'Pending source-matched capture'}
(O/'authoring.json').write_text(json.dumps(receipt,indent=2)+'\n')
del before,after,old_objects,new_objects;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
assert (R/'world/v3/wayfarer-spatial.json').stat().st_size<100*1024*1024
print('Native street-depth candidate:',len(plan['parklets']),'owned tree-and-seat parklets;',added,'added triangles',flush=True)
