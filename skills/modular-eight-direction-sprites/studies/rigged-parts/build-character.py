"""Original editable modular character, authored as geometry on one named rig.

Run with Blender, not host Python. No input game art or rejected sprite is used.
This is a part-production prototype; its look is not artistically approved.
"""
import bpy, bmesh, json, math, sys, time
from pathlib import Path
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'
OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((OUT/'rig-poses.json').read_text())
KEYS=DATA['keys']; REST=KEYS[0]
DIRS=['S','SE','E','NE','N','NW','W','SW']
PARTS={}; BIND={}; MARKERS=[]
def q(v):return Vector((v[0],-v[1],v[2]))
def frame(a,b):
    a,b=Vector(a),Vector(b)
    return Matrix.Translation(a)@(b-a).to_track_quat('Y','Z').to_matrix().to_4x4()
def matrices(p):
    hip=q(p['hip']);head=q(p['head']);ct=-p['chestTwist'];pt=-p['pelvisTwist']
    result={'root':Matrix.Identity(4),
      'pelvis':Matrix.Translation(hip)@Matrix.Rotation(pt,4,'Z'),
      'chest':Matrix.Translation(hip+Vector((0,-p['lean'],.27)))@Matrix.Rotation(ct,4,'Z')@Matrix.Rotation(-p['lean']*.65,4,'X'),
      'head':Matrix.Translation(head)@Matrix.Rotation(ct*.12,4,'Z')@Matrix.Rotation(-p['lean']*.35,4,'X')}
    for side in ['right','left']:
        for family,upper,lower in [('arms','upperarm','forearm'),('legs','thigh','shin')]:
            l=p[family][side]
            result[side+'.'+upper]=frame(q(l['start']),q(l['joint']))
            result[side+'.'+lower]=frame(q(l['joint']),q(l['end']))
        f=p['feet'][side];a=q(f['ankle']);toe=q(f['toe']);heel=q(f['heel'])
        forward=(toe-heel).normalized();result[side+'.foot']=frame(a,a+forward*.18)
        hand=q(p['arms'][side]['end'])
        axis=q(p['swordDirection']) if side=='right' else Vector((0,-.1,-.02)).normalized()
        result[side+'.hand']=frame(hand,hand+axis*.10)
    # Slot ownership is anatomical and does not depend on projected screen X.
    result['weapon.right']=result['right.hand'].copy()
    return result

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
arm=bpy.data.armatures.new('SilverScarf_rig_family_A');rig=bpy.data.objects.new('SilverScarfRig',arm)
scene.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
restmat=matrices(REST)
parents={'root':None,'pelvis':'root','chest':'pelvis','head':'chest','weapon.right':'right.hand'}
for side in ['right','left']:
    parents.update({side+'.upperarm':'chest',side+'.forearm':side+'.upperarm',side+'.hand':side+'.forearm',side+'.thigh':'pelvis',side+'.shin':side+'.thigh',side+'.foot':side+'.shin'})
for name,m in restmat.items():
    b=arm.edit_bones.new(name);b.head=m.translation;b.tail=m.translation+m.to_3x3()@Vector((0,.12,0))
    b.matrix=m
    if name=='root':b.head=(0,0,0);b.tail=(0,0,.12)
for name,parent in parents.items():
    if parent:arm.edit_bones[name].parent=arm.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
BIND={n:arm.bones[n].matrix_local.copy() for n in restmat}
rig['rig_family']='silver-scarf-A';rig['weapon_owner']='anatomical_right'

def mat(name,color,unlit=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    ns=m.node_tree.nodes;ns.clear();output=ns.new('ShaderNodeOutputMaterial');em=ns.new('ShaderNodeEmission');m.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
    if unlit:em.inputs['Color'].default_value=(*color,1);return m
    geo=ns.new('ShaderNodeNewGeometry');dot=ns.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.45,-.55,.705)
    m.node_tree.links.new(geo.outputs['Normal'],dot.inputs[0])
    rng=ns.new('ShaderNodeMapRange');rng.inputs['From Min'].default_value=-1;rng.inputs['From Max'].default_value=1
    m.node_tree.links.new(dot.outputs['Value'],rng.inputs['Value'])
    ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    levels=[(.0,.38),(.34,.58),(.50,.76),(.69,.94),(.83,1.11)]
    for i,(at,intensity) in enumerate(levels):
        el=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(at)
        el.position=at;el.color=tuple(min(1,c*intensity) for c in color)+(1,)
    # Full-scene and isolated BVHs can differ at floating-point normal boundaries.
    # Quantize the shading input before discontinuous toon bands, not output pixels.
    mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=4096
    rounding=ns.new('ShaderNodeMath');rounding.operation='ROUND'
    div=ns.new('ShaderNodeMath');div.operation='DIVIDE';div.inputs[1].default_value=4096
    m.node_tree.links.new(rng.outputs['Result'],mul.inputs[0]);m.node_tree.links.new(mul.outputs[0],rounding.inputs[0]);m.node_tree.links.new(rounding.outputs[0],div.inputs[0])
    m.node_tree.links.new(div.outputs[0],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs['Color'],em.inputs['Color'])
    return m
M={n:mat(n,c) for n,c in {'skin':(.69,.39,.24),'cream':(.80,.73,.58),'navy':(.048,.067,.12),'teal':(.025,.18,.20),'gold':(.72,.39,.065),'bronze':(.45,.25,.10),'bronzeLight':(.76,.49,.22),'brown':(.17,.08,.043),'olive':(.13,.13,.066),'silver':(.57,.50,.61),'silverLight':(.85,.78,.83),'hairDark':(.11,.035,.018),'hairLight':(.26,.10,.04),'steel':(.50,.64,.70),'black':(.012,.014,.025),'white':(.92,.94,.94),'violet':(.09,.07,.19)}.items()}

def geo(part,name,verts,faces,bone,material,bone_space=False,smooth=False):
    if bone_space:world=[BIND[bone]@Vector(v) for v in verts]
    else:world=[Vector(v)+BIND[bone].translation for v in verts]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(world,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.parent=rig
    obj.data.materials.append(M[material]);obj['part_id']=part;obj['socket']=bone;obj['source_is_complete']=True
    group=obj.vertex_groups.new(name=bone);group.add(list(range(len(verts))),1,'REPLACE')
    modifier=obj.modifiers.new('SharedRig','ARMATURE');modifier.object=rig
    for face in mesh.polygons:face.use_smooth=smooth
    PARTS.setdefault(part,[]).append(obj)
    return obj

def ellipsoid(part,name,center,radii,bone,material,segments=20,rings=12,bone_space=False):
    verts=[];faces=[]
    for j in range(rings+1):
        p=math.pi*j/rings
        for i in range(segments):
            a=2*math.pi*i/segments
            verts.append(tuple(center[k]+[radii[0]*math.sin(p)*math.cos(a),radii[1]*math.sin(p)*math.sin(a),radii[2]*math.cos(p)][k] for k in range(3)))
    for j in range(rings):
        for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    return geo(part,name,verts,faces,bone,material,bone_space,True)

def cylinder(part,name,bone,start,end,r0,r1,material,segments=12):
    verts=[];faces=[]
    for y,r in [(start,r0),(end,r1)]:
        for i in range(segments):
            a=2*math.pi*i/segments;verts.append((r*math.cos(a),y,r*math.sin(a)))
    for i in range(segments):faces.append((i,(i+1)%segments,segments+(i+1)%segments,segments+i))
    faces.extend([tuple(range(segments-1,-1,-1)),tuple(range(segments,segments*2))])
    return geo(part,name,verts,faces,bone,material,True,True)

def box(part,name,center,size,bone,material,bone_space=False):
    vertices=[tuple(center[i]+s[i]*size[i]/2 for i in range(3)) for s in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return geo(part,name,vertices,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],bone,material,bone_space)

def strand(part,name,points,width,bone,material):
    pts=[Vector(p) for p in points];verts=[];faces=[]
    for j,p in enumerate(pts):
        tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
        u=tangent.cross(Vector((0,1,0)))
        if u.length<.001:u=tangent.cross(Vector((1,0,0)))
        u.normalize();v=tangent.cross(u).normalized();w=width*(1-j/(len(pts)-1))+.002
        for i in range(6):verts.append(p+u*math.cos(i*math.pi/3)*w+v*math.sin(i*math.pi/3)*w*.58)
    for j in range(len(pts)-1):
        for i in range(6):faces.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
    faces.append(tuple(range(5,-1,-1)));faces.append(tuple(range((len(pts)-1)*6,len(pts)*6)))
    return geo(part,name,verts,faces,bone,material,smooth=True)

# Complete bare body and bald head exist under replacement clothing/hair.
ellipsoid('body.base','Skin torso',(0,0,0),(.205,.12,.24),'chest','skin')
ellipsoid('body.base','Skin pelvis',(0,0,0),(.20,.125,.125),'pelvis','skin')
ellipsoid('head.base','Bald head',(0,0,0),(.285,.245,.305),'head','skin',24,16)
ellipsoid('head.base','Neck',(0,0,-.31),(.078,.075,.12),'head','skin')
for side,sign in [('right',-1),('left',1)]:
    for bone,length,r0,r1 in [(side+'.upperarm',.31,.060,.053),(side+'.forearm',.31,.050,.038),(side+'.thigh',.34,.067,.053),(side+'.shin',.34,.049,.037)]:
        cylinder('body.base','Skin '+bone,bone,0,length,r0,r1,'skin')
    ellipsoid('body.base','Palm '+side,(0,.022,0),(.053,.07,.047),side+'.hand','skin',bone_space=True)
    ellipsoid('body.base','Bare foot '+side,(0,.050,-.010),(.072,.130,.050),side+'.foot','skin',bone_space=True)
    ellipsoid('head.base','Ear '+side,(sign*.28,.0,-.055),(.041,.05,.073),'head','skin')
    ellipsoid('head.base','Eye white '+side,(sign*.112,-.230,-.016),(.067,.025,.042),'head','white')
    ellipsoid('head.base','Iris '+side,(sign*.112,-.254,-.014),(.032,.009,.035),'head','violet')
    ellipsoid('head.base','Pupil '+side,(sign*.112,-.261,-.014),(.013,.006,.025),'head','black')
    ellipsoid('head.base','Eye glint '+side,(sign*.112-.009,-.269,.003),(.009,.004,.009),'head','white',12,8)
    strand('head.base','Brow '+side,[(sign*.169,-.23,.042),(sign*.113,-.255,.052),(sign*.063,-.245,.027)],.012,'head','brown')
ellipsoid('head.base','Nose',(0,-.249,-.056),(.025,.025,.026),'head','skin',12,8)
strand('head.base','Mouth',[(-.027,-.236,-.123),(0,-.245,-.126),(.030,-.234,-.117)],.005,'head','brown')

for side in ['right','left']:
    cylinder('legs.olive','Trouser '+side,side+'.thigh',-.016,.36,.103,.074,'olive')
    cylinder('legs.olive','Lower trouser '+side,side+'.shin',-.02,.22,.073,.058,'olive')
    cylinder('boots.brown','Boot shin '+side,side+'.shin',.11,.345,.080,.068,'brown')
    for at in [.12,.29]:cylinder('boots.brown','Boot band '+side+str(at),side+'.shin',at,at+.033,.084,.084,'bronzeLight')
    ellipsoid('boots.brown','Foot '+side,(0,.054,-.013),(.083,.158,.064),side+'.foot','brown',bone_space=True)
    box('boots.brown','Sole '+side,(0,.062,-.063),(.164,.286,.028),side+'.foot','brown',True)
    ellipsoid('gloves.brown','Glove '+side,(0,.020,0),(.058,.074,.052),side+'.hand','brown',bone_space=True)
    cylinder('gloves.brown','Glove cuff '+side,side+'.forearm',.264,.31,.061,.058,'brown')
    ellipsoid('armor.bronze','Pauldron '+side,(0,.016,0),(.126,.13,.123),side+'.upperarm','bronze',bone_space=True)
    cylinder('armor.bronze','Pauldron rim '+side,side+'.upperarm',.03,.062,.127,.123,'bronzeLight')
    cylinder('armor.bronze','Bracer '+side,side+'.forearm',.108,.268,.068,.058,'bronze')
    for at in [.12,.243]:cylinder('armor.bronze','Bracer edge '+side+str(at),side+'.forearm',at,at+.019,.073,.067,'bronzeLight')

for part,color,panel in [('torso.tabard','navy',True),('torso.travel','teal',False)]:
    ellipsoid(part,'Jacket '+part,(0,0,-.035),(.24,.148,.23),'chest',color)
    for side in ['right','left']:
        cylinder(part,'Sleeve '+part+side,side+'.upperarm',-.02,.315,.089,.074,color)
        cylinder(part,'Fore-sleeve '+part+side,side+'.forearm',-.02,.17,.072,.064,color)
    box(part,'Belt '+part,(0,0,.0),(.44,.29,.063),'pelvis','brown')
    box(part,'Buckle '+part,(0,-.153,.002),(.10,.025,.073),'pelvis','bronzeLight')
    box(part,'Buckle inset '+part,(0,-.169,.003),(.048,.008,.040),'pelvis','brown')
    if panel:
        geo(part,'Cream breast', [(-.097,-.151,-.205),(.105,-.151,-.205),(.108,-.146,.175),(-.106,-.146,.175)],[(0,1,2,3)],'chest','cream')
        for sign in [-1,1]:
            geo(part,'Tabard flap '+str(sign),[(sign*.014,-.16,-.03),(sign*.17,-.153,-.03),(sign*.18,-.155,-.275),(sign*.024,-.174,-.30)],[(0,1,2,3)],'pelvis','cream')
            geo(part,'Gold tabard diamond '+str(sign),[(sign*.10,-.178,-.16),(sign*.125,-.178,-.19),(sign*.10,-.178,-.225),(sign*.075,-.178,-.19)],[(0,1,2,3)],'pelvis','bronzeLight')
        geo(part,'Left teal sash',[(.19,-.16,-.012),(.24,-.17,-.04),(.29,-.17,-.25),(.18,-.17,-.29)],[(0,1,2,3)],'pelvis','teal')
    else:
        for at in [.08,-.025,-.13]:box(part,'Travel fastener '+str(at),(0,-.16,at),(.072,.025,.017),'chest','bronzeLight')

def hair_cap(part,material,bob=False):
    seg=28;rings=10;verts=[];faces=[]
    for j in range(rings+1):
        for i in range(seg):
            a=2*math.pi*i/seg;front=max(0,-math.sin(a));maxphi=2.0-.64*front
            if bob:maxphi=2.20-.86*front
            p=maxphi*j/rings
            verts.append((.305*math.sin(p)*math.cos(a),.267*math.sin(p)*math.sin(a),.325*math.cos(p)+.025))
    for j in range(rings):
        for i in range(seg):faces.append((j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i))
    geo(part,'Full hair cap '+part,verts,faces,'head',material,smooth=True)

hair_cap('hair.silver','silver')
for i in range(18):
    a=2*math.pi*i/18;front=math.sin(a)<-.3
    z=.18 if front else .075
    start=(.23*math.cos(a),.20*math.sin(a),z+.10)
    mid=(.30*math.cos(a+.18),.25*math.sin(a+.18),z-.025)
    tip=(.36*math.cos(a+.24),.30*math.sin(a+.24),z-.13)
    strand('hair.silver','Silver lock '+str(i),[start,mid,tip],.072,'head','silverLight' if i%3==0 else 'silver')
for i,x in enumerate([-.21,-.11,-.01,.09,.19]):
    strand('hair.silver','Front fringe '+str(i),[(x-.04,-.12,.265),(x-.055,-.255,.15),(x-.060,-.259,.018+.03*(i%2))],.063,'head','silverLight' if i%2 else 'silver')
strand('hair.silver','Crown curl',[(-.055,.025,.27),(-.06,.02,.37),(.025,.012,.45),(.11,-.004,.43)],.055,'head','silverLight')
hair_cap('hair.chestnut','hairDark',True)
for i in range(12):
    a=2*math.pi*i/12
    if math.sin(a)<-.6:continue
    strand('hair.chestnut','Bob lock '+str(i),[(.23*math.cos(a),.20*math.sin(a),.14),(.29*math.cos(a),.26*math.sin(a),-.04),(.27*math.cos(a),.25*math.sin(a),-.24)],.083,'head','hairLight' if i%3==0 else 'hairDark')
for i,x in enumerate([-.18,-.085,.02,.12,.21]):
    strand('hair.chestnut','Bob fringe '+str(i),[(x+.02,-.14,.25),(x+.02,-.27,.15),(x+.035,-.25,.048)],.052,'head','hairLight' if i%2 else 'hairDark')

for part,color,length in [('cape.gold','gold',.68),('cape.teal','teal',.44)]:
    # Full mesh, including the portion hidden by the torso in front views.
    vs=[];fs=[];rows=8;cols=8
    for j in range(rows+1):
        t=j/rows;width=.20+.20*t
        for i in range(cols+1):
            x=(i/cols*2-1)*width
            vs.append((x,.13+.20*t+.025*math.cos(i/cols*math.pi*4),.16-length*t+.018*math.sin(i/cols*math.pi*3)))
    for j in range(rows):
        for i in range(cols):a=j*(cols+1)+i;fs.append((a,a+1,a+cols+2,a+cols+1))
    obj=geo(part,'Complete cape '+part,vs,fs,'chest',color,smooth=True)
    solid=obj.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.012
    ellipsoid(part,'Scarf '+part,(0,-.012,.205),(.242,.181,.075),'chest',color)
    ellipsoid(part,'Scarf clasp '+part,(-.175,-.158,.166),(.039,.018,.039),'chest','bronzeLight',12,8)

for part,curved in [('weapon.straight',False),('weapon.falchion',True)]:
    cylinder(part,'Grip '+part,'weapon.right',-.092,.044,.025,.026,'brown')
    ellipsoid(part,'Pommel '+part,(0,-.096,0),(.032,.028,.032),'weapon.right','bronzeLight',bone_space=True)
    box(part,'Guard '+part,(0,.066,0),(.195,.040,.051),'weapon.right','bronzeLight',True)
    verts=[];faces=[]
    for j,(y,w) in enumerate([(.09,.047),(.35,.043),(.61,.036),(.72,0)]):
        shift=.065*(y/.72)**2 if curved else 0
        if curved:w*=1.5
        verts.extend([(shift-w,y,0),(shift,y,.013),(shift+w,y,0),(shift,y,-.013)])
    for j in range(3):
        for i in range(4):faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
    faces.append((3,2,1,0))
    geo(part,'Blade '+part,verts,faces,'weapon.right','steel',True)

hair_cap('headgear.helm','steel')
box('headgear.helm','Helmet brow rim',(0,-.251,.11),(.48,.035,.034),'head','bronzeLight')
strand('headgear.helm','Helmet crest',[(0,.16,.29),(0,0,.38),(0,-.12,.33)],.033,'head','bronzeLight')

scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1;scene.cycles.use_denoising=False
scene.cycles.pixel_filter_type='BOX';scene.cycles.filter_width=.01
scene.cycles.use_animated_seed=False
scene.render.use_persistent_data=True;scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.world=bpy.data.worlds.new('Transparent world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[1].default_value=0
bpy.ops.object.camera_add(location=(0,-5*math.cos(math.pi/6),.96+5*math.sin(math.pi/6)))
camera=bpy.context.object;camera.name='FixedSpriteCamera';camera.data.type='ORTHO';camera.data.ortho_scale=2.65
camera.rotation_euler=(Vector((0,0,.96))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
# A fixed subpixel capture offset avoids primary rays landing on exact symmetric
# mesh edges. It is shared by every part/pose/view, never normalized per frame.
camera.data.shift_x=.00173
scene.view_layers[0].use_pass_z=True
scene.view_layers[0].pass_alpha_threshold=.001
scene.use_nodes=True;nodes=scene.node_tree.nodes;nodes.clear();rl=nodes.new('CompositorNodeRLayers');comp=nodes.new('CompositorNodeComposite');scene.node_tree.links.new(rl.outputs['Image'],comp.inputs['Image'])
depth=nodes.new('CompositorNodeOutputFile');depth.format.file_format='OPEN_EXR';depth.format.color_depth='32';depth.base_path=str(OUT/'raw-depth');depth.file_slots[0].path='depth-';scene.node_tree.links.new(rl.outputs['Depth'],depth.inputs[0])
DEFAULT=['body.base','head.base','legs.olive','boots.brown','gloves.brown','armor.bronze','torso.tabard','hair.silver','cape.gold','weapon.straight']
ALTERNATE=['body.base','head.base','legs.olive','boots.brown','gloves.brown','armor.bronze','torso.travel','hair.chestnut','cape.teal','weapon.falchion']

TRAIL_OBJECTS={}
trail_mat=bpy.data.materials.new('Blade history ribbon');trail_mat.use_nodes=True
ns=trail_mat.node_tree.nodes;ns.clear();output=ns.new('ShaderNodeOutputMaterial');mix=ns.new('ShaderNodeMixShader');transparent=ns.new('ShaderNodeBsdfTransparent');emission=ns.new('ShaderNodeEmission');color=ns.new('ShaderNodeVertexColor');color.layer_name='trail_tint'
trail_mat.node_tree.links.new(color.outputs['Color'],emission.inputs['Color']);trail_mat.node_tree.links.new(color.outputs['Alpha'],mix.inputs[0]);trail_mat.node_tree.links.new(transparent.outputs[0],mix.inputs[1]);trail_mat.node_tree.links.new(emission.outputs[0],mix.inputs[2]);trail_mat.node_tree.links.new(mix.outputs[0],output.inputs['Surface'])
for weapon in ['straight','falchion']:
    mesh=bpy.data.meshes.new('Ribbon '+weapon);obj=bpy.data.objects.new('Trail '+weapon,mesh);scene.collection.objects.link(obj);obj.parent=rig;obj.data.materials.append(trail_mat)
    part='trail.'+weapon;obj['part_id']=part;obj['source_is_complete']=True;obj['socket']='blade-history:right.hand';PARTS[part]=[obj];TRAIL_OBJECTS[weapon]=obj

def update_trail(p):
    # No free-standing crescent: the strip is the actual recent blade sweep.
    for weapon,obj in TRAIL_OBJECTS.items():
        vertices=[];faces=[];values=[];now=p['time'];samples=DATA['samples']
        if .28<=now<=.40:
            history=[s for s in samples if max(.25,now-.070)<=s['time']<=min(now,.36)]
            for s in history:
                grip=q(s['arms']['right']['end']);axis=q(s['swordDirection']).normalized()
                # The same hand basis supplies the curved weapon's lateral tip.
                hand=matrices(s)['right.hand'];side=hand.to_3x3()@Vector((1,0,0))
                start=grip+axis*.11;tip=grip+axis*.72+(side*.065 if weapon=='falchion' else Vector((0,0,0)))
                age=now-s['time'];fade=max(0,1-age/.070);width=fade**.40
                inner=tip+(start-tip)*width
                vertices.extend([tuple(inner),tuple(tip)]);values.extend([(.32,.60,.76,.18*fade),(.90,.97,1,.70*fade)])
            for j in range(len(history)-1):faces.append((j*2,j*2+1,j*2+3,j*2+2))
        mesh=bpy.data.meshes.new('Ribbon sample '+weapon);mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(trail_mat)
        if vertices:
            attr=mesh.color_attributes.new(name='trail_tint',type='FLOAT_COLOR',domain='POINT')
            for entry,value in zip(attr.data,values):entry.color=value
        old=obj.data;obj.data=mesh;bpy.data.meshes.remove(old)

def select(parts):
    for part,objects in PARTS.items():
        for obj in objects:obj.hide_render=part not in parts
def set_pose(p,direction=0):
    # Render evaluates animation at scene.frame_current. Keep the authored pose
    # and evaluated action time identical; manually posing frame 1 is insufficient.
    scene.frame_set(round(p['time']*1000)+1)
    rig.rotation_euler=(0,0,direction*math.pi/4)
    desired=matrices(p)
    for name in restmat:
        rig.pose.bones[name].matrix=desired[name]
        bpy.context.view_layer.update()
    bpy.context.view_layer.update()
    update_trail(p)
def socket(v):
    p=world_to_camera_view(scene,camera,rig.matrix_world@q(v));return [p.x*256,(1-p.y)*256]
def render(destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(destination);depth.base_path=str(destination.parent);depth.file_slots[0].path=destination.stem+'-depth-'
    bpy.ops.render.render(write_still=True)
def export_metadata():
    slots={'body':['body.base'],'head':['head.base'],'hair':['hair.silver','hair.chestnut'],'torso':['torso.tabard','torso.travel'],'legs':['legs.olive'],'boots':['boots.brown'],'gloves':['gloves.brown'],'armor':['armor.bronze'],'cape':['cape.gold','cape.teal',None],'weapon':['weapon.straight','weapon.falchion'],'headgear':[None,'headgear.helm']}
    keys=[];max_error=0
    for d,name in enumerate(DIRS):
        for i,p in enumerate(KEYS):
            set_pose(p,d)
            grip=rig.pose.bones['weapon.right'].matrix.translation
            intended=q(p['arms']['right']['end']);error=(grip-intended).length;max_error=max(max_error,error)
            assert error<1e-5,('Hand attachment error',d,i,error)
            keys.append({'direction':name,'index':i,'phase':p['phase'],'duration_ms':p['duration_ms'],'right_grip':socket(p['arms']['right']['end']),'left_hand':socket(p['arms']['left']['end']),'blade_tip':socket(p['swordTip']),'head_socket':socket(p['head']),'weapon_owner':'anatomical_right','source_socket':'weapon.right -> right.hand','grip_error_world':error})
    manifest={'version':4,'acceptance':'TECHNICAL_PROOF_ART_NOT_APPROVED','rig_family':'silver-scarf-A','canvas':[256,256],'native_canvas':[128,128],'resolve':'Compose opaque source visibility at 2x native size, then area-resolve to native 128px','directions':DIRS,'clips':{'attack':{'duration_ms':800,'frame_delays_ms':[p['duration_ms'] for p in KEYS],'keys':8}},'parts':{part:{'geometry_objects':len(objects),'source_is_complete':True,'attached_bones':sorted({obj['socket'] for obj in objects})} for part,objects in PARTS.items()},'slots':slots,'default':DEFAULT,'alternate':ALTERNATE,'coverage_rules':{'headgear.helm':{'hides_slots':['hair'],'reason':'Closed helmet replaces hair coverage; bald head remains complete'}},'poses':keys,'maximum_right_grip_error_world':max_error,'projection':{'camera_elevation_degrees':30,'orthographic_scale':2.65,'fixed_camera':True,'root_world':[0,0,0]},'trail':{'source':'Actual continuous right-hand blade base/tip samples','emitting_seconds':[.25,.36],'lifetime_seconds':.070,'active_key_indices':[3,4,5],'separate_per_weapon_shape':True,'scope':'Unapproved ribbon proof; translucent self-overlap and clipping require additional production review'},'limits':['Original modeled look is an unapproved prototype, not approved painted RO art','Only attack/ready keys; no complete locomotion action family','Single body-proportion family','Normal-based stylized lighting intentionally avoids cross-part cast shadows','Depth compositing is a research preview, not an integrated production game shader','No claim of actual RO ACT/SPR binary compatibility']}
    for part in manifest['parts'].values():
        part.update({'rig_family':'silver-scarf-A','directions':DIRS,'attack_keys':8,'is_mirrored':False})
    manifest['projection']['capture_shift_x']=camera.data.shift_x
    root=world_to_camera_view(scene,camera,Vector((0,0,0)))
    manifest['anchors']={'ground_root_source_pixels':[root.x*256,(1-root.y)*256],'shared_for_every_part_pose_and_facing':True}
    manifest['encoding']={'color':'8-bit RGBA straight alpha','depth':'24-bit integer packed big-endian into RGB, range 0..8 world units, code 0xffffff means blank','visibility':'Compose at 256x256 then premultiplied 2x2 resolve to 128x128','strip':'8 poses across; one facing per strip; fixed untrimmed source cells'}
    (OUT/'rig-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

export_metadata()
# The editable .blend includes playable held keys, not only a posed mannequin.
scene.render.fps=1000;scene.frame_start=1;scene.frame_end=801
for p,ms in zip(KEYS,DATA['times_ms']):
    scene.frame_set(ms+1);set_pose(p,1)
    for bone in rig.pose.bones:
        bone.rotation_mode='QUATERNION'
        bone.keyframe_insert(data_path='location',frame=ms+1)
        bone.keyframe_insert(data_path='rotation_quaternion',frame=ms+1)
        bone.keyframe_insert(data_path='scale',frame=ms+1)
for curve in rig.animation_data.action.fcurves:
    for key in curve.keyframe_points:key.interpolation='CONSTANT'
scene.frame_set(1);set_pose(KEYS[0],1);select(DEFAULT)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'silver-scarf-modular-source.blend'))
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'preview'
if mode=='preview':
    for i in [0,2,3,4,5,6]:
        set_pose(KEYS[i],1);select(DEFAULT);render(OUT/'blocking-review'/f'SE-{i:02}.png')
    set_pose(KEYS[0],1);select(ALTERNATE);render(OUT/'blocking-review/alternate.png')
elif mode=='batch':
    start=time.time();count=0
    for d,direction in enumerate(DIRS):
        for i,p in enumerate(KEYS):
            set_pose(p,d)
            for part in PARTS:
                dest=OUT/'parts'/part/direction/f'{i:02}.png'
                if dest.exists():continue
                select([part]);render(dest);count+=1
            # Full-scene reference checks use the same source scene, not the part compositor.
            if i in [0,2,4,5]:
                for variant,parts in [('default',DEFAULT),('alternate',ALTERNATE),('helmet',[x for x in DEFAULT if x!='hair.silver']+['headgear.helm'])]:
                    select(parts);render(OUT/'references'/variant/direction/f'{i:02}.png')
            print('BATCH_PROGRESS',direction,i,count,round(time.time()-start,2),flush=True)
    (OUT/'render-receipt.json').write_text(json.dumps({'blender':bpy.app.version_string,'new_part_frames':count,'part_items':len(PARTS),'directions':8,'pose_keys':8,'source_objects':sum(map(len,PARTS.values())),'seconds':time.time()-start,'engine':'Cycles CPU','samples':1,'source':'original complete meshes, independently rendered with no other slot geometry visible','scope':'Bounded modular source proof; not art approval'},indent=2)+'\n')
print('MODE_COMPLETE',mode,flush=True)
