"""Authored costume relief on the fresh source, before UV coating.

All forms turn with the source. No directional image patches or imported meshes.
"""
import bpy, math
from mathutils import Vector

scene=bpy.context.scene
assert scene.name=='ASTRAEON_SOURCE_LOOKDEV_03'
root=bpy.data.objects['ROOT_ReferenceFit']
gear=bpy.data.collections['MAJOR_FORM_BLOCKOUT']
P={o.name.removeprefix('GUIDE_'):o.location.copy() for o in bpy.data.collections['LANDMARK_GUIDES'].objects}
bronze=bpy.data.objects['Pauldron_R'].data.materials[0]
gold=bpy.data.objects['Pauldron_Rim_R'].data.materials[0]
leather=bpy.data.objects['Belt_Mass'].data.materials[0]
ivory=bpy.data.objects['Tunic_IvoryFront'].data.materials[0]

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);gear.objects.link(obj);obj.parent=root
    data.materials.append(mat)
    for face in data.polygons:face.use_smooth=True
    obj['detailAuthority']='Native source geometry; no per-heading correction'
    return obj

def line(name,points,radius,mat):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=3
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points):point.co=(*co,1)
    obj=bpy.data.objects.new(name,data);gear.objects.link(obj);obj.parent=root
    data.materials.append(mat)
    return obj

def ring(name,center,axis,rx,ry,mat,radius=.008):
    axis=axis.normalized();x=Vector((0,1,0)).cross(axis).normalized();y=axis.cross(x).normalized()
    points=[center+x*rx*math.cos(math.tau*j/48)+y*ry*math.sin(math.tau*j/48) for j in range(49)]
    return line(name,points,radius,mat)

def jewel(name,center,x,z,size):
    x=x.normalized()*size;z=z.normalized()*size*1.25
    normal=x.cross(z).normalized()
    verts=[center-x,center+z,center+x,center-z,center+normal*size*.45]
    return mesh(name,verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],gold)

def surface_border(obj,name,mat,radius=.004):
    # Structured cloth rows retain their actual surface placement.
    vertices=obj.data.vertices;cols=9
    if len(vertices)!=45:return
    indices=list(range(9))+[r*cols+8 for r in range(1,5)]+list(range(43,35,-1))+[r*cols for r in range(3,-1,-1)]
    line(name,[vertices[i].co+Vector((0,-.008,0)) for i in indices],radius,mat)

for side in ('R','L'):
    shoulder,elbow,wrist,knee,ankle=[P[n+'_'+side] for n in ('shoulder','elbow','wrist','knee','ankle')]
    forearm=(wrist-elbow).normalized()
    ring('Forged_BracerUpperRim_'+side,elbow.lerp(wrist,.30),forearm,.105,.096,gold)
    ring('Forged_BracerWristRim_'+side,elbow.lerp(wrist,1.01),forearm,.063,.060,gold,.007)
    # Raised longitudinal ridge on the front, not a cylindrical bracelet.
    center=elbow.lerp(wrist,.54)+Vector((0,-.083,0))
    jewel('Bracer_Crest_'+side,center,Vector((1,0,0)),forearm,.023)
    points=[elbow.lerp(wrist,t)+Vector((0,-(.094*(1-t)+.059*t),0)) for t in [.30,.44,.65,.89]]
    line('Bracer_FrontRidge_'+side,points,.005,gold)
    # Navy sleeve folds are displacement of the removable sleeve, not drawing
    # opaque elbow parts over the body in image space.
    sleeve=bpy.data.objects['Fitted_Sleeve_'+side]
    a=shoulder;b=elbow;ab=b-a
    for vertex in sleeve.data.vertices:
        t=(vertex.co-a).dot(ab)/ab.length_squared
        if .18<t<.99:
            radial=vertex.co-a-ab*t
            front=max(0,min(1,-radial.y/.075))
            envelope=math.sin(math.pi*max(0,min(1,(t-.18)/.81)))**2
            height=.008*math.sin(t*math.pi*7+radial.x*12)*front*envelope
            vertex.co+=vertex.normal*height
    sleeve.data.update()
    # Layered knee cuff and ankle bands wrap the same leg on all headings.
    axis=(ankle-knee).normalized()
    ring('Boot_KneeBorder_'+side,knee.lerp(ankle,.13),axis,.116,.108,gold,.008)
    ring('Boot_AnkleBand_'+side,ankle+Vector((0,0,.065)),axis,.072,.084,bronze,.015)
    jewel('Boot_KneeCrest_'+side,knee.lerp(ankle,.19)+Vector((0,-.114,0)),Vector((1,0,0)),Vector((0,0,1)),.034)
    # Calf panel adds defined stitched edges, while the underlying boot remains
    # a removable complete fitted shell.
    top=knee.lerp(ankle,.31);bottom=knee.lerp(ankle,.91)
    for sign in (-1,1):
        points=[top.lerp(bottom,t)+Vector((sign*(.057*(1-t)+.039*t),-.086*(1-t)-.066*t,0)) for t in [0,.25,.5,.75,1]]
        line('Boot_ShinPiping_'+side+'_'+str(sign),points,.0045,leather)
    foot=bpy.data.objects['Fitted_Boot_'+side]
    minz=min(v.co.z for v in foot.data.vertices)
    # The sole follows a measured section of the actual foot, not a screen box.
    sole=[v.co for v in foot.data.vertices if minz+.015<v.co.z<minz+.028]
    if sole:
        cx=sum(v.x for v in sole)/len(sole);cy=sum(v.y for v in sole)/len(sole)
        rx=max(abs(v.x-cx) for v in sole);ry=max(abs(v.y-cy) for v in sole)
        points=[Vector((cx+rx*math.cos(math.tau*j/48),cy+ry*math.sin(math.tau*j/48),minz+.013)) for j in range(49)]
        line('Boot_Sole_'+side,points,.009,leather)

for name in ('Tunic_FrontFlap','Tunic_NearFlap','Teal_HipMass'):
    surface_border(bpy.data.objects[name],name+'_WovenBorder',bronze if name=='Teal_HipMass' else leather)

# Buckle is leather-backed; two small belt rivets and straps read as clothing
# construction. Their material and geometry remain removable with the outfit.
waist=P['waist']+Vector((.025,-.192,-.008))
x=Vector((.061,0,0));z=Vector((0,0,.043))
back=mesh('Buckle_LeatherBack',[waist-x-z,waist+x-z,waist+x+z,waist-x+z],[(0,1,2,3)],leather)
solid=back.modifiers.new('BuckleThickness','SOLIDIFY');solid.thickness=.008
bevel=back.modifiers.new('BuckleCorners','BEVEL');bevel.width=.006;bevel.segments=3
for dx in (-.095,.095):jewel('Belt_Rivet_'+str(dx),waist+Vector((dx,-.002,0)),Vector((1,0,0)),Vector((0,0,1)),.011)
strap=P['chest']+Vector((-.105,-.182,.08))
jewel('Chest_StarClasp',strap,Vector((1,0,0)),Vector((0,0,1)),.039)
line('Chest_StrappedTrim',[strap,strap+Vector((.02,-.005,-.09)),P['waist']+Vector((-.085,-.184,.03))],.006,gold)

scene['sourceLookdevPass']='Native costume relief and UV material paint; unapproved'
print('NATIVE_COSTUME_RELIEF_AUTHORED',len(gear.objects),'REMOVAL_QA_REQUIRED')
