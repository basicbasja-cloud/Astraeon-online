"""Source-native armor, shoe, cape and hair fitting on the fresh anime anatomy."""
import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;assert s.name=='ASTRAEON_ANATOMY_SOURCE_05'
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05'];body=bpy.data.objects[p+'Body']
receipt=json.loads(s['anatomySourceReceipt'])
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
P['blade_tip']=Vector(bpy.data.scenes['ASTRAEON_ASSET_FIT_04']['swordDepthOriginalTip'])
bronze=bpy.data.materials['Fit04_ForgedBronze'];gold=bpy.data.materials['Fit04_GoldTrim'];leather=bpy.data.materials['Fit04_BootLeather']
for obj in list(s.objects):
    if obj.name.startswith(p+'Polish_'):bpy.data.objects.remove(obj,do_unlink=True)
def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(p+'Polish_'+name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(p+'Polish_'+name,data);s.collection.objects.link(obj);obj.parent=root;data.materials.append(mat)
    for f in data.polygons:f.use_smooth=True
    uv=data.uv_layers.new(name='PainterSurface')
    xs=[v.co.x for v in data.vertices];zs=[v.co.z for v in data.vertices]
    for loop in data.loops:
        co=data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((co.x-min(xs))/max(max(xs)-min(xs),.001),(co.z-min(zs))/max(max(zs)-min(zs),.001))
    return obj
def line(name,points,radius,mat):
    data=bpy.data.curves.new(p+'Polish_'+name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    sp=data.splines.new('POLY');sp.points.add(len(points)-1)
    for point,co in zip(sp.points,points):point.co=(*co,1)
    obj=bpy.data.objects.new(p+'Polish_'+name,data);s.collection.objects.link(obj);obj.parent=root;data.materials.append(mat);return obj
def diamond(name,c,rx,rz,mat):
    return mesh(name,[c+Vector((-rx,0,0)),c+Vector((0,0,rz)),c+Vector((rx,0,0)),c+Vector((0,0,-rz)),c+Vector((0,-.012,0))],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],mat)
# Each bracer is a continuous curved plate with its own wrist opening.
for side in ['R','L']:
    elbow=P['elbow_'+side];wrist=Vector(receipt['handTargets'][side]['wrist']);axis=(wrist-elbow).normalized()
    across=Vector((0,1,0)).cross(axis).normalized();front=axis.cross(across).normalized()
    if front.y>0:front=-front
    verts=[];rows=9;cols=24
    for row in range(rows):
        t=.12+.83*row/(rows-1);c=elbow.lerp(wrist,t)
        radius=.079*(1-t)+.045*t
        for j in range(cols):
            a=math.tau*j/cols;verts.append(c+across*radius*math.cos(a)+front*radius*math.sin(a))
    faces=[(r*cols+j,r*cols+(j+1)%cols,(r+1)*cols+(j+1)%cols,(r+1)*cols+j) for r in range(rows-1) for j in range(cols)]
    plate=mesh('Bracer_'+side,verts,faces,bronze)
    solid=plate.modifiers.new('ForgedPlateThickness','SOLIDIFY');solid.thickness=.006;solid.offset=0
    bevel=plate.modifiers.new('PlateEdgeBevel','BEVEL');bevel.width=.002;bevel.segments=2
    for r in [0,rows-1]:line('BracerRim_'+side+'_'+str(r),verts[r*cols:(r+1)*cols]+[verts[r*cols]],.004,gold)
    line('BracerRidge_'+side,[elbow.lerp(wrist,t)+front*(.079*(1-t)+.045*t+.005) for t in [.14,.3,.5,.7,.94]],.0025,gold)
    for obj in s.objects:
        if obj.name.startswith((p+'Forged_Bracer',p+'Bracer_')):obj.hide_render=True
    # Boot foot room and sole derive from the new actual foot, not old bulbs.
    boot=bpy.data.objects[p+'Cloth_Boot_'+side];backup=bpy.data.meshes.get('Anatomy05BootBeforePolish_'+side)
    if backup is None:backup=boot.data.copy();backup.name='Anatomy05BootBeforePolish_'+side;backup.use_fake_user=True
    ankle=P['ankle_'+side]
    for v,old in zip(boot.data.vertices,backup.vertices):
        v.co=old.co;t=max(0,min(1,(ankle.z+.10-v.co.z)/.12))
        v.co.x=ankle.x+(old.co.x-ankle.x)*(1+.18*t)
        v.co.y=ankle.y+(old.co.y-ankle.y)*(1+.28*t)
        v.co.z+=.016*t
    boot.data.update();vs=[v.co.copy() for v in boot.data.vertices]
    floor=min(v.z for v in vs);low=[v for v in vs if v.z<floor+.10]
    xmin=min(v.x for v in low);xmax=max(v.x for v in low);ymin=min(v.y for v in low);ymax=max(v.y for v in low)
    cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;rx=(xmax-xmin)/2+.006;ry=(ymax-ymin)/2+.006
    verts=[];cols=40
    for z,factor in [(floor-.006,.97),(floor+.013,1.02),(floor+.029,1)]:
        for j in range(cols):
            a=math.tau*j/cols;xx=math.copysign(abs(math.cos(a))**.72,math.cos(a));yy=math.copysign(abs(math.sin(a))**.8,math.sin(a))
            verts.append(Vector((cx+rx*factor*xx,cy+ry*factor*yy,z)))
    faces=[tuple(range(cols-1,-1,-1)),tuple(range(2*cols,3*cols))]
    faces.extend((r*cols+j,r*cols+(j+1)%cols,(r+1)*cols+(j+1)%cols,(r+1)*cols+j) for r in range(2) for j in range(cols))
    mesh('BootSole_'+side,verts,faces,leather);line('BootWelt_'+side,verts[2*cols:]+[verts[2*cols]],.003,bronze)
    knee=P['knee_'+side];axis=(knee-ankle).normalized();across=Vector((1,0,0));front=axis.cross(across).normalized()
    verts=[];rows=3;cols=32
    for row,t in enumerate([.70,.84,.94]):
        c=ankle.lerp(knee,t);r=.074+.015*t
        for j in range(cols):
            a=math.tau*j/cols;verts.append(c+across*r*math.cos(a)+front*r*math.sin(a))
    cuff=mesh('BootKneeCuff_'+side,verts,[(r*cols+j,r*cols+(j+1)%cols,(r+1)*cols+(j+1)%cols,(r+1)*cols+j) for r in range(2) for j in range(cols)],leather)
    thick=cuff.modifiers.new('BootCuffThickness','SOLIDIFY');thick.thickness=.007
    for r in [0,2]:line('BootKneeRim_'+side+'_'+str(r),verts[r*cols:(r+1)*cols]+[verts[r*cols]],.0035,bronze)
    c=ankle.lerp(knee,.84)+Vector((0,-.095,0));diamond('BootCrest_'+side,c,.025,.039,gold)
# Match the hilt to the native hand. Diameter is physical, shared across views.
hilt=bpy.data.objects[p+'Hilt_Provisional'];guard=P['guard'];axis=(P['blade_tip']-guard).normalized()
backup=bpy.data.meshes.get('Anatomy05HiltBeforePolish')
if backup is None:backup=hilt.data.copy();backup.name='Anatomy05HiltBeforePolish';backup.use_fake_user=True
for v,old in zip(hilt.data.vertices,backup.vertices):
    axial=(old.co-guard).dot(axis);center=guard+axis*axial
    v.co=guard+axis*(axial*.80)+(old.co-center)*.625
hilt.data.update()
# Restore the measured asymmetric full cape, retaining genuine depth and UVs.
source=bpy.data.scenes['ASTRAEON_SOURCE_LOOKDEV_03']
for obj in s.objects:
    if obj.name.startswith(p+'CapeRefit_'):obj.hide_render=True
for name in ['Cape_PrimaryMass','Cape_Hem','Cape_LightningStudy']:
    old=next(o for o in source.objects if o.name==name)
    obj=old.copy();obj.data=old.data.copy();obj.name=p+'Polish_'+name;s.collection.objects.link(obj);obj.parent=root;obj.hide_render=False
    obj['authority']='Original measured concept outline; full modeled depth, not an image card'
# Give each existing hair lock a rounder depth profile at every heading.
haircenter=Vector((.0553,-.045,1.601))
for obj in s.objects:
    if not obj.name.startswith(p+'Hair_') or obj.type!='MESH':continue
    key='Anatomy05HairBeforePolish_'+obj.name;backup=bpy.data.meshes.get(key)
    if backup is None:backup=obj.data.copy();backup.name=key;backup.use_fake_user=True
    for v,old in zip(obj.data.vertices,backup.vertices):v.co=old.co
    if len(obj.data.vertices)==156:
        for ring in range(13):
            vs=list(obj.data.vertices)[ring*12:(ring+1)*12]
            center=sum((v.co.copy() for v in vs),start=Vector((0,0,0)))/12
            thin=(vs[3].co-center).normalized()
            for v in vs:v.co+=thin*(v.co-center).dot(thin)*.70
    for v in obj.data.vertices:
        d=v.co-haircenter;v.co=haircenter+Vector((d.x*.87,d.y*.97,d.z*.94))
    obj.data.update()
# Native anime iris palette through the original registered UVs.
head=bpy.data.objects[p+'Head']
for i,mat in enumerate(list(head.data.materials)):
    if mat and 'EyeIris' in mat.name:
        copy=mat.copy();copy.name='Anatomy05_VioletIris';head.data.materials[i]=copy
        nodes=copy.node_tree.nodes;links=copy.node_tree.links
        tex=next(n for n in nodes if n.type=='TEX_IMAGE');hue=nodes.new('ShaderNodeHueSaturation')
        hue.inputs['Hue'].default_value=.60;hue.inputs['Saturation'].default_value=.30;hue.inputs['Value'].default_value=.82
        for link in list(tex.outputs['Color'].links):links.new(hue.outputs[0],link.to_socket)
        links.new(tex.outputs['Color'],hue.inputs['Color'])
receipt['polish']=['native-depth hair tufts','measured asymmetric full cape','new forearm plates around corrected wrist','new fitted shoe soles and knee cuffs','native iris UV recolor','hilt fitted to native hand diameter']
s['anatomySourceReceipt']=json.dumps(receipt)
out='C:/Users/Lenovo/Bas/Astra online/authoring/characters/swordsman-production/anatomy-base-05/renders/'
s.render.resolution_x=1280;s.render.resolution_y=1280
for direction,angle in [('SE',45),('W',-90),('NW',-135),('N',-180),('S',0)]:
    root.rotation_euler.z=math.radians(angle);s.render.filepath=out+direction+'-polished-base-large.png';bpy.ops.render.render(write_still=True)
root.rotation_euler.z=math.radians(45);s.render.resolution_x=320;s.render.resolution_y=320
print('NEW_BASE_SOURCE_POLISHED; NO_OWNER_APPROVAL_OR_PRODUCTION_RIG')
