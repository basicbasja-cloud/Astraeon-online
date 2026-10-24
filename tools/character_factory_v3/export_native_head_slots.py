"""Export verified neck pivots and camera-relative native head orientation.

Run in Blender. This does not render or modify painted artwork. Projected joint
locations do not imply that the corresponding hand/skin surface is visible.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);path=a.guide/'manifest.json';guide=json.loads(path.read_text());job=guide['job']
    if job.get('retarget_to')or job.get('floor_sit_adapter')or job.get('staff_arm_reference')or job.get('entry_transition')or job.get('exit_transition'):raise ValueError('Use a native unadapted source capture')
    source=Path(job['source_file']).resolve()
    if sha(source)!=job['source_sha256']:raise ValueError('Source file changed')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));scene=bpy.context.scene
    rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
    for track in rig.animation_data.nla_tracks:track.mute=True
    original=rig.matrix_world.copy();scene.render.resolution_x=scene.render.resolution_y=job['resolution'];scene.render.resolution_percentage=100
    camera_data=bpy.data.cameras.new('VerifiedSocketCamera');camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
    rows=[];maximum=0.;author_size=768;scale=author_size/job['resolution']
    for direction,view in guide['views'].items():
        camera.location=view['camera']['location'];camera.rotation_euler=view['camera']['rotation'];camera_data.ortho_scale=view['camera']['ortho_scale']
        for i,record in enumerate(view['frames']):
            candidates=[action for action in bpy.data.actions if action.name==record['action']or action.name.startswith(record['action']+'_')]
            exact=bpy.data.actions.get(record['action']+'_'+rig.name)
            action=exact if exact else candidates[0]if len(candidates)==1 else None
            if action is None:raise ValueError('Ambiguous native action')
            if rig.animation_data.action!=action:
                for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
            rig.animation_data.action=action
            if hasattr(rig.animation_data,'action_slot')and action.slots:rig.animation_data.action_slot=action.slots[0]
            f=record['source_frame'];scene.frame_set(math.floor(f),subframe=f%1);rig.matrix_world=original.copy();rig.matrix_world.translation-=Vector(record['actor_root_delta']);bpy.context.view_layer.update()
            def project(name):
                world=rig.matrix_world@rig.pose.bones[name].head;q=world_to_camera_view(scene,camera,world);return [q.x*author_size,(1-q.y)*author_size]
            error=0.
            for name,expected in record['landmarks'].items():
                actual=project(name)
                error=max(error,max(abs(x-y*scale)for x,y in zip(actual,expected)))
            if error>1e-3:raise ValueError('Re-evaluated native socket pose differs from source capture')
            maximum=max(maximum,error)
            sockets={name:project(bone)for name,bone in [('head','head'),('hand_R','hand_r'),('hand_L','hand_l'),('back','spine_02'),('waist','pelvis')]}
            sockets['neck']=project('neck_01');sockets['root']=[384,550.4];sockets['weapon_grip']=[v*scale for v in record['weapon_guide']['grip']]
            rest=rig.data.bones['head'].matrix_local.to_quaternion()
            posed=(rig.matrix_world@rig.pose.bones['head'].matrix).to_quaternion()
            face=posed@(rest.inverted()@Vector((0,-1,0)));up=posed@(rest.inverted()@Vector((0,0,1)))
            axes=camera.rotation_euler.to_matrix();right=axes.col[0];vertical=axes.col[1];toward=axes.col[2]
            face_camera=[face.dot(axis)for axis in [right,vertical,toward]]
            up_camera=[up.dot(axis)for axis in [right,vertical,toward]]
            orientation={'face_camera':face_camera,'up_camera':up_camera,
                         'yaw_degrees':math.degrees(math.atan2(face_camera[0],face_camera[2])),
                         'pitch_degrees':math.degrees(math.atan2(face_camera[1],math.hypot(face_camera[0],face_camera[2]))),
                         'roll_degrees':math.degrees(math.atan2(up_camera[0],up_camera[1]))}
            rows.append({'head_orientation':orientation,'direction':direction,'index':i,'source_action':record['action'],'source_frame':f,'sockets':sockets,'verified_landmark_max_error_author_px':error})
    result={'status':'NATIVE_HEAD_SLOTS_VERIFIED','guide_job':job['id'],'guide_manifest_sha256':sha(path),'source_sha256':sha(source),'implementation_sha256':sha(__file__),'frames':rows,'maximum_landmark_error_author_px':maximum,'visibility_inferred_from_joint_projection':False,'painted_assets_modified':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'frames':len(rows),'maximum_landmark_error_author_px':maximum}))


if __name__=='__main__':main()
