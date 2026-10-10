"""Static anatomical grip correction preserving donor MCP joint placement.

The hand frame roll aligns palm width with the handle. Finger roots follow
that palm frame before curl; independently relocated finger roots are avoided.
No armature or approved motion is created.
"""
import bpy,math,json
from mathutils import Vector,Matrix

s=bpy.context.scene;assert s.name=='ASTRAEON_ASSET_FIT_04'
body=bpy.data.objects['SM_AssetFit04_Body']
donor=bpy.data.scenes['ASTRAEON_FREE_FBX_INSPECTION']
rig=next(o for o in donor.objects if o.type=='ARMATURE')
original=next(o for o in donor.objects if o.name.startswith('SuperHero_Male'))
canonical=Matrix.Rotation(math.pi,4,'Z')
rest={b.name:canonical@rig.matrix_world@b.matrix_local for b in rig.data.bones}
points={b.name:(canonical@rig.matrix_world@b.head_local,canonical@rig.matrix_world@b.tail_local) for b in rig.data.bones}
mapping={n:Matrix(m) for n,m in json.loads(s['fitTransforms']).items()}
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
new_frames={};paths={};palm_rotations={}

def frame(a,b,width_axis):
    y=(b-a).normalized();z=(width_axis-y*width_axis.dot(y)).normalized();x=y.cross(z).normalized()
    m=Matrix((x,y,z)).transposed().to_4x4();m.translation=a
    return m

def set_bone(name,a,b,width_axis,width=.95):
    m=frame(a,b,width_axis);old_a,old_b=points[name]
    suffix=name[-1]
    if not name.startswith('hand_') and suffix in palm_rotations:
        # Preserve each donor bone's actual roll relative to the palm. Thumb
        # and phalange axes do not share a universal local Z convention.
        posed=palm_rotations[suffix]@rest[name].to_3x3()
        turn=posed.col[1].rotation_difference(b-a).to_matrix()
        m=(turn@posed).to_4x4();m.translation=a
    scale=Matrix.Diagonal((width,(b-a).length/(old_b-old_a).length,width,1))
    mapping[name]=m@scale@rest[name].inverted();new_frames[name]=m

for suffix,side in [('r','R'),('l','L')]:
    wrist=P['wrist_'+side];palm=P['palm_'+side]
    axis=(P['blade_tip']-P['guard']).normalized() if side=='R' else (wrist-P['elbow_'+side]).normalized()
    guard=P['guard'] if side=='R' else palm+axis*.096
    across=Vector((0,1,0)).cross(axis).normalized();normal=axis.cross(across).normalized()
    # The dorsal palm runs toward the handle, while its width runs along the
    # handle. Infer a wrist correction in shared source space for that grasp.
    fitted_wrist=guard-axis*.105+normal*.080
    center=fitted_wrist-normal*.044
    # Hand roll, not just its longitudinal direction, controls where MCP joints
    # and palm webbing land. This is a static fitted coordinate frame.
    set_bone('hand_'+suffix,fitted_wrist,center,axis,1.05)
    palm_rotations[suffix]=new_frames['hand_'+suffix].to_3x3()@rest['hand_'+suffix].to_3x3().inverted()
    for digit in ['index','middle','ring','pinky']:
        name=digit+'_01_'+suffix
        start=mapping['hand_'+suffix]@points[name][0]
        distance=(guard-start).dot(axis);c=guard-axis*distance
        radial=start-c;theta=math.atan2(radial.dot(normal),radial.dot(across))
        path=[start]
        # Preserve the MCP start; curl around a centerline just outside the
        # actual handle rather than stretching the web toward arbitrary roots.
        curl_sign=1 if side=='R' else -1
        for delta in [45,160,245,270]:
            angle=theta+math.radians(delta*curl_sign)
            path.append(c+.026*(across*math.cos(angle)+normal*math.sin(angle)))
        for i in range(1,4):set_bone(digit+'_%02d_'%i+suffix,path[i-1],path[i],axis,.95)
        leaf=digit+'_04_leaf_'+suffix
        if leaf in rest:set_bone(leaf,path[3],path[4],axis,.95)
        paths[name]=[list(p) for p in path]
    start=mapping['hand_'+suffix]@points['thumb_01_'+suffix][0]
    c=guard-axis*.057
    thumb_side=1 if side=='R' else -1
    path=[start,c+across*.002*thumb_side+normal*.044,c+across*.021*thumb_side+normal*.021,c+across*.024*thumb_side-normal*.006,c+across*.011*thumb_side-normal*.031]
    for i in range(1,4):set_bone('thumb_%02d_'%i+suffix,path[i-1],path[i],axis,1)
    leaf='thumb_04_leaf_'+suffix
    if leaf in rest:set_bone(leaf,path[3],path[4],axis,1)
    paths['thumb_01_'+suffix]=[list(p) for p in path]

basis=canonical@original.matrix_world
backup=bpy.data.meshes['Fit04_BodyBeforeStyle']
changed=0
for v,donor_v in zip(body.data.vertices,original.data.vertices):
    weights=[(original.vertex_groups[g.group].name,g.weight) for g in donor_v.groups if g.weight>.00001]
    if not any(n in new_frames for n,w in weights):continue
    position=basis@donor_v.co;total=sum(w for n,w in weights)
    v.co=sum((mapping[n]@position*(w/total) for n,w in weights),start=Vector((0,0,0)))
    backup.vertices[v.index].co=v.co;changed+=1
body.data.update();backup.update()

# Match the physical handle diameter to this hand; retain its guard and length.
hilt=bpy.data.objects['SM_AssetFit04_Hilt_Provisional']
old_hilt=bpy.data.meshes.get('Fit04_HiltBeforeGrip')
if old_hilt is None:
    old_hilt=hilt.data.copy();old_hilt.name='Fit04_HiltBeforeGrip';old_hilt.use_fake_user=True
guard=P['guard'];axis=(P['blade_tip']-guard).normalized()
for v,old in zip(hilt.data.vertices,old_hilt.vertices):
    axial=guard+axis*(old.co-guard).dot(axis)
    v.co=axial+(old.co-axial)*.80
hilt.data.update()

# Refit glove surfaces from the corresponding original body face indices.
def glove_side(poly):
    w={}
    for i in poly.vertices:
        for g in body.data.vertices[i].groups:
            n=body.vertex_groups[g.group].name;w[n]=w.get(n,0)+g.weight
    name=max(w,key=w.get)
    if name.startswith(('hand','thumb','index','middle','ring','pinky')):return 'R' if name.endswith('_r') else 'L'
    return None
for side in ['R','L']:
    obj=bpy.data.objects['SM_AssetFit04_Refitted_Glove_'+side]
    indices=sorted({i for f in body.data.polygons if glove_side(f)==side for i in f.vertices})
    assert len(indices)==len(obj.data.vertices),'Glove/body source index registration changed'
    for v,i in zip(obj.data.vertices,indices):v.co=body.data.vertices[i].co+body.data.vertices[i].normal*.004
    obj.data.update()
    for mod in obj.modifiers:
        if mod.type=='SHRINKWRAP':mod.offset=.005
        if mod.type=='SOLIDIFY':mod.thickness=.002
s['gripPaths']=json.dumps(paths);s['gripFrameMethod']='MCP-root-preserving static palm roll and handle-centered curl'
s['fitTransforms']=json.dumps({n:[list(row) for row in m] for n,m in mapping.items()})
print('HAND_FRAME_AND_MCP_ROOTS_REPAIRED',changed,'VERTICES; STATIC_NOT_FK_CONTROL_VALIDATION')
