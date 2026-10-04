"""A raised, connected merchant court and coherent tent/counter ensembles.

Edit the saved native town, including floors, roots, retaining contacts and
stair entrances. No runtime elevation patches or historical scene rebuild.
"""
import bpy, bmesh, json, math, runpy
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('attic_family_version') == 62
PREFIX = 'market-v63-'
HEIGHT = .72
outline = [(73,55),(98.5,55),(100.5,58),(100.5,76),(88,79),(73,79)]
terrain = bpy.data.collections['court-terrain']
court = bpy.data.collections.get('merchant-court')
if not court:
    court = bpy.data.collections.new('merchant-court')
    scene.collection.children.link(court)
court['family'] = 'market'
owner, root = court, None
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX): bpy.data.objects.remove(o, do_unlink=True)

def inside(x,y):
    return sum((a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0] for a,b in zip(outline,outline[1:]+outline[:1]))%2

def mesh(name, vs, fs, mat, role='decorative', shadow=True, walkable=False):
    inv = root.matrix_world.inverted() if root else Matrix.Identity(4)
    d=bpy.data.meshes.new(PREFIX+name)
    d.from_pydata([inv@Vector(p) for p in vs],[],fs)
    bm=bmesh.new();bm.from_mesh(d)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.to_mesh(d);bm.free()
    d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
    for f in d.polygons:
        for li in f.loop_indices:
            p=d.vertices[d.loops[li].vertex_index].co;n=f.normal
            d.uv_layers.active.data[li].uv=(p.x/3,p.y/3) if abs(n.z)>.65 else (p.y/3,p.z/3) if abs(n.x)>.65 else (p.x/3,p.z/3)
    o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o)
    o['role']=role;o['shadow']=shadow
    if root:o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4)
    if owner==terrain:o['surface_role']='forecourt';o['walkable']=walkable;o['shadow']=False
    return o

def box(name,c,size,mat='stone',role='decorative',shadow=True):
    x,y,z=c;a,b,h=[v/2 for v in size]
    return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)

def beam(name,a,b,r,mat='oak',sides=8):
    a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,0,1)))
    if u.length<.01:u=Vector((1,0,0))
    u.normalize();w=v.cross(u).normalized()
    vs=[tuple(p+r*(math.cos(k*math.tau/sides)*u+math.sin(k*math.tau/sides)*w)) for p in (a,b) for k in range(sides)]
    return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[k,(k+1)%sides,(k+1)%sides+sides,k+sides] for k in range(sides)],mat)

def lathe(name,x,y,z,profile,mat,sides=12):
    vs=[(x+r*math.cos(k*math.tau/sides),y+r*math.sin(k*math.tau/sides),z+h) for h,r in profile for k in range(sides)]
    fs=[[j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k] for j in range(len(profile)-1) for k in range(sides)]
    fs.append(list(range(sides-1,-1,-1)))
    return mesh(name,vs,fs,mat)

for name,color in [('sailIvory',(.83,.73,.54,1)),('produceGreen',(.36,.47,.17,1)),('produceOchre',(.77,.47,.15,1)),('produceRose',(.57,.20,.15,1))]:
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color

# Complete placement owners follow their new floor, including registered props.
moved=[]
for name in ['market-spices','market-supplies','market-textiles','food-market','market-crates','frontage-willow-east']:
    c=bpy.data.collections[name];r=bpy.data.objects.get(name+'-placement')
    assert r,name
    if 'market_v63_base_z' not in r:r['market_v63_base_z']=r.location.z
    r.location.z=r['market_v63_base_z']+HEIGHT;moved.append(r)
bpy.context.view_layer.update()
def owned(o):
    while o:
        if o in moved:return True
        o=o.parent
    return False
for c in bpy.data.collections:
    if not c.get('family') or c['family'] in ('terrain','fortification') or c==court:continue
    for o in c.objects:
        if o.type!='MESH' or owned(o) or not o.get('render_visible',True):continue
        vs=[o.matrix_world@v.co for v in o.data.vertices]
        if not vs:continue
        p=sum(vs,Vector())/len(vs)
        if not inside(p.x,p.y) or max(v.z for v in vs)-min(v.z for v in vs)>15:continue
        if 'market_v63_base_world_z' not in o:o['market_v63_base_world_z']=o.matrix_world.translation.z
        m=o.matrix_world.copy();m.translation.z=o['market_v63_base_world_z']+HEIGHT;o.matrix_world=m
bpy.context.view_layer.update()

owner,root=terrain,None
mesh('raised-floor',[(x,y,HEIGHT+.045) for x,y in outline],[list(range(len(outline)))],'cityPaving',walkable=True)
owner=court
# Openings correspond to four deliberate entrances, not arbitrary curb gaps.
west_gaps=[(57,61),(65,69)];north_gap=(86.5,90.5);south_gap=(76,82)
edges=[((73,55),(73,57)),((73,61),(73,65)),((73,69),(73,79)),((73,55),(86.5,55)),((90.5,55),(98.5,55)),((98.5,55),(100.5,58)),((100.5,58),(100.5,76)),((100.5,76),(88,79)),((88,79),(82,79)),((76,79),(73,79))]
for i,(a,b) in enumerate(edges):
    a,b=Vector((*a,0)),Vector((*b,0));d=b-a;n=Vector((-d.y,d.x,0)).normalized()*.14
    for label,z0,z1,scale,mat in [('wall',-.04,HEIGHT+.17,1,'stone'),('coping',HEIGHT+.17,HEIGHT+.32,1.45,'stoneLight')]:
        vs=[tuple(p+s*n*scale+Vector((0,0,z))) for z in (z0,z1) for p in (a,b) for s in (-1,1)]
        mesh('edge-'+str(i)+'-'+label,vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,'solid')
    # Pilasters mark long retaining edges without walling off the stair mouths.
    for k in range(1,int(d.length/4)):
        p=a+d*k/int(d.length/4)
        box('edge-'+str(i)+'-pier-'+str(k),(p.x,p.y,HEIGHT*.5),(.43,.43,HEIGHT+.4),'stoneLight','solid')

def flight(name,a,b,across):
    # a is the upper edge, b is the lower edge; across is a half-width vector.
    a,b,across=Vector((*a,0)),Vector((*b,0)),Vector((*across,0))
    for k in range(6):
        p=a+(b-a)*(5-k)/6;q=a+(b-a)*(6-k)/6;z=(k+1)*HEIGHT/6+.045
        owner_before=None
        globals()['owner']=court
        vs=[tuple(v+Vector((0,0,h))) for h in (0,z) for v in (p-across,p+across,q-across,q+across)]
        mesh(name+'-riser-'+str(k),vs,[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],'stoneLight')
        globals()['owner']=terrain
        mesh(name+'-tread-'+str(k),[tuple(v+Vector((0,0,z))) for v in (p-across,p+across,q+across,q-across)],[[0,1,2,3]],'avenuePaving',walkable=True)
    globals()['owner']=court
for name,a,b,w in [('west-north',(73,59),(70.6,59),(0,2)),('west-south',(73,67),(70.6,67),(0,2)),('north',(88.5,55),(88.5,52.6),(2,0)),('south',(79,79),(79,81.4),(3,0))]:flight(name,a,b,w)

# New native tents use one coherent scale, visible trusses and draped cloth.
# Existing counters/barrels keep their original ground contact/collision lots.
def stall(name,x,y,w,d,z,cloth,goods,new_counter=False):
    if new_counter:
        box(name+'-counter',(x,y,z+.58),(w*.83,d*.61,1.12),'oak','solid')
        box(name+'-counter-top',(x,y,z+1.16),(w*.88,d*.67,.13),'timber')
    top=z+1.18;edge=z+2.85;peak=z+3.75
    for side in (-1,1):
        for end in (-1,1):
            px=x+side*(w/2-.19);py=y+end*(d/2-.16)
            beam(name+'-post-'+str((side,end)),(px,py,z),(px,py,edge+.22),.075,'timber')
            box(name+'-post-shoe-'+str((side,end)),(px,py,z+.12),(.24,.24,.24),'stoneLight')
            beam(name+'-brace-'+str((side,end)),(px,py,edge-.48),(px-side*.52,py,edge+.03),.045,'oak')
        beam(name+'-ridge-pole-'+str(side),(x+side*(w/2-.18),y,z+2.72),(x+side*(w/2-.18),y,peak+.13),.065,'timber')
    beam(name+'-ridge',(x-w/2-.22,y,peak+.06),(x+w/2+.22,y,peak+.06),.065,'oak')
    # Six broad fabric gores, each draped through a fixed source profile.
    profile=[(-1,0),(-.70,.22),(-.33,.59),(0,1),(.33,.59),(.70,.22),(1,0)]
    for j in range(6):
        left=x-w/2+w*j/6;right=x-w/2+w*(j+1)/6
        vs=[(xx,y+u*d/2,edge+(peak-edge)*h-.09*math.sin(math.pi*j/6)) for xx in (left,right) for u,h in profile]
        mesh(name+'-sail-'+str(j),vs,[[k,k+1,k+8,k+7] for k in range(6)],cloth if j%3 else 'sailIvory','overhead')
        # Curved valance lobes replace a straight rectangle under the eave.
        for end in (-1,1):
            yy=y+end*d/2;center=(left+right)/2
            poly=[(left,yy,edge),(right,yy,edge)]+[(center+math.cos(k*math.pi/8)*w/12,yy,edge-.10-.19*math.sin(k*math.pi/8)) for k in range(9)]
            mesh(name+'-valance-'+str((j,end)),poly,[list(range(len(poly)))],cloth)
    for side in (-1,1):
        beam(name+'-eave-'+str(side),(x-w/2,y+side*d/2,edge),(x+w/2,y+side*d/2,edge),.055,'oak')
    for j in range(4):
        xx=x-w*.30+j*w*.20
        box(name+'-display-tray-'+str(j),(xx,y+.08,top+.04),(w*.17,.70,.09),'oak')
        for sign in (-1,1):box(name+'-tray-rim-'+str((j,sign)),(xx,y+.08+sign*.35,top+.11),(w*.17,.05,.15),'timber')
        if goods=='cloth':
            for k in range(3):box(name+'-fold-'+str((j,k)),(xx,y-.08+k*.18,top+.15+k*.025),(w*.15,.22,.15),['clothBlue','clothRose','sailIvory'][(j+k)%3])
        elif goods=='pottery':
            for k in range(2):lathe(name+'-pot-'+str((j,k)),xx+.10*(k*2-1),y+.08,top+.09,[(0,.10),(.09,.17),(.25,.18),(.36,.09),(.40,.11),(.40,.075),(.33,.075)],'terracotta' if j%2 else 'teal')
        else:
            lathe(name+'-basket-'+str(j),xx,y+.08,top+.09,[(0,.13),(.10,.25),(.30,.29),(.34,.29),(.34,.25),(.29,.25)],'oak')
            for k in range(7):
                angle=k*2.4;rr=.10+.025*(k%3);px=xx+math.cos(angle)*rr;py=y+.08+math.sin(angle)*rr
                lathe(name+'-produce-'+str((j,k)),px,py,top+.34,[(0,.03),(.05,.075),(.13,.06),(.16,0)],['produceGreen','produceOchre','produceRose'][j%3],8)
    # Larger hand-thrown vessels and stacked timber packing at the counter foot.
    for side in (-1,1):
        lathe(name+'-storage-jar-'+str(side),x+side*w*.37,y-d*.36,z,[(0,.18),(.14,.31),(.48,.34),(.67,.16),(.71,.19),(.71,.12),(.64,.12)],'terracotta')
        beam(name+'-jar-handle-'+str(side),(x+side*w*.37+.18,y-d*.36,z+.45),(x+side*w*.37+.18,y-d*.36,z+.62),.035,'terracotta')

records=[]
for name,cloth,goods in [('market-spices','clothOchre','produce'),('market-supplies','clothBlue','pottery'),('market-textiles','clothRose','cloth'),('food-market','sailIvory','produce')]:
    owner=bpy.data.collections[name];root=bpy.data.objects[name+'-placement']
    counter=next(o for o in owner.objects if o.name.endswith('-counter'))
    pts=[counter.matrix_world@v.co for v in counter.data.vertices]
    x0,x1=min(p.x for p in pts),max(p.x for p in pts);y0,y1=min(p.y for p in pts),max(p.y for p in pts)
    z=min(p.z for p in pts);w=x1-x0+.72;d=y1-y0+.70
    for o in owner.objects:
        if o.type=='MESH' and any(t in o.name for t in ['-canopy','-scallop','-awning-post','-goods','-jar-','-folded-cloth','-front-apron']):
            o['render_visible']=False;o['shadow']=False;o['role']='decorative'
    stall(name,(x0+x1)/2,(y0+y1)/2,w,d,z,cloth,goods)
    records.append({'id':name,'counterGround':z,'canopyEave':z+2.85,'canopyPeak':z+3.75})
owner,root=court,None
for name,x,y,w,d,cloth,goods in [('dye-trader',87.4,70.2,3.6,2.8,'clothRose','cloth'),('potter',87.2,62.9,3.6,2.8,'clothBlue','pottery')]:
    stall(name,x,y,w,d,HEIGHT+.045,cloth,goods,True)
    records.append({'id':name,'counterGround':HEIGHT+.045,'canopyEave':HEIGHT+2.895,'canopyPeak':HEIGHT+3.795})

# Open upper-wall rail sections and stone set-back benches give the terrace
# thickness and street activity while leaving both west stairs legible.
for i,(x,y) in enumerate([(73.65,63),(73.65,73.4),(97.9,57.2),(98.8,74.7)]):
    for xx in (x-.66,x+.66):box('seat-'+str(i)+'-leg-'+str(xx),(xx,y,HEIGHT+.32),(.22,.54,.55),'stoneLight','solid')
    box('seat-'+str(i)+'-slab',(x,y,HEIGHT+.64),(1.8,.62,.17),'stoneLight','solid')
    lathe('seat-'+str(i)+'-urn',x,y+.70,HEIGHT+.045,[(0,.22),(.22,.38),(.60,.43),(.79,.35),(.84,.40),(.84,.33),(.77,.33)],'terracotta')
    # Whole native sprigs, rooted inside the pot rather than floating flowers.
    for j in range(7):
        angle=j*2.4;tip=(x+math.cos(angle)*.38,y+.70+math.sin(angle)*.38,HEIGHT+1.25+.10*(j%3))
        beam('urn-'+str(i)+'-stem-'+str(j),(x,y+.70,HEIGHT+.66),tip,.018,'produceGreen',6)
        tx,ty,tz=tip
        mesh('urn-'+str(i)+'-leaf-'+str(j),[(tx-.14,ty,tz-.20),(tx,ty+.07,tz-.12),(tx+.14,ty,tz-.20),(tx,ty-.07,tz-.26)],[[0,1,2],[0,2,3]],'produceGreen')
        lathe('urn-'+str(i)+'-bloom-'+str(j),tx,ty,tz,[(0,.025),(.04,.075),(.075,.035)],'clothRose',8)

scene['market_court_version']=63
scene['market_court_review_json']=json.dumps({'height':HEIGHT,'outline':outline,'stairFlights':4,'stairTreads':6,'stalls':records,'newCounterLots':2,'visualAccepted':False})
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved raised merchant court, four six-tread approaches, six draped stocked stalls and terrace seating; bakes/routes require refresh',flush=True)
