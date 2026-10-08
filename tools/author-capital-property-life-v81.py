"""Apply the sealed v81 upper-window and connected soft-verge plan once."""
import bpy,json,math,hashlib,runpy,gc
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v81/property-life'
s=bpy.context.scene;assert not s.get('capital_property_life_v81'),'Already applied'
p=json.loads((O/'plan.json').read_text())
assert hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()==p['beforeSourceSHA256']
exporter=runpy.run_path(str(R/'tools/export-world-v3.py'))
helper=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,unlit=helper['fingerprint'],helper['unlit']
base=json.loads((O/'baseline.json').read_text())
# The v80 native/source parity is already sealed. Avoid holding two complete
# baked exports alongside Blender in the8GiB workspace. Validate the candidate
# against compact independent fingerprints instead of a second live world.
native_seal=json.loads((R/'docs/review/wayfarer-capital-v80/unique-neighborhoods/verified-source.json').read_text())
assert hashlib.sha256((R/'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest()==native_seal['nativeSHA256']
Kit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
glass=bpy.data.materials['frontageGlazing'].copy();glass.name='frontageGlazingV81'
glass.diffuse_color=(.115,.15,.235,1)
spec=json.loads(glass['texture_json']);spec['paletteNative']=True;spec['paletteDetail']=.16
glass['texture_json']=json.dumps(spec)
trim=bpy.data.materials['stoneLight'].copy();trim.name='windowIvoryV81'
trim.diffuse_color=(.71,.61,.43,1)
spec=json.loads(trim.get('texture_json','{}'));assert spec
spec['paletteNative']=True;spec['paletteDetail']=.22;trim['texture_json']=json.dumps(spec)

class WindowKit(Kit):
    def window(self,*args,**kwargs):
        prior=set(self.owner.objects)
        kwargs['trim']='windowIvoryV81'
        super().window(*args,**kwargs)
        for o in set(self.owner.objects)-prior:
            if o.type=='MESH' and o.data.materials[0].name=='frontageGlazing':o.data.materials[0]=glass

records=[];removed=[]
for h in p['houses']:
    c=bpy.data.collections[h['id']];r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent)
    for name in base['owners'][h['id']]['removedUpperFaces']:
        o=bpy.data.objects[name];assert o in c.objects[:]
        removed.append({'owner':h['id'],'part':name});bpy.data.objects.remove(o,do_unlink=True)
    k=WindowKit(c,r);k.prefix='capital-v81-'
    w,d,v=h['width'],h['depth'],h['variation']
    mat={'residential':'homeLimewash','market':'merchantLimewash','workshop':'workshopLimewash'}[h['family']]
    if h['design']=='stepped-gables':
        main=w*(.59+v*.15);side=w-main
        wings=[('main-wing',-side/2,0,main,d,6.4+v),('lower-wing',main/2,0,side,d,4.25-v)]
    else:
        name,top={'garden-cottage':('low-home',4.6+v),'dormered-gambrel':('trade-home',5.2+v),'corner-oriel':('corner-home',5.8+v)}[h['design']]
        wings=[(name,0,0,w,d,top)]
    faces=[]
    for name,x,y,ww,dd,top in wings:
        for face,width,origin,angle in [('front',ww,(x,y+dd/2+.10),0),('back',ww,(x,y-dd/2-.08),math.pi),('west',dd,(x-ww/2-.05,y),math.pi/2),('east',dd,(x+ww/2+.05,y),-math.pi/2)]:
            bays=max(1,min(4,int(width/1.9)));spacing=width/(bays+.6)
            centers=[(j-(bays-1)/2)*spacing for j in range(bays)]
            window_w=min(p['newWindowWidthCap'],spacing-.28)
            window_h=min(p['newWindowHeightCap'],top-3.1-.43)
            assert window_w>.4 and window_h>.4,(h['id'],face)
            k.upper_face(name+'-'+face,width,3.1,top,centers,mat,origin,angle,wh=window_h,ww=window_w)
            faces.append({'wing':name,'face':face,'bays':bays,'windowWidth':window_w,'windowHeight':window_h,'baySpacing':spacing,'wallTop':top})
    records.append({'id':h['id'],'faces':faces,'retainedRoofDoorCoreAndGroundUses':True})
    c['property_window_refinement_v81']=True

# Grounded, edge-feathered grass uses the full existing texture. Each small
# patch has a separate native part for editing; transport already batches by
# material/cell, so this introduces no per-patch browser draw call.
c=bpy.data.collections.new(p['newOwner']);c['family']='civic';s.collection.children.link(c)
for a in p['pieces']:
    d=bpy.data.meshes.new(a['id']);d.from_pydata(a['vertices'],[],a['faces'])
    d.materials.append(bpy.data.materials['grass']);d.uv_layers.new(name='WorldUV')
    opacity=d.attributes.new('SurfaceOpacity','FLOAT','POINT')
    for i,val in enumerate(a['vertexOpacity']):opacity.data[i].value=val
    for face in d.polygons:
        for li in face.loop_indices:
            q=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(q.x/7,q.y/7)
    o=bpy.data.objects.new(a['id'],d);c.objects.link(o);o['role']='decorative';o['shadow']=False;o['property_zone']=a['block']
bpy.context.view_layer.update()
after=exporter['export'](s);now={o['id']:o for o in after['objects']}
for old_id,entry in base['owners'].items():
    current=now[old_id]
    assert fp(helper['metadata'](current))==entry['metadata'],old_id
    if old_id not in {h['id'] for h in p['houses']}:assert fp([unlit(a) for a in current['parts']])==entry['parts'],old_id
    else:
        parts={a['id']:a for a in current['parts']}
        for name,digest in entry['retainedParts'].items():assert fp(unlit(parts[name]))==digest,(old_id,name)
assert fp({k:v for k,v in after.items() if k not in ('objects','materials','lighting')})==base['common']
assert all(after['materials'][name]==value for name,value in base['materials'].items())
tri=lambda world:sum(len(f)-2 for o in world['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces'])
addition=tri(after)-p['beforeVisibleTriangles'];assert 0<addition<4500,addition
city=json.loads(s['capital_plan_json'])
city['propertyLifeRefinement']={'revision':81,'houses':records,'newGrassOwner':p['newOwner'],'grassPatches':p['patches'],'newPlantedArea':p['newPlantedArea']}
s['capital_plan_json']=json.dumps(city);s['capital_property_life_v81']=1
s['ground_shadow_asset']='assets/wayfarer-ground-shadow-v81-property-life.png'
for name in ('plan.json','native-plan.json'):(O.parent/name).write_text(json.dumps(city,indent=2)+'\n')
(O/'authoring.json').write_text(json.dumps({'beforeSourceSHA256':p['beforeSourceSHA256'],'houses':records,'removedParts':removed,'newOwner':p['newOwner'],'netAddedVisibleTriangles':addition,'newImageAssets':0,'originalRoofFormsDoorsCollisionTerrainNavigationGameplayExact':True,'visualAcceptance':'Pending source-matched normal gameplay review'},indent=2)+'\n')
del after,now,base;gc.collect()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('PASS saved12 houses with larger pierced upper openings and',p['patches'],'connected path-edge patches; net triangles',addition,flush=True)
