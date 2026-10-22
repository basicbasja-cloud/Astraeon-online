"""Certify subpixel RPG pose holds from actual rig/mesh evaluation, not paint bboxes.

Run under Blender. The certificate never changes event timing or source assets.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from kaykit_motion_adapter import KayKitMotionAdapter


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--from-index',type=int,required=True);p.add_argument('--to-index',type=int,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime-size',type=int,default=240);p.add_argument('--threshold-px',type=float,default=.5);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not 0<a.threshold_px<=.5:raise ValueError('Pose hold threshold must not exceed half a runtime pixel')
    manifest=json.loads((a.guide/'manifest.json').read_text());job=manifest['job'];frames=next(iter(manifest['views'].values()))['frames'];ra,rb=frames[a.from_index],frames[a.to_index]
    source_path=Path(job['source_file']).resolve();target_path=Path(job['retarget_to']).resolve()
    if sha(source_path)!=job['source_sha256']:raise ValueError('Motion source digest differs')
    if job.get('retarget_to_sha256')and sha(target_path)!=job['retarget_to_sha256']:raise ValueError('Human rig digest differs')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source_path));source=next(o for o in bpy.data.objects if o.type=='ARMATURE');old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(target_path));target=next(o for o in bpy.data.objects if o not in old and o.type=='ARMATURE')
    meshes=[o for o in bpy.data.objects if o not in old and o.type=='MESH'and any(m.type=='ARMATURE'and m.object==target for m in o.modifiers)]
    if not meshes:raise ValueError('Missing weighted human mesh')
    for actor in [source,target]:
        for track in actor.animation_data.nla_tracks:track.mute=True
    adapter=KayKitMotionAdapter(source,target,archery_contact=job['archery_contact_adapter'])
    def snapshot(record):
        name=record['action'];frame=record['source_frame']
        if 'transition_from'in record:
            if record['transition_weight']==0:name=record['transition_from'];frame=record['transition_frame']
            elif record['transition_weight']!=1:raise ValueError('Interior joint blends require a dedicated evaluator')
        chosen=bpy.data.actions.get(name+'_'+source.name)
        if chosen is None:raise ValueError('Missing source action '+name)
        for bone in source.pose.bones:bone.matrix_basis=Matrix.Identity(4)
        source.animation_data.action=chosen
        if hasattr(source.animation_data,'action_slot')and chosen.slots:source.animation_data.action_slot=chosen.slots[0]
        bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update();adapter.apply();target.matrix_world.translation-=Vector(record['actor_root_delta']);bpy.context.view_layer.update()
        names={'root':'root','head':'head','pelvis':'pelvis','hand_r':'hand_r','hand_l':'hand_l','foot_r':'foot_r','foot_l':'foot_l'}
        reference_error=max((target.matrix_world@target.pose.bones[bone].head-Vector(record['world_landmarks'][key])).length for key,bone in names.items())
        if reference_error>1e-4:raise ValueError('Fresh evaluation differs from retained guide geometry')
        bones={b.name:{'head':target.matrix_world@b.head,'tail':target.matrix_world@b.tail,'matrix':target.matrix_world@b.matrix,'q':(target.matrix_world@b.matrix).to_quaternion()}for b in target.pose.bones};vertices={};depsgraph=bpy.context.evaluated_depsgraph_get()
        for obj in meshes:
            evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh();vertices[obj.name]=[evaluated.matrix_world@v.co for v in mesh.vertices];evaluated.to_mesh_clear()
        return bones,vertices,reference_error
    ba,va,ea=snapshot(ra);bb,vb,eb=snapshot(rb)
    endpoint=max((ba[n][k]-bb[n][k]).length for n in ba for k in ['head','tail']);angle=lambda x,y:2*math.acos(min(1,abs(x.dot(y))));max_angle=max(angle(ba[n]['q'],bb[n]['q'])for n in ba);hand_angle=max(angle(ba[n]['q'],bb[n]['q'])for n in ['hand_l','hand_r'])
    if set(va)!=set(vb)or any(len(va[n])!=len(vb[n])for n in va):raise ValueError('Mesh topology changed')
    vertex=max((x-y).length for n in va for x,y in zip(va[n],vb[n]));matrix_error=max(abs(ba[n]['matrix'][r][c]-bb[n]['matrix'][r][c])for n in ba for r in range(4)for c in range(4));ppm=a.runtime_size/job['ortho_scale'];body_bound=max(endpoint,vertex)*ppm;weapon_bound=(endpoint+.6*hand_angle)*ppm
    control=max(math.dist(ra['weapon_guide'][k],rb['weapon_guide'][k])*a.runtime_size/job['resolution']for k in ['grip','string_nock','arrow_tip']);same_arrow=ra['weapon_guide']['arrow_visible']==rb['weapon_guide']['arrow_visible'];exact=matrix_error<1e-5;same_phase=ra['action']==rb['action']
    roles=[]
    if body_bound<=a.threshold_px and math.degrees(max_angle)<=5 and(same_phase or exact):roles=['HeadHair','BodyCostume','WeaponHandOccluder','BackAccessory']
    if roles and same_arrow and weapon_bound<=a.threshold_px and control<=a.threshold_px:roles.append('Weapon')
    result={'status':'ELIGIBLE_FOR_SUBPIXEL_RPG_POSE_HOLD'if roles else'REJECTED_FOR_POSE_HOLD','guide_job':job['id'],'guide_manifest_sha256':sha(a.guide/'manifest.json'),'from_index':a.from_index,'to_index':a.to_index,'source_records':[{'action':r['action'],'source_frame':r['source_frame']}for r in [ra,rb]],'source_sha256':sha(source_path),'human_rig_sha256':sha(target_path),'adapter_sha256':sha(Path(__file__).with_name('kaykit_motion_adapter.py')),'certifier_sha256':sha(__file__),'runtime_size':a.runtime_size,'threshold_runtime_px':a.threshold_px,'bones_checked':len(ba),'mesh_vertices_checked':sum(map(len,va.values())),'source_replay_error_m':max(ea,eb),'max_bone_endpoint_delta_m':endpoint,'max_weighted_mesh_vertex_delta_m':vertex,'max_bone_rotation_degrees':math.degrees(max_angle),'max_matrix_component_difference':matrix_error,'exact_pose_within_numeric_tolerance':exact,'body_motion_runtime_px_upper_bound':body_bound,'weapon_sweep_runtime_px_upper_bound':weapon_bound,'weapon_control_runtime_px_difference':control,'same_held_arrow_state':same_arrow,'eligible_roles':roles,'event_timing_changed':False,'owner_approved':False,'runtime_admitted':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('POSE_HOLD_CERTIFICATE '+json.dumps(result),flush=True)

if __name__=='__main__':main()
