"""Apply the bounded source-space clearance fit to sword and whole palm together."""
import bpy,math,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05'];body=bpy.data.objects[p+'Body']
r=json.loads(s['anatomySourceReceipt']);guard=bpy.data.objects['GUIDE_guard'].location.copy()
oldtip=Vector(bpy.data.scenes['ASTRAEON_ASSET_FIT_04']['swordDepthOriginalTip']);newtip=oldtip+Vector((.10,.10,-.08))
oldaxis=(oldtip-guard).normalized();axis=(newtip-guard).normalized();turn=oldaxis.rotation_difference(axis)
rigid=Matrix.Translation(guard)@turn.to_matrix().to_4x4()@Matrix.Translation(-guard)
ratio=(newtip-guard).length/(oldtip-guard).length
for obj in s.objects:
    if not obj.name.startswith((p+'Blade_',p+'Hilt_',p+'Identity_Weapon')):continue
    key='Anatomy05BeforeClearance_'+obj.data.name
    backup=bpy.data.meshes.get(key) if obj.type=='MESH' else bpy.data.curves.get(key)
    if backup is None:backup=obj.data.copy();backup.name=key;backup.use_fake_user=True
    if obj.type=='MESH':
        for v,old in zip(obj.data.vertices,backup.vertices):
            co=old.co.copy()
            if obj.name.startswith(p+'Blade_'):co+=oldaxis*((co-guard).dot(oldaxis)*(ratio-1))
            v.co=rigid@co
        obj.data.update()
    elif obj.type=='CURVE':
        for sp,oldsp in zip(obj.data.splines,backup.splines):
            for point,old in zip(sp.points,oldsp.points):point.co=(*(rigid@old.co.xyz),1)
backup=bpy.data.meshes.get('Anatomy05BodyBeforeClearance')
if backup is None:backup=body.data.copy();backup.name='Anatomy05BodyBeforeClearance';backup.use_fake_user=True
handgroups={g.index for g in body.vertex_groups if g.name.startswith('J_Bip_R_') and any(d in g.name for d in ['Hand','Thumb','Index','Middle','Ring','Little'])}
for v,old in zip(body.data.vertices,backup.vertices):
    total=sum(g.weight for g in v.groups);amount=sum(g.weight for g in v.groups if g.group in handgroups)/max(total,.000001)
    v.co=old.co.lerp(rigid@old.co,amount)
body.data.update()
regions={'Glove_R':[],'Sleeve_R':[]}
for face in body.data.polygons:
    weights={}
    for i in face.vertices:
        for g in body.data.vertices[i].groups:
            name=body.vertex_groups[g.group].name;weights[name]=weights.get(name,0)+g.weight
    name=max(weights,key=weights.get)
    if not name.startswith('J_Bip_R_'):continue
    if any(d in name for d in ['Hand','Index','Middle','Ring','Little','Thumb']):regions['Glove_R'].append(face)
    elif any(d in name for d in ['UpperArm','LowerArm','Shoulder']):regions['Sleeve_R'].append(face)
for name,faces in regions.items():
    indices=sorted({i for f in faces for i in f.vertices});obj=bpy.data.objects[p+'Cloth_'+name]
    assert len(indices)==len(obj.data.vertices)
    offset=.003 if name.startswith('Glove') else .014
    for v,i in zip(obj.data.vertices,indices):v.co=body.data.vertices[i].co+body.data.vertices[i].normal*offset
    obj.data.update()
original=r.get('handTargetsBeforeClearance')
if original is None:r['handTargetsBeforeClearance']=json.loads(json.dumps(r['handTargets']));original=r['handTargetsBeforeClearance']
for label in ['center','wrist']:r['handTargets']['R'][label]=list(rigid@Vector(original['R'][label]))
r['handTargets']['R']['axis']=list(axis)
# Refit the corrected plate to the updated wrist/sleeve in the same source.
elbow=bpy.data.objects['GUIDE_elbow_R'].location.copy();wrist=Vector(r['handTargets']['R']['wrist']);direction=(wrist-elbow).normalized()
across=Vector((0,1,0)).cross(direction).normalized();front=direction.cross(across).normalized()
if front.y>0:front=-front
sleeve=bpy.data.objects[p+'Cloth_Sleeve_R'];tree=BVHTree.FromPolygons([v.co for v in sleeve.data.vertices],[list(f.vertices) for f in sleeve.data.polygons])
verts=[];rows=9;cols=24
for row in range(rows):
    t=.18+.75*row/(rows-1);center=elbow.lerp(wrist,t)
    for j in range(cols):
        a=math.tau*j/cols;radial=across*math.cos(a)+front*math.sin(a)
        hit,no,idx,distance=tree.ray_cast(center+radial*.25,-radial,.45)
        radius=max(.022,min(.095,(.25-distance if hit is not None else .032*(1-t)+.020*t)+.006))
        verts.append(center+radial*radius)
plate=bpy.data.objects[p+'Polish_Bracer_R']
for v,co in zip(plate.data.vertices,verts):v.co=co
plate.data.update()
for row in [0,8]:
    curve=bpy.data.objects[p+'Polish_BracerRim_R_'+str(row)]
    for point,co in zip(curve.data.splines[0].points,verts[row*cols:(row+1)*cols]+[verts[row*cols]]):point.co=(*co,1)
ridge=bpy.data.objects[p+'Polish_BracerRidge_R']
for point,row in zip(ridge.data.splines[0].points,[0,2,4,6,8]):point.co=(*(verts[row*cols+6]+front*.003),1)
r['weaponClearanceStudy']={'oldTip':list(oldtip),'newTip':list(newtip),'rotationDegrees':math.degrees(turn.angle),'referenceTipDeviationPixels':1.18481,'minimumTipGroundClearance':newtip.z,'palmAndHiltShareRigidTransform':True,'fingerLengthsScaled':False,'viewDependentGeometry':False,'ownerApproved':False}
s['anatomySourceReceipt']=json.dumps(r)
saved=(root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath)
try:
    s.render.resolution_x=1280;s.render.resolution_y=1280
    for d,yaw in [('SE',45),('NW',-135)]:
        root.rotation_euler.z=math.radians(yaw);s.render.filepath='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'+d+'-clearance-study.png';bpy.ops.render.render(write_still=True)
finally:root.rotation_euler.z,s.render.resolution_x,s.render.resolution_y,s.render.filepath=saved
print('BOUNDED_SOURCE_CLEARANCE_STUDY '+json.dumps(r['weaponClearanceStudy']))
