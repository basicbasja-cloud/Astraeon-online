"""Bake a source-rig overhead attack from Mesh2Motion B and its recovery.

The native raised guard and recovery retain source weight transfer and root motion.
The source GLB is immutable. Run using Blender in background mode.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image, ImageDraw


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',default='authoring/characters/factory-v3/motions/raw/mesh2motion/human-base-animations.glb')
    ap.add_argument('--output',required=True)
    ap.add_argument('--size',type=int,default=1024)
    ap.add_argument('--compact',action='store_true',help='Shorten the native post-strike hold using B 0–8 and recovery 8–22')
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=Path(args.source).resolve();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
    sc=bpy.context.scene;rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    for track in rig.animation_data.nla_tracks:track.mute=True
    for obj in bpy.data.objects:
        if obj.type=='MESH' and obj.name!='Mannequin':obj.hide_render=True
    def capture(name,frame):
        a=bpy.data.actions[name+'_Armature'];rig.animation_data.action=a
        if hasattr(rig.animation_data,'action_slot') and len(a.slots):rig.animation_data.action_slot=a.slots[0]
        sc.frame_set(math.floor(frame),subframe=frame%1);bpy.context.view_layer.update()
        return {b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in rig.pose.bones}
    def mix(a,b,t):
        return {n:(v[0].lerp(b[n][0],t),v[1].slerp(b[n][1],t),v[2].lerp(b[n][2],t)) for n,v in a.items()}
    poses=[];records=[]
    def add(pose,segment,source_frame=None):
        poses.append(pose);records.append({'frame':len(poses)-1,'segment':segment,'source_frame':source_frame})
    strike_end=8 if args.compact else 11
    recovery_start=8 if args.compact else 0
    strike_intervals=20 if args.compact else 28
    recovery_intervals=35 if args.compact else 56
    for i in range(strike_intervals+1):
        f=strike_end*i/strike_intervals;add(capture('Sword_Regular_B',f),'Sword_Regular_B',round(f,6))
    end=poses[-1];rec=capture('Sword_Regular_B_Rec',recovery_start)
    for i in range(1,5):add(mix(end,rec,i/4),'authored_recovery_join')
    for i in range(1,recovery_intervals+1):
        f=recovery_start+(22-recovery_start)*i/recovery_intervals;add(capture('Sword_Regular_B_Rec',f),'Sword_Regular_B_Rec',round(f,6))
    rig.animation_data.action=None
    baked=bpy.data.actions.new('M2M_Overhead_B_SourceRig_60fps');rig.animation_data.action=baked
    for i,pose in enumerate(poses):
        for n,(loc,rot,scale) in pose.items():
            b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.location=loc;b.rotation_quaternion=rot;b.scale=scale
            b.keyframe_insert('location',frame=i);b.keyframe_insert('rotation_quaternion',frame=i);b.keyframe_insert('scale',frame=i)
    if hasattr(baked,'fcurves'):
        for f in baked.fcurves:
            for k in f.keyframe_points:k.interpolation='LINEAR'
    sc.frame_start=0;sc.frame_end=len(poses)-1;sc.render.fps=60
    sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=sc.render.resolution_y=args.size;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True
    sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_cavity=True;sh.show_shadows=True
    cd=bpy.data.cameras.new('Locked_SE_Orthographic');camera=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(camera);sc.camera=camera
    cd.type='ORTHO';cd.ortho_scale=3.4;target=Vector((0,0,.85));camera.location=target+Vector((3,-5,3.1));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    # Sword shaft crosses the curled fingers from pinky toward index.
    bpy.ops.mesh.primitive_cube_add(size=1);blade=bpy.context.object;blade.name='WeaponProxy_Blade';blade.scale=(.045,.015,.72)
    bm=bpy.data.materials.new('BladeSteel');bm.diffuse_color=(.68,.79,.9,1);blade.data.materials.append(bm)
    bpy.ops.mesh.primitive_cube_add(size=1);guard=bpy.context.object;guard.name='WeaponProxy_Guard';guard.scale=(.22,.035,.025)
    gm=bpy.data.materials.new('GuardGold');gm.diffuse_color=(.65,.36,.07,1);guard.data.materials.append(gm)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.02,depth=.16);handle=bpy.context.object;handle.name='WeaponProxy_Handle'
    hm=bpy.data.materials.new('GripBrown');hm.diffuse_color=(.16,.07,.025,1);handle.data.materials.append(hm)
    # Fit one camera to the union of the ENTIRE action, including the blade.
    # This prepass changes camera framing once; never per frame.
    right=camera.rotation_euler.to_matrix()@Vector((1,0,0));up=camera.rotation_euler.to_matrix()@Vector((0,1,0))
    projected=[];mannequin=bpy.data.objects['Mannequin']
    for i in range(len(records)):
        sc.frame_set(i);bpy.context.view_layer.update()
        evaluated=mannequin.evaluated_get(bpy.context.evaluated_depsgraph_get())
        points=[evaluated.matrix_world@Vector(v) for v in evaluated.bound_box]
        bones=rig.pose.bones;ix=rig.matrix_world@bones['index_01_r'].head;pink=rig.matrix_world@bones['pinky_01_r'].head
        grip=(ix+pink)*.5;axis=(ix-pink).normalized();points += [grip-axis*.15,grip+axis*.82]
        projected.extend([(p.dot(right),p.dot(up)) for p in points])
    min_x=min(p[0] for p in projected);max_x=max(p[0] for p in projected);min_y=min(p[1] for p in projected);max_y=max(p[1] for p in projected)
    camera.location += right*((min_x+max_x)/2-camera.location.dot(right))+up*((min_y+max_y)/2-camera.location.dot(up))
    cd.ortho_scale=max(max_x-min_x,max_y-min_y)*1.16
    frames=out/'frames';frames.mkdir(exist_ok=True);thumbs=[]
    def project(p):
        v=world_to_camera_view(sc,camera,p);return [round(v.x*args.size,4),round((1-v.y)*args.size,4)]
    for i,rec in enumerate(records):
        sc.frame_set(i);bpy.context.view_layer.update();bones=rig.pose.bones
        ix=rig.matrix_world@bones['index_01_r'].head;pink=rig.matrix_world@bones['pinky_01_r'].head;wrist=rig.matrix_world@bones['hand_r'].head
        grip=(ix+pink)*.5;axis=(ix-pink).normalized();palm=(grip-wrist).normalized();normal=axis.cross(palm).normalized();across=normal.cross(axis).normalized();rotation=Matrix((across,normal,axis)).transposed().to_quaternion()
        for obj,offset in [(blade,.44),(guard,.07),(handle,-.035)]:
            obj.location=grip+axis*offset;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=rotation
            obj.keyframe_insert('location',frame=i);obj.keyframe_insert('rotation_quaternion',frame=i)
        rec['landmarks']={n:project(rig.matrix_world@bones[n].head) for n in ['head','pelvis','upperarm_r','lowerarm_r','hand_r','upperarm_l','lowerarm_l','hand_l','thigh_l','thigh_r','calf_l','calf_r','foot_l','foot_r','ball_l','ball_r']}
        rec['sword_grip']=project(grip);rec['sword_tip']=project(grip+axis*.8)
        rec['feet_world']={n:list(rig.matrix_world@bones[n].head) for n in ['foot_l','foot_r','ball_l','ball_r']}
        rec['root_world']=list(rig.matrix_world@bones['root'].head)
        path=frames/f'{i:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        im=Image.open(path).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);bg=Image.new('RGBA',im.size,'#ececec');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
    durations=[round((i+1)*100/60)*10-round(i*100/60)*10 for i in range(len(thumbs))];durations[-1]=300
    thumbs[0].save(out/'overhead-B-one-shot.gif',save_all=True,append_images=thumbs[1:],duration=durations,disposal=2,optimize=False)
    ids=[round(i*(len(records)-1)/23) for i in range(24)]
    sheet=Image.new('RGB',(320*4,320*6),'#ececec');d=ImageDraw.Draw(sheet)
    for n,i in enumerate(ids):
        x,y=n%4*320,n//4*320;sheet.paste(thumbs[i].resize((320,320)),(x,y));d.text((x+4,y+4),f"{i} {records[i]['segment']}",fill='black')
    sheet.save(out/'overhead-B-contact.png')
    root_start=records[0]['root_world']
    for rec in records:rec['root_motion_delta']=[v-s for v,s in zip(rec['root_world'],root_start)]
    manifest={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_fps':24,'output_fps':60,'frame_count':len(records),'status':'GUIDE_REVIEW_ONLY','compact_hold_trim':args.compact,'playback':'one-shot; native raised guard to neutral recovery, no forced return to first pose','retargeting':'none; original source mannequin','source_ranges':{'Sword_Regular_B':[0,strike_end],'Sword_Regular_B_Rec':[recovery_start,22]},'authored_transitions':['4 frames pose blend at recovery join'],'root_motion':'native source displacement retained; per-frame root track provided for later actor-motion integration','camera':{'location':list(camera.location),'rotation':list(camera.rotation_euler),'type':'ORTHO','scale':cd.ortho_scale,'fit':'one union of all deformed body bounds and sword endpoints, 16 percent margin'},'frames':records,'gif_durations_ms':durations}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    sc.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out/'overhead-B-source-rig.blend'),compress=True)

if __name__=='__main__':main()
