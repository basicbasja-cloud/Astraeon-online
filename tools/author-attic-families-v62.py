"""Open recessed attic bays and strengthen roof-family silhouettes in source.

Uses the current saved frontage envelope, never a historical town rebuild.
Ground footprints, service anchors and routes are retained.
"""
import bpy,bmesh,math,json,runpy
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('side_facade_version')==59
PREFIX='attic-v62-';owner=root=None
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,mat,shadow=True):
    d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(d);bm.free()
    d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
    for f in d.polygons:
        for li in f.loop_indices:
            p=d.vertices[d.loops[li].vertex_index].co;n=f.normal
            d.uv_layers.active.data[li].uv=(p.x/3,p.y/3) if abs(n.z)>.65 else (p.y/3,p.z/3) if abs(n.x)>.65 else (p.x/3,p.z/3)
    o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o['role']='overhead';o['shadow']=shadow
    return o
def prism(name,poly,y,depth,mat,shadow=True):
    n=len(poly);return mesh(name,[(x,yy,z) for yy in (y-depth/2,y+depth/2) for x,z in poly],[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],mat,shadow)
def box(name,c,size,mat,shadow=True):
    x,y,z=c;a,b,h=[v/2 for v in size];return prism(name,[(x-a,z-h),(x+a,z-h),(x+a,z+h),(x-a,z+h)],y,b*2,mat,shadow)
def beam(name,a,b,width,mat):
    a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,1,0)))
    if u.length<.01:u=v.cross(Vector((1,0,0)))
    u.normalize();w=v.cross(u).normalized();u*=width/2;w*=width/2
    return mesh(name,[tuple(p+i*u+j*w) for p in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
records=[]
for index,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
    owner=c;root=bpy.data.objects[c.name+'-placement'];inv=root.matrix_world.inverted()
    original=next(o for o in c.objects if 'organic-v47-' in o.name and '-shaped-gable' in o.name)
    points=[inv@original.matrix_world@v.co for v in original.data.vertices];y=sum(v.y for v in points)/len(points);eave=min(v.z for v in points);peak=max(points,key=lambda p:p.z);profile=sorted({(round(p.x,6),round(p.z,6)) for p in points});x0,x1=profile[0][0],profile[-1][0];span=x1-x0
    def roof_at(x):
        for (a,za),(b,zb) in zip(profile,profile[1:]):
            if a-1e-6<=x<=b+1e-6:return za+(zb-za)*(x-a)/(b-a)
        raise ValueError(x)
    attic_height=peak.z-eave;half=min(.57,span*.09,attic_height*.25);lo=eave+.27;hi=min(lo+1.12,roof_at(peak.x-half)-.22,roof_at(peak.x+half)-.22)
    assert hi-lo>.48,(c.name,attic_height,hi-lo)
    a,b=peak.x-half,peak.x+half;breaks=sorted(set([p[0] for p in profile]+[a,b]))
    original['render_visible']=False;original['shadow']=False
    for o in c.objects:
        if o.name.startswith('organic-v47-'+c.name) and any(t in o.name for t in ['gable-kingpost','gable-brace']):o['render_visible']=False;o['shadow']=False
    for i,(left,right) in enumerate(zip(breaks,breaks[1:])):
        za,zb=roof_at(left),roof_at(right)
        if left>=a-1e-6 and right<=b+1e-6:
            prism(c.name+'-under-bay-'+str(i),[(left,eave),(right,eave),(right,lo),(left,lo)],y,.20,'plaster')
            prism(c.name+'-above-bay-'+str(i),[(left,hi),(right,hi),(right,zb),(left,za)],y,.20,'plaster')
        else:prism(c.name+'-gable-pier-'+str(i),[(left,eave),(right,eave),(right,zb),(left,za)],y,.20,'plaster')
    zz=(lo+hi)/2;hh=hi-lo;family='residential' if c.get('family')=='residential' else 'workshop';trim='oak' if family=='residential' else 'timber'
    box(c.name+'-bay-reveal',(peak.x,y-.19,zz),(half*2,.08,hh),'timber',False)
    box(c.name+'-bay-glass',(peak.x,y-.12,zz),(half*2-.09,.035,hh-.08),'glass',False)
    for dx in (-half-.045,half+.045):box(c.name+'-bay-jamb-'+str(dx),(peak.x+dx,y+.105,zz),(.13,.30,hh+.18),trim)
    for z in (lo-.05,hi+.05):box(c.name+'-bay-lintel-'+str(z),(peak.x,y+.13,z),(half*2+.25,.34,.13),trim)
    box(c.name+'-bay-mullion',(peak.x,y-.08,zz),(.06,.06,hh-.06),'stoneLight',False)
    box(c.name+'-bay-transom',(peak.x,y-.08,zz-.06),(half*2-.06,.06,.055),'stoneLight',False)
    beam(c.name+'-kingpost',(peak.x,y+.15,hi+.16),(peak.x,y+.15,peak.z-.12),.14,trim)
    box(c.name+'-gable-tie',((x0+x1)/2,y+.12,eave+.03),(span-.16,.21,.19),'timber')
    for side in (-1,1):
        beam(c.name+'-fan-brace-'+str(side),(peak.x+side*(span*.30),y+.14,eave+.13),(peak.x+side*(half+.18),y+.14,hi+.13),.11,trim)
        if family=='residential':box(c.name+'-attic-shutter-'+str(side),(peak.x+side*(half+.27),y+.13,zz),(.28,.14,hh+.12),'oak')
    # Roof ridge caps and broad structural verge blocks read at gameplay scale.
    roofs=[o for o in c.objects if o.get('render_visible',True) and '-curved-roof-' in o.name]
    roof_points=[inv@o.matrix_world@v.co for o in roofs for v in o.data.vertices];ry0=min(v.y for v in roof_points);ry1=max(v.y for v in roof_points)
    roofmat='slate' if index%3==0 else 'terracotta'
    beam(c.name+'-ridge-crown',(peak.x,ry0,peak.z+.07),(peak.x,ry1,peak.z+.07),.23,roofmat)
    for yy in (ry0,ry1):
        box(c.name+'-ridge-peg-'+str(yy),(peak.x,yy,peak.z+.21),(.17,.17,.42),'timber')
        for side in (-1,1):beam(c.name+'-ridge-finial-'+str((yy,side)),(peak.x,yy,peak.z+.37),(peak.x+side*.22,yy,peak.z+.55),.08,'oak')
    records.append({'owner':c.name,'family':family,'atticWindowHeight':hh,'actualRecessDepth':.22,'groundFootprintRetained':True})
scene['attic_family_version']=62;scene['attic_family_review_json']=json.dumps(records)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved',len(records),'recessed attic bays with structural framing and roof crowns; both light bakes required',flush=True)
