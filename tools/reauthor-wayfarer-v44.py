"""Expand district spacing and author a connected street plan in the saved source.

The concept establishes atmosphere and civic hierarchy, not exact coordinates.
Run once on the v43 source, then export with export-world-v3.py.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
assert scene.get('town_plan_version',43)==43, 'Expansion is a one-time source migration'
source=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())
terrain=bpy.data.collections['court-terrain']
pivots={o['id']:o['presentation']['position'] for o in source['objects'] if o.get('presentation')}
building_ids={o['id'] for o in source['objects'] if o['family'] in ('residential','market','workshop','inn','shrine','civic') and (o.get('services') or any(p['role']=='solid' and max(v[2] for v in p['vertices'])>2 for p in o['parts']))}
# Bake each object's own world mesh before changing parents/shared mesh datablocks.
original={o.name:([o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else o.matrix_world.copy()) for o in bpy.data.objects}
def transform(p,pivot=None,scale=1.35):
    if pivot:return Vector((pivot[0]*2+(p.x-pivot[0])*scale,pivot[1]*2+(p.y-pivot[1])*scale,p.z*scale))
    return Vector((p.x*2,p.y*2,p.z*1.2))
def pivot_for(o,c):
    if c.name in building_ids and c.name in pivots:return pivots[c.name]
    if c.name=='guild-board' or c.name in ('planter-a','planter-b'):return pivots['guild-hall']
    if c==terrain:
        oid=o.get('object_id')
        if oid in building_ids and oid in pivots:return pivots[oid]
        if o.name.startswith(('civic-terrace','civic-stair')):return pivots['guild-hall']
        if o.name.startswith(('shrine-stair','shrine-landing')):return pivots['moon-shrine']
    if c.name=='wayfarer-street-details':
        for bid in sorted(building_ids,key=len,reverse=True):
            if '-'+bid+'-' in o.name and bid in pivots:return pivots[bid]
        if 'statue' in o.name or 'wing' in o.name:return pivots['astral-fountain']
    return None
seen=set()
for c in bpy.data.collections:
    if not c.get('family'):continue
    for o in c.objects:
        if o.name in seen:continue
        seen.add(o.name);pivot=pivot_for(o,c)
        # Small fountain remains a monument with a human scale, inside a bigger plaza.
        if c.name=='astral-fountain':pivot=pivots[c.name]
        if o.type=='MESH':
            if pivot and c.name in building_ids:
                center=sum(original[o.name],Vector())/max(1,len(original[o.name]))
                if math.hypot(center.x-pivot[0],center.y-pivot[1])>9:
                    o['render_visible']=False;o['role']='decorative';o['shadow']=False
            vs=[transform(v,pivot) for v in original[o.name]]
            o.data=o.data.copy();o.parent=None;o.matrix_world=Matrix.Identity(4)
            for v,p in zip(o.data.vertices,vs):v.co=p
            o.data.update()
        elif o.get('kind'):
            before=original[o.name];o.parent=None;o.matrix_world=before;o.location=transform(before.translation,pivot)
            if o.get('kind')=='walker':
                route=[before@Vector(p) for p in json.loads(o['route_json'])]
                o.matrix_world=Matrix.Identity(4);o['route_json']=json.dumps([list(transform(p)) for p in route])

# Remove the old overlapping surface network. Retain physical stairs, raised
# landings, waterfront and bridge contact surfaces, with matching transformed meshes.
for o in list(terrain.objects):
    if o.type!='MESH' or not o.get('surface_role'):continue
    keep=o['surface_role']=='water' or 'contact-surface' in o.name or o.name in ('civic-terrace','civic-stair-navigation','shrine-stair-navigation','shrine-landing-navigation','west-arrival-bridge-surface','goldenfield-bank') or o.name.startswith('south-bridge-road')
    if not keep:bpy.data.objects.remove(o,do_unlink=True)
# Canals compete with the avenue and make neighbourhoods feel like disconnected pads.
for c in bpy.data.collections:
    if '-canal-' in c.name:
        for o in c.objects:
            if o.type=='MESH':o['render_visible']=False;o['role']='decorative';o['shadow']=False
for o in list(terrain.objects):
    if 'civic-canal' in o.name:bpy.data.objects.remove(o,do_unlink=True)

owner=bpy.data.collections.new('wayfarer-v44-streets');scene.collection.children.link(owner);owner['family']='civic'
prefix='plan-v44-'
def mesh(name,vs,fs,mat='paving',collection=owner,role='decorative',shadow=False):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    data.materials.append(bpy.data.materials[mat]);o=bpy.data.objects.new(prefix+name,data);collection.objects.link(o);o['role']=role;o['shadow']=shadow;return o
def box(name,c,size,mat='stoneLight',role='decorative',shadow=False):
    x,y,z=c;a,b,h=[v/2 for v in size]
    return mesh(name,[(x+u*a,y+v*b,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role=role,shadow=shadow)
def surface(name,points,z=.048,role='primary',mat='paving'):
    o=mesh(name,[(x,y,z) for x,y in points],[list(range(len(points)))],mat,terrain);o['surface_role']=role;o['walkable']=True;return o
streets=[]
def road(name,a,b,width=5.5):
    dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*width/2,dx/n*width/2
    points=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
    o=surface(name,points);o['road_segment']=True;o['legacy_role']='avenue' if width>=7 else 'street'
    streets.append({'id':name,'a':a,'b':b,'width':width})
    # Narrow pale coping edges give each street a consistent legible boundary.
    for side in (-1,1):
        off=width/2+.12;ux,uy=-dy/n*off*side,dx/n*off*side
        if abs(dx)<.01:box(name+f'-curb-{side}',(a[0]+ux,(a[1]+b[1])/2,.09),(.16,n,.10))
        elif abs(dy)<.01:box(name+f'-curb-{side}',((a[0]+b[0])/2,a[1]+uy,.09),(n,.16,.10))

# Single civic spine, connected commercial crossroads and two neighbourhood loops.
road('arrival-avenue',(54,90),(54,60),8)
road('consortium-walk',(54,42),(54,25.7),8)
surface('central-square',[(54+11*math.cos(i*math.tau/64),51+10*math.sin(i*math.tau/64)) for i in range(64)],role='plaza')
road('west-crossroad',(54,49),(23,49),6)
road('east-crossroad',(54,54),(88,54),6)
road('western-lane',(28,49),(28,80),5.5)
road('willow-street',(28,80),(90,80),5.5)
road('east-lane',(90,80),(90,28),5.5)
road('north-garden-street',(90,31),(31,31),5)
road('inn-lane',(23,49),(23,31),5.5)
road('forge-lane',(28,70),(22,70),5)
road('market-court',(80,54),(80,64),6)
road('shrine-walk',(86,31),(86,26),4)
# Proper door aprons connect the street network to every service entrance.
for o in source['objects']:
    for service in o.get('services',[]):
        p=transform(Vector(service['position']),pivots.get(o['id']) if o['id'] in building_ids else None)
        if o['id']=='guild-board':p=transform(Vector(service['position']),pivots['guild-hall'])
        if service['kind'] in ('guild','journal'):continue
        near=min(streets,key=lambda s:sum((p[i]-(s['a'][i]+s['b'][i])/2)**2 for i in range(2)))
        a,b=near['a'],near['b'];dx,dy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/(dx*dx+dy*dy)))
        q=(a[0]+dx*t,a[1]+dy*t)
        if math.hypot(p.x-q[0],p.y-q[1])>.3:road('approach-'+service['id'],q,(p.x,p.y),3.2)

# Individually assembled frontage lots. Distinct widths, eaves, storeys, porch
# lengths and roof orientation; shared architectural materials, no cloned houses.
lots=[('baker',37,44,7,5,4.8,2),('apothecary',40,60,6,5,5.5,1),('cobbler',34,73,6,5,4.7,2),('weaver',65,73,7,5,5.3,2),('bookbinder',70,46,6,5,5.5,1),('market-arcade',80,44,9,6,4.6,2),('garden-home',38,23,6,5,5,2),('scribe',64,24,6,5,5.2,1),('willow-east',80,73,6,5,5.1,2),('riverside',70,86,7,4,4.4,2),('joiner',20,62,6,5,4.8,2),('copper-shop',35,66,6,4,4.4,1)]
for index,(name,x,y,w,d,h,tile) in enumerate(lots):
    mat='terracotta' if tile==2 else 'slate'
    box(name+'-foundation',(x,y,.22),(w+.22,d+.22,.44),'stone','solid',True)
    box(name+'-walls',(x,y,h/2+.2),(w,d,h),'plaster','solid',True)
    for z in (.55,h*.53,h+.16):box(name+f'-floorbelt-{z}',(x,y,z),(w+.08,d+.08,.13),'timber')
    for xx in (x-w/2+.05,x+w/2-.05):box(name+f'-corner-{xx}',(xx,y,h/2+.2),(.17,d+.14,h),'timber')
    ridge=h+2.2+(index%3)*.25;eave=h+.35
    mesh(name+'-gable',[(x-w/2,y+d/2,eave),(x+w/2,y+d/2,eave),(x,y+d/2,ridge)],[[0,1,2]],'plaster')
    for side in (-1,1):
        xx=x+side*(w/2+.35)
        mesh(name+f'-roof-{side}',[(xx,y-d/2-.32,eave),(xx,y+d/2+.32,eave),(x,y+d/2+.32,ridge),(x,y-d/2-.32,ridge)],[[0,1,2,3]],mat,role='overhead',shadow=True)
    box(name+'-door',(x,y+d/2+.018,1.1),(1.05,.08,1.9),'oak')
    for j,xx in enumerate((x-w*.32,x+w*.32)):
        for floor in range(2):
            zz=1.5+floor*h*.5
            box(name+f'-window-{j}-{floor}',(xx,y+d/2+.025,zz),(.95,.06,1.05),'glass')
            box(name+f'-sill-{j}-{floor}',(xx,y+d/2+.10,zz-.57),(1.2,.24,.10))
            for side in (-1,1):box(name+f'-shutter-{j}-{floor}-{side}',(xx+side*.61,y+d/2+.06,zz),(.24,.10,1.15),'oak')
    box(name+'-chimney',(x+w*.28,y-d*.2,h+1.8),(.6,.7,2),'stone')
    box(name+'-chimney-cap',(x+w*.28,y-d*.2,h+2.82),(.8,.9,.18))
    # South-facing threshold aligned to the lot, with an intentional lane apron.
    surface(name+'-threshold',[(x-1.5,y+d/2),(x+1.5,y+d/2),(x+1.5,y+d/2+1.3),(x-1.5,y+d/2+1.3)],role='forecourt')

# Materials have a physical repeat length. Re-unwrap in world metres so tiny
# trim does not inherit a full roof tile and roofs keep the same texel density.
for name,tile,size in [('paving',0,4),('streetIvory',0,4),('slate',1,3.2),('roofBlue',1,3.2),('roofMoss',1,3.2),('civicSlate',1,3.2),('civicSlateLight',1,3.2),('terracotta',2,3.2),('roofClay',2,3.2),('plaster',3,4)]:
    if name in bpy.data.materials:bpy.data.materials[name]['texture_json']=json.dumps({'file':'assets/wayfarer-materials-v44.webp','grid':[2,2],'tile':tile,'worldSize':size})
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.materials:continue
    m=o.data.materials[0]
    if not m.get('texture_json'):continue
    spec=json.loads(m['texture_json']);size=spec.get('worldSize',2.4)
    if spec.get('alphaCutoff'):continue
    if not o.data.uv_layers.active:o.data.uv_layers.new(name='World-scale-UV')
    for face in o.data.polygons:
        n=face.normal;axes=(0,1) if abs(n.z)>.65 else (0,2) if abs(n.y)>abs(n.x) else (1,2)
        for li in face.loop_indices:
            p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            o.data.uv_layers.active.data[li].uv=(p[axes[0]]/size,p[axes[1]]/size)
scene['world_bounds_json']=json.dumps({'minX':0,'minY':0,'maxX':112,'maxY':128})
scene['spawn_json']=json.dumps([54,94.2,0]);scene['safe_spawn_json']=json.dumps([54,65,0])
scene['route_json']=json.dumps([{'name':r['name'],'position':[v*2 for v in r['position']]} for r in source['route']])
scene['districts_json']=json.dumps([{**d,'x':d['x']*2,'y':d['y']*2} for d in source['districts']])
scene['layout_id']='wayfarer-connected-districts-v44';scene['town_plan_version']=44
scene['street_plan_json']=json.dumps(streets)
scene['ambient']=.73;scene['sun_strength']=.28
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved v44: four times land area, connected civic spine and neighbourhood loops,',len(lots),'new frontage lots')
