"""Render four fixed-camera samples of a simple single Mesh2Motion Sword_Attack.

Run in Blender: blender -b --python this_file.py -- --output /path
The sword is a review proxy; its grip still needs human visual inspection.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb')
    parser.add_argument('--output', required=True)
    parser.add_argument('--samples', type=int, default=12)
    parser.add_argument('--size', type=int, default=512)
    parser.add_argument('--clips', default='SW,NW,NE,SE')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    source = Path(args.source).resolve(); output = Path(args.output).resolve();output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    scene = bpy.context.scene
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name != 'Mannequin': obj.hide_render = True
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.render.fps = 24
    shade = scene.display.shading
    shade.light = 'STUDIO'; shade.color_type = 'MATERIAL';shade.show_cavity = True
    shade.show_shadows = True
    camera_data = bpy.data.cameras.new('LockedSourceReview')
    camera = bpy.data.objects.new('LockedSourceReview', camera_data)
    scene.collection.objects.link(camera);scene.camera = camera
    camera_data.type = 'ORTHO';camera_data.ortho_scale = 3.4
    target = Vector((0,0,0.85));camera.location = target + Vector((3,-5,3.1))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    # Local sword: +Z points from the pinky toward index across closed knuckles.
    verts=[(-.035,0,.08),(.035,0,.08),(.025,0,.68),(0,0,.8),(-.025,0,.68),(-.035,.012,.08),(.035,.012,.08),(.025,.012,.68),(0,.012,.8),(-.025,.012,.68)]
    faces=[(0,1,2,3,4),(5,9,8,7,6),(0,5,6,1),(1,6,7,2),(2,7,8,3),(3,8,9,4),(4,9,5,0)]
    mesh=bpy.data.meshes.new('SwordBlade');mesh.from_pydata(verts,[],faces)
    sword=bpy.data.objects.new('ReviewSword',mesh);scene.collection.objects.link(sword)
    mat=bpy.data.materials.new('BladeSilver');mat.diffuse_color=(.65,.76,.88,1);sword.data.materials.append(mat)
    bpy.ops.mesh.primitive_cube_add(size=1)
    guard=bpy.context.object;guard.name='ReviewGuard';guard.scale=(.21,.035,.025)
    gm=bpy.data.materials.new('GuardGold');gm.diffuse_color=(.65,.37,.07,1);guard.data.materials.append(gm)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.021,depth=.16)
    handle=bpy.context.object;handle.name='ReviewHandle'
    hm=bpy.data.materials.new('HandleBrown');hm.diffuse_color=(.19,.085,.035,1);handle.data.materials.append(hm)
    definitions={d:['Sword_Attack'] for d in ['SW','NW','NE','SE']}
    source_samples=[0,3,6,8,10,11,12,13,14,15,25,28,31,34,37,39]
    manifests=[]
    for clip in args.clips.split(','):
        folder=output/clip;folder.mkdir(exist_ok=True)
        yaw=math.radians({'SW':-45,'NW':-135,'NE':135,'SE':45}[clip]);offset=Vector((6*math.sin(yaw),-6*math.cos(yaw),3.1));camera.location=target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler()
        records=[];thumbs=[]
        for segment in definitions[clip]:
            action=bpy.data.actions[segment+'_Armature'];rig.animation_data.action=action
            if hasattr(rig.animation_data,'action_slot') and len(action.slots): rig.animation_data.action_slot=action.slots[0]
            start,end=action.frame_range
            # Exported A/B clips contain a terminal return to their first pose.
            # Match the recovery entry before this exporter tail instead.
            review_ends={'Sword_Regular_A':9,'Sword_Regular_A_Rec':22,
                         'Sword_Regular_B':11,'Sword_Regular_B_Rec':22,
                         'Sword_Regular_Combo':70,'Sword_Attack':45}
            end=min(end,review_ends.get(segment,end))
            count=len(source_samples)
            for index in range(count):
                frame=source_samples[index]
                scene.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
                bones=rig.pose.bones
                index_base=rig.matrix_world@bones['index_01_r'].head
                pinky=rig.matrix_world@bones['pinky_01_r'].head
                wrist=rig.matrix_world@bones['hand_r'].head
                knuckle=(index_base+pinky)*.5
                axis=(index_base-pinky).normalized()
                palm=(knuckle-wrist).normalized()
                normal=axis.cross(palm).normalized(); across=normal.cross(axis).normalized()
                rot=Matrix((across,normal,axis)).transposed().to_4x4();rot.translation=knuckle
                sword.matrix_world=rot
                guard.location=knuckle+axis*.07;guard.rotation_euler=rot.to_euler()
                handle.location=knuckle-axis*.035;handle.rotation_euler=rot.to_euler()
                path=folder/f'{len(records):03d}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
                def point(v):
                    q=world_to_camera_view(scene,camera,v);return [round(q.x*args.size,3),round((1-q.y)*args.size,3)]
                landmarks={n:point(rig.matrix_world@bones[n].head) for n in ['root','head','pelvis','upperarm_r','lowerarm_r','hand_r','foot_l','foot_r']}
                records.append({'action':segment,'source_frame':round(frame,4),'image':str(path.relative_to(output)),'landmarks':landmarks,'sword_grip':point(knuckle),'sword_tip':point(knuckle+axis*.8)})
                im=Image.open(path).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
                bg=Image.new('RGBA',im.size,'#ececec');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
        sheet=Image.new('RGB',(320*4,320*math.ceil(len(thumbs)/4)),'#ececec');draw=ImageDraw.Draw(sheet)
        for i,(im,rec) in enumerate(zip(thumbs,records)):
            x,y=i%4*320,i//4*320;sheet.paste(im,(x,y));draw.text((x+5,y+5),f"{clip} {rec['action'].removeprefix('Sword_Regular_')} {rec['source_frame']:.1f}",fill='black')
        sheet.save(output/f'{clip}-contact.png')
        durations=[]
        for i,rec in enumerate(records):
            if i+1<len(records) and records[i+1]['action']==rec['action']:durations.append(min(100,max(40,round((records[i+1]['source_frame']-rec['source_frame'])*1000/24))))
            else:durations.append(42 if i+1<len(records) else 300)
        thumbs[0].save(output/f'{clip}-one-shot.gif',save_all=True,append_images=thumbs[1:],duration=durations,disposal=2,optimize=False)
        manifests.append({'clip':clip,'segments':definitions[clip],'source_fps':24,'camera':{'projection':'ORTHO','ortho_scale':3.4,'location':list(camera.location),'target':list(target),'yaw_degrees':{'SW':-45,'NW':-135,'NE':135,'SE':45}[clip],'fixed_during_action':True},'frames':records,'durations_ms':durations})
    (output/'manifest.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'camera':{'type':'ORTHO','scale':3.4,'location':list(camera.location),'rotation':list(camera.rotation_euler)},'source_rig':'unretargeted','source_samples':source_samples,'directions':['SW','NW','NE','SE'],'mirroring':False,'timing_policy':'single strike with held follow-through compacted to at most 100ms/sample; source poses unchanged','sword_proxy':'index-to-pinky knuckle axis, visual grip validation pending','clips':manifests},indent=2)+'\n')

if __name__=='__main__': main()
