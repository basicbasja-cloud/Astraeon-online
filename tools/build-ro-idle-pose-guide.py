"""Create an original, RO-referenced idle pose guide; do not replace baked art."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Quaternion, Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/characters/swordsman-production/paint-finish-01'
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / '.character-tools/checkpoints/fantasy-base-01-native.blend'
source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
assert Path(bpy.data.filepath).resolve() == source.resolve()
s = bpy.context.scene
rig = bpy.data.objects[s['rigObject']]
root = bpy.data.objects[s['rootObject']]
root.rotation_euler.z = 0
rig.animation_data.action = bpy.data.actions['F01_Idle']
s.frame_set(1)
action = bpy.data.actions.new('RO_Referenced_Idle_Pose_01')
action.use_fake_user = True
rig.animation_data.action = action
rig.pose.bones['Hips'].rotation_quaternion = Quaternion()
rig.pose.bones['Hips'].location = (0, 0, 0)
bpy.context.view_layer.update()

def aim(name, direction):
    """Rotate a bone in armature space, keeping its actual length and joints."""
    p = rig.pose.bones[name]
    correction = (p.tail-p.head).normalized().rotation_difference(Vector(direction).normalized())
    rotation = correction @ p.matrix.to_quaternion()
    matrix = rotation.to_matrix().to_4x4()
    matrix.translation = p.head.copy()
    p.matrix = matrix
    bpy.context.view_layer.update()

# Original joint targets chosen by observation of RO's compact idle silhouette.
# No proprietary motion coordinates, animation curves, sprite pixels or meshes
# enter this file or its outputs. Ready/attack poses will need separate guides.
targets = {
    'Thigh.R': (-.035, .12, -.992), 'Shin.R': (0, -.14, -.99),
    'Thigh.L': (.035, -.03, -.999), 'Shin.L': (0, .06, -.998),
    'Foot.R': (-.05, -1, -.376), 'Foot.L': (.05, -1, -.376),
    'UpperArm.R': (-.035, -.045, -.998),
    'Forearm.R': (.12, -.89, -.44),
    'UpperArm.L': (.055, -.025, -.998),
    'Forearm.L': (.05, -.27, -.962),
}
for name, direction in targets.items():
    aim(name, direction)
rig.pose.bones['Hand.R'].rotation_quaternion = Quaternion()
bpy.context.view_layer.update()
contact = json.loads(s['swordContact'])
axis = Vector(contact['axisModel'])
fore = rig.pose.bones['Forearm.R']
hand = rig.pose.bones['Hand.R']
longitudinal = (fore.tail-fore.head).normalized()
current = ((hand.matrix @ hand.bone.matrix_local.inverted()).to_3x3() @ axis).normalized()
wanted = Vector((-.04, -.02, -1))
wanted = (wanted-longitudinal*wanted.dot(longitudinal)).normalized()
twist = math.atan2(longitudinal.dot(current.cross(wanted)), current.dot(wanted))
fore.rotation_quaternion = fore.rotation_quaternion @ Quaternion((0,1,0), twist)
bpy.context.view_layer.update()

# Put actual deformed soles on the common floor, rather than shifting PNGs.
dg = bpy.context.evaluated_depsgraph_get()
body = bpy.data.objects['F01_BodyOutfit'].evaluated_get(dg)
mesh = body.to_mesh()
minimum = min(v.co.z for v in mesh.vertices)
body.to_mesh_clear()
hips = rig.pose.bones['Hips']
hips.location = hips.bone.matrix_local.to_3x3().inverted() @ Vector((0,0,-minimum))
bpy.context.view_layer.update()
for p in rig.pose.bones:
    p.keyframe_insert(data_path='rotation_quaternion', frame=1, group=p.name)
    p.keyframe_insert(data_path='location', frame=1, group=p.name)
s.frame_start = s.frame_end = 1
s.frame_set(1)
hand = rig.pose.bones['Hand.R']
deform = hand.matrix @ hand.bone.matrix_local.inverted()
weapon_axis = (deform.to_3x3() @ axis).normalized()
forearm_axis = (rig.pose.bones['Forearm.R'].tail-rig.pose.bones['Forearm.R'].head).normalized()
grip_angle = math.degrees(weapon_axis.angle(forearm_axis))
assert abs(grip_angle-90) < .05
assert hand.rotation_quaternion.angle < 1e-5
assert all(abs(v-1)<1e-5 for p in rig.pose.bones for v in p.scale)
s['ownerApproved'] = False
s['runtimeAdmitted'] = False
s['poseGuideStatus'] = 'RO_REFERENCED_IDLE_TRIAL_REQUIRES_VISUAL_REVIEW'
native = ROOT / '.character-tools/checkpoints/ro-idle-pose-guide-01.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native))
views = {}
joint_names = ['Hips','Head','UpperArm.R','Forearm.R','Hand.R',
               'UpperArm.L','Forearm.L','Hand.L','Thigh.R','Shin.R','Foot.R',
               'Thigh.L','Shin.L','Foot.L']
for direction, yaw in [('S',0),('SW',-45),('W',-90),('NW',-135),
                       ('N',-180),('NE',-225),('E',-270),('SE',45)]:
    root.rotation_euler.z = math.radians(yaw)
    bpy.context.view_layer.update()
    size = 1280 if direction == 'SE' else 640
    s.render.resolution_x = s.render.resolution_y = size
    s.render.filepath = str(OUT/f'ro-idle-guide-{direction}.png')
    joints = {}
    def pixel(point):
        v = world_to_camera_view(s, s.camera, rig.matrix_world @ point)
        return [v.x*size, (1-v.y)*size]
    for name in joint_names:
        p = rig.pose.bones[name]
        joints[name] = {'head':pixel(p.head), 'tail':pixel(p.tail),
                        'length':p.length, 'restLength':p.bone.length}
        assert abs(p.length-p.bone.length) < 1e-5
    hilt = deform @ Vector(contact['centerModel'])
    sword_line = [pixel(hilt), pixel(hilt+weapon_axis*.24)]
    views[direction] = {'yawDegrees':yaw,'canvas':[size,size],
                        'joints':joints,'swordAxis':sword_line}
    bpy.ops.render.render(write_still=True)
    print('RO_IDLE_GUIDE_RENDERED '+direction, flush=True)
root.rotation_euler.z = math.radians(45)
s.render.resolution_x = s.render.resolution_y = 320
bpy.ops.wm.save_as_mainfile(filepath=str(native))
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
report = {'sourceNativeSHA256':source_sha,'guideNative':native.relative_to(ROOT).as_posix(),
          'guideNativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),
          'sourceNativeUnchanged':True,'ownerApproved':False,'runtimeAdmitted':False,
          'scope':'One original compact idle pose referenced to RO silhouettes; not a traced animation or full action set.',
          'referenceURL':'https://ragnarokonline.gungho.jp/gameguide/character/swordman/swordman.html',
          'poseTargets':targets,'gripForearmDegrees':grip_angle,'neutralWrist':True,
          'directions':views,'paintedRegistrationEstablished':False}
(OUT/'pose-guide.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('RO_IDLE_GUIDE_COMPLETE', flush=True)
