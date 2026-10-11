"""Prepare shared-rig grip and hairstyle sources without RO pose changes.

Run in Blender on the preserved fantasy-swap-bank.blend. Source geometry is
a painting guide, never automatically approved painted output.
"""
import bpy, bmesh, hashlib, json, math
from array import array
from pathlib import Path
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/characters/swordsman-production/painted-factory-02'
OUT.mkdir(parents=True, exist_ok=True)
s = bpy.context.scene
rig = bpy.data.objects[s['rigObject']]
root = bpy.data.objects[s['rootObject']]
source = Path(bpy.data.filepath)
assert source.name == 'fantasy-swap-bank.blend'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
clips = json.loads(s['clips'])
digits = [d + str(j) + '.R' for d in ['Index','Middle','Ring','Pinky','Thumb'] for j in range(1,4)]
rest_lengths = {b.name:b.length for b in rig.data.bones}


def motion_digest():
    values = []
    for clip in clips:
        rig.animation_data.action = bpy.data.actions[clip['action']]
        for frame in range(1, clip['frames'] + 1):
            s.frame_set(frame)
            for bone in rig.pose.bones:
                if bone.name in digits:
                    continue
                values.append([clip['name'], frame, bone.name,
                               [round(v, 7) for row in bone.matrix for v in row]])
    return hashlib.sha256(json.dumps(values, separators=(',',':')).encode()).hexdigest()


before_motion = motion_digest()
curl = {'Index':[45,75,45], 'Middle':[50,75,40],
        'Ring':[52,75,40], 'Pinky':[58,65,40]}
thumb_targets = [Vector((-.030,.036,-.010)), Vector((-.025,.048,0)),
                 Vector((-.014,.053,-.002))]


def fingers():
    for digit, angles in curl.items():
        for j, angle in enumerate(angles,1):
            rig.pose.bones[digit+str(j)+'.R'].rotation_quaternion = Quaternion((1,0,0), math.radians(-angle))
    bpy.context.view_layer.update()
    # Oppose the thumb across the index finger; do not bend the wrist to close it.
    hand = rig.pose.bones['Hand.R']
    for j, target in enumerate(thumb_targets,1):
        bone = rig.pose.bones['Thumb'+str(j)+'.R']
        desired = hand.matrix @ target - bone.head
        rotation = (bone.tail-bone.head).normalized().rotation_difference(desired.normalized()) @ bone.matrix.to_quaternion()
        matrix = rotation.to_matrix().to_4x4()
        matrix.translation = bone.head
        bone.matrix = matrix
        bpy.context.view_layer.update()


for clip in clips:
    rig.animation_data.action = bpy.data.actions[clip['action']]
    for frame in range(1, clip['frames'] + 1):
        s.frame_set(frame)
        fingers()
        for name in digits:
            rig.pose.bones[name].keyframe_insert(data_path='rotation_quaternion', frame=frame, group=name)
after_motion = motion_digest()
assert before_motion == after_motion, 'Unrelated pose changed while closing fingers'
assert all(abs(rig.data.bones[n].length-v)<1e-7 for n,v in rest_lengths.items())

# Make the glove surfaces legible in the pose guide. This does not paint the
# finished sprite or change the owner's original texture image.
glove = bpy.data.materials.new('PF02_ConnectedBrownGloveGuide')
glove.use_nodes = True
shader = next(n for n in glove.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value = (.10,.047,.025,1)
shader.inputs['Roughness'].default_value = .85
rig.animation_data.action = bpy.data.actions['F01_Idle']
s.frame_set(1)
bpy.context.view_layer.update()
glove_faces = {}
for name in ['F01_BodyOutfit','SWAP_CrimsonOutfit']:
    body = bpy.data.objects[name]
    body.data.materials.append(glove)
    index = len(body.data.materials)-1
    bm = bmesh.new()
    bm.from_mesh(body.data)
    removed = [f for f in bm.faces if all(v.co.x<-.408 and .675<v.co.z<.78 for v in f.verts)]
    removed_count = len(removed)
    bmesh.ops.delete(bm,geom=removed,context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm,geom=loose,context='VERTS')
    deform_weights = bm.verts.layers.deform.verify()

    def ellipsoid(center, radii, orientation, bone_name):
        """A closed glove form bound to its real hand/finger control."""
        bone = rig.pose.bones[bone_name]
        inverse = (bone.matrix @ bone.bone.matrix_local.inverted()).inverted()
        vertices = []
        for ring in range(1,10):
            lat = -math.pi/2 + math.pi*ring/10
            row = []
            for column in range(16):
                lon = math.tau*column/16
                delta = Vector((radii[0]*math.cos(lat)*math.cos(lon),
                                radii[1]*math.cos(lat)*math.sin(lon),radii[2]*math.sin(lat)))
                vertex = bm.verts.new(inverse @ (center + orientation @ delta))
                vertex[deform_weights][body.vertex_groups[bone_name].index] = 1
                row.append(vertex)
            vertices.append(row)
        faces = []
        for a,b in zip(vertices,vertices[1:]):
            faces.extend([bm.faces.new((a[i],a[(i+1)%16],b[(i+1)%16],b[i])) for i in range(16)])
        faces += [bm.faces.new(tuple(reversed(vertices[0]))),bm.faces.new(tuple(vertices[-1]))]
        for f in faces:
            f.material_index = index
            f.smooth = True

    hand = rig.pose.bones['Hand.R']
    ellipsoid(hand.matrix @ Vector((.002,.026,-.002)),(.031,.026,.012),hand.matrix.to_3x3(),'Hand.R')
    ellipsoid(hand.matrix @ Vector((0,.001,0)),(.012,.013,.010),hand.matrix.to_3x3(),'Hand.R')
    for digit in ['Index','Middle','Ring','Pinky','Thumb']:
        for j in range(1,4):
            bone = rig.pose.bones[digit+str(j)+'.R']
            radius = (.0058 if digit=='Thumb' else .0050 if digit=='Pinky' else .0062)
            center = (bone.head+bone.tail)/2
            ellipsoid(center,(radius,bone.length/2+radius*.55,radius),bone.matrix.to_3x3(),bone.name)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()
    glove_faces[name] = {'removedSourceFaces':removed_count,'newDigitControls':15,
                        'palmBoundTo':'Hand.R','surface':'Closed overlapping glove forms; visual guide pending.'}

# A distinct shortened chestnut hairstyle shares the same complete head and
# Head bone. Face/neck vertices outside the hair selection are not moved.
head = bpy.data.objects['F01_HeadHair']
alt = head.copy()
alt.data = head.data.copy()
alt.name = 'PF02_SilverCropHeadHair'
s.collection.objects.link(alt)
alt['spriteModule'] = 'HeadHair'
alt['swapModule'] = 'HeadHairAlt'
image = next(n.image for n in head.data.materials[0].node_tree.nodes
             if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == 'sRGB')
pixels = array('f',[0]) * len(image.pixels)
image.pixels.foreach_get(pixels)
width, height = image.size
uv = head.data.uv_layers.active
hair_faces = []
for p in head.data.polygons:
    u = sum(uv.data[i].uv.x for i in p.loop_indices) / len(p.loop_indices)
    v = sum(uv.data[i].uv.y for i in p.loop_indices) / len(p.loop_indices)
    at = (min(height-1,max(0,int(v*height)))*width+min(width-1,max(0,int(u*width))))*4
    red,green,blue = pixels[at:at+3]
    center = sum((head.data.vertices[i].co for i in p.vertices), Vector()) / len(p.vertices)
    if p.material_index == 0 and center.z > .892 and blue > green*.95 and blue > red*.85:
        hair_faces.append(p.index)
selected = {i for p in hair_faces for i in alt.data.polygons[p].vertices}
assert len(selected)>100, 'No reliable hair geometry selected'
pivot = Vector((0,.082,.947))
for index in selected:
    vertex = alt.data.vertices[index]
    delta = vertex.co-pivot
    vertex.co = pivot + Vector((delta.x*.92,delta.y*.82,delta.z*.74))
alt.data.update()
assert any((a.co-b.co).length>.005 for a,b in zip(head.data.vertices,alt.data.vertices))

def appearance(hair_variant='silver', outfit='original', weapon='original', headgear=False, cape=True):
    for o in s.objects:
        if o.type != 'MESH' or o.get('referenceOnly'):
            continue
        module = o.get('swapModule')
        if module:
            o.hide_render = not {'BodyAlt':outfit=='crimson','WeaponAlt':weapon=='short',
                                 'Headgear':headgear,'Offhand':False,
                                 'HeadHairAlt':hair_variant=='cropped'}.get(module,False)
        elif o.get('spriteModule') == 'BodyOutfit':
            o.hide_render = outfit!='original'
        elif o.get('spriteModule') == 'HeadHair':
            o.hide_render = hair_variant!='silver'
        elif o.get('spriteModule') == 'Weapon':
            o.hide_render = weapon!='original'
        elif o.get('spriteModule') == 'Cape':
            o.hide_render = not cape

rig.animation_data.action = bpy.data.actions['F01_Idle']
s.frame_set(1)
appearance()
root.rotation_euler.z = math.radians(45)
native = ROOT / '.character-tools/checkpoints/painted-factory-02-master.blend'
s['paintedFactoryStatus'] = 'SOURCE_AND_SWAP_GUIDES_NOT_APPROVED_PAINTED_OUTPUT'
s['ownerApproved'] = False
s['runtimeAdmitted'] = False
s['poseAuthority'] = 'Restored pre-RO source actions; no RO pose targets or motion curves.'
s.render.resolution_x = s.render.resolution_y = 320
bpy.ops.wm.save_as_mainfile(filepath=str(native))
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
report = {'sourceBankSHA256':source_sha,'native':native.relative_to(ROOT).as_posix(),
          'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),
          'bodyMotionSHA256Before':before_motion,'bodyMotionSHA256After':after_motion,
          'unrelatedMotionUnchanged':True,'boneLengthsUnchanged':True,
          'gripScope':'Finger curl and thumb opposition only; no wrist/arm/body pose edits.',
          'gloveGuideFaces':glove_faces,'hairGeometryVerticesChanged':len(selected),
          'hairFacePolygons':len(hair_faces),'hairstyles':['silver','cropped-silver'],
          'outfits':['original','crimson-cuirass'],'weapons':['original','short','none'],
          'headgear':['none','circlet'],'cape':['original','none'],
          'actions':[c['name'] for c in clips],
          'sourcePoseSetsAvailable':sum(c['frames'] for c in clips)*8,
          'paintedOutputApproved':False,'paintedAnimationCoverageEstablished':False,
          'runtimeSwapProofComplete':False,'ownerApproved':False}
(OUT/'master-source.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

# Critical-view contact reviews render native geometry, not a corrective PNG.
contact = json.loads(s['swordContact'])
camera_location = s.camera.location.copy()
camera_rotation = s.camera.rotation_euler.copy()
span = s.camera.data.ortho_scale
for direction,yaw in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
    root.rotation_euler.z = math.radians(yaw)
    bpy.context.view_layer.update()
    for variant in ['silver','cropped']:
        appearance(variant)
        s.camera.location = camera_location
        s.camera.rotation_euler = camera_rotation
        s.camera.data.ortho_scale = span
        s.render.resolution_x = s.render.resolution_y = 640
        s.render.filepath = str(OUT/f'guide-{variant}-{direction}.png')
        bpy.ops.render.render(write_still=True)
    appearance()
    hand = rig.pose.bones['Hand.R']
    center = rig.matrix_world @ (hand.matrix @ hand.bone.matrix_local.inverted() @ Vector(contact['centerModel']))
    s.camera.data.ortho_scale = .165
    s.camera.location = center - (camera_rotation.to_matrix() @ Vector((0,0,-1))) * 5
    s.render.resolution_x = s.render.resolution_y = 960
    s.render.filepath = str(OUT/f'grip-{direction}.png')
    bpy.ops.render.render(write_still=True)
    print('PAINTED_FACTORY_MASTER_GUIDE '+direction,flush=True)
print('PAINTED_FACTORY_MASTER_READY_FOR_VISUAL_INSPECTION',flush=True)
