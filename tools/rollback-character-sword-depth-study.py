"""Restore only the unsuccessful owned 04 sword-depth experiment."""
import bpy,json
from mathutils import Vector
s=bpy.data.scenes['ASTRAEON_ASSET_FIT_04'];p='SM_AssetFit04_'
for obj in s.objects:
    if not obj.name.startswith((p+'Blade_',p+'Hilt_',p+'Identity_Weapon')):continue
    backup=bpy.data.meshes.get('DepthBefore_'+obj.data.name) if obj.type=='MESH' else bpy.data.curves.get('DepthBefore_'+obj.data.name)
    if backup is None:continue
    if obj.type=='MESH':
        for v,old in zip(obj.data.vertices,backup.vertices):v.co=old.co
        obj.data.update()
    elif obj.type=='CURVE':
        for sp,oldsp in zip(obj.data.splines,backup.splines):
            for v,old in zip(sp.points,oldsp.points):v.co=old.co
body=bpy.data.objects[p+'Body'];backup=bpy.data.meshes['Fit04_BodyBeforeSwordDepth']
for v,old in zip(body.data.vertices,backup.vertices):v.co=old.co
body.data.update()
def right(poly):
    weights={}
    for i in poly.vertices:
        for group in body.data.vertices[i].groups:
            name=body.vertex_groups[group.group].name;weights[name]=weights.get(name,0)+group.weight
    name=max(weights,key=weights.get)
    return name.endswith('_r') and name.startswith(('hand','thumb','index','middle','ring','pinky'))
indices=sorted({i for f in body.data.polygons if right(f) for i in f.vertices})
glove=bpy.data.objects[p+'Refitted_Glove_R'];assert len(indices)==len(glove.data.vertices)
for v,i in zip(glove.data.vertices,indices):v.co=body.data.vertices[i].co+body.data.vertices[i].normal*.004
glove.data.update()
bpy.data.objects['GUIDE_blade_tip'].location=Vector(s['swordDepthOriginalTip'])
s['gripPaths']=s['swordDepthOriginalPaths']
r=json.loads(s['swordDepthRefinement']);r['status']='FAILED_INTERNAL_REVIEW_ROLLED_BACK';r['reason']='Did not resolve NW visibility and inherited hand anatomy remained incorrect';s['swordDepthRefinement']=json.dumps(r)
bpy.context.window.scene=bpy.data.scenes['ASTRAEON_ANATOMY_SOURCE_05']
print('OWNED_04_DEPTH_EXPERIMENT_ROLLED_BACK; NEW_05_SOURCE_UNCHANGED')
