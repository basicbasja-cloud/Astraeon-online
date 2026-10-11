"""Native face expression and whole-head pose; one geometry for all headings."""
import bpy,math,json
from mathutils import Vector,Matrix
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';center=Vector((.0553,-.045,1.601));turn=Matrix.Rotation(math.radians(-20),3,'Z')
face=bpy.data.objects[p+'Head'];donor=bpy.data.scenes['ASTRAEON_VROID_BASE_MALE_INSPECTION']
native=next(o for o in donor.objects if o.type=='MESH' and o.name.startswith('Face'))
backup=bpy.data.meshes.get('Anatomy05HeadBeforePose')
if backup is None:backup=face.data.copy();backup.name='Anatomy05HeadBeforePose';backup.use_fake_user=True
assert len(face.data.vertices)==len(native.data.vertices)
scale=Matrix.Diagonal((1.55,1.30,1.35));canonical=Matrix.Rotation(math.pi,3,'Z')
keys=native.data.shape_keys.key_blocks
for v,old in zip(face.data.vertices,backup.vertices):
    delta=(keys['target_3'].data[v.index].co-keys['Basis'].data[v.index].co)*0
    co=old.co+scale@canonical@delta
    # Lift/open the eye region continuously through the surrounding skin,
    # preserving the registered iris/white/lid surface relationships.
    eye=math.exp(-((abs(co.x-center.x)-.067)/.062)**4-((co.z-1.555)/.052)**4)
    front=max(0,min(1,(-co.y-.09)/.035))
    co.z+=(.014+(co.z-1.555)*.20)*eye*front
    v.co=center+turn@(co-center)
face.data.update()
for i,material in enumerate(list(face.data.materials)):
    if material is None or 'FaceBrow' not in material.name:continue
    if 'Anatomy05_DarkBrow' not in material.name:
        material=material.copy();material.name='Anatomy05_DarkBrow';face.data.materials[i]=material
    nodes=material.node_tree.nodes;links=material.node_tree.links
    if nodes.get('Anatomy05BrowDarken') is None:
        tex=next(n for n in nodes if n.type=='TEX_IMAGE');mix=nodes.new('ShaderNodeMixRGB');mix.name='Anatomy05BrowDarken';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.20,.15,.23,1)
        for link in list(tex.outputs['Color'].links):links.new(mix.outputs[0],link.to_socket)
        links.new(tex.outputs['Color'],mix.inputs[1])
for obj in s.objects:
    if not obj.name.startswith(p+'Hair_') or obj.type!='MESH':continue
    original=bpy.data.meshes.get('Anatomy05HairBeforePolish_'+obj.name)
    if original is None:continue
    for v,old in zip(obj.data.vertices,original.vertices):v.co=old.co
    if len(obj.data.vertices)==156:
        for ring in range(13):
            vs=list(obj.data.vertices)[ring*12:(ring+1)*12]
            c=sum((v.co.copy() for v in vs),start=Vector((0,0,0)))/12
            thin=(vs[3].co-c).normalized()
            for v in vs:v.co-=thin*(v.co-c).dot(thin)*.35
    for v in obj.data.vertices:
        d=v.co-center;d=Vector((d.x*.87,d.y*.97,d.z*.94));v.co=center+turn@d
    obj.data.update()
root=bpy.data.objects['ROOT_AnatomySource05'];saved=(root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
try:
    s.render.resolution_x=1280;s.render.resolution_y=1280
    for label,yaw in [('SE',45),('W',-90)]:
        root.rotation_euler.z=math.radians(yaw)
        s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'+label+'-face-pose-study.png'
        bpy.ops.render.render(write_still=True)
finally:root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath=saved
r=json.loads(s['anatomySourceReceipt']);r['headPoseStudy']={'yawDegrees':-20,'nativeExpressions':{'Neutral':1},'discardedTrial':'Angry .2 plus Surprised .2 produced an unsuitable smile','eyeRegionLift':.014,'eyeVerticalOpeningGain':.20,'hairDepthFraction':.65,'sharedAcrossHeadings':True,'ownerApproved':False};s['anatomySourceReceipt']=json.dumps(r)
print('SOURCE_FACE_POSE_STUDY_RENDERED')
