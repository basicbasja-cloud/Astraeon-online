"""Project actual weighted head/hand/feet geometry for paint continuity diagnosis.

Runs in Blender. This does not move or fit any painted pixels and does not grant
visual approval. Every evaluated pose must reproduce the retained source rig.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from kaykit_motion_adapter import KayKitMotionAdapter

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);manifest=json.loads((a.guide/'manifest.json').read_text());job=manifest['job']
    for field,path in [('source_sha256',job['source_file']),('retarget_to_sha256',job['retarget_to'])]:
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=job[field]:raise ValueError('Source digest changed')
    if hashlib.sha256(Path(__file__).with_name('kaykit_motion_adapter.py').read_bytes()).hexdigest()!=job['retarget_implementation_sha256']:raise ValueError('Adapter changed')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path(job['source_file']).resolve()));source=next(o for o in bpy.data.objects if o.type=='ARMATURE');old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(Path(job['retarget_to']).resolve()));target=next(o for o in bpy.data.objects if o not in old and o.type=='ARMATURE');meshes=[o for o in bpy.data.objects if o not in old and o.type=='MESH'and o.name!='Icosphere'and any(m.type=='ARMATURE'and m.object==target for m in o.modifiers)]
    for actor in [source,target]:
        for track in actor.animation_data.nla_tracks:track.mute=True
    adapter=KayKitMotionAdapter(source,target,archery_contact=job['archery_contact_adapter']);scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=job['resolution'];scene.render.resolution_percentage=100
    camera=bpy.data.objects.new('ProjectionAuditCamera',bpy.data.cameras.new('ProjectionAuditCamera'));scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=job['ortho_scale']
    finger_groups={side:{'hand_'+side}|{f'{finger}_{segment}_{side}'for finger in ['thumb','index','middle','ring','pinky']for segment in ['01','02','03','04_leaf']}for side in ['l','r']}
    groups={}
    for obj in meshes:
        names={v.index:v.name for v in obj.vertex_groups};groups[obj.name]={}
        for role,allowed in {'HeadHair':{'head','head_leaf'},'FootL':{'foot_l','ball_l','ball_leaf_l'},'FootR':{'foot_r','ball_r','ball_leaf_r'},'HandL':finger_groups['l'],'HandR':finger_groups['r']}.items():
            groups[obj.name][role]=[v.index for v in obj.data.vertices if sum(g.weight for g in v.groups if names.get(g.group)in allowed)>=.5]
    def evaluate(name,frame):
        chosen=bpy.data.actions.get(name+'_'+source.name)
        if chosen is None:raise ValueError('Missing source action '+name)
        for b in source.pose.bones:b.matrix_basis=Matrix.Identity(4)
        source.animation_data.action=chosen
        if hasattr(source.animation_data,'action_slot')and chosen.slots:source.animation_data.action_slot=chosen.slots[0]
        scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
    first=next(iter(manifest['views'].values()))['frames'];records=[];head_states=[];head_projections={d:[]for d in manifest['views']};foot_states={role:[]for role in ['FootL','FootR']}
    for i,record in enumerate(first):
        evaluate(record['action'],record['source_frame'])
        if 'transition_from'in record:
            end={b.name:b.matrix_basis.copy()for b in source.pose.bones};evaluate(record['transition_from'],record['transition_frame']);start={b.name:b.matrix_basis.copy()for b in source.pose.bones};source.animation_data.action=None;w=record['transition_weight']
            for b in source.pose.bones:
                loc,q,s=start[b.name].decompose();loc2,q2,s2=end[b.name].decompose();b.matrix_basis=Matrix.LocRotScale(loc.lerp(loc2,w),q.slerp(q2,w),s.lerp(s2,w))
            bpy.context.view_layer.update()
        adapter.apply();target.matrix_world.translation-=Vector(record['actor_root_delta']);bpy.context.view_layer.update();error=max((target.matrix_world@target.pose.bones[n].head-Vector(record['world_landmarks'][n])).length for n in ['head','pelvis','foot_l','foot_r','hand_l','hand_r'])
        if error>1e-4:raise ValueError('Mesh audit replay differs from retained pose')
        points={r:[]for r in ['HeadHair','FootL','FootR','HandL','HandR']};depsgraph=bpy.context.evaluated_depsgraph_get()
        for obj in meshes:
            evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh()
            for role,indices in groups[obj.name].items():points[role].extend(evaluated.matrix_world@mesh.vertices[n].co for n in indices)
            evaluated.to_mesh_clear()
        head_states.append((points['HeadHair'],(target.matrix_world@target.pose.bones['head'].matrix).to_quaternion()))
        for role,bone in [('FootL','foot_l'),('FootR','foot_r')]:foot_states[role].append((points[role],(target.matrix_world@target.pose.bones[bone].matrix).to_quaternion()))
        views={}
        for direction,view in manifest['views'].items():
            camera.location=view['camera']['location'];camera.rotation_euler=view['camera']['rotation'];bpy.context.view_layer.update();parts={}
            for role,vertices in points.items():
                if not vertices:raise ValueError('Missing weighted mesh group '+role)
                projected=[world_to_camera_view(scene,camera,v)for v in vertices];xs=[q.x*job['resolution']for q in projected];ys=[(1-q.y)*job['resolution']for q in projected];parts[role]={'projected_bbox':[min(xs),min(ys),max(xs),max(ys)],'projected_vertex_centroid':[sum(xs)/len(xs),sum(ys)/len(ys)],'weighted_vertex_count':len(vertices)}
                if role=='HeadHair':head_projections[direction].append(np.array(list(zip(xs,ys))))
            views[direction]=parts
        records.append({'index':i,'source_action':record['action'],'source_frame':record['source_frame'],'replay_error_m':error,'views':views})
    head_pairs=[]
    for i,(va,qa)in enumerate(head_states):
        for j,(vb,qb)in enumerate(head_states):
            if j<=i:continue
            if len(va)!=len(vb):raise ValueError('Weighted head topology changed')
            bound=max((x-y).length for x,y in zip(va,vb))*240/job['ortho_scale']
            angle=math.degrees(qa.rotation_difference(qb).angle)
            head_pairs.append({'from_index':i,'to_index':j,'weighted_head_vertices':len(va),'runtime_size':240,'head_vertex_delta_runtime_px_upper_bound':bound,'head_rotation_degrees':angle,'subpixel_head_reuse_candidate':bound<=.5 and angle<=5})
    foot_pairs=[]
    for role,states in foot_states.items():
        for i,(va,qa)in enumerate(states):
            for j,(vb,qb)in enumerate(states):
                if j<=i:continue
                if len(va)!=len(vb):raise ValueError('Weighted foot topology changed')
                bound=max((x-y).length for x,y in zip(va,vb))*240/job['ortho_scale'];angle=math.degrees(qa.rotation_difference(qb).angle)
                foot_pairs.append({'role':role,'from_index':i,'to_index':j,'weighted_vertices':len(va),'runtime_size':240,'vertex_delta_runtime_px_upper_bound':bound,'rotation_degrees':angle,'subpixel_foot_reuse_candidate':bound<=.5 and angle<=5})
    rigid_pairs=[]
    for i in range(len(records)):
        for j in range(i+1,len(records)):
            views={}
            for direction,states in head_projections.items():
                source,target=states[i],states[j];ca,cb=source.mean(0),target.mean(0);u,_,vt=np.linalg.svd((source-ca).T@(target-cb));rotation=u@vt
                if np.linalg.det(rotation)<0:u[:,-1]*=-1;rotation=u@vt
                translation=cb-ca@rotation;residual=np.linalg.norm(source@rotation+translation-target,axis=1)*240/job['resolution']
                views[direction]={'row_rotation':rotation.tolist(),'translation_source_px':translation.tolist(),'max_residual_runtime_px':float(residual.max()),'rotation_degrees':math.degrees(math.atan2(rotation[0,1],rotation[0,0]))}
            maximum=max(v['max_residual_runtime_px']for v in views.values())
            rigid_pairs.append({'from_index':i,'to_index':j,'views':views,'max_residual_runtime_px':maximum,'illustrated_envelope_safety_factor':1.5,'eligible_rigid_head_layout_candidate':maximum*1.5<=.5,'scale':1.,'reflection':False,'whole_pose_hold':False,'art_approved':False})
    result={'status':'SOURCE_WEIGHTED_MESH_PROJECTION_DIAGNOSTIC','guide_job':job['id'],'guide_manifest_sha256':hashlib.sha256((a.guide/'manifest.json').read_bytes()).hexdigest(),'per_frame_paint_fitting':False,'source_resolution':job['resolution'],'frames':records,'head_pose_pairs':head_pairs,'foot_pose_pairs':foot_pairs,'rigid_head_pose_pairs':rigid_pairs,'limitations':['Vertex-group bounds include occluded geometry. They are not visible segmentation masks.','Painted hair and boots have their own envelopes; compare movement relative to one fixed calibration, not raw silhouette sizes.','Head reuse candidates only bound the weighted source head mesh; costume-neck seams and the illustrated hair envelope still need review.','Foot reuse candidates exclude the calf, trouser cuff and painted boot envelope. They do not authorize replacing an entire boot or lower body.','Rigid head candidates translate/rotate one separate head layer from source geometry only, without scaling or reflection. They do not authorize moving a complete painted body, nor certify neck seams or hair-depth occlusion.','No painted pixels were changed and no visual approval is granted.']};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('MESH_ALIGNMENT_DIAGNOSTIC '+json.dumps({'frames':len(records),'max_replay_error_m':max(r['replay_error_m']for r in records)}),flush=True)

if __name__=='__main__':main()
