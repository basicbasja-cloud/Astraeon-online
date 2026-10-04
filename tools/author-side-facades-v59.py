"""Repair full-depth 'corner posts' and open coherent upper side façades.

The v44 corner helper accidentally made each post as deep as its building.
Replace those broad timber slabs with actual posts. Lower footprints and
service approaches remain native; upper envelopes contain real window holes.
"""
import bpy,bmesh,runpy,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('frontage_depth_version')==58
PREFIX='side-v59-'
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
owner=None;root=None
def mesh(name,vs,fs,mat,role='overhead',shadow=True):
    d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
    d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
    for f in d.polygons:
        for li in f.loop_indices:
            p=d.vertices[d.loops[li].vertex_index].co;n=f.normal
            d.uv_layers.active.data[li].uv=(p.x/3,p.y/3) if abs(n.z)>.65 else (p.y/3,p.z/3) if abs(n.x)>.65 else (p.x/3,p.z/3)
    o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o['role']=role;o['shadow']=shadow
    return o
def box(name,c,size,mat,role='overhead',shadow=True):
    x,y,z=c;a,b,h=[v/2 for v in size]
    return mesh(name,[(x+i*a,y+j*b,z+k*h) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]],mat,role,shadow)
count=0
for c in sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name):
    owner=c;root=bpy.data.objects[c.name+'-placement'];inv=root.matrix_world.inverted()
    walls=next(o for o in c.objects if o.name.endswith('-walls'));vs=[inv@walls.matrix_world@v.co for v in walls.data.vertices]
    x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);z0=min(v.z for v in vs);h=max(v.z for v in vs);w=x1-x0;d=y1-y0;x=(x0+x1)/2;y=(y0+y1)/2;floor=h*.53
    for o in c.objects:
        if o.name.startswith('plan-v44-') and '-corner-' in o.name:o['render_visible']=False;o['shadow']=False;o['role']='decorative';count+=1
    walls['render_visible']=False;walls['shadow']=False;walls['role']='decorative'
    box(c.name+'-lower-walls',(x,y,(z0+floor)/2),(w,d,floor-z0),'plaster','solid')
    for yy in (y0,y1):box(c.name+'-upper-crosswall-'+str(yy),(x,yy,(floor+h)/2),(w,.20,h-floor),'plaster')
    for side,xx in [(-1,x0),(1,x1)]:
        outer=xx+side*.07;zz=h*.77;lo=zz-.62;hi=zz+.62;last=y0
        for j,yy in enumerate([y0+d*.28,y0+d*.72]):
            a,b=yy-.49,yy+.49
            box(c.name+'-side-pier-'+str((side,j)),(outer,(last+a)/2,(floor+h)/2),(.22,a-last,h-floor),'plaster')
            box(c.name+'-side-base-'+str((side,j)),(outer,yy,(floor+lo)/2),(.22,.98,lo-floor),'plaster')
            box(c.name+'-side-head-'+str((side,j)),(outer,yy,(hi+h)/2),(.22,.98,h-hi),'plaster');last=b
            box(c.name+'-recess-'+str((side,j)),(outer-side*.21,yy,zz),(.05,1.02,1.30),'timber',shadow=False)
            box(c.name+'-glass-'+str((side,j)),(outer-side*.16,yy,zz),(.035,.85,1.12),'glass',shadow=False)
            for dy in (-.51,.51):box(c.name+'-jamb-'+str((side,j,dy)),(outer+side*.13,yy+dy,zz),(.22,.12,1.38),'oak')
            for dz in (-.67,.67):box(c.name+'-lintel-'+str((side,j,dz)),(outer+side*.13,yy,zz+dz),(.24,1.16,.12),'oak')
            box(c.name+'-mullion-'+str((side,j)),(outer-side*.11,yy,zz),(.06,.045,1.13),'stoneLight',shadow=False)
            box(c.name+'-transom-'+str((side,j)),(outer-side*.11,yy,zz-.10),(.06,.85,.045),'stoneLight',shadow=False)
            box(c.name+'-shutter-'+str((side,j)),(outer+side*.12,yy+.77,zz),(.17,.31,1.26),'oak')
        box(c.name+'-side-end-'+str(side),(outer,(last+y1)/2,(floor+h)/2),(.22,y1-last,h-floor),'plaster')
        box(c.name+'-side-floor-beam-'+str(side),(outer+side*.11,y,floor),(.22,d+.14,.18),'timber')
        for corner,yy in enumerate([y0+.06,y1-.06]):box(c.name+'-actual-corner-'+str((side,corner)),(xx+side*.045,yy,(z0+h)/2),(.18,.19,h-z0),'timber')
scene['side_facade_version']=59
# Less fill creates stronger sun/shade separation with the same authored sun
# direction. Keep the quiet painterly palette rather than sharpening textures.
scene['ambient']=.50;scene['sun_strength']=.55
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Repaired',count,'full-depth timber slabs; 48 recessed side windows; sun/fill .55/.50',flush=True)
