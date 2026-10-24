"""Project captured head rotations and a native head-mesh center for guide kits.

Uses recorded evaluated target-rig controls, so right-arm adaptations and archery
retargeting need not be reenacted. This is guide metadata, not visibility/art QA.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector,Quaternion
from bpy_extras.object_utils import world_to_camera_view


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);manifest=a.guide/'manifest.json';capture=json.loads(manifest.read_text());job=capture['job']
    source=Path(job.get('retarget_to',job['source_file'])).resolve();expected=job.get('retarget_to_sha256',job['source_sha256'])
    if sha(source)!=expected:raise ValueError('Captured target rig source differs')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));scene=bpy.context.scene;rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
    head=rig.data.bones.get('head')
    if head is None:raise ValueError('Expected retained Mesh2Motion target head bone')
    scales=rig.matrix_world.to_scale()
    if max(scales)-min(scales)>1e-6:raise ValueError('Nonuniform target rig scale is unsupported')
    inverse=(rig.matrix_world@head.matrix_local).inverted();points=[]
    for obj in bpy.data.objects:
        if obj.type!='MESH' or not any(m.type=='ARMATURE'and m.object==rig for m in obj.modifiers):continue
        groups={g.index for g in obj.vertex_groups if g.name.startswith('head')}
        if not groups:continue
        for v in obj.data.vertices:
            if any(g.group in groups and g.weight>.75 for g in v.groups):points.append(inverse@(obj.matrix_world@v.co))
    if len(points)<20:raise ValueError('Insufficient native head mesh samples')
    # Leaf weights are rigid descendants of the recorded head control. Reject
    # independent leaf animation or head scale instead of inventing its pose.
    for action in bpy.data.actions:
        for curve in action.fcurves:
            path=curve.data_path
            if 'head_leaf' in path or ('["head"]' in path and path.endswith('.scale')):
                expected_value=1. if path.endswith('.scale') or path.endswith('.rotation_quaternion') and curve.array_index==0 else 0.
                if any(abs(key.co.y-expected_value)>1e-6 for key in curve.keyframe_points):
                    raise ValueError('Independent head-leaf/scale animation requires full pose capture')
    center=sum(points,Vector())/len(points);rest=head.matrix_local.to_quaternion();face_local=rest.inverted()@Vector((0,-1,0));up_local=rest.inverted()@Vector((0,0,1))
    data=bpy.data.cameras.new('CapturedHeadGuideCamera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera;data.type='ORTHO';scene.render.resolution_x=scene.render.resolution_y=job['resolution'];scene.render.resolution_percentage=100
    rows=[];maximum=0.
    for direction,view in capture['views'].items():
        camera.location=view['camera']['location'];camera.rotation_euler=view['camera']['rotation'];data.ortho_scale=view['camera']['ortho_scale'];bpy.context.view_layer.update();axes=camera.rotation_euler.to_matrix();right,up,toward=[axes.col[i]for i in range(3)]
        def project(point):
            q=world_to_camera_view(scene,camera,point);return [q.x*768,(1-q.y)*768]
        for index,record in enumerate(view['frames']):
            position=Vector(record['world_landmarks']['head']);posed=Quaternion(record['bone_rotations']['head']);base=project(position);reference=[v*768/job['resolution']for v in record['landmarks']['head']];error=max(abs(x-y)for x,y in zip(base,reference))
            if error>1e-3:raise ValueError('Captured head projection/camera differs')
            maximum=max(maximum,error);face=posed@face_local;vertical=posed@up_local;f=[face.dot(axis)for axis in [right,up,toward]];v=[vertical.dot(axis)for axis in [right,up,toward]]
            rows.append({'direction':direction,'index':index,'source_action':record['action'],'source_frame':record['source_frame'],'source_head_joint_author_px':base,'head_mesh_center_author_px':project(position+posed@(center*scales[0])),'head_orientation':{'yaw_degrees':math.degrees(math.atan2(f[0],f[2])),'pitch_degrees':math.degrees(math.atan2(f[1],math.hypot(f[0],f[2]))),'roll_degrees':math.degrees(math.atan2(v[0],v[1]))},'captured_head_projection_error_author_px':error})
    result={'status':'CAPTURED_HEAD_GUIDE_MARKERS_NOT_ART_OR_VISIBILITY_APPROVAL','guide_job':job['id'],'guide_manifest_sha256':sha(manifest),'target_rig_sha256':expected,'implementation_sha256':sha(Path(__file__)),'head_mesh_vertices':len(points),'head_mesh_center_bone_local':list(center),'maximum_captured_projection_error_author_px':maximum,'visibility_inferred':False,'source_images_modified':False,'frames':rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'poses':len(rows),'maximum_projection_error':maximum,'head_mesh_vertices':len(points)}))

if __name__=='__main__':main()
