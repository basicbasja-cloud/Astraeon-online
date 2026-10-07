"""Original, editable architectural families for the saved Wayfarer capital.

Share material/construction vocabulary, not complete buildings. All envelopes
fit the reviewed street setbacks. Pierced upper walls keep real window reveals.
"""
import math, bpy
from mathutils import Vector, Matrix

def roof(k,name,x,y,w,d,eave,rise,mat,kind='gable',along=False):
    # Physical slope UVs prevent stretched tiles on newly authored roof shapes.
    if kind in ('hip','mansard','half-hip'):
        a,b=w/2,d/2;ridge=max(.18,(w-d)/2) if along else max(.18,(d-w)/2)
        pts=[(x-a,y-b,eave),(x+a,y-b,eave),(x+a,y+b,eave),(x-a,y+b,eave)]
        if kind=='mansard':
            inset=min(w,d)*.18;aa,bb=a-inset,b-inset;z=eave+rise*.72
            pts += [(x-aa,y-bb,z),(x+aa,y-bb,z),(x+aa,y+bb,z),(x-aa,y+bb,z)]
            pts += [(x-ridge,y,eave+rise),(x+ridge,y,eave+rise)] if along else [(x,y-ridge,eave+rise),(x,y+ridge,eave+rise)]
            faces=[[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]+([[4,5,9,8],[5,6,9],[6,7,8,9],[7,4,8]] if along else [[4,5,8],[5,6,9,8],[6,7,9],[7,4,8,9]])
        else:
            pts += [(x-ridge,y,eave+rise),(x+ridge,y,eave+rise)] if along else [(x,y-ridge,eave+rise),(x,y+ridge,eave+rise)]
            faces=[[0,1,5,4],[1,2,5],[2,3,4,5],[3,0,4]] if along else [[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]]
    else:
        pts=[(x-w/2,y-d/2,eave),(x+w/2,y-d/2,eave),(x+w/2,y+d/2,eave),(x-w/2,y+d/2,eave)]
        pts += [(x-w/2,y,eave+rise),(x+w/2,y,eave+rise)] if along else [(x,y-d/2,eave+rise),(x,y+d/2,eave+rise)]
        faces=[[0,1,5,4],[3,4,5,2]] if along else [[0,3,5,4],[1,4,5,2]]
    o=k.mesh(name+'-roof',pts,faces,mat);o['role']='overhead'
    for f in o.data.polygons:
        n=f.normal;u=Vector((0,1,0)) if abs(n.x)>abs(n.y) else Vector((1,0,0));v=n.cross(u).normalized()
        for li in f.loop_indices:
            q=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(q.dot(u)/2.4,q.dot(v)/2.4)
    # Slender physical fascia follows every lower edge, not repeated thick bars.
    for i in range(4):k.beam(name+'-fascia-'+str(i),pts[i],pts[(i+1)%4],.16,'timber' if mat.startswith('roof') else 'civicShadow')
    if kind=='gable':
        for side in (-1,1):
            tri=[(x-w/2,y+side*d/2,eave),(x+w/2,y+side*d/2,eave),(x,y+side*d/2,eave+rise)] if not along else [(x+side*w/2,y-d/2,eave),(x+side*w/2,y+d/2,eave),(x+side*w/2,y,eave+rise)]
            k.mesh(name+'-gable-'+str(side),tri,[[0,1,2]],'homeLimewash' if mat.startswith('roof') else 'civicIvory')
            for j in (0,1):k.beam(name+'-verge-'+str((side,j)),tri[j],tri[2],.16,'timber' if mat.startswith('roof') else 'civicGold')
            k.beam(name+'-kingpost-'+str(side),tuple((Vector(tri[0])+Vector(tri[1]))/2),tri[2],.14,'timber' if mat.startswith('roof') else 'civicShadow')
    return eave+rise

def window_box(k,name,x,y,z,w=1.05):
    k.box(name+'-planter',(x,y,z),(w,.34,.23),'oak')
    k.box(name+'-soil',(x,y,z+.13),(w-.08,.25,.03),'soil',False)
    for j in range(4):
        xx=x-w*.36+j*w*.24;k.box(name+'-leaf-'+str(j),(xx,y,z+.21),(.21,.24,.14),'leaf',False)
        k.mesh(name+'-bloom-'+str(j),[(xx-.06,y-.06,z+.30),(xx+.06,y-.06,z+.32),(xx+.06,y+.06,z+.30),(xx-.06,y+.06,z+.32)],[[0,1,2,3]],'flowerRose',False)

def build_house(l,i,collection,root,kit,floor):
    c=collection(l['id'],l['family']);c['capital_district']=l['district'];r=root(c,(*l['center'],.04),l['angle']);k=kit(c,r)
    w,d=l['width'],l['depth'];t=l['architectureType'];name=l['id'];mat={'market':'merchantLimewash','workshop':'workshopLimewash','residential':'homeLimewash'}[l['family']]
    low=t=='craft-lodge';three=t in ('front-gable','guild-mansard') and (l.get('floors')==3 or i%4==0)
    story=3.12;top=4.75 if low else 8.45 if three else 6.25+(i%3)*.16
    if t=='merchant-hall':top=7.15
    if t=='gallery-villa':top=5.65
    if t=='twin-gable':top=6.5
    core=k.box(name+'-physical-core',(0,0,top/2),(w,d,top),mat,False);core['role']='solid';core['render_visible']=False
    k.box(name+'-ground-core',(0,0,(story+.2)/2),(w,d,story-.2),mat)
    k.box(name+'-foundation',(0,0,.26),(w+.10,d+.10,.52),'stone')
    front=d/2+.22;back=-d/2-.10
    boundaries=[story,top] if not three else [story,story+(top-story)/2,top]
    bays=max(2,min(5,int(w/1.9)));centers=[(j-(bays-1)/2)*(w-.90)/bays for j in range(bays)]
    for j,(za,zb) in enumerate(zip(boundaries,boundaries[1:])):
        for side,origin,angle,width,cs in [('front',(0,front),0,w+.12,centers),('back',(0,back),math.pi,w+.12,centers),('west',(-w/2-.06,.06),math.pi/2,d+.32,[-d*.22,d*.22]),('east',(w/2+.06,.06),-math.pi/2,d+.32,[-d*.22,d*.22])]:
            k.upper_face(name+f'-{side}-story-{j}',width,za,zb,cs,mat,origin,angle,wh=min(1.5,(zb-za)*.62),ww=min(1.1,(w-.9)/bays-.15) if side in ('front','back') else 1.05)
    # Entry stays on the true model front for every family and both owned courts.
    doorx=-w*.21 if t in ('half-hip','oriel-house','merchant-hall') else 0
    doorw=1.36 if w<6 else 1.7;doorh=2.65
    k.box(name+'-door-leaf',(doorx,d/2+.035,.42+doorh/2),(doorw,.035,doorh),'oak',False)
    for side in (-1,1):k.box(name+'-door-jamb-'+str(side),(doorx+side*(doorw/2+.1),d/2+.08,.42+doorh/2),(.2,.16,doorh+.18),'timber')
    k.box(name+'-door-head',(doorx,d/2+.09,doorh+.5),(doorw+.4,.18,.18),'timber')
    for j in (1,2,3):k.box(name+'-door-plank-'+str(j),(doorx-doorw/2+j*doorw/4,d/2+.063,1.77),(.028,.02,doorh-.1),'timber',False)
    k.box(name+'-door-pull',(doorx+doorw*.26,d/2+.09,1.65),(.055,.06,.2),'gold',False)
    gx=w*.24 if doorx<0 else -w*.29
    k.window(name+'-ground-window',gx,d/2,1.86,min(1.45,w*.26),1.3,recess=-.025,low=True)
    for side in (-1,1):k.box(name+'-ground-post-'+str(side),(side*(w/2-.10),d/2+.06,story/2),(.2,.16,story),'timber')
    # Secondary side glazing makes end units occupied rather than blank walls.
    before=set(c.objects);k.window(name+'-side-ground',0,0,1.84,1.18,1.24,recess=-.025,low=True)
    for o in set(c.objects)-before:
        for v in o.data.vertices:v.co=Matrix.Rotation(-math.pi/2,4,'Z')@v.co+Vector((w/2,0,0))
    clay=l.get('clay','roofClayWarm');eave=top+.18
    if t in ('half-hip','merchant-hall'):
        peak=roof(k,name,0,.10,w+.6,d+.75,eave,min(w,d)*.49,clay,'hip',along=w>d)
    elif t=='guild-mansard':
        peak=roof(k,name,0,.10,w+.6,d+.75,eave,min(w,d)*.6,clay,'mansard',along=w>d)
        k.box(name+'-guild-panel',(0,front+.14,top-.60),(min(1.75,w*.38),.08,.52),'oak')
        k.box(name+'-guild-inlay',(0,front+.19,top-.60),(.32,.025,.18),'gold',False)
    elif t=='twin-gable':
        peak=0
        for side in (-1,1):
            ww=w/2+.26;cx=side*w/4;h=eave+(.85 if side<0 else 0)
            if side<0:k.box(name+'-raised-wing',(cx,0,top+.4),(w/2,d,.8),mat)
            peak=max(peak,roof(k,name+'-wing-'+str(side),cx,.10,ww,d+.75,h,ww*.65,clay))
        k.box(name+'-joined-belt',(0,front+.12,story),(w,.22,.2),'timber')
    elif t=='gallery-villa':
        peak=roof(k,name,0,-.25,w+.6,d+.05,eave,2.6,clay,'hip',along=True)
        # Covered gallery occupies the plot front; it does not spill into streets.
        for j,xx in enumerate([-w*.42,-w*.14,w*.14,w*.42]):
            k.box(name+'-gallery-post-'+str(j),(xx,d/2+.66,1.71),(.16,.16,3.42),'timber')
        canopy=k.mesh(name+'-gallery-roof',[(-w/2-.12,d/2-.04,3.7),(w/2+.12,d/2-.04,3.7),(w/2+.12,d/2+1.07,3.24),(-w/2-.12,d/2+1.07,3.24)],[[0,1,2,3]],clay);canopy['role']='overhead'
    elif t in ('cross-gable','oriel-house'):
        peak=roof(k,name,0,.08,w+.6,d+.75,eave,d*.47,clay,along=True)
        ww=min(w*.57,3.2);cx=w*.14
        if t=='cross-gable':
            peak=max(peak,roof(k,name+'-front-cross',cx,d*.22,ww,d*.64+1.0,eave+.22,ww*.72,clay))
            for side in (-1,1):k.beam(name+'-cross-eave-brace-'+str(side),(cx+side*ww*.38,front,top-.48),(cx+side*ww*.38,d/2+.60,top+.18),.13)
        else:
            # Three glazed bay faces and a compact polygonal cap: distinct silhouette.
            y=d/2+.24;outline=[(cx-ww/2,y),(cx-ww*.37,y+.52),(cx+ww*.37,y+.52),(cx+ww/2,y)]
            for j,(a,b) in enumerate(zip(outline,outline[1:])):
                width=math.dist(a,b);angle=math.atan2(b[1]-a[1],b[0]-a[0]);mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
                k.upper_face(name+'-oriel-'+str(j),width,story+.15,top-.25,[0],mat,mid,angle,wh=min(1.7,top-story-.8),ww=min(.88,width-.24))
            center=(cx,y+.25,top+1.35);cap=k.mesh(name+'-oriel-cap',[(a,b,top-.15) for a,b in outline]+[center],[[0,1,4],[1,2,4],[2,3,4]],clay);cap['role']='overhead'
            k.box(name+'-oriel-soffit',(cx,y+.23,story+.05),(ww,.64,.16),'oak')
    else:peak=roof(k,name,0,.08,w+.6,d+.75,eave,w*(.65 if not low else .51),clay)
    # Distinct uses add small frontage detail; broad rows no longer all wear awnings.
    if t in ('half-hip','merchant-hall') or l['family']=='market':
        aw=min(2.1,w*.43);x=gx;y=d/2
        for j in range(5):
            xa=x-aw/2+j*aw/5;k.mesh(name+'-canopy-'+str(j),[(xa,y+.05,3.03),(xa+aw/5,y+.05,3.03),(xa+aw/5,y+.98,2.72),(xa,y+.98,2.72)],[[0,1,2,3]],'shopAwningSage' if j%2 else 'homeLimewash')
        k.box(name+'-shop-counter',(gx,d/2+.43,.475),(aw,.55,.95),'oak')
        for j in range(4):k.box(name+'-shop-goods-'+str(j),(gx-aw*.34+j*aw*.22,d/2+.43,1.04),(.22,.27,.18),['produceGreen','produceOchre','produceRose'][j%3],False)
    elif t=='craft-lodge':
        k.box(name+'-craft-bench',(w*.22,d/2+.50,.76),(min(1.6,w*.35),.55,.16),'oak')
        for side in (-1,1):k.box(name+'-bench-leg-'+str(side),(w*.22+side*.55,d/2+.50,.38),(.12,.35,.76),'timber')
    else:
        window_box(k,name+'-front-flowers',gx,d/2+.26,1.03,min(1.05,w*.25))
        for side in (-1,1):k.beam(name+'-flower-bracket-'+str(side),(gx+side*.32,d/2,.72),(gx+side*.32,d/2+.38,.91),.09)
    # A different chimney position reinforces family identity without new textures.
    xx=-w*.22 if i%2 else w*.23;yy=-d*.22;chimneybottom=top-.10;chimneytop=peak+.62
    k.box(name+'-chimney',(xx,yy,(chimneybottom+chimneytop)/2),(.5,.55,chimneytop-chimneybottom),'stoneLight')
    k.box(name+'-chimney-cap',(xx,yy,chimneytop+.08),(.68,.72,.16),'stoneLight')
    k.box(name+'-chimney-mouth',(xx,yy,chimneytop+.17),(.36,.4,.015),'iron',False)
    for j in range(2):
        ya=d/2+(2-j)*.22;yb=ya+.24;z=(j+1)*.22;k.box(name+'-entry-step-'+str(j),(doorx,(ya+yb)/2,z/2),(doorw+.18,.24,z),'stoneLight')
        pts=[r.matrix_basis@Vector((x,y,z)) for x,y in [(doorx-doorw/2-.09,ya),(doorx+doorw/2+.09,ya),(doorx+doorw/2+.09,yb),(doorx-doorw/2-.09,yb)]]
        floor({'id':name+'-entry-contact-'+str(j),'vertices':[list(v) for v in pts],'faces':[[0,1,2,3]],'material':'stoneLight','role':'forecourt','objectId':name})
    return c

def build_civic(spec,c,r,k,floor):
    name=spec['id'];w,d=spec['width'],spec['depth'];t=spec['architectureType'];council='council' in name;archive='archive' in name;exchange='exchange' in name
    h=12.0 if council else 13.1 if archive else 7.8
    def mass(suffix,cx,cy,ww,dd,hh,stories):
        core=k.box(name+suffix+'-physical',(cx,cy,hh/2),(ww,dd,hh),'civicIvory',False);core['role']='solid';core['render_visible']=False
        k.box(name+suffix+'-base',(cx,cy,.28),(ww+.24,dd+.24,.56),'civicShadow')
        for face,width,origin,angle in [('front',ww,(cx,cy+dd/2),0),('rear',ww,(cx,cy-dd/2),math.pi),('west',dd,(cx-ww/2,cy),math.pi/2),('east',dd,(cx+ww/2,cy),-math.pi/2)]:
            bays=max(2,int(width/3.0));centers=[(j-(bays-1)/2)*width/(bays+.6) for j in range(bays)]
            for j in range(stories):
                za=.6+j*(hh-.6)/stories;zb=.6+(j+1)*(hh-.6)/stories
                k.upper_face(name+suffix+face+str(j),width,za,zb,centers,'civicIvory',origin,angle,wh=min(2.25,(zb-za)*.65),ww=min(1.5,width/(bays+.6)-.3))
        for xx in (cx-ww/2,cx+ww/2):
            for yy in (cy-dd/2,cy+dd/2):k.box(name+suffix+'-pilaster-'+str((xx,yy)),(xx,yy,hh/2),(.42,.42,hh),'civicShadow')
        k.box(name+suffix+'-cornice',(cx,cy,hh+.18),(ww+.55,dd+.55,.40),'civicIvory')
        return hh
    if council:
        mass('-palazzo',0,0,w,d,h,3)
        roof(k,name+'-palazzo',0,0,w+1,d+1,h+.35,6.5,'civicSlate','hip',True)
        # Raised central clock pavilion over an otherwise horizontal hipped palace.
        mass('-clock-pavilion',0,d*.12,5.8,5.8,21,5)
        roof(k,name+'-clock-crown',0,d*.12,6.6,6.6,21.3,3.6,'civicSlate','hip')
        k.box(name+'-clock-face',(0,d*.12+2.98,18.8),(2.5,.05,2.5),'civicGold',False)
        k.box(name+'-clock-inset',(0,d*.12+3.02,18.8),(2.20,.04,2.20),'civicIvory',False)
        k.beam(name+'-clock-hour',(0,d*.12+3.06,18.8),(.65,d*.12+3.06,19.25),.075,'civicShadow')
        k.beam(name+'-clock-minute',(0,d*.12+3.06,18.8),(0,d*.12+3.06,19.7),.075,'civicShadow')
    elif archive:
        # Tall central reading nave, low side galleries, one separate stair tower.
        mass('-nave',0,0,12.4,d,h,3);roof(k,name+'-nave',0,0,13.3,d+1.1,h+.3,7.3,'civicSlate')
        for side in (-1,1):
            cx=side*10.1;mass('-reading-wing-'+str(side),cx,-.6,7.2,d-1.2,8.7,2);roof(k,name+'-reading-wing-'+str(side),cx,-.6,7.7,d-.4,9.0,3.6,'civicSlate','hip')
        mass('-stair-tower',-w*.34,d*.27,4.0,4.0,23.0,5);roof(k,name+'-stair-spire',-w*.34,d*.27,4.8,4.8,23.3,5.5,'civicSlate','hip')
        # Rosette is relief on the gable, clear of the pierced story windows.
        cx,yy,zz,rad=0,d/2+.60,h+2.75,2.45
        for j in range(16):
            aa,bb=j*math.tau/16,(j+1)*math.tau/16
            k.mesh(name+'-rose-stone-'+str(j),[(cx+rr*math.cos(a),yy,zz+rr*math.sin(a)) for a,rr in [(aa,rad),(bb,rad),(bb,rad-.18),(aa,rad-.18)]],[[0,1,2,3]],'civicGold',False)
            k.mesh(name+'-rose-glass-'+str(j),[(0,yy-.025,zz),((rad-.18)*math.cos(aa),yy-.025,zz+(rad-.18)*math.sin(aa)),((rad-.18)*math.cos(bb),yy-.025,zz+(rad-.18)*math.sin(bb))],[[0,1,2]],'civicGlass',False)
            k.beam(name+'-rose-ray-'+str(j),(0,yy+.02,zz),((rad-.2)*math.cos(aa),yy+.02,zz+(rad-.2)*math.sin(aa)),.045,'civicIvory')
    else:
        mass('-market',0,-.45,w,d-.9,h,2)
        roof(k,name+'-market',0,-.45,w+1,d+.2,h+.35,5.3,'roofClayOchre',along=True)
        # Long open front colonnade and low canopy define a commercial building.
        for j in range(9):
            xx=-w/2+1+j*(w-2)/8;o=k.box(name+'-arcade-column-'+str(j),(xx,d/2+.85,1.95),(.34,.40,3.9),'civicIvory');o['role']='solid'
            k.box(name+'-arcade-base-'+str(j),(xx,d/2+.85,.30),(.52,.64,.60),'civicShadow')
        k.box(name+'-arcade-entablature',(0,d/2+.85,4.05),(w+.4,.6,.38),'civicIvory')
        k.mesh(name+'-arcade-canopy',[(-w/2-.3,d/2-.2,5.2),(w/2+.3,d/2-.2,5.2),(w/2+.3,d/2+1.45,4.30),(-w/2-.3,d/2+1.45,4.30)],[[0,1,2,3]],'roofClayOchre')
        mass('-belfry',-w*.34,-d*.20,3.6,3.6,18.0,4);roof(k,name+'-belfry',-w*.34,-d*.2,4.6,4.6,18.3,4.0,'civicSlate','hip')
    # Main door and entry steps share unchanged, genuinely accessible forecourt.
    k.box(name+'-door-leaf',(0,d/2+.05,2.1),(3.2,.08,3.5),'civicDoor',False)
    for side in (-1,1):k.box(name+'-portal-jamb-'+str(side),(side*1.8,d/2+.12,2.15),(.36,.5,3.8),'civicIvory')
    k.box(name+'-portal-head',(0,d/2+.12,4.16),(4.0,.55,.38),'civicGold')
    for side in (-1,1):k.box(name+'-banner-'+str(side),(side*5.5,d/2+.34,5.6),(.95,.04,2.45),'clothBlue',False)
    for j in range(3):
        ya=d/2+(3-j)*.42;yb=ya+.46;z=(j+1)*.20;k.box(name+'-entry-riser-'+str(j),(0,ya+.23,z/2),(6.4,.46,z),'civicIvory')
        x,y=spec['center'];floor({'id':name+'-entry-tread-'+str(j),'vertices':[[x-3.2,y+ya,z],[x+3.2,y+ya,z],[x+3.2,y+yb,z],[x-3.2,y+yb,z]],'faces':[[0,1,2,3]],'material':'civicIvory','role':'forecourt','objectId':name})
    for o in c.objects:
        if o.type!='MESH':continue
        m=o.data.materials[0].name
        if m=='timber':o.data.materials[0]=bpy.data.materials['civicShadow']
        elif m=='stoneLight':o.data.materials[0]=bpy.data.materials['civicIvory']
        elif m=='frontageGlazing':o.data.materials[0]=bpy.data.materials['civicGlass']
