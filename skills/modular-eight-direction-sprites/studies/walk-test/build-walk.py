"""Fresh original modular mesh, actual source-transform walk bake and CPU render.

Author animation transforms are CC0. All visible geometry is constructed here;
no source mannequin mesh or rejected project art is used. No generated-art claim.
"""
import argparse, gzip, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'source-motion'))
from retarget_math import fk, two_segment

SOURCE_SHA = 'be684571ed655a1b892c2c07e6e2aeca053b606c442d34004adaf1d944090d01'
DIRS = ['S','SE','E','NE','N','NW','W','SW']
KEYS = [0,5,10,15,20,25,30,35]
p=argparse.ArgumentParser();p.add_argument('--capture',type=Path);p.add_argument('--output',type=Path,required=True)
p.add_argument('--mode',choices=['build','render'],default='build');p.add_argument('--blend',type=Path)
p.add_argument('--views',default='SE');p.add_argument('--parts',action='store_true');p.add_argument('--variant',choices=['silver','auburn'],default='silver')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])

def material(name, color, metallic=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Roughness'].default_value=.78;n.inputs['Metallic'].default_value=metallic
    return m

def build():
    if a.output.exists():raise ValueError('Use a fresh build directory')
    blob=a.capture.read_bytes();s=json.loads(gzip.decompress(blob))
    if s['source_sha256']!=SOURCE_SHA or len(s['rest_bones'])!=65:raise ValueError('Audited source adapter only')
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    rest=s['rest_bones'];ordered=list(rest)
    factors={n:(.64 if n in ['root','pelvis'] or n.startswith(('thigh_','calf_','foot_','ball_'))
                  else .70 if n.startswith(('spine_','clavicle_','upperarm_','lowerarm_','hand_'))
                  else .64 if n.startswith(('neck_','Head')) else .70) for n in rest}
    tr=fk(rest,{n:v['local_matrix'] for n,v in rest.items()},factors,s['object_world_matrix'])
    arm=bpy.data.armatures.new('SilverScarfWalkRig');rig=bpy.data.objects.new('original.walk.rig',arm);scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for name in ordered:
        b=arm.edit_bones.new(name);m=Matrix(tr[name].tolist());b.head=m.translation
        b.tail=m.translation+m.to_3x3()@Vector((0,.06,0));b.align_roll(m.to_3x3()@Vector((0,0,1)))
        if rest[name]['parent']:b.parent=arm.edit_bones[rest[name]['parent']]
        b.use_connect=False
    # Independent authored cape controls; not source recovered joints or physics.
    chest=Vector(tr['spine_03'][:3,3]);neck=Vector(tr['neck_01'][:3,3])
    for n,h,t,parent in [('cape.upper',(0,.12,neck.z-.02),(0,.17,chest.z-.16),'spine_03'),
                         ('cape.lower',(0,.17,chest.z-.16),(0,.24,chest.z-.42),'cape.upper')]:
        b=arm.edit_bones.new(n);b.head=h;b.tail=t;b.parent=arm.edit_bones[parent];b.use_connect=False
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    for b in rig.pose.bones:b.rotation_mode='QUATERNION'
    mats={
      'skin':material('skin.warm',(0.72,.42,.27)), 'skin.light':material('skin.face',(.88,.64,.44)),
      'ink':material('ink.warm',(.035,.026,.040)), 'cloth':material('cloth.charcoal',(.043,.047,.073)),
      'linen':material('linen.ivory',(.80,.73,.59)), 'leather':material('leather.brown',(.19,.092,.052)),
      'pants':material('pants.olive',(.19,.18,.13)), 'gold':material('metal.bronze',(.56,.33,.12),.25),
      'gold.light':material('metal.edge',(.82,.58,.24),.18), 'scarf':material('scarf.ochre',(.86,.48,.045)),
      'teal':material('cloth.teal',(.06,.26,.27)), 'silver':material('hair.silver',(.45,.40,.53)),
      'silver.light':material('hair.silver.light',(.62,.56,.67)), 'auburn':material('hair.auburn',(.22,.08,.045)),
      'auburn.light':material('hair.auburn.light',(.41,.19,.09)), 'white':material('eye.ivory',(.94,.88,.75)),
      'iris':material('eye.violet',(.22,.14,.32)), 'blush':material('face.blush',(.67,.31,.26)),
    }
    objects=[]
    def bind(obj,slot,weights):
        obj['slot']=slot;objects.append(obj)
        group={n:obj.vertex_groups.new(name=n) for n in set(k for w in weights for k in w)}
        for i,w in enumerate(weights):
            total=sum(w.values())
            for n,v in w.items():group[n].add([i],v/total,'REPLACE')
        mod=obj.modifiers.new('original.rig.skin','ARMATURE');mod.object=rig
        for poly in obj.data.polygons:poly.use_smooth=True
        return obj
    def mesh(name,verts,faces,mat,slot,weights):
        data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);data.materials.append(mats[mat])
        return bind(obj,slot,weights)
    def ellipsoid(name,center,scale,mat,bone,slot,rotation=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=center)
        o=bpy.context.object;o.name=name;o.scale=scale
        if rotation:o.rotation_euler=rotation
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        o.data.materials.append(mats[mat]);return bind(o,slot,[{bone:1}]*len(o.data.vertices))
    def segment(name,start,end,r1,r2,mat,bone,slot,sides=12):
        start,end=Vector(start),Vector(end);axis=(end-start).normalized()
        ref=Vector((0,1,0)) if abs(axis.y)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized();v=axis.cross(u).normalized()
        verts=[]
        for t,r in [(0,r1),(.08,r1),(.92,r2),(1,r2)]:
            for k in range(sides):verts.append(list(start.lerp(end,t)+r*(math.cos(k*2*math.pi/sides)*u+math.sin(k*2*math.pi/sides)*v)))
        faces=[tuple(range(sides-1,-1,-1)),tuple(range(3*sides,4*sides))]
        for ring in range(3):
            for k in range(sides):faces.append((ring*sides+k,ring*sides+(k+1)%sides,(ring+1)*sides+(k+1)%sides,(ring+1)*sides+k))
        return mesh(name,verts,faces,mat,slot,[{bone:1}]*len(verts))
    def point(n):return Vector(tr[n][:3,3])
    def torso(name,extra,mat,slot):
        levels=[('pelvis',.11,.09),('spine_01',.115,.09),('spine_02',.14,.09),('spine_03',.155,.095),('neck_01',.105,.075)]
        verts=[];weights=[];sides=16
        for bone,rx,ry in levels:
            h=point(bone)
            for k in range(sides):
                th=k*2*math.pi/sides;verts.append((h.x+(rx+extra)*math.cos(th),h.y+(ry+extra)*math.sin(th),h.z))
                weights.append({bone:1})
        faces=[tuple(range(sides-1,-1,-1)),tuple(range(4*sides,5*sides))]
        for ring in range(4):
            for k in range(sides):faces.append((ring*sides+k,ring*sides+(k+1)%sides,(ring+1)*sides+(k+1)%sides,(ring+1)*sides+k))
        return mesh(name,verts,faces,mat,slot,weights)
    # Complete base body under clothing: no pre-cut hidden torso/limbs/head.
    torso('body.complete.torso',-.004,'skin','body')
    head=point('Head')+Vector((0,-.025,.095))
    ellipsoid('body.complete.head',head,(.178,.150,.192),'skin.light','Head','body')
    for side,suffix in [('right','r'),('left','l')]:
        hip,knee,ankle=map(point,['thigh_'+suffix,'calf_'+suffix,'foot_'+suffix])
        shoulder,elbow,wrist=map(point,['upperarm_'+suffix,'lowerarm_'+suffix,'hand_'+suffix])
        segment('body.'+side+'.thigh',hip,knee,.059,.047,'skin','thigh_'+suffix,'body')
        segment('body.'+side+'.shin',knee,ankle,.044,.033,'skin','calf_'+suffix,'body')
        segment('body.'+side+'.upperarm',shoulder,elbow,.049,.039,'skin','upperarm_'+suffix,'body')
        segment('body.'+side+'.forearm',elbow,wrist,.039,.031,'skin','lowerarm_'+suffix,'body')
        for bone,h,rad in [('upperarm_'+suffix,shoulder,.049),('lowerarm_'+suffix,elbow,.039),('calf_'+suffix,knee,.047)]:
            ellipsoid('body.joint.'+bone,h,(rad,rad,rad),'skin',bone,'body')
        palm=point('hand_'+suffix).lerp(point('middle_01_'+suffix),.58)
        # Rest-space paddle aligned to the source wrist/knuckle axis.
        ellipsoid('body.'+side+'.palm',palm,(.046,.031,.029),'skin','hand_'+suffix,'body')
        ellipsoid('glove.'+side+'.palm',palm,(.049,.034,.031),'leather','hand_'+suffix,'gloves')
        for finger in ['thumb','index','middle','ring','pinky']:
            for j in range(1,4):
                n=f'{finger}_{j:02}_{suffix}';nextn=f'{finger}_{j+1:02}'+('_leaf' if j==3 else '')+'_'+suffix
                segment('body.'+n,point(n),point(nextn),.010,.008,'skin',n,'body',8)
                segment('glove.'+n,point(n),point(nextn),.011,.009,'leather',n,'gloves',8)
        segment('pants.'+side,hip,knee,.070,.055,'pants','thigh_'+suffix,'pants')
        ellipsoid('pants.'+side+'.knee',knee,(.057,.058,.051),'pants','calf_'+suffix,'pants')
        segment('sleeve.'+side,shoulder,elbow,.059,.045,'cloth','upperarm_'+suffix,'torso')
        segment('sleeve.'+side+'.lower',elbow,wrist,.046,.035,'cloth','lowerarm_'+suffix,'torso')
        ellipsoid('armor.'+side+'.pauldron',shoulder,(.073,.079,.064),'gold','upperarm_'+suffix,'armor')
        segment('armor.'+side+'.bracer',elbow.lerp(wrist,.42),wrist,.049,.041,'gold','lowerarm_'+suffix,'armor')
        segment('armor.'+side+'.bracer.rim',elbow.lerp(wrist,.83),wrist,.052,.044,'gold.light','lowerarm_'+suffix,'armor')
        segment('boot.'+side+'.shaft',knee.lerp(ankle,.14),ankle,.064,.048,'leather','calf_'+suffix,'boots')
        segment('boot.'+side+'.cuff',knee.lerp(ankle,.09),knee.lerp(ankle,.27),.068,.066,'leather','calf_'+suffix,'boots')
        # A complete foot under the boot, then footwear heel/body and articulated toe.
        foot_center=Vector((ankle.x,ankle.y-.027,.035))
        ellipsoid('body.'+side+'.foot',foot_center,(.041,.085,.031),'skin','foot_'+suffix,'body')
        ellipsoid('boot.'+side+'.heel',foot_center,(.051,.081,.035),'leather','foot_'+suffix,'boots')
        ball=point('ball_'+suffix)
        ellipsoid('boot.'+side+'.toe',(ball.x,ball.y-.018,.027),(.052,.059,.027),'leather','ball_'+suffix,'boots')
        # Named flattened sole meshes also provide actual deformation/contact samples.
        ellipsoid('sole.'+side+'.heel',(ankle.x,ankle.y+.012,.008),(.048,.047,.008),'ink','foot_'+suffix,'boots')
        ellipsoid('sole.'+side+'.toe',(ball.x,ball.y-.020,.007),(.049,.057,.007),'ink','ball_'+suffix,'boots')
        ellipsoid('boot.'+side+'.gold',(ankle.x,ankle.y-.010,.104),(.057,.054,.014),'gold.light','calf_'+suffix,'boots')
    torso('tunic.complete',.002,'cloth','torso')
    # Ivory chest panel, skirt front and asymmetric teal sash, all separately bound.
    for name,z,half,mat in [('tabard.chest',point('spine_02').z,.063,'linen'),('tabard.lower',point('pelvis').z-.095,.078,'linen')]:
        bone='spine_02' if 'chest' in name else 'pelvis';cy=point(bone).y-.102
        mesh(name,[(-half,cy,z-.105),(half,cy,z-.105),(half,cy,z+.105),(-half,cy,z+.105)],[(0,1,2,3)],mat,'torso',[{bone:1}]*4)
    h=point('pelvis');ellipsoid('belt',(0,h.y,h.z+.02),(.135,.106,.026),'leather','pelvis','belt')
    ellipsoid('belt.buckle',(0,h.y-.108,h.z+.02),(.037,.012,.032),'gold.light','pelvis','belt')
    mesh('sash.teal',[(.065,h.y-.09,h.z),(.146,h.y-.095,h.z-.02),(.172,h.y-.12,h.z-.22),(.085,h.y-.11,h.z-.20)],[(0,1,2,3)],'teal','sash',[{'pelvis':1}]*4)
    # Cloth cape with two deforming sections, independently replaceable.
    verts=[];weights=[]
    for row in range(5):
        t=row/4;z=neck.z-.03-.46*t;cy=.115+.13*t;half=.095+.11*t
        for col in range(5):
            u=(col-2)/2;verts.append((u*half,cy+.025*(1-u*u),z+.025*abs(u)))
            weights.append({'spine_03':1-t,'cape.upper':min(t,.6),'cape.lower':max(0,t-.6)})
    faces=[]
    for row in range(4):
        for col in range(4):faces.append((row*5+col,row*5+col+1,(row+1)*5+col+1,(row+1)*5+col))
    cape=mesh('cape.complete',verts,faces,'scarf','cape',weights)
    solid=cape.modifiers.new('cloth.thickness','SOLIDIFY');solid.thickness=.005
    # Scarf collar binds to neck; no forced camera-facing piece.
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(0,neck.y,neck.z-.016),major_radius=.126,minor_radius=.042)
    o=bpy.context.object;o.name='scarf.collar';o.scale=(1,.9,.62);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    o.data.materials.append(mats['scarf']);bind(o,'scarf',[{'neck_01':1}]*len(o.data.vertices))
    # Complete cap + original spikes; alternate variant is real separate geometry.
    for variant,mat in [('silver','silver'),('auburn','auburn')]:
        radius=.187;verts=[];faces=[]
        for row in range(6):
            for k in range(24):
                phi=k*2*math.pi/24;theta=.03+(row/5)*(1.61-.55*max(0,-math.sin(phi)))
                verts.append((head.x+radius*math.sin(theta)*math.cos(phi),head.y+.159*math.sin(theta)*math.sin(phi),head.z+.205*math.cos(theta)))
        for row in range(5):
            for k in range(24):faces.append((row*24+k,row*24+(k+1)%24,(row+1)*24+(k+1)%24,(row+1)*24+k))
        slot='hair.'+variant;mesh(slot+'.complete.cap',verts,faces,mat,slot,[{'Head':1}]*len(verts))
        # Hair locks taper along authored 3D directions, not flat image rotations.
        for k in range(11):
            theta=k*2*math.pi/11;start=head+Vector((.15*math.cos(theta),.132*math.sin(theta),.025))
            end=start+Vector((.055*math.cos(theta),.047*math.sin(theta),-.055 if math.sin(theta)<-.25 else .002))
            segment(slot+f'.lock.{k}',start,end,.051,.004,mat,'Head',slot,8)
        for k in range(5):
            x=(k-2)*.062;start=head+Vector((x*.75,-.126,.145));end=head+Vector((x-.022,-.162,.069+(k%2)*.018))
            segment(slot+f'.fringe.{k}',start,end,.044,.006,mat if k%2 else mat+'.light','Head',slot,8)
        segment(slot+'.tuft',head+Vector((-.025,.005,.178)),head+Vector((.029,.028,.271 if variant=='silver' else .237)),.041,.002,mat+'.light','Head',slot,8)
    for sign in [-1,1]:
        ellipsoid('ear.'+str(sign),head+Vector((sign*.173,-.018,-.021)),(.037,.026,.047),'skin.light','Head','body')
        ellipsoid('eye.white.'+str(sign),head+Vector((sign*.065,-.143,.018)),(.047,.012,.033),'white','Head','face')
        ellipsoid('eye.iris.'+str(sign),head+Vector((sign*.065,-.155,.017)),(.024,.008,.030),'iris','Head','face')
        ellipsoid('eye.pupil.'+str(sign),head+Vector((sign*.065,-.162,.015)),(.010,.004,.022),'ink','Head','face')
        ellipsoid('eye.light.'+str(sign),head+Vector((sign*.059,-.167,.032)),(.007,.003,.008),'white','Head','face')
        segment('brow.'+str(sign),head+Vector((sign*.031,-.143,.060)),head+Vector((sign*.092,-.135,.067)),.007,.009,'ink','Head','face',8)
        ellipsoid('cheek.'+str(sign),head+Vector((sign*.095,-.122,-.038)),(.026,.004,.010),'blush','Head','face')
    ellipsoid('nose',head+Vector((0,-.155,-.021)),(.015,.014,.018),'skin.light','Head','face')
    segment('mouth',head+Vector((-.022,-.143,-.068)),head+Vector((.016,-.146,-.068)),.003,.003,'ink','Head','face',8)

    # Actual dense source timestamps are baked; only 8 selected exposures render.
    clip=next(c for c in s['clips'] if c['name']=='Walk_Loop');scene.render.fps=1000;scene.render.fps_base=1
    frames=[];max_joint_error=0;max_edge_error=0
    rest_lengths={n:float(np.linalg.norm(tr[n][:3,3]-tr[v['parent']][:3,3])) for n,v in rest.items() if v['parent'] and n!='pelvis'}
    for f in clip['frames']:
        t=f['time_seconds'];scene.frame_set(round(t*1000));desired=fk(rest,f['local_matrices'],factors,s['object_world_matrix']);travel=desired['root'][:3,3].copy()
        # Explicit in-place extraction: recorded world travel is retained for engine use.
        for name,m in desired.items():
            m[:3,3]-=travel;desired[name]=Matrix(m.tolist())
        def assign():
            for name in ordered:
                bone=arm.bones[name];kwargs={}
                if bone.parent:kwargs={'parent_matrix':desired[bone.parent.name],'parent_matrix_local':bone.parent.matrix_local}
                rig.pose.bones[name].matrix_basis=bone.convert_local_to_pose(desired[name],bone.matrix_local,invert=True,**kwargs)
            bpy.context.view_layer.update()
        assign();corrections={}
        # Actual authored footwear differs from the source rig: correct measured
        # sole penetration with fixed-length leg IK, not root lifting or stretching.
        deps=bpy.context.evaluated_depsgraph_get()
        for side,suffix in [('right','r'),('left','l')]:
            lowest=1
            for o in objects:
                if o.name.startswith(('sole.'+side+'.','boot.'+side+'.','body.'+side+'.foot')):
                    evaluated=o.evaluated_get(deps);data=evaluated.to_mesh()
                    try:lowest=min(lowest,min((evaluated.matrix_world@v.co).z for v in data.vertices))
                    finally:evaluated.to_mesh_clear()
            lift=max(0,.001-lowest);corrections[side]={'uncorrected_min_z':lowest,'ankle_lift':lift}
            if lift>0:
                hip,kn,ft=['thigh_'+suffix,'calf_'+suffix,'foot_'+suffix]
                h,k,end=[desired[n].translation.copy() for n in [hip,kn,ft]];goal=end+Vector((0,0,lift))
                solution=two_segment(h,k,goal,rest_lengths[kn],rest_lengths[ft])
                if not solution['reachable']:raise ValueError('Floor correction needs full-body reblocking; no leg stretch')
                nk=Vector(solution['middle'].tolist());ne=Vector(solution['end'].tolist())
                for name,before,after,newhead in [(hip,k-h,nk-h,h),(kn,end-k,ne-nk,nk)]:
                    rotation=before.rotation_difference(after).to_matrix()@desired[name].to_3x3()
                    m=rotation.to_4x4();m.translation=newhead;desired[name]=m
                translate=Matrix.Translation(ne-end)
                for name in ordered:
                    if name==ft or ft in [b.name for b in arm.bones[name].parent_recursive]:desired[name]=translate@desired[name]
                assign()
        phase=t/clip['duration_seconds']*2*math.pi
        for n,amp,lag in [('cape.upper',.045,.6),('cape.lower',.075,1.1)]:
            rig.pose.bones[n].rotation_mode='XYZ';rig.pose.bones[n].rotation_euler=(amp*math.sin(phase-lag),.015*math.sin(phase),0)
        bpy.context.view_layer.update()
        measured={n:list(rig.matrix_world@rig.pose.bones[n].head) for n in rest}
        max_joint_error=max(max_joint_error,max((Vector(measured[n])-desired[n].translation).length for n in rest))
        for n,length in rest_lengths.items():max_edge_error=max(max_edge_error,abs((Vector(measured[n])-Vector(measured[rest[n]['parent']])).length-length))
        for pb in rig.pose.bones:
            for prop in ['location','rotation_euler' if pb.rotation_mode=='XYZ' else 'rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=t*1000)
        frames.append({'source_index':f['source_index'],'time_seconds':t,'root_world':travel.tolist(),'in_place_joints':measured,'footwear_floor_corrections':corrections})
    if max_joint_error>2e-5 or max_edge_error>2e-5:raise ValueError(f'Actual rig pose/length failure {max_joint_error}, {max_edge_error}')
    action=rig.animation_data.action;action.name='original.source-based.walk';action.use_fake_user=True
    for curve in action.fcurves:
        for k in curve.keyframe_points:k.interpolation='LINEAR'
    scene.frame_start=0;scene.frame_end=round(clip['duration_seconds']*1000)
    # One fixed render camera, world lighting, transparent registered canvas.
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=False
    scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.world=bpy.data.worlds.new('sprite.world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.62,.66,.75,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55
    for name,location,power,size in [('key',(-3,-4,5),220,4),('fill',(3,-2,3),80,4),('rim',(0,3,4),120,3)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=location;o.rotation_euler=(Vector((0,0,.65))-o.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('sprite.camera');cam=bpy.data.objects.new('sprite.camera',data);scene.collection.objects.link(cam)
    cam.location=(0,-4,2.92);cam.rotation_euler=(Vector((0,0,.64))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=1.58;scene.camera=cam
    # A physical rig rotation changes facing; camera/scale/root never bbox-follow.
    pivot=bpy.data.objects.new('facing.pivot',None);scene.collection.objects.link(pivot)
    rig.parent=pivot
    for o in objects:o.parent=pivot
    for o in objects:o.hide_render=o['slot']=='hair.auburn'
    a.output.mkdir(parents=True)
    report={'schema':'original-walk-test-v1','status':'UNAPPROVED_ORIGINAL_MOTION_TEST','source_animation_author':'Quaternius','source_url':'https://quaternius.itch.io/universal-animation-library','source_glb_sha256':SOURCE_SHA,'capture_sha256':hashlib.sha256(blob).hexdigest(),'source_clip':'Walk_Loop','source_samples':len(frames),'target_bones':len(arm.bones),'target_edge_factors':factors,'duration_seconds':clip['duration_seconds'],'selected_source_indices':KEYS,'frames':frames,'max_assigned_target_joint_error':max_joint_error,'max_anatomical_edge_length_error':max_edge_error,'source_geometry_used':False,'rejected_project_art_used':False,'parts':sorted(set(o['slot'] for o in objects)),'source_geometry':'Every visible mesh constructed in this script; author animation transforms only','root_policy':'Explicit measured-root extraction for registered in-place sprites. World root travel retained; runtime must advance at matching speed.','secondary_motion':'Two authored phase-lag cape bones, not cloth physics','camera':{'canvas':[256,256],'native':[128,128],'ortho_scale':1.58,'location':list(cam.location),'target':[0,0,.64]},'release_ready':False,'limits':['Unapproved blockout art, not painted original final style','Walking is unarmed; no weapon/palm-hilt claim','Source motion not full-body physics or contact-locked','No arbitrary text-to-sprite or production engine integration']}
    (a.output/'motion.json').write_text(json.dumps(report,indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(a.output/'original-modular-walk.blend'),compress=True)
    print('BUILT_WALK',len(objects),'meshes',len(arm.bones),'bones',max_joint_error,max_edge_error)

def render():
    if a.output.exists():raise ValueError('Use new render output')
    bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;rig=bpy.data.objects['original.walk.rig'];pivot=bpy.data.objects['facing.pivot']
    meta=json.loads((a.blend.parent/'motion.json').read_text());objects=[o for o in scene.objects if o.type=='MESH'];views=a.views.split(',')
    if any(v not in DIRS for v in views):raise ValueError('Unknown facing')
    a.output.mkdir(parents=True);samples=[]
    if a.parts:
        scene.view_layers[0].use_pass_z=True;scene.use_nodes=True;nodes=scene.node_tree.nodes;nodes.clear()
        layer=nodes.new('CompositorNodeRLayers');comp=nodes.new('CompositorNodeComposite');scene.node_tree.links.new(layer.outputs['Image'],comp.inputs[0])
        depth=nodes.new('CompositorNodeOutputFile');depth.format.file_format='OPEN_EXR';depth.format.color_depth='32';depth.file_slots[0].path='depth_'
        scene.node_tree.links.new(layer.outputs['Depth'],depth.inputs[0])
    for view in views:
        pivot.rotation_euler.z=DIRS.index(view)*math.pi/4
        slots=meta['parts'] if a.parts else ['composite']
        for slot in slots:
            directory=a.output/view/slot;directory.mkdir(parents=True)
            for k,index in enumerate(KEYS):
                t=meta['frames'][index]['time_seconds'];pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos))
                chosen=slot.split('.')[1] if slot.startswith('hair.') else a.variant
                for o in objects:
                    o.hide_render=o['slot']=='hair.'+('auburn' if chosen=='silver' else 'silver')
                    o.visible_camera=True if slot=='composite' else o['slot']==slot
                if a.parts:depth.base_path=str(directory)
                bpy.context.view_layer.update();scene.render.filepath=str(directory/f'{k:02}.png');bpy.ops.render.render(write_still=True)
                if a.parts:
                    outputs=list(directory.glob('depth_*.exr'))
                    if len(outputs)!=1:raise ValueError('Expected exactly one new depth pass')
                    outputs[0].rename(directory/f'{k:02}-depth.exr')
                samples.append({'view':view,'slot':slot,'key':k,'source_index':index,'time_seconds':t})
    (a.output/'render-receipt.json').write_text(json.dumps({'blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'views':views,'variant':a.variant,'parts_only':a.parts,'samples':samples,'rendered':len(samples)},indent=2)+'\n')
    print('RENDERED',len(samples))

if a.mode=='build':build()
else:render()
