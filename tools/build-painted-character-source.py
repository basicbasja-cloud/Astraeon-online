"""Reference-fit head and anatomical grasp refinement, executed through Blender MCP.

No source mesh is loaded. This is a proportion/pose gate, not final rig topology.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Constants are image-space observations from the unchanged approved concept.
ROOT_REF = (645, 1155)
K = 176 / 1113
UNIT = .0017
ELEV = math.radians(25)
YAW = math.radians(45)
OUT = "C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/source-lookdev-03"
LANDMARKS = {
    "head": (668,290), "neck": (665,432), "chest": (660,527),
    "waist": (658,637), "pelvis": (658,746),
    "shoulder_R": (539,478), "elbow_R": (480,612), "wrist_R": (451,727),
    "palm_R": (473,766), "shoulder_L": (759,444), "elbow_L": (802,577),
    "wrist_L": (825,668), "palm_L": (836,713),
    "hip_R": (588,769), "knee_R": (540,940), "ankle_R": (542,1110),
    "hip_L": (737,746), "knee_L": (749,895), "ankle_L": (765,1036),
    "guard": (522,797), "blade_tip": (706,1085),
}

# Only replace the owned disposable tool scene, never an owner source scene.
assert bpy.context.scene.name in {"ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST", "ASTRAEON_REFERENCE_FIT_01", "ASTRAEON_SOURCE_REFINEMENT_02", "ASTRAEON_SOURCE_LOOKDEV_03"}
scene = bpy.context.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name.startswith(("BODY_BLOCKOUT", "MAJOR_FORM_BLOCKOUT", "LANDMARK_GUIDES", "HEAD_FEATURES")) and not col.objects:
        bpy.data.collections.remove(col)
scene.name = "ASTRAEON_SOURCE_LOOKDEV_03"
model = bpy.data.objects.new("ROOT_ReferenceFit", None)
scene.collection.objects.link(model)
model.rotation_euler.z = YAW
body_collection = bpy.data.collections.new("BODY_BLOCKOUT")
gear_collection = bpy.data.collections.new("MAJOR_FORM_BLOCKOUT")
guide_collection = bpy.data.collections.new("LANDMARK_GUIDES")
for col in (body_collection, gear_collection, guide_collection):
    scene.collection.children.link(col)


def unproject(pixel, depth=0):
    u = (pixel[0] - ROOT_REF[0]) * UNIT
    v = (ROOT_REF[1] - pixel[1]) * UNIT
    x = (u + math.sin(YAW) * depth) / math.cos(YAW)
    z = (v - math.sin(ELEV) * (math.sin(YAW)*x + math.cos(YAW)*depth)) / math.cos(ELEV)
    return Vector((x, depth, z))


def ground(pixel):
    xw = (pixel[0] - ROOT_REF[0]) * UNIT
    yw = (ROOT_REF[1] - pixel[1]) * UNIT / math.sin(ELEV)
    return Vector((math.cos(YAW)*xw + math.sin(YAW)*yw,
                   -math.sin(YAW)*xw + math.cos(YAW)*yw, 0))


depths = {"head": .025,"neck": .015,"chest": .025,"waist": .035,"pelvis": .04,
          "shoulder_R": .00,"elbow_R": -.045,"wrist_R": -.15,"palm_R": -.22,
          "shoulder_L": .00,"elbow_L": -.02,"wrist_L": -.035,"palm_L": -.045,
          "hip_R": .04,"knee_R": .05,"ankle_R": .14,
          "hip_L": -.06,"knee_L": .06,"ankle_L": .12,
          "guard": -.25,"blade_tip": -.35}
P = {name: unproject(pixel, depths[name]) for name,pixel in LANDMARKS.items()}


def material(name, color):
    color = tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in color)
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    m.use_nodes = True
    node = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    node.inputs["Base Color"].default_value = (*color,1)
    node.inputs["Roughness"].default_value = .83
    return m


M = {n: material(n,c) for n,c in {
    "WarmClay": (.86,.64,.49), "HairMass": (.70,.65,.73),
    "Navy": (.10,.12,.17), "Ivory": (.82,.77,.64),
    "BronzeLight": (.80,.57,.28), "Bronze": (.60,.36,.14), "Mustard": (.78,.49,.11),
    "Teal": (.035,.19,.22), "Olive": (.12,.14,.085),
    "BootBrown": (.29,.14,.075), "BladeGuide": (.69,.73,.79),
    "GloveSeam": (.43,.24,.13), "EyeWhite": (.94,.92,.88),
    "Ink": (.055,.045,.07), "SkinShade": (.58,.32,.25),
    "Iris": (.31,.24,.30), "Brow": (.26,.19,.22), "Lip": (.43,.23,.23),
    "HairShadow": (.44,.39,.50), "HairLight": (.81,.76,.83),
}.items()}


def mesh(name, verts, faces, mat, col, parent=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    if parent:
        obj.parent = model
    data.materials.append(mat)
    for poly in data.polygons:
        poly.use_smooth = True
    return obj


def loft(name, centers, sizes, mat, col, sides=20, axis=None):
    if axis is None:
        ax = Vector((1,0,0)); ay = Vector((0,1,0))
    else:
        axis = Vector(axis).normalized()
        ax = Vector((0,1,0)).cross(axis).normalized()
        if ax.length < .5:
            ax = Vector((1,0,0)).cross(axis).normalized()
        ay = axis.cross(ax).normalized()
    verts=[]; faces=[]
    for center, (rx,ry) in zip(centers,sizes):
        for j in range(sides):
            a = math.tau*j/sides
            verts.append(Vector(center)+ax*rx*math.cos(a)+ay*ry*math.sin(a))
    for i in range(len(centers)-1):
        for j in range(sides):
            n=(j+1)%sides
            faces.append((i*sides+j,i*sides+n,(i+1)*sides+n,(i+1)*sides+j))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((len(centers)-1)*sides+j for j in range(sides)))
    obj=mesh(name,verts,faces,mat,col)
    obj['paintRingSize']=sides;obj['paintRingCount']=len(centers)
    return obj


def limb(name,a,b,profile,mat,col):
    centers=[a.lerp(b,t) for t,rx,ry in profile]
    return loft(name,centers,[(rx,ry) for t,rx,ry in profile],mat,col,axis=b-a)


"""Source-local modeled details; inserted into the MCP build script before use."""

def curved_tube(name, points, radii, mat, col, sides=12):
    points=[Vector(p) for p in points]
    verts=[];faces=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
        seed=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0))
        ax=seed.cross(tangent).normalized();ay=tangent.cross(ax).normalized()
        for j in range(sides):
            a=math.tau*j/sides
            verts.append(p+radii[i][0]*math.cos(a)*ax+radii[i][1]*math.sin(a)*ay)
    for i in range(len(points)-1):
        for j in range(sides):
            n=(j+1)%sides
            faces.append((i*sides+j,i*sides+n,(i+1)*sides+n,(i+1)*sides+j))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple((len(points)-1)*sides+j for j in range(sides)))
    obj=mesh(name,verts,faces,mat,col)
    obj['paintRingSize']=sides;obj['paintRingCount']=len(points)
    return obj


def line(name, points, radius, mat, col):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.resolution_u=12;data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,v in zip(spline.points,points):p.co=(*Vector(v),1)
    obj=bpy.data.objects.new(name,data);col.objects.link(obj);obj.parent=model
    data.materials.append(mat)
    return obj


def grasp(name, guard, axis, wrist, mat, col, dressed=False):
    """Four anatomical digit paths about the hilt plus an opposing thumb.

    This is modeled contact geometry, not automatic acceptance of the grasp.
    The current body union is still a static sculpt and needs retopology.
    """
    axis=axis.normalized()
    b=Vector((0,1,0)).cross(axis).normalized();c=axis.cross(b).normalized()
    center=guard-axis*.096
    palm_center=center+c*.038
    pad=.006 if dressed else 0
    palm=loft(name+'_Palm',[palm_center-axis*.070,palm_center,palm_center+axis*.061],
        [(.032+pad,.021+pad),(.052+pad,.026+pad),(.038+pad,.020+pad)],mat,col,20,axis=axis)
    connector=curved_tube(name+'_Wrist',[wrist,wrist.lerp(palm_center,.55),palm_center-axis*.025],
        [(.048+pad,.044+pad),(.046+pad,.042+pad),(.037+pad,.035+pad)],mat,col,20)
    parts=[palm,connector]
    for n,distance in [('index',.042),('middle',.078),('ring',.114),('little',.15)]:
        digit_center=guard-axis*distance
        points=[]
        for i in range(17):
            a=math.radians(77-182*i/16)
            points.append(digit_center+.033*(b*math.cos(a)+c*math.sin(a)))
        r=.018 if dressed else .012
        radii=[(r*(1-.15*(i/16)**4),r*(1-.15*(i/16)**4)) for i in range(17)]
        obj=curved_tube(name+'_'+n,points,radii,mat,col,12)
        obj['digit']=n;obj['curlIsModeledNotRigged']=True
        parts.append(obj)
        if dressed:
            # The seam follows the curved glove's outer knuckle, never the hilt.
            seam=[points[i]+(points[i]-digit_center).normalized()*(r+.0008) for i in range(2,7)]
            line(name+'_'+n+'_Seam',seam,.0017,M['GloveSeam'],col)
    thumb_center=guard-axis*.063
    thumb=[palm_center-b*.038+axis*.018,
           thumb_center-b*.042+c*.018,
           thumb_center-b*.031-c*.015,
           thumb_center-b*.003-c*.033]
    r=.022 if dressed else .0155
    parts.append(curved_tube(name+'_thumb',thumb,[(r,r),(r,r),(r*.9,r*.9),(r*.7,r*.7)],mat,col,16))
    for obj in parts:
        obj['anatomicalGraspStudy']=True;obj['ownerGripApproved']=False
    return parts


def modeled_head():
    center=hc+Vector((-.05,-.025,.038))
    def face(x,z,offset=.003):
        # Front of the actual skull loft, with a flatter central cheek plane.
        profiles=[(-.225,.06,.065),(-.18,.125,.105),(-.06,.205,.165),(.10,.22,.18),(.205,.15,.14),(.24,.025,.025)]
        lower=profiles[0];upper=profiles[-1]
        for a,b in zip(profiles,profiles[1:]):
            if a[0]<=z<=b[0]:lower=a;upper=b;break
        t=max(0,min(1,(z-lower[0])/(upper[0]-lower[0])))
        rx=lower[1]*(1-t)+upper[1]*t;ry=lower[2]*(1-t)+upper[2]*t
        y=-ry*math.sqrt(max(.025,1-(x/rx)**2))
        return center+Vector((x,y-offset,z))

    for side,sign in [('R',-1),('L',1)]:
        ex=sign*.085;ez=-.020 if side=='R' else -.037;verts=[];faces=[]
        for row in range(7):
            v=row/6*2-1
            for j in range(17):
                u=j/16*2-1
                x=ex+u*.068;z=ez+v*.025*(1-u*u)**.6
                verts.append(face(x,z,.006))
        for row in range(6):
            for j in range(16):
                a=row*17+j;faces.append((a,a+1,a+18,a+17))
        eye=mesh('EyeWhite_'+side,verts,faces,M['EyeWhite'],gear_collection)
        solid=eye.modifiers.new('EyeSurfaceThickness','SOLIDIFY');solid.thickness=.002
        upper=[face(ex+u*.068,ez+.025*(1-u*u)**.6,.011) for u in [j/16*2-1 for j in range(17)]]
        lower=[face(ex+u*.068,ez-.024*(1-u*u)**.6,.010) for u in [j/16*2-1 for j in range(17)]]
        line('UpperLid_'+side,upper,.0035,M['Ink'],gear_collection)
        line('LowerLid_'+side,lower,.002,M['SkinShade'],gear_collection)
        for name,rx,rz,offset,mat in [('Iris',.025,.023,.013,M['Iris']),('Pupil',.010,.017,.016,M['Ink'])]:
            vs=[face(ex,ez,offset)];fs=[]
            for j in range(32):
                a=math.tau*j/32;vs.append(face(ex+rx*math.cos(a),ez+rz*math.sin(a),offset))
            for j in range(32):fs.append((0,j+1,(j+1)%32+1))
            mesh(name+'_'+side,vs,fs,mat,gear_collection)
        p=face(ex-.009,ez+.012,.020)
        curved_tube('EyeCatchlight_'+side,[p,p+Vector((0,-.001,.003))],[(.005,.005),(.004,.004)],M['EyeWhite'],gear_collection,12)
        brow=[face(ex+u*.065,ez+.059+.008*(1-u*u)-sign*u*.005,.012) for u in [j/8*2-1 for j in range(9)]]
        line('Brow_'+side,brow,.007,M['Brow'],gear_collection)
        ec=center+Vector((sign*.204,.005,-.037))
        ear=loft('Ear_'+side,[ec+Vector((0,0,z)) for z in [-.075,-.025,.036,.06]],
            [(.019,.022),(.044,.038),(.039,.03),(.01,.013)],M['WarmClay'],gear_collection,20)
        line('EarFold_'+side,[ec+Vector((sign*.026,-.026,z)) for z in [-.038,-.015,.009,.033]],.005,M['SkinShade'],gear_collection)
    nose_points=[face(0,-.023,.009),face(0,-.063,.021),face(0,-.085,.017)]
    curved_tube('NoseForm',nose_points,[(.010,.008),(.013,.015),(.010,.007)],M['WarmClay'],gear_collection,12)
    mouth=[face(x,-.132+.008*(x/.035)**2,.009) for x in [j/8*.07-.035 for j in range(9)]]
    line('Mouth',mouth,.0035,M['Lip'],gear_collection)

    # Scalp is a true volume; clumps lie over its front, sides and rear.
    cap=loft('Hair_Scalp',[hc+Vector((-.025,.008,z+.040)) for z in [-.035,.07,.18,.255,.30]],
        [(.16,.135),(.24,.20),(.235,.20),(.15,.14),(.025,.025)],M['HairMass'],gear_collection,40)
    def lock(name,points,width):
        points=[Vector(p) for p in points]
        centers=[];radii=[]
        a,b,c,d=points
        for i in range(13):
            t=i/12
            centers.append(a*(1-t)**3+3*b*t*(1-t)**2+3*c*t*t*(1-t)+d*t**3)
            radius=width*(.28+.85*math.sin(math.pi*t)**.8)*(1-t)**.35 if i<12 else .001
            radii.append((radius,radius*.29))
        obj=curved_tube(name,centers,radii,M['HairMass'],gear_collection,12)
        obj.data.materials.append(M['HairShadow']);obj.data.materials.append(M['HairLight'])
        for poly in obj.data.polygons:
            sector=poly.index%12
            poly.material_index=2 if sector in [1,2,3] else 1 if sector in [7,8,9] else 0
        return obj
    for i in range(16):
        a=math.tau*i/16+.07*math.sin(i*2.1)
        start=hc+Vector((.07*math.cos(a),.06*math.sin(a),.225))
        mid=hc+Vector((.25*math.cos(a+.15),.215*math.sin(a+.15),.235))
        bend=hc+Vector((.28*math.cos(a+.22),.24*math.sin(a+.22),.145))
        end=hc+Vector((.31*math.cos(a+.28),.265*math.sin(a+.28),.025+(i%3)*.036 if math.sin(a)>-.4 else .11))
        lock('Hair_Radial_%02d'%i,[start,mid,bend,end],.076)
    forelocks=[[(639,175),(596,228),(562,277),(575,340)],
        [(696,190),(636,252),(617,300),(629,350)],
        [(708,189),(698,248),(679,285),(669,306)],
        [(714,191),(751,227),(716,259),(712,283)],
        [(734,200),(794,226),(763,285),(751,303)],
        [(757,177),(820,259),(789,295),(773,345)]]
    for i,points in enumerate(forelocks):
        lock('Hair_Forelock_%02d'%i,[unproject(p,d) for p,d in zip(points,[-.065,-.14,-.20,-.215])],.052)
    lock('Hair_CrownCurl',[unproject(p,.035) for p in [(683,175),(715,98),(661,85),(618,94)]],.047)
    lock('Hair_CrownSide',[unproject(p,.065) for p in [(635,180),(600,125),(564,127),(551,132)]],.044)

# Continuous anatomy is formed from tapered volume cross-sections, not a
# MakeHuman body or the rejected primitive mannequin. Voxel union is blockout
# topology only; final deformation loops must be authored after acceptance.
body_parts=[]
torso_centers=[P["pelvis"]+Vector((0,0,-.13)),P["pelvis"],P["waist"],P["chest"],
               P["neck"]+Vector((0,0,-.09)),P["neck"]]
body_parts.append(loft("TorsoVolume",torso_centers,
    [(.14,.115),(.215,.14),(.195,.12),(.255,.14),(.22,.12),(.075,.075)],M["WarmClay"],body_collection))
hc=P["head"]
body_parts.append(limb("NeckVolume",P["neck"],hc+Vector((.025,-.05,-.16)),
    [(0,.074,.074),(1,.073,.07)],M["WarmClay"],body_collection))
body_parts.append(loft("SkullVolume",[hc+Vector((-.05,-.025,z+.038)) for z in [-.225,-.18,-.06,.10,.205,.24]],
    [(.06,.065),(.125,.105),(.205,.165),(.22,.18),(.15,.14),(.025,.025)],M["WarmClay"],body_collection,32))
for side in ("R","L"):
    shoulder,elbow,wrist,hip,knee,ankle=[P[n+"_"+side] for n in ("shoulder","elbow","wrist","hip","knee","ankle")]
    body_parts.append(limb("Clavicle_"+side,P["chest"]+Vector((0,0,.09)),shoulder,
        [(0,.14,.12),(1,.09,.08)],M["WarmClay"],body_collection))
    body_parts.append(limb("UpperArm_"+side,shoulder,elbow,
        [(0,.095,.085),(.30,.10,.087),(.80,.075,.07),(1,.075,.07)],M["WarmClay"],body_collection))
    body_parts.append(limb("Forearm_"+side,elbow,wrist,
        [(0,.075,.07),(.26,.085,.075),(.8,.06,.052),(1,.047,.045)],M["WarmClay"],body_collection))
    body_parts.append(limb("Thigh_"+side,hip,knee,
        [(0,.14,.13),(.32,.14,.13),(.75,.102,.095),(1,.08,.08)],M["WarmClay"],body_collection))
    body_parts.append(limb("Calf_"+side,knee,ankle,
        [(0,.085,.08),(.26,.105,.095),(.62,.08,.075),(1,.045,.055)],M["WarmClay"],body_collection))
    palm=P["palm_"+side]
    if side=="R":
        hand_axis=(P["blade_tip"]-P["guard"]).normalized();hand_guard=P["guard"]
    else:
        hand_axis=(wrist-elbow).normalized();hand_guard=palm+hand_axis*.096
    body_parts.extend(grasp("BodyHand_"+side,hand_guard,hand_axis,wrist,M["WarmClay"],body_collection))
    foot=ground((535,1161) if side=="R" else (790,1076))
    body_parts.append(loft("FootVolume_"+side,[foot+Vector((0,-.04,.016)),foot+Vector((0,-.04,.08)),ankle],
        [(.06,.125),(.06,.125),(.045,.055)],M["WarmClay"],body_collection))

bpy.ops.object.select_all(action="DESELECT")
for part in body_parts:
    part.select_set(True)
bpy.context.view_layer.objects.active=body_parts[0]
bpy.ops.object.join()
body=bpy.context.active_object
body.name="Body_VolumeBlockout"
remesh=body.modifiers.new("ContinuousVolumeBlockout","REMESH")
remesh.mode="VOXEL";remesh.voxel_size=.007;remesh.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=body.modifiers.new("BlockoutSurfaceRelax","SMOOTH")
smooth.factor=.65;smooth.iterations=4
bpy.ops.object.modifier_apply(modifier=smooth.name)
body["final_deformation_topology"]=False

# Removable primary costume masses for a fair dressed silhouette comparison.
loft("Tunic_MainMass",[P["waist"]+Vector((0,-.015,-.055)),P["waist"]+Vector((0,-.015,0)),
                       P["chest"]+Vector((0,-.015,0)),P["neck"]+Vector((0,-.015,-.09))],
     [(.205,.132),(.205,.13),(.27,.155),(.24,.14)],M["Navy"],gear_collection)
loft("Belt_Mass",[P["waist"]+Vector((0,0,z)) for z in [-.04,.025]],
     [(.225,.145),(.225,.145)],M["BootBrown"],gear_collection)
for side in ("R","L"):
    shoulder,elbow,wrist,hip,knee,ankle=[P[n+"_"+side] for n in ("shoulder","elbow","wrist","hip","knee","ankle")]
    limb("Sleeve_"+side,shoulder,elbow,[(0,.105,.095),(.4,.108,.1),(1,.085,.08)],M["Navy"],gear_collection)
    limb("Bracer_"+side,elbow.lerp(wrist,.28),wrist,
         [(0,.105,.09),(.45,.092,.08),(1,.064,.06)],M["Bronze"],gear_collection)
    limb("Pauldron_"+side,shoulder+Vector((0,0,.080)),shoulder.lerp(elbow,.36),
         [(0,.014,.014),(.12,.084,.078),(.32,.136,.120),
          (.58,.147,.130),(.86,.143,.124),(1,.137,.120)],M["Bronze"],gear_collection)
    limb("Trouser_"+side,hip,knee,[(0,.14,.13),(.3,.145,.13),(.85,.117,.108),(1,.09,.09)],M["Olive"],gear_collection)
    foot=ground((535,1161) if side=="R" else (790,1076))
    boot_top=knee.lerp(ankle,.25)
    loft("Boot_"+side,[foot+Vector((0,-.035,.012)),foot+Vector((0,-.06,.085)),ankle+Vector((0,-.01,.07)),boot_top],
         [(.072,.155),(.075,.155),(.069,.082),(.103,.096)],M["BootBrown"],gear_collection)
    limb("KneeCuff_"+side,knee.lerp(ankle,.13),knee.lerp(ankle,.27),
         [(0,.116,.108),(1,.112,.104)],M["Bronze"],gear_collection)
    limb("Undersleeve_"+side,elbow,elbow.lerp(wrist,.48),
         [(0,.086,.081),(1,.075,.072)],M["Navy"],gear_collection)
    if side=="R":
        hand_axis=(P["blade_tip"]-P["guard"]).normalized();hand_guard=P["guard"]
    else:
        hand_axis=(wrist-elbow).normalized();hand_guard=P["palm_L"]+hand_axis*.096
    grasp("Glove_"+side,hand_guard,hand_axis,wrist,M["BootBrown"],gear_collection,True)

# Real facial surfaces and full-volume stylized hair, not projected image cards.
modeled_head()
verts=[];faces=[]
for row in range(9):
    t=row/8
    cp=P["waist"].lerp(P["neck"]+Vector((0,0,-.11)),t)
    for j in range(9):
        u=j/8*2-1
        verts.append(cp+Vector((u*.150,-.173+.018*u*u,0)))
for row in range(8):
    for j in range(8):
        a=row*9+j;faces.append((a,a+1,a+10,a+9))
front=mesh("Tunic_IvoryFront",verts,faces,M["Ivory"],gear_collection)
solid=front.modifiers.new("FrontThickness","SOLIDIFY");solid.thickness=.008
loft("Scarf_PrimaryMass",[P["neck"]+Vector((0,-.025,z)) for z in [-.09,-.020,.040]],
     [(.245,.20),(.245,.19),(.205,.17)],M["Mustard"],gear_collection)

# Curved cape surface inferred in depth, pinned to the back of the shoulder.
rows=[((548,420),(760,431),(.19,.22)),((441,520),(708,520),(.27,.20)),
      ((342,591),(660,591),(.36,.18)),((269,654),(628,654),(.40,.16)),
      ((309,686),(596,686),(.38,.15)),((314,727),(571,706),(.37,.14)),
      ((349,770),(552,704),(.35,.14)),((378,819),(447,687),(.33,.14))]
verts=[];faces=[];cols=12
for left,right,depth in rows:
    for j in range(cols+1):
        t=j/cols
        pix=(left[0]*(1-t)+right[0]*t,left[1]*(1-t)+right[1]*t)
        verts.append(unproject(pix,depth[0]*(1-t)+depth[1]*t+.06*math.sin(math.pi*t)))
for i in range(len(rows)-1):
    for j in range(cols):
        a=i*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
cape=mesh("Cape_PrimaryMass",verts,faces,M["Mustard"],gear_collection)
solid=cape.modifiers.new("CapeThickness","SOLIDIFY");solid.thickness=.014
# Keep the measured outside edge at this coarse form gate; subdivision
# previously shrank the cape into the arm silhouette.

# Split hanging tunic pieces have real curved depth and thickness. They are
# untextured garment geometry attached at the belt, never image cutouts.
for name,outline,depth,mat in [
    ("Tunic_FrontFlap",[(642,659),(713,669),(745,821),(666,809)],-.14,M["Ivory"]),
    ("Tunic_NearFlap",[(566,672),(623,687),(580,802),(535,779)],-.11,M["Ivory"]),
    ("Teal_HipMass",[(720,656),(775,673),(813,813),(754,840)],-.10,M["Teal"])]:
    verts=[];cols=8
    for row in range(5):
        t=row/4
        left=(outline[0][0]*(1-t)+outline[3][0]*t,outline[0][1]*(1-t)+outline[3][1]*t)
        right=(outline[1][0]*(1-t)+outline[2][0]*t,outline[1][1]*(1-t)+outline[2][1]*t)
        for j in range(cols+1):
            u=j/cols
            pixel=(left[0]*(1-u)+right[0]*u,left[1]*(1-u)+right[1]*u)
            verts.append(unproject(pixel,depth-.025*math.sin(math.pi*u)))
    faces=[]
    for row in range(4):
        for j in range(cols):
            a=row*(cols+1)+j;faces.append((a,a+1,a+cols+2,a+cols+1))
    panel=mesh(name,verts,faces,mat,gear_collection)
    solid=panel.modifiers.new("GarmentThickness","SOLIDIFY");solid.thickness=.016

# A straight blade-axis guide plus provisional hilt. Grip is a later gate.
guard=P["guard"];tip=P["blade_tip"];axis=(tip-guard).normalized()
start=guard-axis*.04
blade=loft("Blade_AxisGuide",[start,guard.lerp(tip,.85),tip],
           [(.045,.009),(.035,.008),(.001,.001)],M["BladeGuide"],gear_collection,4,axis=axis)
limb("Hilt_Provisional",guard-axis*.17,guard,
     [(0,.018,.018),(1,.018,.018)],M["BootBrown"],gear_collection)
cross=Vector((0,1,0)).cross(axis).normalized()
limb("Guard_Provisional",guard-cross*.09,guard+cross*.09,
     [(0,.014,.018),(1,.014,.018)],M["Bronze"],gear_collection)

"""Fitted garment extraction from the new body; no imported assets."""

def fitted_garments():
    obsolete=('Tunic_MainMass','Sleeve_','Undersleeve_','Bracer_','Trouser_','Boot_','Glove_')
    for obj in list(gear_collection.objects):
        if obj.name.startswith(obsolete):bpy.data.objects.remove(obj,do_unlink=True)
    segments=[]
    segments.append(('Torso',P['pelvis']+Vector((0,0,-.12)),P['chest'],.23))
    segments.append(('Torso',P['chest'],P['neck'],.17))
    segments.append(('Head',P['neck'],hc+Vector((0,-.025,.18)),.205))
    for side in ('R','L'):
        for tag,a,b,r in [('UpperArm','shoulder','elbow',.10),('Forearm','elbow','wrist',.079),
                          ('Thigh','hip','knee',.142),('Calf','knee','ankle',.095),('Hand','wrist','palm',.070)]:
            segments.append((tag+'_'+side,P[a+'_'+side],P[b+'_'+side],r))
        foot=ground((535,1161) if side=='R' else (790,1076))
        segments.append(('Foot_'+side,P['ankle_'+side],foot+Vector((0,-.04,.06)),.13))
    def classify(p):
        # Hands use their actual hilt/fist frame. A nearest-limb heuristic alone
        # assigned parts of the palm to trousers and cut holes in glove passes.
        for side in ('R','L'):
            if side=='R':
                axis=(P['blade_tip']-P['guard']).normalized();g=P['guard']
            else:
                axis=(P['wrist_L']-P['elbow_L']).normalized();g=P['palm_L']+axis*.096
            relative=p-(g-axis*.096)
            axial=relative.dot(axis)
            radial=(relative-axis*axial).length
            if abs(axial)<.118 and radial<.099:return 'Glove_'+side
        choices=[]
        for tag,a,b,r in segments:
            if tag=='Torso' and p.z<P['pelvis'].z+.038:continue
            t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared))
            d=(p-a.lerp(b,t)).length/r
            choices.append((d,tag,t))
        d,tag,t=min(choices)
        if tag=='Head':return None
        if tag=='Torso':return 'Tunic'
        region,side=tag.split('_')
        if region=='UpperArm':return 'Sleeve_'+side
        if region=='Forearm':return ('Sleeve_' if t<.3 else 'Bracer_' if t<.90 else 'Glove_')+side
        if region=='Thigh':return 'Trouser_'+side
        if region in ('Calf','Foot'):return 'Boot_'+side
        return 'Glove_'+side
    groups={}
    for poly in body.data.polygons:
        group=classify(poly.center)
        if group:groups.setdefault(group,[]).append(poly)
    for name,polys in groups.items():
        if name.startswith(('Glove','Bracer')):continue
        indices=sorted({v for poly in polys for v in poly.vertices})
        remap={v:i for i,v in enumerate(indices)}
        offset=.014 if name.startswith('Glove') else .017
        verts=[body.data.vertices[i].co+body.data.vertices[i].normal*offset for i in indices]
        faces=[tuple(remap[v] for v in poly.vertices) for poly in polys]
        mat=M['Navy'] if name.startswith(('Tunic','Sleeve')) else M['Bronze'] if name.startswith('Bracer') else M['Olive'] if name.startswith('Trouser') else M['BootBrown']
        obj=mesh('Fitted_'+name,verts,faces,mat,gear_collection)
        obj['fittedFromBody']=True;obj['bodyNormalOffset']=offset
        solid=obj.modifiers.new('GarmentThickness','SOLIDIFY');solid.thickness=.007;solid.offset=-1
        # Root-local source landmarks remain shared by body and every fitted shell.
    for side in ('R','L'):
        elbow,wrist=P['elbow_'+side],P['wrist_'+side]
        limb('Fitted_Bracer_'+side,elbow.lerp(wrist,.23),elbow.lerp(wrist,1.025),
             [(0,.092,.086),(.10,.105,.095),(.28,.104,.091),
              (.55,.083,.075),(.83,.065,.063),(1,.061,.058)],M['Bronze'],gear_collection)
    loft('Navy_Collar',[P['neck']+Vector((0,0,z)) for z in [-.12,-.025,.035]],
         [(.23,.15),(.14,.105),(.11,.09)],M['Navy'],gear_collection)
    # Closed glove volumes use the actual grasp paths. Nearest-limb garment
    # classification can cut wrist holes and label nearby thigh patches as glove.
    for side in ('R','L'):
        wrist=P['wrist_'+side]
        axis=(P['blade_tip']-P['guard']).normalized() if side=='R' else (wrist-P['elbow_L']).normalized()
        guard=P['guard'] if side=='R' else P['palm_L']+axis*.096
        parts=grasp('ClosedGlove_'+side,guard,axis,wrist,M['BootBrown'],gear_collection,True)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in parts:obj.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join()
        glove=bpy.context.active_object;glove.name='Fitted_Glove_'+side
        remesh=glove.modifiers.new('ClosedGloveVolume','REMESH')
        remesh.mode='VOXEL';remesh.voxel_size=.004;remesh.use_smooth_shade=True
        bpy.ops.object.modifier_apply(modifier=remesh.name)
        relax=glove.modifiers.new('GloveSurfaceRelax','SMOOTH');relax.factor=.45;relax.iterations=2
        bpy.ops.object.modifier_apply(modifier=relax.name)
        bm=bmesh.new();bm.from_mesh(glove.data)
        unseen=set(bm.verts);small=[]
        while unseen:
            seed=unseen.pop();stack=[seed];component=[]
            while stack:
                vertex=stack.pop();component.append(vertex)
                for edge in vertex.link_edges:
                    other=edge.other_vert(vertex)
                    if other in unseen:unseen.remove(other);stack.append(other)
            if len(component)<12:small.extend(component)
        if small:bmesh.ops.delete(bm,geom=small,context='VERTS')
        bm.to_mesh(glove.data);bm.free();glove.data.update()
        glove['closedStaticGraspVolume']=True;glove['deformationReady']=False
    print('FITTED_BODY_SURFACE_GROUPS',sorted(groups))


fitted_garments()

"""Raised seams and costume forms belong to the shared 3D source."""

def costume_details():
    for side in ('R','L'):
        obj=bpy.data.objects['Pauldron_'+side]
        points=[v.co.copy() for v in list(obj.data.vertices)[-20:]]
        points.append(points[0])
        line('Pauldron_Rim_'+side,points,.010,M['BronzeLight'],gear_collection)
        bevel=obj.modifiers.new('ForgedEdges','BEVEL');bevel.width=.010;bevel.segments=3
        cuff=bpy.data.objects['KneeCuff_'+side]
        # Costume surface modifiers are geometric finishing, not image overlays.
        bevel=cuff.modifiers.new('CuffEdges','BEVEL');bevel.width=.008;bevel.segments=2
    waist=P['waist']+Vector((.025,-.184,-.008))
    buckle=[waist+Vector((x,0,z)) for x,z in [(-.055,-.036),(.055,-.036),(.055,.036),(-.055,.036),(-.055,-.036)]]
    line('Belt_Buckle',buckle,.008,M['BronzeLight'],gear_collection)
    line('Belt_BucklePin',[waist+Vector((-.033,-.003,0)),waist+Vector((.043,-.003,0))],.004,M['BronzeLight'],gear_collection)
    a=P['chest']+Vector((-.09,-.17,.09));b=P['waist']+Vector((-.09,-.17,0))
    line('Chest_LeatherStrap',[a,a.lerp(b,.35)+Vector((0,-.017,0)),a.lerp(b,.70)+Vector((0,-.012,0)),b],.015,M['BootBrown'],gear_collection)
    for x in (-.150,.150):
        pts=[P['waist'].lerp(P['neck']+Vector((0,0,-.11)),t)+Vector((x,-.175,0)) for t in [0,.25,.5,.75,1]]
        line('Tunic_FrontPiping_'+str(x),pts,.003,M['Bronze'],gear_collection)
    # Hem is lifted slightly toward the camera from the modeled cape surface.
    points=[]
    for left,right,depth in rows[1:]:
        points.append(unproject((left[0]+8,left[1]+2),depth[0]-.012))
    line('Cape_Hem',points,.006,M['Ivory'],gear_collection)
    emblem=[(319,629),(361,613),(357,661),(397,650),(384,705),(414,686),(402,754)]
    line('Cape_LightningStudy',[unproject(p,.36-.015) for p in emblem],.009,M['Ivory'],gear_collection)
    # Every gem has physical thickness and turns with its garment.
    for name,pixel,depth in [('TunicGem',(713,788),-.152),('HipGem',(778,797),-.115)]:
        c=unproject(pixel,depth)
        x=Vector((.035,0,0));z=Vector((0,0,.045));front=Vector((0,-.014,0))
        verts=[c-x,c+z,c+x,c-z,c+front]
        mesh(name,verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],M['BronzeLight'],gear_collection)


costume_details()

head_features=bpy.data.collections.new("HEAD_FEATURES")
scene.collection.children.link(head_features)
feature_names=('EyeWhite_','UpperLid_','LowerLid_','Iris_','Pupil_','EyeCatchlight_','Brow_','Ear_','EarFold_','NoseForm','Mouth')
for obj in list(gear_collection.objects):
    if obj.name.startswith(feature_names):
        gear_collection.objects.unlink(obj);head_features.objects.link(obj)
        obj['sourceRole']='BaseBody_HeadFeatures'
# Registration guides are render-hidden and separately editable.
for name,p in P.items():
    obj=bpy.data.objects.new("GUIDE_"+name,None)
    guide_collection.objects.link(obj);obj.parent=model;obj.location=p
    obj.empty_display_type="SPHERE";obj.empty_display_size=.025;obj.hide_render=True
    obj["observed_reference_x"]=LANDMARKS[name][0]
    obj["observed_reference_y"]=LANDMARKS[name][1]
    obj["depth_is_inferred"]=True

cam_data=bpy.data.cameras.new("CAM_ReferenceFit")
camera=bpy.data.objects.new("CAM_ReferenceFit",cam_data);scene.collection.objects.link(camera)
up=Vector((0,math.sin(ELEV),math.cos(ELEV)))
toward=Vector((0,-math.cos(ELEV),math.sin(ELEV)))
world_pixel=UNIT/K
center=up*(104*world_pixel)
camera.location=center+toward*10
camera.rotation_euler=(center-camera.location).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO";cam_data.ortho_scale=320*world_pixel
scene.camera=camera
for name,location,energy,size in [
    ("Key",(-3,-4,6),450,4),("Fill",(4,-2,4),220,4),("Rim",(0,3,4),300,3)]:
    data=bpy.data.lights.new(name,"AREA");obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj);obj.location=location;data.energy=energy;data.shape="DISK";data.size=size
    obj.rotation_euler=(Vector((0,0,1))-obj.location).to_track_quat("-Z","Y").to_euler()
scene.world=bpy.data.worlds.new("ReferenceFitWorld");scene.world.use_nodes=True
background=next(n for n in scene.world.node_tree.nodes if n.type=="BACKGROUND")
background.inputs["Color"].default_value=(.22,.25,.30,1)
background.inputs["Strength"].default_value=.55
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=320;scene.render.resolution_y=320;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="Standard"
scene["status"]="HEAD_GRIP_REFINEMENT_UNAPPROVED"
scene["grip_approved"]=False
scene["owner_approved"]=False
scene["reference_concept_sha256"]="2fa0145d82ae3eabd6c04aadbf89d485b2bf0b0db3c228d278ca95b7f463253b"
scene["no_rejected_source_imported"]=True
bpy.context.view_layer.update()
max_error=0
for name,p in P.items():
    cam_point=camera.matrix_world.inverted() @ (model.matrix_world@p)
    got=Vector(((.5+cam_point.x/cam_data.ortho_scale)*320,
                (.5-cam_point.y/cam_data.ortho_scale)*320))
    ref=LANDMARKS[name]
    expected=Vector((160+(ref[0]-ROOT_REF[0])*K,264+(ref[1]-ROOT_REF[1])*K))
    max_error=max(max_error,(got-expected).length)
print("REFERENCE_LANDMARK_REGISTRATION_ERROR_PX",max_error)
print("BODY_BLOCKOUT_VERTICES",len(body.data.vertices))
print("NOT_FINAL_TOPOLOGY_NOT_SKINNED_NOT_APPROVED")
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/painted-source.blend")
scene.render.filepath=OUT+"/renders/SE.png"
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=OUT+"/renders/SE-large.png"
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
for label, angle in [("S",0),("SW",-45),("W",-90),("NW",-135),("N",-180),("NE",-225),("E",-270)]:
    model.rotation_euler.z=math.radians(angle)
    scene.render.filepath=OUT+"/renders/"+label+".png"
    bpy.ops.render.render(write_still=True)
model.rotation_euler.z=YAW
for obj in gear_collection.objects:
    obj.hide_render=True
scene.render.filepath=OUT+"/renders/body-only-SE.png"
bpy.ops.render.render(write_still=True)
for obj in gear_collection.objects:
    obj.hide_render=False
scene.render.filepath=OUT+"/renders/SE.png"
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/painted-source.blend")
print("REFERENCE_FIT_BLOCKOUT_SAVED")
