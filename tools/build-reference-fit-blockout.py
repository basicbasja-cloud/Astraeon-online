"""Fresh reference-calibrated volume blockout, executed through Blender MCP.

No source mesh is loaded. This is a proportion/pose gate, not final rig topology.
"""
import bpy
import math
from mathutils import Vector, Matrix

# Constants are image-space observations from the unchanged approved concept.
ROOT_REF = (645, 1155)
K = 176 / 1113
UNIT = .0017
ELEV = math.radians(25)
YAW = math.radians(45)
OUT = "C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/reference-fit-01"
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
assert bpy.context.scene.name in {"ASTRAEON_MCP_DISPOSABLE_CONNECTION_TEST", "ASTRAEON_REFERENCE_FIT_01"}
scene = bpy.context.scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name.startswith(("BODY_BLOCKOUT", "MAJOR_FORM_BLOCKOUT", "LANDMARK_GUIDES")) and not col.objects:
        bpy.data.collections.remove(col)
scene.name = "ASTRAEON_REFERENCE_FIT_01"
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
          "shoulder_R": .00,"elbow_R": .015,"wrist_R": .025,"palm_R": -.015,
          "shoulder_L": .00,"elbow_L": -.02,"wrist_L": -.035,"palm_L": -.045,
          "hip_R": .04,"knee_R": .05,"ankle_R": .14,
          "hip_L": -.06,"knee_L": .06,"ankle_L": .12,
          "guard": -.025,"blade_tip": -.15}
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
    "WarmClay": (.54,.40,.32), "HairMass": (.57,.51,.64),
    "Navy": (.055,.065,.085), "Ivory": (.67,.59,.43),
    "Bronze": (.36,.20,.065), "Mustard": (.78,.49,.11),
    "Teal": (.035,.19,.22), "Olive": (.12,.14,.085),
    "BootBrown": (.16,.075,.038), "BladeGuide": (.42,.47,.52),
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
    return mesh(name,verts,faces,mat,col)


def limb(name,a,b,profile,mat,col):
    centers=[a.lerp(b,t) for t,rx,ry in profile]
    return loft(name,centers,[(rx,ry) for t,rx,ry in profile],mat,col,axis=b-a)


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
body_parts.append(loft("SkullVolume",[hc+Vector((.035,-.075,z)) for z in [-.225,-.185,-.07,.10,.205,.24]],
    [(.065,.06),(.12,.10),(.185,.15),(.205,.175),(.14,.13),(.025,.025)],M["WarmClay"],body_collection,32))
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
    body_parts.append(limb("HandMass_"+side,wrist,palm+Vector((0,0,-.035)),
        [(0,.05,.048),(.4,.07,.059),(.85,.062,.058),(1,.032,.035)],M["WarmClay"],body_collection))
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
remesh.mode="VOXEL";remesh.voxel_size=.011;remesh.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth=body.modifiers.new("BlockoutSurfaceRelax","SMOOTH")
smooth.factor=.65;smooth.iterations=4
bpy.ops.object.modifier_apply(modifier=smooth.name)
body["final_deformation_topology"]=False

# Removable primary costume masses for a fair dressed silhouette comparison.
loft("Tunic_MainMass",[P["waist"]+Vector((0,-.015,-.055)),P["waist"]+Vector((0,-.015,0)),
                       P["chest"]+Vector((0,-.015,0)),P["neck"]+Vector((0,-.015,-.09))],
     [(.205,.132),(.205,.13),(.27,.155),(.24,.14)],M["Ivory"],gear_collection)
loft("Belt_Mass",[P["waist"]+Vector((0,0,z)) for z in [-.04,.025]],
     [(.225,.145),(.225,.145)],M["BootBrown"],gear_collection)
for side in ("R","L"):
    shoulder,elbow,wrist,hip,knee,ankle=[P[n+"_"+side] for n in ("shoulder","elbow","wrist","hip","knee","ankle")]
    limb("Sleeve_"+side,shoulder,elbow,[(0,.105,.095),(.4,.108,.1),(1,.085,.08)],M["Navy"],gear_collection)
    limb("Bracer_"+side,elbow.lerp(wrist,.28),wrist,
         [(0,.105,.09),(.45,.092,.08),(1,.064,.06)],M["Bronze"],gear_collection)
    limb("Pauldron_"+side,shoulder+Vector((0,0,.055)),shoulder.lerp(elbow,.32),
         [(0,.075,.075),(.25,.135,.12),(1,.13,.115)],M["Bronze"],gear_collection)
    limb("Trouser_"+side,hip,knee,[(0,.14,.13),(.3,.145,.13),(.85,.117,.108),(1,.09,.09)],M["Olive"],gear_collection)
    foot=ground((535,1161) if side=="R" else (790,1076))
    boot_top=knee.lerp(ankle,.25)
    loft("Boot_"+side,[foot+Vector((0,-.035,.012)),foot+Vector((0,-.06,.085)),ankle+Vector((0,-.01,.07)),boot_top],
         [(.072,.155),(.075,.155),(.069,.082),(.103,.096)],M["BootBrown"],gear_collection)
    limb("KneeCuff_"+side,knee.lerp(ankle,.13),knee.lerp(ankle,.27),
         [(0,.116,.108),(1,.112,.104)],M["Bronze"],gear_collection)
    limb("Glove_"+side,wrist,P["palm_"+side]+Vector((0,0,-.03)),
         [(0,.057,.05),(.4,.077,.066),(.8,.069,.063),(1,.036,.039)],M["BootBrown"],gear_collection)

# Hair is one broad volume, deliberately without identity/detail claims.
hair=loft("Hair_PrimaryMass",[hc+Vector((-.015,.005,z)) for z in [-.04,.03,.19,.31,.38]],
     [(.175,.145),(.285,.235),(.285,.235),(.195,.17),(.045,.045)],M["HairMass"],gear_collection,40)
for v in hair.data.vertices:
    a=math.atan2(v.co.y-hc.y-.005,v.co.x-hc.x+.015)
    ripple=1+.045*math.sin(a*7)+.025*math.cos(a*11)
    v.co.x=hc.x-.015+(v.co.x-hc.x+.015)*ripple
    v.co.y=hc.y+.005+(v.co.y-hc.y-.005)*ripple
    v.co.z+=.012*math.sin(a*5)
loft("Scarf_PrimaryMass",[P["neck"]+Vector((0,-.02,z)) for z in [-.09,-.045,.018]],
     [(.19,.14),(.205,.145),(.155,.115)],M["Mustard"],gear_collection)

# Curved cape surface inferred in depth, pinned to the back of the shoulder.
rows=[((548,420),(760,431),.19),((441,520),(708,520),.27),
      ((342,591),(660,591),.36),((269,654),(628,654),.40),
      ((309,686),(596,686),.38),((314,727),(571,706),.37),
      ((349,770),(552,704),.35),((378,819),(447,687),.33)]
verts=[];faces=[];cols=12
for left,right,depth in rows:
    for j in range(cols+1):
        t=j/cols
        pix=(left[0]*(1-t)+right[0]*t,left[1]*(1-t)+right[1]*t)
        verts.append(unproject(pix,depth+.06*math.sin(math.pi*t)))
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
scene["status"]="PROPORTION_POSE_BLOCKOUT_UNAPPROVED"
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
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/source-blockout.blend")
scene.render.filepath=OUT+"/renders/SE.png"
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=1280;scene.render.resolution_y=1280
scene.render.filepath=OUT+"/renders/SE-large.png"
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=320;scene.render.resolution_y=320
for label, angle in [("W",-90),("NW",-135),("N",-180)]:
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
bpy.ops.wm.save_as_mainfile(filepath=OUT+"/source-blockout.blend")
print("REFERENCE_FIT_BLOCKOUT_SAVED")
