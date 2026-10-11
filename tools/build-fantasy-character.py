"""Fit an editable skeleton to the owner's textured model, retaining source UVs.

Run on fantasy-base-01-inspection.blend in an isolated Blender process. This is
the source gate, not an art approval. No previous candidate geometry is imported.
"""
import bpy, bmesh, json, math
from array import array
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'authoring/characters/swordsman-production/fantasy-base-01'
s=bpy.context.scene;s.name='ASTRAEON_FANTASY_PRODUCTION_01'
source=next(o for o in s.objects if o.type=='MESH')
oldroot=bpy.data.objects['ROOT_FantasyInspection'];oldroot.rotation_euler.z=0
mw=source.matrix_world.copy();source.parent=None
for v in source.data.vertices:v.co=mw@v.co
source.matrix_world=Matrix.Identity(4)
bpy.data.objects.remove(oldroot,do_unlink=True)
root=bpy.data.objects.new('ROOT_FantasyCharacter01',None);s.collection.objects.link(root)
data=bpy.data.armatures.new('RIG_FantasyCharacter01')
rig=bpy.data.objects.new('ARM_FantasyCharacter01',data);s.collection.objects.link(rig);rig.parent=root;rig.show_in_front=True
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None,deform=True):
    b=data.edit_bones.new(name);b.head=head;b.tail=tail;b.use_deform=deform
    if parent:b.parent=data.edit_bones[parent]
    b.align_roll(Vector((0,0,1)) if abs((Vector(tail)-Vector(head)).normalized().z)<.95 else Vector((0,-1,0)))
    return b
bone('root',(0,0,0),(0,0,.1),deform=False)
bone('Hips',(0,.018,.49),(0,.018,.56),'root')
bone('Spine',(0,.018,.56),(0,.024,.65),'Hips')
bone('Chest',(0,.024,.65),(0,.024,.766),'Spine')
bone('Neck',(0,.025,.766),(0,.028,.821),'Chest')
bone('Head',(0,.028,.821),(0,.031,.944),'Neck')
for side,sign in [('R',-1),('L',1)]:
    def pt(x,y,z):return (sign*x,y,z)
    bone('Clavicle.'+side,pt(.018,.024,.762),pt(.14,.018,.756),'Chest')
    bone('UpperArm.'+side,pt(.14,.018,.756),pt(.276,.015,.744),'Clavicle.'+side)
    bone('Forearm.'+side,pt(.276,.015,.744),pt(.395,.007,.735),'UpperArm.'+side)
    bone('Hand.'+side,pt(.395,.007,.735),pt(.441,.014,.735),'Forearm.'+side)
    for digit,yy,zz,xx,end in [('Index',-.007,.733,.440,.491),('Middle',.011,.740,.443,.498),('Ring',.030,.738,.439,.489),('Pinky',.044,.733,.436,.475)]:
        length=end-xx;xs=[xx,xx+length*.46,xx+length*.77,end]
        for j in range(3):bone(digit+str(j+1)+'.'+side,pt(xs[j],yy,zz),pt(xs[j+1],yy,zz),('Hand.'+side) if j==0 else digit+str(j)+'.'+side)
    points=[pt(.419,-.003,.725),pt(.430,-.025,.719),pt(.442,-.029,.716),pt(.451,-.030,.714)]
    for j in range(3):bone('Thumb'+str(j+1)+'.'+side,points[j],points[j+1],('Hand.'+side) if j==0 else 'Thumb'+str(j)+'.'+side)
    bone('Thigh.'+side,pt(.085,.019,.49),pt(.087,.012,.279),'Hips')
    bone('Shin.'+side,pt(.087,.012,.279),pt(.087,.034,.075),'Thigh.'+side)
    bone('Foot.'+side,pt(.087,.034,.075),pt(.087,-.067,.037),'Shin.'+side)
    bone('Toe.'+side,pt(.087,-.067,.037),pt(.087,-.109,.029),'Foot.'+side)
    bone('CTRL_Foot.'+side,pt(.087,.034,.075),pt(.087,-.067,.037),'root',False)
    bone('CTRL_Knee.'+side,pt(.087,-.28,.28),pt(.087,-.28,.33),'root',False)
for j in range(3):bone('Cape'+str(j),(0,.082,.747-j*.112),(0,.056,.635-j*.112),'Chest' if j==0 else 'Cape'+str(j-1))
bone('CTRL_Sword',(0,0,0),(0,0,.08),'root',False)
bpy.ops.object.mode_set(mode='OBJECT')
for p in rig.pose.bones:p.rotation_mode='QUATERNION'
for side in ['R','L']:
    c=rig.pose.bones['Shin.'+side].constraints.new('IK');c.name='GroundContactIK';c.target=rig;c.subtarget='CTRL_Foot.'+side;c.pole_target=rig;c.pole_subtarget='CTRL_Knee.'+side;c.chain_count=2;c.influence=0
    c.use_stretch=False;c.pole_angle=math.radians(-90)
# Partition original polygons, preserving every face, every loop UV and paint.
texture=next(n.image for n in source.active_material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.colorspace_settings.name=='sRGB')
pixels=array('f',[0])*len(texture.pixels);texture.pixels.foreach_get(pixels)
tw,th=texture.size;uv=source.data.uv_layers.active
def color(p):
    u=sum(uv.data[i].uv.x for i in p.loop_indices)/len(p.loop_indices);v=sum(uv.data[i].uv.y for i in p.loop_indices)/len(p.loop_indices)
    idx=(min(th-1,max(0,int(v*th)))*tw+min(tw-1,max(0,int(u*tw))))*4
    return pixels[idx:idx+3]
labels={}
for p in source.data.polygons:
    co=sum((source.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    r,g,b=color(p)
    hair=(b>g*.95 and r>g*.93 and co.z>.793)
    if co.z>.813 or hair:label='HeadHair'
    elif .37<co.z<.712 and abs(co.x)<.34 and co.y>.014 and (g>.07 and r>g*1.15 and b<g*.78 or min(r,g,b)>.55):label='Cape'
    else:label='BodyOutfit'
    labels[p.index]=label
# Fill texture-noise islands on the continuous cloth surface. Growth is confined
# to the source cape's back-space; it cannot reach the arms, hair or front tunic.
adjacent=[set() for _ in source.data.polygons];edge_faces={}
for p in source.data.polygons:
    for edge in p.edge_keys:edge_faces.setdefault(tuple(sorted(edge)),[]).append(p.index)
for fs in edge_faces.values():
    for f in fs:adjacent[f].update(i for i in fs if i!=f)
for iteration in range(5):
    additions=[]
    for p in source.data.polygons:
        if labels[p.index]!='BodyOutfit':continue
        co=sum((source.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
        if not (.37<co.z<.712 and abs(co.x)<.34 and co.y>.014):continue
        neighbors=[i for i in adjacent[p.index] if labels[i]=='Cape']
        if len(neighbors)>=2 or abs(co.x)>.14 and any(p.normal.dot(source.data.polygons[i].normal)>.35 for i in neighbors):additions.append(p.index)
    for i in additions:labels[i]='Cape'
modules={}
for label in ['BodyOutfit','HeadHair','Cape']:
    mesh=source.data.copy();obj=bpy.data.objects.new('F01_'+label,mesh);s.collection.objects.link(obj)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[f for f in bm.faces if labels[f.index]!=label],context='FACES')
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj['spriteModule']=label;obj['sourcePolygonCount']=len(mesh.polygons);obj.parent=rig
    mod=obj.modifiers.new('Deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    modules[label]=obj
assert sum(len(o.data.polygons) for o in modules.values())==len(source.data.polygons)
def hidden_material(name,col):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value=(*col,1);shader.inputs['Roughness'].default_value=.85
    return mat
hidden_materials={'BodyOutfit':hidden_material('F01_HiddenNavy',(.024,.025,.035)),
                  'HeadHair':hidden_material('F01_HiddenNeck',(.43,.27,.17)),
                  'Cape':hidden_material('F01_HiddenCapeEdge',(.62,.34,.085))}
repair_counts={}
for label,obj in modules.items():
    obj.data.materials.append(hidden_materials[label]);idx=len(obj.data.materials)-1
    bm=bmesh.new();bm.from_mesh(obj.data)
    boundary=[e for e in bm.edges if e.is_boundary]
    filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[])
    obj.data.materials.append(hidden_material('F01_HiddenOlive_'+label,(.072,.058,.035)))
    for face in filled:face.material_index=idx+1 if label=='BodyOutfit' and face.calc_center_median().z<.49 else idx
    repair_counts[label]={'boundaryEdgesBefore':len(boundary),'newCapFaces':len(filled)}
    # Triangulate newly concealed caps only; preserve every supplied UV polygon.
    if filled:bmesh.ops.triangulate(bm,faces=filled)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
source.name='REFERENCE_OriginalFantasyMesh';source.hide_render=True;source.hide_set(True);source['referenceOnly']=True
# Tone the imported gray glove/boot patches through materials, retaining source
# UVs and paint detail. Geometry and source images themselves remain unchanged.
def tint_material(name,tint):
    mat=source.active_material.copy();mat.name=name
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    for link in list(shader.inputs['Metallic'].links):links.remove(link)
    shader.inputs['Metallic'].default_value=0
    colorlink=shader.inputs['Base Color'].links[0];socket=colorlink.from_socket;links.remove(colorlink)
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*tint,1)
    links.new(socket,mix.inputs[1]);links.new(mix.outputs[0],shader.inputs['Base Color'])
    shader.inputs['Emission Strength'].default_value=.15;links.new(mix.outputs[0],shader.inputs['Emission Color'])
    for node in nodes:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.25
    return mat
glove=tint_material('F01_OriginalPaint_Gloves',(.62,.39,.23));boots=tint_material('F01_OriginalPaint_Boots',(.80,.58,.37));bracer=tint_material('F01_OriginalPaint_Bronze',(.86,.65,.37))
body=modules['BodyOutfit'];first=len(body.data.materials)
for mat in [glove,boots,bracer]:body.data.materials.append(mat)
for p in body.data.polygons:
    if p.material_index!=0:continue
    co=sum((body.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    if abs(co.x)>.403 and co.z>.67:p.material_index=first
    elif co.z<.31:p.material_index=first+1
    elif abs(co.x)>.32 and co.z>.69:p.material_index=first+2
def painted_shader(mat):
    """Fixed world-normal paint shading: identical for independent module bakes."""
    if mat.get('factoryPaintShader'):return
    mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shader=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not shader:return
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    geometry=nodes.new('ShaderNodeNewGeometry');dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=Vector((-.35,-.65,.68)).normalized();links.new(geometry.outputs['Normal'],dot.inputs[0])
    maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';maximum.inputs[1].default_value=0;links.new(dot.outputs['Value'],maximum.inputs[0])
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=.22;links.new(maximum.outputs[0],multiply.inputs[0])
    add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.78;links.new(multiply.outputs[0],add.inputs[0])
    color=nodes.new('ShaderNodeMixRGB');color.blend_type='MULTIPLY';color.inputs[0].default_value=1
    original=shader.inputs['Base Color']
    if original.is_linked:links.new(original.links[0].from_socket,color.inputs[1])
    else:color.inputs[1].default_value=original.default_value
    links.new(add.outputs[0],color.inputs[2]);emission=nodes.new('ShaderNodeEmission');links.new(color.outputs[0],emission.inputs['Color'])
    for link in list(output.inputs['Surface'].links):links.remove(link)
    links.new(emission.outputs[0],output.inputs['Surface']);mat['factoryPaintShader']=True
deform={b.name:(b.head_local,b.tail_local) for b in data.bones if b.use_deform}
def distance(p,a,b):
    d=b-a;t=min(1,max(0,(p-a).dot(d)/d.length_squared));return (p-(a+d*t)).length
def blend(weights):
    weights=sorted(((n,w) for n,w in weights.items() if w>1e-6),key=lambda p:-p[1])[:4];total=sum(w for n,w in weights)
    return {n:w/total for n,w in weights}
def weights(co,label):
    if label=='HeadHair':return {'Head':1}
    if label=='Cape':
        k=max(0,min(2,(.729-co.z)/.112));i=int(k);return {'Cape'+str(i):1-k+i,**({'Cape'+str(i+1):k-i} if i<2 else {})}
    ax=abs(co.x);side='R' if co.x<0 else 'L'
    if ax>.406 and co.z>.675:
        if co.y<-.019:digit='Thumb'
        else:digit=min([('Index',-.007),('Middle',.011),('Ring',.030),('Pinky',.044)],key=lambda pair:abs(co.y-pair[1]))[0]
        names=['Hand.'+side]+[digit+str(j)+'.'+side for j in range(1,4)]
        if ax<.426:names=['Hand.'+side,'Forearm.'+side]
    elif ax>.143 and co.z>.65:names=['Clavicle.'+side,'UpperArm.'+side,'Forearm.'+side,'Hand.'+side]
    elif co.z<.465:
        names=['Hips','Thigh.'+side,'Shin.'+side,'Foot.'+side,'Toe.'+side]
        # Tunic flaps follow pelvis/thigh, never shin/foot behind another surface.
        if co.z>.36:names=['Hips','Thigh.'+side]
        if co.z<.20:names=['Shin.'+side,'Foot.'+side,'Toe.'+side]
    else:names=['Hips','Spine','Chest','Neck']
    ranked=sorted([(distance(co,*deform[n]),n) for n in names])
    sharpness=.008 if ax>.426 else .025
    return blend({n:math.exp(-(d-ranked[0][0])/sharpness) for d,n in ranked[:3]})
for label,obj in modules.items():
    ws=[weights(v.co,label) for v in obj.data.vertices]
    adjacency=[set() for _ in ws]
    for e in obj.data.edges:a,b=e.vertices;adjacency[a].add(b);adjacency[b].add(a)
    # Limited Laplacian cleanup on source-connected neighbors. Avoid cross-hand,
    # cape/body, and facial influence leakage by smoothing within each module.
    for iteration in range(3):
        updated=[]
        for i,w in enumerate(ws):
            if label=='HeadHair' or not adjacency[i]:updated.append(w);continue
            mixed={n:.65*x for n,x in w.items()}
            for j in adjacency[i]:
                for n,x in ws[j].items():mixed[n]=mixed.get(n,0)+.35*x/len(adjacency[i])
            updated.append(blend(mixed))
        ws=updated
    groups={n:obj.vertex_groups.new(name=n) for n in deform}
    for i,w in enumerate(ws):
        for n,x in w.items():groups[n].add([i],x,'REPLACE')
    # Add render density on existing UV surfaces without inventing texture tiles.
    sub=obj.modifiers.new('SurfaceSubdivision','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1;sub.render_levels=1
def reset():
    for p in rig.pose.bones:p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
def turn(name,axis,angle):
    p=rig.pose.bones[name];local=p.bone.matrix_local.to_3x3().inverted()@Vector(axis)
    p.rotation_quaternion=p.rotation_quaternion@Quaternion(local.normalized(),math.radians(angle))
def relaxed(curl=True):
    reset()
    for side,sign in [('R',-1),('L',1)]:
        turn('UpperArm.'+side,(0,1,0),sign*69)
        turn('Forearm.'+side,(0,1,0),-sign*8)
        if curl:
            for digit in ['Index','Middle','Ring','Pinky']:
                for j,angle in enumerate([45,85,70] if side=='R' else [15,18,12],1):rig.pose.bones[digit+str(j)+'.'+side].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
            for j,angle in enumerate([12,32,40],1):rig.pose.bones['Thumb'+str(j)+'.R'].rotation_quaternion=Quaternion((1,0,0),math.radians(-angle))
    turn('Cape0',(1,0,0),12);turn('Cape1',(1,0,0),8);turn('Cape2',(1,0,0),6)
    bpy.context.view_layer.update()
relaxed()
# Source-authored sword aligned to the curved right fingers. All source geometry
# stays editable and moves with the same hand; semantic exports omit occlusions.
def material(name,col,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.65;return m
gold=material('F01_Bronze',(.45,.27,.085),.35);steel=material('F01_Steel',(.6,.67,.73),.15);leather=material('F01_Grip',(.055,.032,.024))
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat)
    o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.parent=rig;o['spriteModule']='Weapon'
    g=o.vertex_groups.new(name='Hand.R');g.add(list(range(len(verts))),1,'REPLACE');m=o.modifiers.new('HandAttachment','ARMATURE');m.object=rig;return o
center=Vector((-.448,.012,.721));axis=Vector((0,-1,0))
def cylinder(name,a,b,radius,mat):
    tangent=(b-a).normalized();seed=Vector((1,0,0)) if abs(tangent.x)<.9 else Vector((0,0,1))
    u=(seed-tangent*seed.dot(tangent)).normalized();v=tangent.cross(u).normalized();verts=[]
    for end in [a,b]:
        for i in range(12):verts.append(end+radius*(u*math.cos(i*math.tau/12)+v*math.sin(i*math.tau/12)))
    faces=[(i,(i+1)%12,(i+1)%12+12,i+12) for i in range(12)]+[tuple(range(11,-1,-1)),tuple(range(12,24))]
    return mesh(name,verts,faces,mat)
cylinder('F01_SwordHandle',center-axis*.044,center+axis*.044,.0065,leather)
guard=center+axis*.05
cylinder('F01_SwordGuard',guard+Vector((-.036,0,0)),guard+Vector((.036,0,0)),.006,gold)
cylinder('F01_SwordPommel',center-axis*.057,center-axis*.045,.009,gold)
start=guard+axis*.008;tip=guard+axis*.335;width=.017;depth=.003
mesh('F01_SwordBlade',[start+Vector((-width,0,0)),start+Vector((width,0,0)),start+Vector((0,0,depth)),start-Vector((0,0,depth)),tip],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(0,3,1,2)],steel)
for obj in s.objects:
    if obj.get('spriteModule'):
        for slot in obj.material_slots:
            if slot.material:painted_shader(slot.material)
p=rig.pose.bones['Hand.R'];current=(p.matrix@p.bone.matrix_local.inverted()).to_3x3()@axis
delta=current.normalized().rotation_difference(Vector((.45,-.3,-.841)).normalized())
p.matrix=Matrix.Translation(p.head)@delta.to_matrix().to_4x4()@Matrix.Translation(-p.head)@p.matrix
bpy.context.view_layer.update()
s['restingHandQuaternion']=json.dumps(list(p.rotation_quaternion))
s['swordContact']=json.dumps({'centerModel':list(center),'axisModel':list(axis),'radius':.0065,'bone':'Hand.R','visualAccepted':False})
s['factoryWorkspace']=str(BASE);s['factoryVersion']='fantasy-base-1';s['ownerApproved']=False;s['runtimeAdmitted']=False
s['directions']=json.dumps([['S',0],['SW',-45],['W',-90],['NW',-135],['N',-180],['NE',-225],['E',-270],['SE',45]])
s['rigObject']=rig.name;s['rootObject']=root.name;s['logicalModules']=json.dumps(['BodyOutfit','HeadHair','Headgear','Weapon','Cape'])
s['sourceLicense']='User-supplied archive; no license document included; local authoring input.'
s['sourceTopologyStatus']='Source boundaries and generated topology require deformation inspection.'
s.render.resolution_x=320;s.render.resolution_y=320
s.camera.name='CAM_FantasySprite';s.camera.data.ortho_scale=1.720090866
s.camera.rotation_euler=(math.radians(65),0,0)
s.camera.location=(0,-4.29528284,2.6197443)
s['canvas']=json.dumps([320,320]);s['rootPixel']=json.dumps([160,264])
root.rotation_euler.z=math.radians(45)
report={'rig':rig.name,'bones':len(data.bones),'digitBones':30,'modules':{n:{'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for n,o in modules.items()},'sourcePolygonsRetained':len(source.data.polygons),'concealedSurfaceRepairs':repair_counts,'ownerApproved':False,'runtimeAdmitted':False,'status':'FITTED_RIG_REQUIRES_DEFORMATION_AND_GRIP_REVIEW'}
(OUT/'rig-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'.character-tools/checkpoints/fantasy-base-01-fitted.blend'))
for d,y in json.loads(s['directions']):
    root.rotation_euler.z=math.radians(y);s.render.resolution_x=640;s.render.resolution_y=640
    s.render.filepath=str(OUT/'renders'/(d+'-fitted.png'));bpy.ops.render.render(write_still=True)
# Equipment removals diagnose hidden source surfaces before independent modules.
root.rotation_euler.z=math.radians(-135)
modules['Cape'].hide_render=True;s.render.filepath=str(OUT/'renders/NW-cape-removed.png');bpy.ops.render.render(write_still=True);modules['Cape'].hide_render=False
print('FANTASY_FIT_COMPLETE '+json.dumps(report),flush=True)
