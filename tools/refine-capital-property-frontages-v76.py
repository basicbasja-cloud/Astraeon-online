"""Author use-specific frontages in the saved city, preserving its urban plan.

RO3 beta 01:40/03:35 inform recessed shops, sheltered entries and owned work
areas. These are original modular meshes, using the existing material palette.
The architecture revision identifies the retained massing; frontage revision 1
identifies this finishing pass. No collision core or approach is moved.
"""
import bpy, bmesh, json, math, runpy, hashlib
from pathlib import Path
from mathutils import Vector

R = Path(__file__).resolve().parents[1]
O = R / 'docs/review/wayfarer-capital-v76/property-frontages'
O.mkdir(parents=True, exist_ok=True)
s = bpy.context.scene
assert s.get('capital_architecture_revision') == 76
assert not s.get('capital_property_frontages'), 'Frontage pass already applied'
Kit = runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
exporter = runpy.run_path(str(R/'tools/export-world-v3.py'))
before = exporter['export'](s)
p = json.loads(s['capital_plan_json'])

def invariant(data):
    return {'terrain': data['terrain'], 'navigation': data['navigation'],
            'spawn': data['spawn'], 'route': data['route'],
            'anchors': [{key: owner.get(key) for key in
                         ('id', 'portals', 'services', 'walkers', 'presentation')}
                        for owner in data['objects']],
            'solids': [(owner['id'], part) for owner in data['objects']
                       for part in owner['parts'] if part['role'] == 'solid'],
            'doors': [(owner['id'], part) for owner in data['objects']
                      for part in owner['parts'] if part['id'].endswith('-door-leaf')]}

preserved = invariant(before)
base_triangles = sum(len(f)-2 for a in before['objects'] for m in a['parts']
                     if m.get('visible', True) for f in m['faces'])
before_hash = hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest()
del before

def remove_components(c, fragments):
    """Delete only whole component faces; retain UVs, weights and old lighting."""
    for obj in list(c.objects):
        if obj.type != 'MESH': continue
        if not obj.get('component_count'):
            if any(f in obj.name for f in fragments):
                bpy.data.objects.remove(obj, do_unlink=True)
            continue
        chosen = [g for g in obj.vertex_groups if any(f in g.name for f in fragments)]
        selections = [{v.index for v in obj.data.vertices
                       if any(a.group == g.index for a in v.groups)} for g in chosen]
        if not selections: continue
        doomed = {face.index for face in obj.data.polygons
                  if any(set(face.vertices).issubset(indices) for indices in selections)}
        if not doomed: continue
        bm = bmesh.new(); bm.from_mesh(obj.data); bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in doomed], context='FACES_ONLY')
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.to_mesh(obj.data); bm.free()
        for group in chosen: obj.vertex_groups.remove(group)
        obj['component_count'] = len(obj.vertex_groups)
        if not obj.data.polygons: bpy.data.objects.remove(obj, do_unlink=True)

def plant_pot(k, name, x, y, z, radius=.16):
    rings = [(radius*.65, z), (radius, z+.30), (radius*.84, z+.34)]
    pts = [(x+r*math.cos(j*math.tau/8), y+r*math.sin(j*math.tau/8), h)
           for r,h in rings for j in range(8)]
    faces = [[i*8+j, i*8+(j+1)%8, (i+1)*8+(j+1)%8, (i+1)*8+j]
             for i in range(2) for j in range(8)]
    k.mesh(name+'-pot', pts, faces, 'roofClayOchre')
    k.mesh(name+'-soil', [(x,y,z+.325)]+pts[16:],
           [[0,j+1,(j+1)%8+1] for j in range(8)], 'soil', False)
    for j in range(3):
        a=j*math.tau/3
        k.mesh(name+'-herb-'+str(j), [(x,y,z+.34),
            (x+.22*math.cos(a),y+.22*math.sin(a),z+.55),
            (x+.06*math.cos(a+.8),y+.06*math.sin(a+.8),z+.70)],
            [[0,1,2]], 'leaf', False)

def sign(k, name, x, y, style):
    k.beam(name+'-sign-bracket', (x,y,3.12),(x,y+.58,3.12),.07,'iron')
    for xx in (x-.23,x+.23):
        k.beam(name+'-sign-chain'+str(xx),(xx,y+.54,3.12),(xx,y+.54,2.91),.035,'iron')
    k.box(name+'-sign-board',(x,y+.54,2.63),(.65,.08,.52),'oak')
    # A readable geometric emblem rather than text pasted across a window.
    yy=y+.595
    if style=='clothier':
        k.mesh(name+'-cloth-emblem',[(x-.16,yy,2.77),(x+.10,yy,2.77),
            (x+.17,yy,2.51),(x-.12,yy,2.49)],[[0,1,2,3]],'clothBlue',False)
    elif style=='apothecary':
        k.box(name+'-bottle-emblem',(x,yy,2.60),(.20,.018,.20),'produceGreen',False)
        k.box(name+'-bottle-neck',(x,yy,2.75),(.09,.018,.11),'gold',False)
    elif style=='carpenter':
        k.beam(name+'-hammer-handle',(x-.12,yy,2.48),(x+.10,yy,2.75),.045,'gold')
        k.beam(name+'-hammer-head',(x-.02,yy,2.81),(x+.19,yy,2.64),.09,'gold')
    else:
        for j in range(3):
            xx=x+(j-1)*.13
            k.beam(name+'-grain-stem'+str(j),(xx,yy,2.46),(xx,yy,2.78),.025,'gold')
            k.mesh(name+'-grain-ear'+str(j),[(xx,yy,2.82),(xx+.06,yy,2.71),
                (xx,yy,2.63),(xx-.06,yy,2.71)],[[0,1,2,3]],'gold',False)

def shop(k, l, use):
    name,w,d,t=l['id'],l['width'],l['depth'],l['architectureType']
    doorx=-w*.21 if t in ('half-hip','oriel-house','merchant-hall') else 0
    doorw=1.36 if w<6 else 1.7
    lo,hi=(doorx+doorw/2+.23,w/2-.24) if doorx<0 else (-w/2+.24,-doorw/2-.23)
    ww=min(3.6,hi-lo);gx=(lo+hi)/2;y=d/2
    assert ww>.55, (name,'No room for shop bay')
    mat={'market':'merchantLimewash','workshop':'workshopLimewash'}[l['family']]
    # Replace the visible block with a real front opening. The independent
    # hidden physical core, actual door and two contact treads remain intact.
    for suffix,cx,cy,sx,sy in [('rear',0,-d/2+.12,w,.24),
            ('west',-w/2+.12,0,.24,d-.24),('east',w/2-.12,0,.24,d-.24)]:
        k.box(name+'-shop-shell-'+suffix,(cx,cy,1.66),(sx,sy,2.92),mat)
    openings=sorted([(doorx-doorw/2,doorx+doorw/2,.42,3.07),
                     (gx-ww/2,gx+ww/2,1.0,2.64)])
    last=-w/2
    for j,(a,b,low,high) in enumerate(openings):
        if a>last:k.box(name+'-shop-pier'+str(j),((last+a)/2,y-.12,1.66),(a-last,.24,2.92),mat)
        if low>.20:k.box(name+'-shop-sill-wall'+str(j),((a+b)/2,y-.12,(low+.20)/2),(b-a,.24,low-.20),mat)
        if high<3.12:k.box(name+'-shop-head-wall'+str(j),((a+b)/2,y-.12,(high+3.12)/2),(b-a,.24,3.12-high),mat)
        last=b
    if last<w/2:k.box(name+'-shop-end',((last+w/2)/2,y-.12,1.66),(w/2-last,.24,2.92),mat)
    k.window(name+'-display-bay',gx,y,1.82,ww,1.64,recess=.18)
    aw=min(ww+.22,w*.70);edges=[(y+.16,3.04),(y+.44,3.00),(y+.76,2.80)]
    for j in range(6):
        xa=gx-aw/2+j*aw/6;xb=xa+aw/6
        color=('clothBlue' if use=='clothier' else 'shopAwningSage') if j%2==0 else 'homeLimewash'
        for n,((ya,za),(yb,zb)) in enumerate(zip(edges,edges[1:])):
            obj=k.mesh(name+f'-trade-canopy-{j}-{n}',[(xa,ya,za),(xb,ya,za),(xb,yb,zb),(xa,yb,zb)],[[0,1,2,3]],color)
            obj['role']='overhead'
        k.mesh(name+f'-trade-valance-{j}',[(xa,y+.76,2.80),(xb,y+.76,2.80),
            (xb-.04,y+.76,2.61),((xa+xb)/2,y+.76,2.55),(xa+.04,y+.76,2.61)],[[0,1,2,3,4]],color)
    for xx in (gx-aw/2+.06,gx+aw/2-.06):
        k.beam(name+'-awning-support'+str(xx),(xx,y+.04,2.5),(xx,y+.76,2.80),.06,'iron')
    k.box(name+'-trade-counter',(gx,y+.38,.50),(max(.5,ww-.12),.48,.92),'oak')
    for j in range(max(2,int(ww/.6))):
        xx=gx-ww*.34+j*ww*.68/max(1,int(ww/.6)-1)
        if use=='apothecary':plant_pot(k,name+'-herbs'+str(j),xx,y+.38,.96,.11)
        elif use=='clothier':
            k.box(name+'-folded-cloth'+str(j),(xx,y+.38,1.02),(.32,.33,.12),
                  'clothBlue' if j%2 else 'shopAwningSage',False)
            k.box(name+'-cloth-fold'+str(j),(xx,y+.38,1.13),(.27,.29,.08),'homeLimewash',False)
        else:
            k.box(name+'-produce-tray'+str(j),(xx,y+.38,1.01),(.35,.32,.10),'oak')
            for q in range(3):k.box(name+f'-produce-{j}-{q}',(xx+(q-1)*.10,y+.38,1.12),(.08,.13,.12),
                                    ['produceGreen','produceOchre','produceRose'][j%3],False)
    sx=(w/2-.25) if doorx<0 else (-w/2+.25)
    sign(k,name,sx,y+.12,use)
    return {'use':use,'displayWidth':round(ww,3),'recess':.18,'projection':.76}

def workshop(k,l):
    name,w,d=l['id'],l['width'],l['depth'];y=d/2
    # A working bench occupies the free bay below the ground window. Store
    # tools above its surface; neither rack nor tools cover the glazing.
    t=l['architectureType'];doorx=-w*.21 if t in ('half-hip','oriel-house','merchant-hall') else 0
    gx=w*.24 if doorx<0 else -w*.29;bw=min(1.15,w*.23)
    k.box(name+'-workbench',(gx,y+.38,.81),(bw+.10,.45,.14),'oak')
    for side in (-1,1):
        k.box(name+'-workbench-leg'+str(side),(gx+side*bw*.36,y+.38,.38),(.12,.34,.76),'timber')
    k.box(name+'-tool-rack',(gx,y+.19,.85),(bw,.10,.25),'oak')
    for j in range(3):
        xx=gx+(j-1)*bw*.27
        k.beam(name+'-tool-handle'+str(j),(xx,y+.28,.72),(xx,y+.28,1.00),.045,'oak')
        k.box(name+'-tool-head'+str(j),(xx,y+.28,1.035),(.21 if j!=1 else .10,.06,.08 if j!=1 else .10),'iron')
    sign(k,name,w/2-.25,y+.1,'carpenter')
    return {'use':'carpenter','projection':.68}

def home(k,l,style):
    name,w,d,t=l['id'],l['width'],l['depth'],l['architectureType'];y=d/2
    doorx=-w*.21 if t in ('half-hip','oriel-house','merchant-hall') else 0
    doorw=1.36 if w<6 else 1.7;pw=min(w-.30,doorw+.54)
    if style=='gable-entry':
        a,b=doorx-pw/2,doorx+pw/2
        pts=[(a,y+.03,3.22),(b,y+.03,3.22),(a,y+.72,3.16),(b,y+.72,3.16),
             (doorx,y+.03,3.85),(doorx,y+.72,3.79)]
        obj=k.mesh(name+'-porch-gable',pts,[[0,2,5,4],[1,4,5,3]],l['clay']);obj['role']='overhead'
        for side in (-1,1):
            xx=doorx+side*pw/2
            k.beam(name+'-porch-verge'+str(side),(xx,y+.72,3.16),(doorx,y+.72,3.79),.10)
    else:
        obj=k.mesh(name+'-entry-shed',[(doorx-pw/2,y+.03,3.48),(doorx+pw/2,y+.03,3.48),
            (doorx+pw/2,y+.72,3.16),(doorx-pw/2,y+.72,3.16)],[[0,1,2,3]],l['clay']);obj['role']='overhead'
    k.box(name+'-porch-front-beam',(doorx,y+.69,3.15),(pw,.13,.15),'timber')
    for side in (-1,1):
        xx=doorx+side*(doorw/2+.20)
        k.box(name+'-porch-post'+str(side),(xx,y+.63,1.65),(.11,.11,3.10),'timber')
        k.box(name+'-porch-foot'+str(side),(xx,y+.63,.19),(.20,.20,.30),'stoneLight')
    # Read saved component bounds rather than assuming every family has the
    # same upper story. Low lodges use their existing ground window instead.
    c=k.owner
    def saved_windows(fragment):
        result=[]
        for obj in c.objects:
            if obj.type!='MESH':continue
            selections=[[v.co for v in obj.data.vertices if any(a.group==group.index for a in v.groups)]
                        for group in obj.vertex_groups if fragment in group.name and group.name.endswith('-glass')]
            if not obj.get('component_count') and fragment in obj.name and obj.name.endswith('-glass'):
                selections.append([v.co for v in obj.data.vertices])
            for vs in selections:
                if vs:result.append((min(v.x for v in vs),max(v.x for v in vs),min(v.z for v in vs),max(v.z for v in vs)))
        return result
    windows=saved_windows('-front-story-0-window-') or saved_windows('-ground-window-glass')
    assert windows,(name,'Missing saved window components')
    for j,(xa,xb,za,zb) in enumerate(windows):
        x=(xa+xb)/2;zz=(za+zb)/2;hh=zb-za;ww=xb-xa+.18
        # Narrow leaves respect the nearby timber piers rather than spreading
        # across neighboring glazing or beyond the owned facade.
        for side in (-1,1):
            xx=x+side*(ww/2+.17)
            k.box(name+f'-shutter-{j}-{side}',(xx,y+.43,zz),(.24,.065,hh),'oak')
            for h in (-hh*.27,hh*.27):k.box(name+f'-shutter-strap-{j}-{side}-{h}',
                (xx,y+.47,zz+h),(.23,.03,.045),'iron',False)
    if t=='oriel-house':
        # A projecting upper bay already shelters the entry; another porch
        # would intersect its soffit. Keep the shutters and clear that volume.
        remove_components(c,('capital-property-v76-'+name+'-entry-shed',
                             'capital-property-v76-'+name+'-porch-'))
        return {'use':'shuttered-oriel','projection':.47,'shutterBays':len(windows)}
    return {'use':style,'projection':.72,'shutterBays':len(windows)}

residential_ids={
 'capital-townhouse-083','capital-townhouse-085','capital-townhouse-089',
 'capital-residential-073-a','capital-townhouse-087','capital-townhouse-081',
 'capital-townhouse-090','capital-residential-077-a','capital-residential-071',
 'capital-residential-076-b','capital-townhouse-080'}
records=[]
for l in p['lots']:
    if l['existing'] or not (l['family'] in ('market','workshop') or l['id'] in residential_ids):continue
    c=bpy.data.collections[l['id']]
    root=next(obj for obj in c.objects if obj.type=='EMPTY' and not obj.parent)
    k=Kit(c,root);k.prefix='capital-property-v76-'
    if l['family']=='market':
        use='clothier' if l['district']=='Lantern Market' else 'apothecary' if l['district']=='Willow Borough' else 'provisioner'
        remove_components(c,('-ground-core','-ground-window','-canopy-','-shop-counter','-shop-goods-','-front-flowers-','-flower-bracket-','-craft-bench','-bench-leg-'))
        detail=shop(k,l,use)
    elif l['family']=='workshop':
        remove_components(c,('-shop-counter','-shop-goods-','-front-flowers-',
                             '-flower-bracket-','-craft-bench','-bench-leg-'))
        detail=workshop(k,l)
    else:detail=home(k,l,'gable-entry' if l['architectureType'] in ('front-gable','craft-lodge','cross-gable') else 'shed-entry')
    c['property_frontage_json']=json.dumps(detail)
    records.append({'id':l['id'],'district':l['district'],**detail})
    print('PROPERTY FRONTAGE',l['id'],detail['use'],flush=True)
bpy.context.view_layer.update()
after=exporter['export'](s)
assert invariant(after)==preserved,'Public geometry, actual entries, collision or actors changed'
after_triangles=sum(len(f)-2 for a in after['objects'] for m in a['parts'] if m.get('visible',True) for f in m['faces'])
assert after_triangles-base_triangles<15000, 'Exceeded bounded frontage triangle budget'
s['capital_property_frontages']=1
report={'beforeSHA256':before_hash,'frontageRevision':1,'properties':records,
        'beforeStaticTriangles':base_triangles,'afterStaticTriangles':after_triangles,
        'addedTriangles':after_triangles-base_triangles,'triangleBudget':15000,
        'preservedUrbanGeometryNavigationAnchorsAndSolids':True,
        'newTextures':0,'referenceFrames':['Houses_Shops_Roofs_01m40s.jpg','Houses_Shops_Roofs_03m35s.jpg'],
        'visualAcceptance':'Pending source-matched gameplay review'}
(O/'authoring.json').write_text(json.dumps(report,indent=2)+'\n')
del after,preserved
# Consolidate new geometry by owner/material/role; component selections remain
# editable. The following bakes refresh building, foliage and floor lighting.
runpy.run_path(str(R/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
