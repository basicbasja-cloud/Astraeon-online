"""One bounded native pass for closed side windows and royal river masonry."""
import bpy,json,hashlib,runpy,math,gc
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v82/grounded-frontages'
s=bpy.context.scene;assert not s.get('capital_grounded_frontages_v82'),'Already applied'
p=json.loads((O/'plan.json').read_text());base=json.loads((O/'baseline.json').read_text())
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['beforeSourceSHA256']
assert hashlib.sha256((R/'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest()==p['beforeNativeSHA256']
helper=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,unlit,metadata=helper['fingerprint'],helper['unlit'],helper['metadata']
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
records=[]
for h in p['houses']:
    c=bpy.data.collections[h['id']];r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent)
    k=Kit(c,r);k.prefix='capital-v82-';w,d=h['width'],h['depth']
    for i,a in enumerate(h['westWindows']):
        prior=set(c.objects)
        k.window('west-ground-'+str(i),a['y'],0,a['z'],a['width'],a['height'],trim='windowIvoryV81',recess=-.025,low=True)
        for o in set(c.objects)-prior:
            for v in o.data.vertices:v.co=Matrix.Rotation(math.pi/2,4,'Z')@v.co+Vector((-w/2,0,0))
            if o.data.materials[0].name=='frontageGlazing':o.data.materials[0]=bpy.data.materials['frontageGlazingV81']
    # Timber ties the formerly blank closed ground core to its existing upper
    # framing. These stay inside the roof/lot envelope, above the stone skirt.
    k.box('west-low-belt',(-w/2-.052,0,.66),(.104,d-.12,.15),'timber')
    for j,y in enumerate((-d/2+.14,d/2-.14)):
        k.box('west-corner-post-'+str(j),(-w/2-.06,y,1.82),(.12,.18,2.6),'timber')
    c['ground_side_occupied_v82']=True
    records.append({'id':h['id'],'closedSideWindows':h['westWindows'],'visibleBlankWestCoreRetained':True,'roofAndOriginalGroundUsesRetained':True})

# Paint the original opaque river surface with the city's full-size dressed
# masonry tile. Continuous station UVs close around an integer repeat count;
# quieter light/dark variants remove the former broad alternating color bands.
for name,color in p['bankColors'].items():
    m=bpy.data.materials[name];m.diffuse_color=(*color,1);m['texture_json']=json.dumps(p['bankTexture'])
bank=bpy.data.collections[p['bankOwner']]
for station in p['bankStations']:
    o=bpy.data.objects[station['id']];assert o in bank.objects[:] and len(o.data.vertices)==10
    for face in o.data.polygons:
        for li in face.loop_indices:
            index=o.data.loops[li].vertex_index;q=o.matrix_world@o.data.vertices[index].co
            o.data.uv_layers.active.data[li].uv=((station['start']+station['length']*(index%2))/p['bankPhysicalRepeat'],q.z/p['bankPhysicalRepeat'])

c=bpy.data.collections.new(p['drainOwner']);c['family']='civic';s.collection.children.link(c)
k=Kit(c,None);k.prefix='capital-v82-'
def top(name,x0,y0,x1,y1,z,material):
    return k.mesh(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[[0,1,2,3]],material,False)
for a in p['drains']:
    before=set(c.objects);w,d=a['width'],a['depth'];z=a['position'][2];n=a['id']
    # Flat grate geometry provides readable thick painted bars without an
    # expensive deep recess, a new image, collision or water simulation.
    top(n+'-pit',-w/2,-d/2,w/2,d/2,z+.006,'civicDoor')
    edge=.07
    for j,(x0,y0,x1,y1) in enumerate([(-w/2,-d/2,w/2,-d/2+edge),(-w/2,d/2-edge,w/2,d/2),(-w/2,-d/2+edge,-w/2+edge,d/2-edge),(w/2-edge,-d/2+edge,w/2,d/2-edge)]):
        top(n+'-frame-'+str(j),x0,y0,x1,y1,z+.014,'stoneLight')
    for j in range(5):
        x=(j-2)*(w-2*edge)/5
        top(n+'-bar-'+str(j),x-.025,-d/2+edge,x+.025,d/2-edge,z+.011,'iron')
    transform=Matrix.Translation(Vector(a['position'][:2]+[0]))@Matrix.Rotation(a['angle'],4,'Z')
    for o in set(c.objects)-before:
        for v in o.data.vertices:v.co=transform@v.co
bpy.context.view_layer.update()
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'));world=exporter['export'](s);now={o['id']:o for o in world['objects']}
chosen={h['id'] for h in p['houses']}
for name,entry in base['owners'].items():
    o=now[name];assert fp(metadata(o))==entry['metadata'],(name,'gameplay')
    parts={a['id']:a for a in o['parts']}
    for n,digest in entry['parts'].items():
        if name==p['bankOwner']:assert fp({k:v for k,v in unlit(parts[n]).items() if k!='uvs'})==entry['opaqueBankPartsExceptUV'][n],n
        else:assert fp(unlit(parts[n]))==digest,(name,n)
    if name not in chosen:assert set(parts)==set(entry['parts']),name
    else:assert all(n in entry['parts'] or n.startswith('capital-v82-') for n in parts),name
assert fp({k:v for k,v in world.items() if k not in ('objects','materials','lighting')})==base['common']
assert all(world['materials'][n]==a for n,a in base['materials'].items() if n not in p['bankColors'])
addition=sum(len(f)-2 for o in world['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces'])-p['beforeVisibleTriangles']
assert 0<addition<p['netTriangleBudget'],addition
city=json.loads(s['capital_plan_json']);city['groundedFrontageRefinement']={'revision':82,'houses':records,'drains':p['drains'],'bankContinuousPhysicalUV':p['bankPhysicalRepeat'],'newImages':0}
s['capital_plan_json']=json.dumps(city);s['capital_grounded_frontages_v82']=1
s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v82-grounded-frontages.png'
for name in ('plan.json','native-plan.json'):(O.parent/name).write_text(json.dumps(city,indent=2)+'\n')
(O/'authoring.json').write_text(json.dumps({'beforeSourceSHA256':p['beforeSourceSHA256'],'houses':records,'drains':p['drains'],'netAddedVisibleTriangles':addition,'newImages':0,'newMaterials':0,'originalCoreRoofDoorsTerrainNavigationGameplayExact':True,'visualAcceptance':'Pending source-matched normal gameplay review'},indent=2)+'\n')
del world,now,base;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('PASS saved occupied side facades,',len(p['drains']),'property drains and continuous shared city masonry; net triangles',addition,flush=True)
