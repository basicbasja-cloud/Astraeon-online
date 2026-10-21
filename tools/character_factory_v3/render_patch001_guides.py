"""Render reusable original-rig motion guides with fixed real cameras.

Run under Blender. These are mannequin guides, never claimed as final artwork.
Horizontal actor-root travel is exported separately from in-place sprite poses.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
from PIL import Image,ImageDraw

YAWS={'S':0,'SW':-45,'W':-90,'NW':-135,'N':180,'NE':135,'E':90,'SE':45}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--static',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    job=json.loads(args.job.read_text());out=args.output;out.mkdir(parents=True,exist_ok=True);source=Path(job['source_file']).resolve()
    if hashlib.sha256(source.read_bytes()).hexdigest()!=job['source_sha256']:raise ValueError('Source digest mismatch')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));sc=bpy.context.scene
    rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
    source_rig=rig;adapter=None
    if 'hand.r' in rig.pose.bones and job.get('native_human_guide_mesh'):
        for obj in bpy.data.objects:
            if obj.type=='MESH':obj.hide_render=True
        from kaykit_human_guide_mesh import bind_human_guide
        bind_human_guide(rig,Path(job['native_human_guide_mesh']).resolve())
    elif 'hand.r' in rig.pose.bones and job.get('retarget_to'):
        old=set(bpy.data.objects)
        for obj in old:
            if obj.type=='MESH':obj.hide_render=True
        bpy.ops.import_scene.gltf(filepath=str(Path(job['retarget_to']).resolve()))
        rig=next(o for o in bpy.data.objects if o not in old and o.type=='ARMATURE')
        from kaykit_motion_adapter import KayKitMotionAdapter
        adapter=KayKitMotionAdapter(source_rig,rig)
    for actor in {rig,source_rig}:
        for track in actor.animation_data.nla_tracks:track.mute=True
    for obj in bpy.data.objects:
        if obj.type=='MESH' and obj.name=='Icosphere':obj.hide_render=True
    sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=sc.render.resolution_y=job.get('resolution',1024);sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;sc.render.fps=24
    sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_cavity=True;sh.show_shadows=True
    # AA is only a guide setting; final painted sprite quality is separate.
    sc.display.render_aa=job.get('guide_aa','8')
    cd=bpy.data.cameras.new('LockedPatch001Camera');camera=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(camera);sc.camera=camera;cd.type='ORTHO';cd.ortho_scale=job.get('ortho_scale',3.55)
    kay='hand.r' in rig.pose.bones
    names={'root':'root','head':'head','pelvis':'hips' if kay else 'pelvis','hand_r':'handslot.r' if kay else 'hand_r','hand_l':'handslot.l' if kay else 'hand_l','foot_r':'foot.r' if kay else 'foot_r','foot_l':'foot.l' if kay else 'foot_l'}
    def action(name):
        options=[a for a in bpy.data.actions if a.name==name or a.name.startswith(name+'_')]
        exact=bpy.data.actions.get(name+'_'+source_rig.name)
        if exact:chosen=exact
        elif len(options)==1:chosen=options[0]
        else:raise ValueError(f'Ambiguous source action {name}: {[a.name for a in options]}')
        source_rig.animation_data.action=chosen
        if hasattr(source_rig.animation_data,'action_slot') and chosen.slots:source_rig.animation_data.action_slot=chosen.slots[0]
        return chosen
    segments=job['source_actions'];count=1 if args.static else job['frames'];samples=[]
    staff_local_axis=None
    if job.get('staff_grip_mode')=='wrist-local-idle-reference':
        neutral=action('Idle_A');sc.frame_set(0);bpy.context.view_layer.update()
        staff_local_axis=(rig.matrix_world@rig.pose.bones['hand_l'].matrix).to_quaternion().inverted()@Vector((0,0,1))
    intervals=job.get('source_ranges',{})
    for i in range(count):
        phase=0 if count==1 else i/count if job['loop'] else i/(count-1)
        position=phase*len(segments);segment=min(len(segments)-1,int(position));local=position-segment
        chosen=action(segments[segment]);start,end=chosen.frame_range
        if segments[segment] in intervals:start,end=intervals[segments[segment]]
        # Known exporter-reset tails are excluded explicitly, not blended away.
        ends={'Sword_Regular_A':9,'Sword_Regular_A_Rec':22,'Sword_Regular_B':8,'Sword_Regular_B_Rec':22,'Sword_Attack':39,'Sword_Regular_Combo':70}
        end=min(end,ends.get(segments[segment],end));f=start+(end-start)*local
        if count==1:f=start
        samples.append({'action':segments[segment],'source_frame':f,'segment_phase':local})
    proxies=[]
    def curve(name,color,radius):
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=1
        obj=bpy.data.objects.new(name,data);sc.collection.objects.link(obj);material=bpy.data.materials.new(name+'Material');material.diffuse_color=(*color,1);data.materials.append(material);proxies.append(obj);return obj
    def points(obj,values):
        obj.data.splines.clear();spline=obj.data.splines.new('POLY');spline.points.add(len(values)-1)
        for p,v in zip(spline.points,values):p.co=(*v,1)
    weapon=job.get('weapon','none')
    if weapon=='bow':bow=curve('BowGuide',(.36,.20,.08),.018);string=curve('StringGuide',(.82,.83,.85),.004);arrow=curve('ArrowGuide',(.67,.59,.38),.007)
    elif weapon in ['sword','staff']:shaft=curve('WeaponGuide',(.59,.69,.82)if weapon=='sword'else(.38,.21,.08),.022);cross=curve('GripCrossGuide',(.70,.41,.09),.018)
    original=rig.matrix_world.copy();records=[]
    for rec in samples:
        action(rec['action']);f=rec['source_frame'];sc.frame_set(math.floor(f),subframe=f%1);rig.matrix_world=original.copy();bpy.context.view_layer.update()
        if adapter:adapter.apply()
        rec['source_root_world']=list(rig.matrix_world@rig.pose.bones[names['root']].head)
    anchor=Vector(samples[0]['source_root_world']);anchor.z=0
    refs={};size=sc.render.resolution_x
    for direction in job['directions']:
        folder=out/direction;folder.mkdir(exist_ok=True);r=math.radians(YAWS[direction]);offset=Vector((6*math.sin(r),-6*math.cos(r),3.1));camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();up=camera.rotation_euler.to_matrix()@Vector((0,1,0));camera.location=anchor+up*(.325*cd.ortho_scale)+offset
        view=[];thumbs=[]
        for i,rec in enumerate(samples):
            action(rec['action']);f=rec['source_frame'];sc.frame_set(math.floor(f),subframe=f%1);rig.matrix_world=original.copy()
            if adapter:adapter.apply()
            delta=Vector(rec['source_root_world'])-Vector(samples[0]['source_root_world']);delta.z=0
            rig.matrix_world.translation-=delta;bpy.context.view_layer.update()
            def project(v):
                q=world_to_camera_view(sc,camera,v);return [round(q.x*size,4),round((1-q.y)*size,4)]
            bones={n:rig.matrix_world@rig.pose.bones[b].head for n,b in names.items()}
            prop={}
            if weapon=='bow':
                left=bones['hand_l'];right=bones['hand_r'];aim=left-right
                if not kay:
                    left=sum((rig.matrix_world@rig.pose.bones[n+'_01_l'].head for n in ['index','pinky']),Vector())*.5
                    right=sum((rig.matrix_world@rig.pose.bones[n+'_01_r'].head for n in ['index','pinky']),Vector())*.5
                    aim=left-right
                if aim.length<.08:aim=Vector((0,-1,0))
                aim.normalize();up=Vector((0,0,1));up-=aim*aim.dot(up)
                if up.length<.1:up=Vector((1,0,0))
                up.normalize();ends=[]
                for k in range(25):
                    t=k/12-1;ends.append(left+up*(.52*t)+aim*(-.16*t*t+.12*abs(t)**6))
                draw='Draw' in rec['action'] or 'Aiming' in rec['action'] or ('Release' in rec['action'] and rec['segment_phase']<.22)
                nock=right if draw else left
                points(bow,ends);points(string,[ends[0],nock,ends[-1]]);points(arrow,[nock,left+aim*.40]);arrow.hide_render=not draw
                prop={'grip':project(left),'string_nock':project(nock),'arrow_tip':project(left+aim*.40),'arrow_visible':draw}
            elif weapon in ['sword','staff']:
                side='r'if weapon=='sword'else'l';grip=bones['hand_'+side]
                if not kay:
                    ix=rig.matrix_world@rig.pose.bones['index_01_'+side].head;pk=rig.matrix_world@rig.pose.bones['pinky_01_'+side].head;grip=(ix+pk)*.5;axis=(ix-pk).normalized()
                else:axis=Vector((0,0,1))
                if weapon=='staff':axis=(rig.matrix_world@rig.pose.bones['hand_l'].matrix).to_quaternion()@staff_local_axis if staff_local_axis is not None else Vector((0,0,1))
                extent=.8 if weapon=='sword'else 1.18;normal=axis.cross(Vector((0,-1,0))).normalized();points(shaft,[grip-axis*.12,grip+axis*extent]);points(cross,[grip+axis*.06-normal*.10,grip+axis*.06+normal*.10]);prop={'grip':project(grip),'tip':project(grip+axis*extent)}
            path=folder/f'{i:03d}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            view.append({'frame':i,**rec,'actor_root_delta':list(delta),'landmarks':{n:project(v) for n,v in bones.items()},'world_landmarks':{n:list(v) for n,v in bones.items()},'weapon_guide':prop,'bone_rotations':{n:list((rig.matrix_world@rig.pose.bones[b].matrix).to_quaternion())for n,b in names.items()},'image':str(path.relative_to(out))})
            im=Image.open(path).convert('RGBA').resize((256,256));bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);thumbs.append(bg.convert('RGB'))
        sheet=Image.new('RGB',(1024,256*math.ceil(count/4)),'white')
        for i,im in enumerate(thumbs):sheet.paste(im,(i%4*256,i//4*256))
        sheet.save(folder/'contact.png')
        refs[direction]={'camera':{'location':list(camera.location),'rotation':list(camera.rotation_euler),'ortho_scale':cd.ortho_scale,'fixed':True},'frames':view}
        print('SOURCE_VIEW_CAPTURED',job['id'],direction,flush=True)
    if args.static:
        sheet=Image.new('RGB',(2048,1024),'white')
        for i,d in enumerate(job['directions']):
            im=Image.open(out/d/'000.png').convert('RGBA').resize((512,512));sheet.paste(im,(i%4*512,i//4*512),im)
        sheet.save(out/'turnaround-guide.png')
    receipt={'job':job,'source_rig':source_rig.name,'guide_rig':rig.name,'retargeting':'rest-space world rotation transfer plus toe-height correction'if adapter else'none; original rig','frame_count':count,'views':refs,'mirroring':False,'root_policy':'fixed camera; horizontal source actor-root travel extracted and recorded separately','status':'SOURCE_MANNEQUIN_GUIDE_NOT_PAINTED_ART','limitations':['Source grip, joins, terminal key behavior and foot contacts require visual review.','This shared donor guide does not prove male/female final-art fitting.','Staff proxy is constrained vertical for fitting review, not a proof of raw finger contact.']}
    (out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
