"""Source-owned architectural massing pass after v45 street fitting.

Individual component assemblies, not complete-house copies. New facade pieces
remain children of their editable lot roots; existing service contacts stay put.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
assert scene.get('street_fitting_version')==45
assert not scene.get('architectural_quality_version'), 'One-time pass on saved v45'
owner=None;root=None

def mesh(name,vs,fs,mat,role='decorative',shadow=True):
    data=bpy.data.meshes.new('quality-v46-'+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
    o=bpy.data.objects.new('quality-v46-'+name,data);owner.objects.link(o)
    o['role']=role;o['shadow']=shadow
    if root:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
    world=root.matrix_world.copy() if root else Matrix.Identity(4)
    spec=json.loads(bpy.data.materials[mat].get('texture_json','{}'));size=spec.get('worldSize',3)
    for f in data.polygons:
        normal=(world.to_3x3()@f.normal).normalized()
        u,v=(Vector((1,0,0)),Vector((0,1,0))) if abs(normal.z)>.65 else (Vector((1,0,0)),Vector((0,0,1))) if abs(normal.y)>abs(normal.x) else (Vector((0,1,0)),Vector((0,0,1)))
        for li in f.loop_indices:
            p=world@data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p.dot(u)/size,p.dot(v)/size)
    return o

def box(name,c,size,mat,role='decorative',shadow=True):
    x,y,z=c;a,b,h=[v/2 for v in size]
    return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)

def roof(name,x,y,w,d,eave,peak,mat):
    for side in (-1,1):
        xx=x+side*w/2
        mesh(name+str(side),[(xx,y-d/2,eave),(xx,y+d/2,eave),(x,y+d/2,peak),(x,y-d/2,peak)],[[0,1,2,3]],mat,'overhead')
        box(name+'-fascia'+str(side),(xx,y,eave-.03),(.14,d,.18),'timber')
    mesh(name+'-gable',[(x-w/2,y+d/2,eave),(x+w/2,y+d/2,eave),(x,y+d/2,peak)],[[0,1,2]],'plaster',shadow=False)
    box(name+'-ridge',(x,y,peak+.03),(.13,d,.12),'oak')

# One remaining overlap found with convex mesh footprints, rather than just
# centre points. The neighbouring weaver and Willow lot retain their setbacks.
bpy.data.objects['avenue-cottage-east-placement'].location.x+=1.5
bpy.context.view_layer.update()

for i,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
    owner=c;root=bpy.data.objects[c.name+'-placement'];walls=next(o for o in c.objects if o.name.endswith('-walls'))
    inv=root.matrix_world.inverted();vs=[inv@walls.matrix_world@v.co for v in walls.data.vertices]
    x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs)
    w,d=x1-x0,y1-y0;x,y=(x0+x1)/2,(y0+y1)/2;h=max(v.z for v in vs)
    prefix=c.name+'-';roofmat='slate' if i%3==0 else 'terracotta'
    # Structural eaves reveal their thickness and an occluded wall band.
    box(prefix+'eave-shade',(x,y1+.025,h-.08),(w,.08,.22),'timber',shadow=False)
    box(prefix+'cornice',(x,y1+.13,h+.04),(w+.25,.28,.17),'stoneLight')
    for xx in (x0+.10,x1-.10):
        box(prefix+'foot-pier'+str(xx),(xx,y1+.08,.45),(.36,.3,.72),'stone')
    # Deep lower facade: varied porches, residential bays and merchants' galleries.
    if c['family']=='residential':
        xx=x+(.23*w if i%2 else -.23*w)
        box(prefix+'bay-body',(xx,y1+.23,2.15),(1.45,.46,2.5),'plaster')
        box(prefix+'bay-glass',(xx,y1+.47,2.3),(1.13,.04,1.42),'glass',shadow=False)
        for dx in (-.67,.67):box(prefix+'bay-frame'+str(dx),(xx+dx,y1+.48,2.25),(.13,.11,2.3),'timber')
        roof(prefix+'bay-roof',xx,y1+.22,1.8,.85,3.5,4.35,roofmat)
        box(prefix+'bay-sill',(xx,y1+.5,1.53),(1.6,.24,.13),'stoneLight')
    elif i%3==0:
        roof(prefix+'porch',x,y1+.42,w*.65,1.28,2.65,3.5,roofmat)
        for xx in (x-w*.28,x+w*.28):
            box(prefix+'porch-post'+str(xx),(xx,y1+.89,1.35),(.18,.18,2.55),'timber')
            box(prefix+'post-foot'+str(xx),(xx,y1+.89,.27),(.3,.3,.45),'stone')
    else:
        box(prefix+'gallery',(x,y1+.34,2.85),(w*.62,.73,.16),'timber')
        for xx in (x-w*.31,x+w*.31):box(prefix+'gallery-support'+str(xx),(xx,y1+.58,1.38),(.17,.18,2.7),'timber')
        box(prefix+'gallery-rail',(x,y1+.72,3.4),(w*.64,.13,.13),'oak')
        for j in range(7):box(prefix+'baluster'+str(j),(x-w*.29+j*w*.58/6,y1+.72,3.13),(.065,.09,.58),'oak',shadow=False)
        mesh(prefix+'shop-awning',[(x-w*.35,y1,2.6),(x+w*.35,y1,2.6),(x+w*.35,y1+.9,2.22),(x-w*.35,y1+.9,2.22)],[[0,1,2,3]],['clothOchre','clothRose','clothBlue'][i%3],'overhead')
    # Dormers interrupt long simple roof planes; differing positions and widths
    # create a family of related, individually authored silhouettes.
    xx=x+(-w*.20 if i%2 else w*.19);yy=y+d*.24
    box(prefix+'dormer-body',(xx,yy,h+1.13),(1.35,1.2,1.5),'plaster')
    box(prefix+'dormer-window',(xx,yy+.615,h+1.17),(.73,.04,.94),'glass',shadow=False)
    roof(prefix+'dormer-roof',xx,yy,1.75,1.65,h+1.92,h+2.78,roofmat)
    for dx in (-.48,.48):box(prefix+'dormer-upright'+str(dx),(xx+dx,yy+.65,h+1.2),(.10,.12,1.35),'timber')
    # A readable hanging sign and bracket, placed at each actual facade.
    box(prefix+'sign-bracket',(x-w*.38,y1+.35,2.8),(.13,.8,.12),'iron')
    box(prefix+'sign',(x-w*.38,y1+.68,2.38),(.72,.13,.66),'oak')

# Major civic silhouette: broad octagonal bell dome, raised lantern and gilded
# ribs, instead of the thin needle matching every small watchtower.
owner=bpy.data.collections['guild-hall'];root=None
for o in owner.objects:
    if o.name.startswith('civic-v4-lantern-crown'):o['render_visible']=False;o['shadow']=False
profile=[(13.85,1.65),(14.12,2.12),(14.55,2.12),(15.0,1.95),(15.65,1.6),(16.2,1.05),(16.48,.72),(17.75,.72),(18.0,1.03),(18.35,.82),(19.0,.36),(19.55,0)]
cx,cy=54,13.4
for k,((z0,r0),(z1,r1)) in enumerate(zip(profile,profile[1:])):
    vs=[(cx+r*math.cos(i*math.tau/8+math.pi/8),cy+r*math.sin(i*math.tau/8+math.pi/8),z) for z,r in [(z0,r0),(z1,r1)] for i in range(8)]
    mesh('hall-dome-'+str(k),vs,[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)],'civicGold' if k in (0,1,5,7) else 'civicSlate','overhead')
    if k not in (0,1,5,7):
        for i in range(8):
            a=i*math.tau/8+math.pi/8;dx,dy=math.cos(a)*.035,math.sin(a)*.035
            mesh('dome-rib-'+str(k)+'-'+str(i),[(cx+r0*math.cos(a)-dy,cy+r0*math.sin(a)+dx,z0),(cx+r0*math.cos(a)+dy,cy+r0*math.sin(a)-dx,z0),(cx+r1*math.cos(a)+dy,cy+r1*math.sin(a)-dx,z1),(cx+r1*math.cos(a)-dy,cy+r1*math.sin(a)+dx,z1)],[[0,1,2,3]],'civicGold',shadow=False)
box('hall-dome-finial',(54,13.4,19.75),(.12,.12,.7),'civicGold')
# Portal canopy adds real projection and a shaded antechamber without moving
# stairs or the registrar. Columns stand outside the central public approach.
for x in (50.7,57.3):
    box('hall-entry-pier'+str(x),(x,22.45,2.53),(.42,.62,3.8),'civicIvory','solid')
    box('hall-entry-cap'+str(x),(x,22.45,4.45),(.7,.86,.25),'civicGold')
    box('hall-entry-plinth'+str(x),(x,22.45,.87),(.68,.85,.48),'civicShadow')
roof('hall-entry-gable',54,22.15,7.1,2.05,4.67,6.8,'civicSlate')
box('hall-entry-frieze',(54,23.14,4.6),(6.65,.17,.27),'civicGold')
box('hall-entry-shadow',(54,21.55,4.35),(6.55,.1,.32),'civicDoor',shadow=False)
# Bind civic additions to the source landmark root so parity/move checks include them.
root=bpy.data.objects['guild-hall-placement'];bpy.context.view_layer.update()
for o in owner.objects:
    if o.name.startswith('quality-v46-'):
        before=o.matrix_world.copy();o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted();o.matrix_world=before

# Deliberate density in the forecourt: shallow arcades flanking the civic walk,
# while the eight-unit processional axis remains clear.
owner=bpy.data.collections.new('consortium-forecourt-arcades');scene.collection.children.link(owner);owner['family']='civic';root=None
for side in (-1,1):
    x=54+side*7.6
    roof('forecourt-'+str(side),x,35,3.6,8.4,3.4,5.0,'slate')
    for yy in (31.3,33.7,36.3,38.7):
        for xx in (x-1.3,x+1.3):
            box('arcade-pier-'+str(xx)+'-'+str(yy),(xx,yy,1.7),(.23,.27,3.25),'stoneLight','solid')
            box('arcade-cap-'+str(xx)+'-'+str(yy),(xx,yy,3.34),(.48,.5,.18),'stoneLight')
    box('arcade-bench'+str(side),(x,35,.65),(2.3,5.6,.18),'oak')

# Preserve geometry-derived navigation for ambient people, including each loop's
# closing leg. The offline plan is generated by the same exact collision checks.
routes=json.loads((ROOT/'authoring/patrol-routes-v46.json').read_text())
for o in bpy.data.objects:
    if o.get('kind')=='walker':o['route_json']=json.dumps([[x,y,0] for x,y in routes[o.name]])
scene['ambient']=.62;scene['sun_strength']=.43
scene['sun_cast_x']=.62;scene['sun_cast_y']=.4
scene['architectural_quality_version']=46;scene['layout_id']='wayfarer-painterly-districts-v46'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved v46: individual deep facades, dormers, civic dome/portal, forecourt arcades and cohesive directional light')
