"""Fit authored lots to full street corridors; resolve road/house and lot/lot overlap.

This is a one-time layout edit on v44. The concept informs the atmosphere and
landmark hierarchy; precise frontage/setback choices follow playable geometry.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;assert scene['town_plan_version']==44
assert scene.get('street_fitting_version')!=45,'Run once; subsequent edits use the saved source'
terrain=bpy.data.collections['court-terrain']
def root_for(cid):
    c=bpy.data.collections[cid];root=bpy.data.objects.get(cid+'-placement')
    if root is None:
        vs=[o.matrix_world@v.co for o in c.objects if o.type=='MESH' and o.get('render_visible',True) for v in o.data.vertices]
        root=bpy.data.objects.new(cid+'-placement',None);c.objects.link(root);root.location=((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,0)
        bpy.context.view_layer.update()
        for o in list(c.objects):
            if o==root:continue
            before=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=before
    return root
def shift(cid,dx=0,dy=0,rotation=0):
    root=root_for(cid);matrix=root.matrix_world.copy();matrix.translation+=Vector((dx,dy,0))
    if rotation:matrix=Matrix.Translation(matrix.translation)@Matrix.Rotation(math.radians(rotation),4,'Z')
    root.matrix_world=matrix
def place(cid,x,y,rotation=0):
    root=root_for(cid);p=root.matrix_world.translation;shift(cid,x-p.x,y-p.y,rotation)
# Frontage slots preserve architectural dimensions. Clear corridors replace
# the earlier direct placement over occupied lots.
shift('east-inn',-6,0)
shift('artisan-workshop',-6,1)
shift('district-southwest-lodge',0,5)
shift('district-southeast-courtyard-house',0,2)
shift('district-east-market-tower-house',3.5,0)
shift('district-northwest-lodge',-3.3,-2)
shift('north-house',6.5,0,90)
shift('willow-house',0,8,180)
shift('avenue-cottage-east',1.5,0)
shift('avenue-home-west',0,0,-90)
for cid,x,y,angle in [('frontage-baker',31.5,43,0),('frontage-apothecary',41.5,61,90),('frontage-cobbler',43,73,0),('frontage-weaver',64,73,0),('frontage-market-arcade',80,38,0),('frontage-garden-home',41.5,25,0),('frontage-scribe',67.5,25,0),('frontage-willow-east',80,74,0),('frontage-riverside',79,86,180),('frontage-joiner',20,63.5,0)]:place(cid,x,y,angle)
bpy.context.view_layer.update()
# A browsing forum, with complete existing stalls along its edges facing inward.
for cid,x,y,angle in [('food-market',85.1,60.5,90),('market-spices',85.1,66,90),('market-textiles',73.9,60,-90),('market-supplies',73.9,65.3,-90),('caravan-cart',95,57,0)]:place(cid,x,y,angle)
for o in bpy.data.collections['district-market-court'].objects:
    if o.type=='MESH':o['render_visible']=False;o['role']='decorative';o['shadow']=False
# The deliberate grove strip sits between frontage and the main avenue.
for i,x,y in [(0,47,65),(1,47,71),(2,47,77),(3,59.4,64),(4,59.4,69),(5,59.4,76)]:
    objects=[o for o in bpy.data.collections['wayfarer-v44-gardens'].objects if o.name.startswith(f'grove-v44-{i}-')]
    old=[(44,65),(43,71),(44,77),(63,65),(64,71),(63,77)][i]
    for o in objects:
        o.location.x+=x-old[0];o.location.y+=y-old[1]

def mesh(name,vs,fs,role='primary'):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials['paving']);data.uv_layers.new(name='PhysicalUV')
    for face in data.polygons:
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p.x/4,p.y/4)
    o=bpy.data.objects.new(name,data);terrain.objects.link(o);o['role']='decorative';o['shadow']=False;o['surface_role']=role;o['walkable']=True;return o
def remove(name):
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
def road(name,a,b,width):
    remove(name);dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*width/2,dx/n*width/2
    o=mesh(name,[(a[0]+nx,a[1]+ny,.048),(b[0]+nx,b[1]+ny,.048),(b[0]-nx,b[1]-ny,.048),(a[0]-nx,a[1]-ny,.048)],[[0,1,2,3]]);o['road_segment']=True;o['legacy_role']='avenue' if width>=7 else 'street';return o
def apron(name,x0,y0,x1,y1,role='forecourt'):return mesh(name,[(x0,y0,.049),(x1,y0,.049),(x1,y1,.049),(x0,y1,.049)],[[0,1,2,3]],role)
for o in list(terrain.objects):
    if o.name.startswith('plan-v44-approach-'):bpy.data.objects.remove(o,do_unlink=True)
road('plan-v44-west-crossroad',(50.7,49),(23,49),6)
road('plan-v44-forge-lane',(28,74),(19,74),3.8)
road('plan-v45-inn-door-lane',(23,44.5),(15,44.5),3.2)
road('plan-v45-apothecary-lane',(28,61),(38.4,61),3.2)
road('plan-v45-copper-lane',(28,69.5),(38,69.5),2.7)
road('plan-v45-home-lane',(43,68.4),(54,68.4),2.7)
road('plan-v45-arcade-lane',(78,43),(78,54),3.2)
road('plan-v45-housing-lane',(28,75.215),(30.22,75.215),3.2)
apron('plan-v45-forge-yard',16,71.48,22.5,74.7,'yard')
apron('plan-v45-market-forum',71.5,57,86.5,66.4,'market')
apron('plan-v45-spice-pad',83.4,66.4,86.5,69,'market')
for name,x,y,w,d,front in [('bookbinder',70,46,6,5,'S'),('cobbler',43,73,6,5,'S'),('weaver',64,73,7,5,'S'),('willow-east',80,74,6,5,'S')]:
    y0=y+d/2;y1=51.2 if name=='bookbinder' else 77.6
    apron('plan-v45-frontage-'+name,x-1.4,y0,x+1.4,y1)
apron('plan-v45-apothecary-threshold',38.4,59.6,39.1,62.4)
# Re-author patrols along unobstructed public routes. Earlier doubled diagonals
# belonged to the compact town and cannot be reused across occupied plots.
routes=[[(54,86),(54,64),(56,64),(56,86)],[(28,77),(28,51),(45,49),(45,54)],[(47,56),(47,46),(61,46),(61,56)],[(78,58),(82,58),(82,65.5),(78,65.5)],[(23,34),(23,46),(28,49),(35,49)],[(28,74),(20,74),(20,73.6)],[(86,28),(86,31),(74,31),(74,42),(61,42)],[(90,36),(90,68),(90,77),(77,80)]]
walkers=sorted([o for o in bpy.data.objects if o.get('kind')=='walker'],key=lambda o:o.name)
for i,o in enumerate(walkers):
    points=routes[i%len(routes)];offset=(i//len(routes))%len(points);points=points[offset:]+points[:offset]
    o.parent=None;o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([[x,y,0] for x,y in points])
    d=json.loads(o['data_json']);d['kind']=['travel','guild','guild','market','inn','craft','shrine','travel'][i%len(routes)];o['data_json']=json.dumps(d)
route=json.loads(scene['route_json'])
for r in route:
    if r['name']=='Inn':r['position']=[17,44.5]
    elif r['name']=='Blacksmith':r['position']=[20,74]
    elif r['name']=='Market':r['position']=[80,57.5]
    elif r['name']=='Residential':r['position']=[76,80]
scene['route_json']=json.dumps(route)
districts=json.loads(scene['districts_json'])
for d in districts:
    if d['name']=='Seafarer Rest':d['x']=16
    elif d['name']=='Bronze Anvil':d.update(x=20,y=71)
    elif d['name']=='Lantern Market':d.update(x=80,y=60)
scene['districts_json']=json.dumps(districts);scene['street_fitting_version']=45;scene['layout_id']='wayfarer-connected-districts-v45'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved fitted frontage lots, clear market browsing forum, service lanes and public patrols')
