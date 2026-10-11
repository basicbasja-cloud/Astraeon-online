"""Fit armor to the actual sleeve; close the physical hilt/pommel gap.

Edits only the owned anatomy-05 source, with backups for repeatable fitting.
This is a static study, not a rig or an acceptance certificate.
"""
import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05']
r=json.loads(s['anatomySourceReceipt'])
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
P['blade_tip']=Vector(bpy.data.scenes['ASTRAEON_ASSET_FIT_04']['swordDepthOriginalTip'])
guard=P['guard'];axis=(P['blade_tip']-guard).normalized()
pommel=bpy.data.objects[p+'Identity_WeaponPommel']
backup=bpy.data.meshes.get('Anatomy05PommelBeforeContact')
if backup is None:backup=pommel.data.copy();backup.name='Anatomy05PommelBeforeContact';backup.use_fake_user=True
for v,old in zip(pommel.data.vertices,backup.vertices):v.co=old.co+axis*.045
pommel.data.update()
fit={}
for side in ['R','L']:
    elbow=P['elbow_'+side];wrist=Vector(r['handTargets'][side]['wrist']);direction=(wrist-elbow).normalized()
    across=Vector((0,1,0)).cross(direction).normalized();front=direction.cross(across).normalized()
    if front.y>0:front=-front
    sleeve=bpy.data.objects[p+'Cloth_Sleeve_'+side]
    tree=BVHTree.FromPolygons([v.co for v in sleeve.data.vertices],[list(f.vertices) for f in sleeve.data.polygons],all_triangles=False)
    plate=bpy.data.objects[p+'Polish_Bracer_'+side];rows=9;cols=24;radii=[];verts=[]
    for row in range(rows):
        t=.18+.75*row/(rows-1);center=elbow.lerp(wrist,t)
        for j in range(cols):
            a=math.tau*j/cols;radial=across*math.cos(a)+front*math.sin(a)
            hit,normal,index,distance=tree.ray_cast(center+radial*.25,-radial,.45)
            radius=(.25-distance if hit is not None else .032*(1-t)+.020*t)+.006
            radius=max(.022,min(.095,radius));radii.append(radius)
            verts.append(center+radial*radius)
    for v,co in zip(plate.data.vertices,verts):v.co=co
    plate.data.update()
    for row in [0,rows-1]:
        curve=bpy.data.objects[p+'Polish_BracerRim_'+side+'_'+str(row)]
        curve.data.bevel_depth=.0025
        for point,co in zip(curve.data.splines[0].points,verts[row*cols:(row+1)*cols]+[verts[row*cols]]):point.co=(*co,1)
    ridge=bpy.data.objects[p+'Polish_BracerRidge_'+side]
    for point,row in zip(ridge.data.splines[0].points,[0,2,4,6,8]):point.co=(*(verts[row*cols+6]+front*.003),1)
    fit[side]={'minRadius':min(radii),'maxRadius':max(radii),'method':'outside-in sleeve surface ray fit with 6mm modeled clearance'}
# A coherent drape grid replaces the earlier single-angle cape outline.
# All positions are in source space; the same cloth is used at every heading.
for obj in s.objects:
    if obj.name.startswith(p+'Polish_Cape_'):obj.hide_render=True
for name in ['DrapeCape','DrapeCapeHem','DrapeCapeStripe']:
    obj=bpy.data.objects.get(p+name)
    if obj:bpy.data.objects.remove(obj,do_unlink=True)
rows=17;cols=25;verts=[]
for row in range(rows):
    t=row/(rows-1);width=.19+.235*math.sin(t*math.pi/2)
    for col in range(cols):
        u=2*col/(cols-1)-1
        x=.055+width*u-.045*t
        y=.145+.47*t+.038*math.sin(3*math.pi*u)*t
        z=1.395-.72*t+.025*math.cos(3*math.pi*u)*t-.02*abs(u)*t
        verts.append((x,y,z))
faces=[(row*cols+c,row*cols+c+1,(row+1)*cols+c+1,(row+1)*cols+c) for row in range(rows-1) for c in range(cols-1)]
data=bpy.data.meshes.new('Anatomy05CoherentCape');data.from_pydata(verts,[],faces);data.update()
obj=bpy.data.objects.new(p+'DrapeCape',data);s.collection.objects.link(obj);obj.parent=root
data.materials.append(bpy.data.objects[p+'Polish_Cape_PrimaryMass'].data.materials[0])
for f in data.polygons:f.use_smooth=True
uv=data.uv_layers.new(name='PainterSurface')
for loop in data.loops:
    row,col=divmod(loop.vertex_index,cols);uv.data[loop.index].uv=(col/(cols-1),1-row/(rows-1))
solid=obj.modifiers.new('ClothThickness','SOLIDIFY');solid.thickness=.004;solid.offset=0
sub=obj.modifiers.new('ClothSmooth','SUBSURF');sub.levels=1;sub.render_levels=1
gold=bpy.data.materials['Fit04_IvoryCloth'] if bpy.data.materials.get('Fit04_IvoryCloth') else bpy.data.objects[p+'Polish_Cape_Hem'].data.materials[0]
def line(name,points,radius):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    sp=data.splines.new('POLY');sp.points.add(len(points)-1)
    for point,co in zip(sp.points,points):point.co=(*co,1)
    obj=bpy.data.objects.new(p+name,data);s.collection.objects.link(obj);obj.parent=root;data.materials.append(gold)
line('DrapeCapeHem',[verts[row*cols] for row in range(rows)]+verts[-cols:]+[verts[row*cols+cols-1] for row in range(rows-2,-1,-1)],.005)
line('DrapeCapeStripe',[Vector(verts[13*cols+c])+Vector((0,-.006,.004)) for c in range(cols)],.009)
r['contactCorrection']={'pommelAxialOffset':.045,'bracers':fit,'cape':'continuous depth-bearing 17x25 quad grid; all headings share geometry','ownerApproved':False}
s['anatomySourceReceipt']=json.dumps(r)
print('CONTACT_CORRECTIONS '+json.dumps(r['contactCorrection']))
