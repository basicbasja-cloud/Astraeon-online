"""Turn the authored rock faces outward and add varied river-facing buttresses.
Does not rebuild the district buildings or change navigable land.
"""
import bpy, bmesh, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
owner=bpy.data.collections['wayfarer-river-fortifications']
ground=next(o for o in bpy.data.collections['court-terrain'].objects if o.type=='MESH' and not o.get('surface_role'))
vs=[tuple(ground.matrix_world@v.co) for v in ground.data.vertices]
outline=[vs[i] for i in json.loads(ground['outline_vertex_indices'])]
for o in list(bpy.data.objects):
    if o.name.startswith('bank-v4-'):bpy.data.objects.remove(o,do_unlink=True)
def rock(name,vertices,faces,mat):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='RockUV')
    for p in data.polygons:
        axis=(0,2) if abs(p.normal.y)>abs(p.normal.x) else (1,2)
        for li in p.loop_indices:
            v=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(v[axis[0]]/1.7,v[axis[1]]/1.7)
    o=bpy.data.objects.new(name,data);owner.objects.link(o);o['role']='decorative';o['shadow']=False
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    if length<.5:continue
    nx,ny=dy/length,-dx/length
    n=max(2,round(length/2))
    for j in range(n):
        old=bpy.data.objects.get(f'district-v4-rock-bank-{i}-{j}')
        if not old:continue
        # Keep the upper rim; reflect each lower vertex across this boundary.
        for v in old.data.vertices:
            if v.co.z<-.01:
                signed=(v.co.x-a[0])*nx+(v.co.y-a[1])*ny
                if signed<0:v.co.x-=2*signed*nx;v.co.y-=2*signed*ny
        old.data.update()
        # Broken outcrops interrupt the otherwise straight lower edge.
        t=(j+.45)/n;x=a[0]+dx*t+nx*.8;y=a[1]+dy*t+ny*.8
        r=.5+(j%3)*.14;z=-2.7;h=1.2+(j%4)*.2
        verts=[(x+math.cos(k*math.tau/6)*r,y+math.sin(k*math.tau/6)*r,z) for k in range(6)]
        verts+=[(x+nx*.18,y+ny*.18,z+h)]
        rock(f'bank-v4-outcrop-{i}-{j}',verts,[[k,(k+1)%6,6] for k in range(6)]+[[5,4,3,2,1,0]],'bankStone' if j%2 else 'bankStoneLight')
scene['bank_authoring_version']=4
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved outward bank faces and broken river-level outcrops')
