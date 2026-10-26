"""Render and measure every supplied CC0 clip using an independent fixed camera.

Reference mannequin studies only; no project artwork or animation is admitted.
Native time is retained; XY root travel is recorded separately for in-place review.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    import bpy
    import numpy as np
    from PIL import Image,ImageDraw
    from mathutils import Vector,Matrix
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','inventory','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--fps',type=int,default=30)
    p.add_argument('--resolution',type=int,default=768)
    p.add_argument('--only',nargs='+')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    inventory=json.loads(a.inventory.read_text());source_sha=sha(a.source)
    if inventory['source_sha256']!=source_sha:raise ValueError('Motion inventory belongs to another source')
    settings={'source_sha256':source_sha,'fps':a.fps,'resolution':a.resolution,
              'ortho_scale':5.325,'camera_direction':'SE','camera_up_offset':1.15375,
              'root_policy':'Remove XY source-root travel only; retain native Z and yaw.',
              'implementation_sha256':sha(__file__)}
    a.output.mkdir(parents=True,exist_ok=True)
    settings_path=a.output/'capture-settings.json'
    if settings_path.exists()and json.loads(settings_path.read_text())!=settings:raise ValueError('Choose a fresh capture for changed settings')
    settings_path.write_text(json.dumps(settings,indent=2)+'\n')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=a.fps;scene.render.fps_base=1
    bpy.ops.import_scene.gltf(filepath=str(a.source.resolve()))
    rigs=[o for o in scene.objects if o.type=='ARMATURE']
    if len(rigs)!=1:raise ValueError('Expected one shared source armature')
    rig=rigs[0];bones=list(rig.pose.bones);bone_names=[b.name for b in bones]
    if 'root'not in rig.pose.bones:raise ValueError('Missing source root bone')
    for obj in scene.objects:
        if obj.animation_data:
            for track in obj.animation_data.nla_tracks:track.mute=True
    base_world=rig.matrix_world.copy()
    skeleton={'bone_names':bone_names,
              'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,
                        'rest_world_matrix':[list(row)for row in rig.matrix_world@b.matrix_local]}
                       for b in rig.data.bones],
              'source_sha256':source_sha,'final_art':False}
    (a.output/'skeleton.json').write_text(json.dumps(skeleton,indent=2)+'\n')
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=scene.render.resolution_y=a.resolution
    scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.display.render_aa='8';shade=scene.display.shading
    shade.light='STUDIO';shade.color_type='MATERIAL';shade.show_shadows=True;shade.show_cavity=True
    camera_data=bpy.data.cameras.new('LockedSourceCamera');camera_data.type='ORTHO';camera_data.ortho_scale=5.325
    camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
    offset=Vector((6*math.sin(math.pi/4),-6*math.cos(math.pi/4),3.1))
    camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler()
    up=camera.rotation_euler.to_matrix()@Vector((0,1,0));camera.location=up*1.15375+offset;scene.camera=camera
    # Independent geometric source-guide weapon, not a production sword or effect.
    curve=bpy.data.curves.new('DiagnosticBlade','CURVE');curve.dimensions='3D';curve.bevel_depth=.012;curve.bevel_resolution=1
    blade=bpy.data.objects.new(curve.name,curve);scene.collection.objects.link(blade)
    material=bpy.data.materials.new('DiagnosticSteel');material.diffuse_color=(.35,.52,.68,1);curve.materials.append(material)
    bone_shapes={b.custom_shape for b in rig.pose.bones if b.custom_shape}
    source_meshes=[o for o in scene.objects if o.type=='MESH' and o not in bone_shapes and not o.hide_render]
    if len(source_meshes)!=2:raise ValueError('Unexpected visible source character mesh count')
    selected=[r for r in inventory['clips']if r['has_animation']and(not a.only or r['id']in a.only)]
    completed={}
    for receipt in a.output.glob('clips/*/receipt.json'):
        r=json.loads(receipt.read_text())
        if r['source_sha256']!=source_sha:raise ValueError('Mixed source capture cache')
        completed[r['clip']]=r
    def progress():
        records=[completed[name]for name in sorted(completed)]
        report={'status':'ALL_SOURCE_CLIPS_CAPTURED_REQUIRES_VISUAL_REVIEW'if len(completed)==inventory['actual_animations']else'SOURCE_CAPTURE_IN_PROGRESS',
                'source_sha256':source_sha,'declared_clips':inventory['declared_clips'],
                'actual_animations':inventory['actual_animations'],'metadata_without_animation':inventory['metadata_without_animation'],
                'captured_clips':len(completed),'captured_native_time_frames':sum(r['frames']for r in records),
                'clips':records,'final_art_or_motion_approval':False,'runtime_admitted':False}
        (a.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    progress()
    for record in selected:
        name=record['id']
        if name in completed:
            root=a.output/'clips'/name
            if sha(root/'motion.gif')!=completed[name]['gif_sha256']:raise ValueError('Completed source GIF changed')
            continue
        folder=a.output/'clips'/name
        if folder.exists():raise ValueError('Incomplete clip folder retained; choose a fresh capture')
        folder.mkdir(parents=True)
        action=bpy.data.actions.get(name)
        if action is None:
            candidates=[x for x in bpy.data.actions if x.name.startswith(name+'_')]
            if len(candidates)!=1:raise ValueError('Missing or ambiguous source action '+name)
            action=candidates[0]
        rig.animation_data_create();rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
        for bone in rig.pose.bones:
            bone.rotation_mode='QUATERNION';bone.matrix_basis=Matrix.Identity(4)
        duration=record['duration_seconds'];loop=record['loop_hint_from_name']
        count=max(1,math.ceil(duration*a.fps-1e-5))+(0 if loop else 1)
        times=np.minimum(np.arange(count,dtype=float)/a.fps,duration)
        first=float(action.frame_range[0]);rendered=[];matrices=[];root_offsets=[];mesh_floors=[];render_hashes=[];tips=[];edge_frames=[];alpha_boxes=[]
        for index,seconds in enumerate(times):
            rig.matrix_world=base_world.copy()
            frame=first+seconds*a.fps;scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
            world=np.array([[list(row)for row in rig.matrix_world@b.matrix]for b in bones],dtype=np.float32)
            if not np.isfinite(world).all():raise ValueError('Nonfinite source bone matrix')
            matrices.append(world)
            root_position=rig.matrix_world@rig.pose.bones['root'].head
            shift=Vector((-root_position.x,-root_position.y,0));adjusted=base_world.copy();adjusted.translation+=shift
            rig.matrix_world=adjusted;bpy.context.view_layer.update();root_offsets.append(list(shift))
            blade.hide_render=not name.startswith('sword_')
            if not blade.hide_render:
                ix=rig.matrix_world@rig.pose.bones['index_01_r'].head;pk=rig.matrix_world@rig.pose.bones['pinky_01_r'].head
                axis=(ix-pk).normalized();grip=(ix+pk)*.5;tip=grip+axis*.7;tips.append(list(tip))
                curve.splines.clear();spline=curve.splines.new('POLY');spline.points.add(1)
                for point,value in zip(spline.points,[grip-axis*.1,tip]):point.co=(*value,1)
            graph=bpy.context.evaluated_depsgraph_get();floor=math.inf
            for obj in source_meshes:
                evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
                floor=min(floor,min((evaluated.matrix_world@v.co).z for v in mesh.vertices));evaluated.to_mesh_clear()
            mesh_floors.append(floor)
            temp=a.output/'_current-frame.png';scene.render.filepath=str(temp.resolve());bpy.ops.render.render(write_still=True)
            im=Image.open(temp).convert('RGBA');render_hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
            box=im.getchannel('A').getbbox()
            if box is None:raise ValueError('Empty source capture')
            alpha_boxes.append(box)
            if min(box[:2])<2 or box[2]>a.resolution-2 or box[3]>a.resolution-2:edge_frames.append(index)
            bg=Image.new('RGBA',im.size,'#ececea');bg.alpha_composite(im);rendered.append(bg.convert('RGB'))
        world=np.stack(matrices);offsets=np.array(root_offsets,dtype=np.float32)
        np.savez_compressed(folder/'kinematics.npz',time_seconds=times.astype(np.float32),
                            bone_world_matrices=world,render_root_offsets=offsets,bone_names=np.array(bone_names,dtype='U64'))
        positions=world[:,:,:3,3].copy();root_index=bone_names.index('root')
        positions[:,:,0]-=world[:,root_index,0,3,None];positions[:,:,1]-=world[:,root_index,1,3,None]
        adjacent=np.sqrt(np.mean(np.sum(np.diff(positions,axis=0)**2,axis=-1),axis=1)) if len(times)>1 else np.array([0.])
        seam=float(np.sqrt(np.mean(np.sum((positions[-1]-positions[0])**2,axis=-1))))
        # Fixed palette avoids per-frame GIF palette flicker.
        atlas=Image.new('RGB',(512,384),'#ececea')
        indices=np.linspace(0,len(rendered)-1,12).round().astype(int)
        for slot,index in enumerate(indices):atlas.paste(rendered[index].resize((128,128)),(slot%4*128,slot//4*128))
        palette=atlas.quantize(colors=256)
        frames=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in rendered]
        edges=np.rint(np.append(times,duration)*100).astype(int)
        delays=np.maximum(1,np.diff(edges))*10
        if not loop:delays[-1]=300
        options={'save_all':True,'append_images':frames[1:],'duration':delays.tolist(),'disposal':2,'optimize':False}
        if loop:options['loop']=0
        frames[0].save(folder/'motion.gif',**options)
        contact=Image.new('RGB',(1024,3*280),'#ececea');draw=ImageDraw.Draw(contact)
        for slot,index in enumerate(indices):
            contact.paste(rendered[index].resize((256,256)),(slot%4*256,slot//4*280+24))
            draw.text((slot%4*256+6,slot//4*280+6),f'{name} | {times[index]:.3f}s',fill='black')
        contact.save(folder/'contact.png')
        metrics={'clip':name,'source_sha256':source_sha,'duration_seconds':duration,'fps':a.fps,
                 'frames':len(times),'loop_hint_from_name':loop,'bone_count':len(bone_names),
                 'minimum_body_mesh_z_m':min(mesh_floors),'maximum_body_mesh_z_m':max(mesh_floors),
                 'root_xy_range_m':np.ptp(world[:,root_index,:2,3],axis=0).tolist(),
                 'in_place_last_to_first_landmark_rms_m':seam,
                 'maximum_adjacent_landmark_rms_m':float(max(adjacent)),
                 'source_height_and_yaw_preserved':True,'per_frame_bbox_fitting':False,
                 'rendered_rgba_sha256':render_hashes,'gif_sha256':sha(folder/'motion.gif'),
                 'kinematics_sha256':sha(folder/'kinematics.npz'),'contact_sha256':sha(folder/'contact.png'),
                 'visible_character_meshes':[o.name for o in source_meshes],
                 'edge_touching_frame_indices':edge_frames,'alpha_boxes':alpha_boxes,
                 'visual_review':'PENDING','naturalness_approved':False,
                 'notes':['One-shot GIFs play once and hold the final native pose; loop clips omit the terminal duplicate.',
                          'Source model-floor values require action context; climbs/jumps/seated actions need their intended support.',
                          'Guide weapon is an independent simple blade proxy only, not final project art.']}
        if tips and len(tips)>1:metrics['maximum_diagnostic_blade_tip_speed_m_s']=float(max(np.linalg.norm(np.diff(np.array(tips),axis=0),axis=1)/np.diff(times)))
        (folder/'receipt.json').write_text(json.dumps(metrics,indent=2)+'\n');completed[name]=metrics;progress()
        print('SOURCE_CLIP_CAPTURED '+json.dumps({'clip':name,'frames':len(times),'done':len(completed),'total':inventory['actual_animations']}),flush=True)
    if sha(a.source)!=source_sha:raise ValueError('Original source file changed')
    temp=a.output/'_current-frame.png'
    if temp.exists():temp.unlink()
    print('SOURCE_STUDY_FINISHED',len(completed),flush=True)


if __name__=='__main__':main()
