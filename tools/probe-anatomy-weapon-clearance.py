"""Read-only search for small shared sword-frame changes with actual occluders.

Measures physical line visibility and reference projection deviation. Does not
move geometry, fingers, cameras or commit a candidate automatically.
"""
import bpy,math,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
s=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05'];bpy.context.window.scene=s
p='SM_Anatomy05_';root=bpy.data.objects['ROOT_AnatomySource05'];yaw=root.rotation_euler.z
root.rotation_euler.z=0;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
verts=[];faces=[]
for obj in s.objects:
    if obj.hide_render or obj.type not in ['MESH','CURVE'] or obj.name.startswith((p+'Blade_',p+'Hilt_',p+'Identity_Weapon')):continue
    data=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps)
    offset=len(verts);verts.extend(obj.matrix_world@v.co for v in data.vertices)
    faces.extend(tuple(offset+i for i in f.vertices) for f in data.polygons);bpy.data.meshes.remove(data)
tree=BVHTree.FromPolygons(verts,faces)
guard=bpy.data.objects['GUIDE_guard'].location.copy();tip=Vector(bpy.data.scenes['ASTRAEON_ASSET_FIT_04']['swordDepthOriginalTip'])
base=tip-guard;camera=s.camera;side=Vector((0,1,0)).cross(base).normalized()
source_view=camera.rotation_euler.to_quaternion()@Vector((0,0,1))
se=Matrix.Rotation(math.radians(45),4,'Z');project=camera.matrix_world.inverted()
oldproj=project@se@tip;records=[]
for dx in [-.15,-.10,-.05,0,.05,.10,.15]:
    for dy in [-.20,-.10,0,.10,.20,.30]:
        for dz in [-.08,0,.08]:
            newtip=tip+Vector((dx,dy,dz));proj=project@se@newtip
            err=math.hypot(proj.x-oldproj.x,proj.y-oldproj.y)*320/camera.data.ortho_scale
            if err>8:continue
            visible={}
            for label,angle in [('NW',-135),('N',-180),('W',-90),('SE',45)]:
                view=Matrix.Rotation(math.radians(-angle),3,'Z')@source_view;count=0
                for i in range(1,31):
                    point=guard.lerp(newtip,i/31)
                    for edge in [-1,0,1]:
                        sample=point+side*.027*edge
                        hit,no,idx,dist=tree.ray_cast(sample+view*5,-view,5.001)
                        if hit is None or dist>=4.999:count+=1
                visible[label]=count
            records.append({'tip':list(newtip),'projectionErrorPixels':err,'visibleSamples':visible,'angleDegrees':math.degrees(base.angle(newtip-guard))})
root.rotation_euler.z=yaw;bpy.context.view_layer.update()
def ranking(item):return (-item['visibleSamples']['NW'],item['projectionErrorPixels'])
records.sort(key=ranking)
print('CLEARANCE_PROBE '+json.dumps(records[:12]))
