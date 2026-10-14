"""v42 slimmer authoring geometry, same v41 source bones and goal-directed pickup, not unchanged KayKit retarget.
Analytic fixed-length limbs + real Blender pose bones, two physical cameras.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;OUT=P/'source';OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.render.fps=30
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=False;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard'
sc.world=bpy.data.worlds.new('World');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
def mat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
M={k:mat(k,c) for k,c in dict(skin=(.71,.57,.45),head=(.68,.68,.77),navy=(.045,.065,.11),gold=(.73,.45,.075),bronze=(.46,.29,.13),brown=(.15,.075,.035),olive=(.18,.20,.12),cream=(.79,.72,.55),teal=(.045,.27,.32),gem=(.05,.72,.90)).items()}
def sphere(name,r,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1);o=bpy.context.object;o.name=name;o.scale=(r,r,r);o.data.materials.append(M[material]);return o
def capsule(name,r,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=1,depth=1);o=bpy.context.object;o.name=name;o.data.materials.append(M[material]);o['radius']=r;return o
def link(o,a,b):
    delta=b-a;o.location=(a+b)/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.scale=(o['radius'],o['radius'],delta.length)
def mesh(name,vertices,faces,material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();o=bpy.data.objects.new(name,data);sc.collection.objects.link(o);o.data.materials.append(M[material]);return o
def ik(a,b,l1,l2,pole):
    d=b-a;n=d.normalized();dist=d.length
    if not abs(l1-l2)+1e-6<dist<l1+l2-1e-6:raise ValueError(('Unreachable',dist,l1+l2,list(a),list(b)))
    v=pole-a;v-=n*v.dot(n);v.normalize();u=(l1*l1-l2*l2+dist*dist)/(2*dist);h=math.sqrt(max(0,l1*l1-u*u));return a+n*u+v*h
def V(x):return Vector(x)
DEPTH=[0,.18,.72,1,.82,.38,.06,0];BEND=[0,12,50,65,54,26,4,0]
PALMS=[[-.36,-.06,.98],[-.30,-.30,.80],[-.14,-.64,.42],[0,-.85,.20],[0,-.80,.43],[-.10,-.68,.75],[-.25,-.20,.95],[-.36,-.06,.98]]
def pose(i):
    d=DEPTH[i];turn=math.radians(BEND[i]);axis=V([0,-math.sin(turn),math.cos(turn)]);hips=V([0,.14*d,.88-.40*d]);pts={'pelvis':hips,'chest':hips+axis*.55,'neck':hips+axis*.72}
    ht=math.radians(5+45*d);pts['head']=pts['neck']+V([0,-math.sin(ht)*.25,math.cos(ht)*.25])
    for side,sign in [('left',1),('right',-1)]:
        hip=hips+V([sign*.14,0,0]);ankle=V([sign*.18,.02,.14]);knee=ik(hip,ankle,.42,.40,V([sign*.17,-1,.45]));shoulder=pts['chest']+V([sign*.22,0,0]);palm=V(PALMS[i]) if side=='right' else V([.36-.10*d,-.06+.10*d,.98-.25*d]);wrist=palm+V([0,0,.06]);elbow=ik(shoulder,wrist,.36,.35,V([sign*.7,-.02,.7]));
        for label,point in dict(hip=hip,knee=knee,ankle=ankle,toe=ankle+V([0,-.20,-.05]),shoulder=shoulder,elbow=elbow,wrist=wrist,palm=palm).items():pts[side+'.'+label]=point
    pts['right.grip']=pts['right.palm']+V([0,0,-.05])
    return pts
poses=[pose(i) for i in range(8)]
bone_defs=[('root','pelvis',None,None),('spine','pelvis','chest','root'),('neck','chest','neck','spine'),('head','neck','head','neck')]
for side in ['left','right']:
    bone_defs.extend([(side+'.hip','pelvis',side+'.hip','root'),(side+'.upperleg',side+'.hip',side+'.knee',side+'.hip'),(side+'.lowerleg',side+'.knee',side+'.ankle',side+'.upperleg'),(side+'.foot',side+'.ankle',side+'.toe',side+'.lowerleg'),(side+'.clavicle','chest',side+'.shoulder','spine'),(side+'.upperarm',side+'.shoulder',side+'.elbow',side+'.clavicle'),(side+'.lowerarm',side+'.elbow',side+'.wrist',side+'.upperarm'),(side+'.hand',side+'.wrist',side+'.palm',side+'.lowerarm')])
bone_defs.append(('right.grip','right.palm','right.grip','right.hand'))
data=bpy.data.armatures.new('OriginalTargetPickup');rig=bpy.data.objects.new('OriginalTargetPickup',data);sc.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name,a,b,parent in bone_defs:
    bone=data.edit_bones.new(name);bone.head=poses[0][a];bone.tail=poses[0][b] if b else poses[0][a]+V([0,0,.06]);
    if parent:bone.parent=data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
parts={};joints={}
for side in ['left','right']:
    for limb,a,b,r,material in [('thigh','hip','knee',.080,'olive'),('shin','knee','ankle',.066,'brown'),('upperarm','shoulder','elbow',.052,'navy'),('forearm','elbow','wrist',.052,'bronze')]:parts[side+'.'+limb]=(capsule(side+'.'+limb,r,material),side+'.'+a,side+'.'+b)
    for joint,r,material in [('shoulder',.080,'bronze'),('elbow',.052,'navy'),('knee',.080,'bronze'),('palm',.048,'brown')]:joints[side+'.'+joint]=sphere(side+'.'+joint,r,material)
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.name=side+'.planted_boot';o.location=(poses[0][side+'.ankle'].x,-.055,.09);o.scale=(.17,.29,.15);o.data.materials.append(M['brown']);bev=o.modifiers.new('Rounded boot','BEVEL');bev.width=.065;bev.segments=3
head=sphere('head',.25,'head');head.scale=(.27,.245,.27)
torso=mesh('body_outfit',[(0,0,0)]*16,[(k,(k+1)%8,(k+1)%8+8,k+8) for k in range(8)]+[tuple(range(7,-1,-1)),tuple(range(8,16))],'navy')
pelvis=sphere('pelvis',.2,'olive');cape=mesh('cape',[(0,0,0)]*9,[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)],'gold')
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);gem=bpy.context.object;gem.name='collectible';gem.scale=(.055,.055,.075);gem.data.materials.append(M['gem'])
for loc,energy in [((3,-5,8),850),((-4,2,5),500)]:
    ld=bpy.data.lights.new('Light','AREA');ld.energy=energy;ld.size=4;obj=bpy.data.objects.new('Light',ld);sc.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(V([0,0,1])-obj.location).to_track_quat('-Z','Y').to_euler()
cams={}
for name,loc in [('rear',(6,9,5.5)),('side',(9,0,5.5))]:
    cd=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,cd);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(V([0,-.05,1.15])-o.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=2.5;cams[name]=o;(OUT/name).mkdir(exist_ok=True)
records=[]
def emission(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeEmission');shader.inputs['Color'].default_value=(*color,1);m.node_tree.links.new(shader.outputs[0],out.inputs['Surface']);return m
emission_materials={k:emission('Visibility_'+k,v) for k,v in dict(blocker=(0,0,0),hand=(0,0,1),forearm=(0,1,0),gem=(1,0,0),left=(1,.30,.01)).items()};(OUT/'visibility').mkdir(exist_ok=True);(OUT/'owner').mkdir(exist_ok=True)
for i,pts in enumerate(poses):
    tick=1+39*i/7;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick))
    for name,a,b,parent in bone_defs:
        start=pts[a];end=pts[b] if b else start+V([0,0,.06]);q=(end-start).to_track_quat('Y','Z');rig.pose.bones[name].matrix=Matrix.LocRotScale(start,q,V([1,1,1]));bpy.context.view_layer.update();pb=rig.pose.bones[name];assert (pb.head-start).length<1e-5 and (pb.tail-end).length<1e-5,(name,list(pb.head),list(start));pb.keyframe_insert(data_path='location',frame=tick);pb.keyframe_insert(data_path='rotation_quaternion',frame=tick)
    for obj,a,b in parts.values():link(obj,pts[a],pts[b])
    for name,obj in joints.items():obj.location=pts[name]
    head.location=pts['head'];head.rotation_euler=(math.radians(5+45*DEPTH[i]),0,0);pelvis.location=pts['pelvis'];pelvis.scale=(.185,.135,.16)
    axis=(pts['neck']-pts['pelvis']).normalized();front=V([0,-axis.z,axis.y]);verts=[]
    for center,rx,ry in [(pts['pelvis'],.18,.13),(pts['chest'],.20,.13)]:
        for k in range(8):a=2*math.pi*k/8;verts.append(center+V([math.cos(a)*rx,0,0])+front*math.sin(a)*ry)
    for v,pos in zip(torso.data.vertices,verts):v.co=pos
    back=-front;top=pts['neck']+back*.20;middle=pts['pelvis']+axis*.32+back*.23;bottom=pts['pelvis']+back*.23+V([0,.18,-.30]);cv=[]
    for center,width in [(top,.25),(middle,.27),(bottom,.31)]:cv.extend([center+V([-width,0,0]),center,center+V([width,0,0])])
    for v,pos in zip(cape.data.vertices,cv):v.co=pos
    gem.hide_render=i==7;gem.location=V([0,-.85,.075]) if i<=3 else pts['right.grip']+V([0,0,-.075]);bpy.context.view_layer.update()
    frame=dict(index=i,rig_frame=tick,time_seconds=(tick-1)/30,hip_hinge_degrees=BEND[i],points={k:dict(world_xyz=list(v),xy={}) for k,v in pts.items()},object_center=list(gem.location),object_visible=not gem.hide_render,grasp_socket_world=list(V([0,-.85,.15]) if i<=3 else pts['right.grip']),views={})
    for name,cam in cams.items():
        sc.camera=cam;path=OUT/name/f'{i:02}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True);frame['views'][name]=dict(path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        for key,p in pts.items():v=world_to_camera_view(sc,cam,p);frame['points'][key]['xy'][name]=[v.x*384,(1-v.y)*512]
    # Colored rendered arm ownership guides, retaining actual scene occlusion.
    owner_original={o.name:list(o.data.materials) for o in sc.objects if o.type=='MESH'}
    for name in owner_original:
        if name.startswith(('right.','left.')) and name.split('.')[1] in ['upperarm','forearm','elbow','palm','shoulder']:
            obj=bpy.data.objects[name];obj.data.materials.clear();obj.data.materials.append(emission_materials['hand' if name.startswith('right.') else 'left'])
    sc.camera=cams['rear'];op=OUT/'owner'/f'{i:02}.png';sc.render.filepath=str(op);bpy.ops.render.render(write_still=True);frame['owner_pass']=dict(path=str(op.relative_to(P)),sha256=hashlib.sha256(op.read_bytes()).hexdigest())
    for name,materials in owner_original.items():
        obj=bpy.data.objects[name];obj.data.materials.clear()
        for material in materials:obj.data.materials.append(material)
    # Full-scene depth-respecting IDs, not isolated-hand masks pasted on top.
    original={o.name:list(o.data.materials) for o in sc.objects if o.type=='MESH'}
    for name,materials in original.items():
        o=bpy.data.objects[name];o.data.materials.clear();kind='hand' if name=='right.palm' else 'forearm' if name=='right.forearm' else 'gem' if name=='collectible' else 'blocker';o.data.materials.append(emission_materials[kind])
    sc.camera=cams['rear'];vp=OUT/'visibility'/f'{i:02}.png';sc.render.filepath=str(vp);bpy.ops.render.render(write_still=True);frame['right_hand_visibility_pass']=dict(path=str(vp.relative_to(P)),sha256=hashlib.sha256(vp.read_bytes()).hexdigest(),scope='Actual full-scene depth test: blue right palm, green right forearm, red collectible, opaque black occluders; not image-side anatomy detection')
    for name,materials in original.items():
        o=bpy.data.objects[name];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
    records.append(frame)
receipt=dict(kind='Original authored target-conditioned3Dpickup, analytic2boneIK, actual Blender pose bones. External CC0clip informed timing only; NOT unchanged retarget or learned GOAL inference.',saved_blend_scope='Animated pose bones at30fps with terminal mesh snapshot; rerun this script to regenerate all per-pose mesh captures. Not a final skinned game asset.',canvas=[384,512],forward_world=[0,-1,0],right_owner_world_negative_x=True,grasp_frame=3,store_frame=7,object_ground_center=[0,-.85,.075],object_half_height=.075,palm_to_grip_world=[0,0,-.05],bone_definitions=bone_defs,limb_lengths=dict(upperleg=.42,lowerleg=.40,upperarm=.36,forearm=.35,hand=.06),cameras={k:dict(world_matrix=[list(r) for r in c.matrix_world],ortho_scale=c.data.ortho_scale) for k,c in cams.items()},frames=records,production_pass=False)
(OUT/'source.json').write_text(json.dumps(receipt,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'authoring-rig.blend'));print('TARGET_PICKUP_RENDERED')
