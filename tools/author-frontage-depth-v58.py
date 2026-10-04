"""Editable jettied frontages, coordinated roofs and recessed glazing.

Extend existing upper floors rather than placing unrelated props in streets.
Ground building footprints, entrances and concept district roots are retained.
Stored baselines make the architectural changes repeatable without drift.
"""
import bpy,bmesh,json,runpy,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('layout_id')=='wayfarer-concept-terraced-town-v49'
PREFIX='frontage-v58-'
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
def beam(name,a,b,width,mat='timber'):
    a,b=Vector(a),Vector(b);v=(b-a).normalized();u=v.cross(Vector((0,1,0)))
    if u.length<.01:u=v.cross(Vector((1,0,0)))
    u.normalize();w=v.cross(u).normalized();u*=width/2;w*=width/2
    return mesh(name,[tuple(p+i*u+j*w) for p in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
def shift(o,fn):
    if not o.get('frontage_v58_original_vertices'):o['frontage_v58_original_vertices']=json.dumps([list(v.co) for v in o.data.vertices])
    original=json.loads(o['frontage_v58_original_vertices']);to_local=root.matrix_world.inverted()@o.matrix_world;to_data=to_local.inverted()
    for vertex,co in zip(o.data.vertices,original):vertex.co=to_data@fn(to_local@Vector(co))
    o.data.update()
records=[]
for index,c in enumerate(sorted([c for c in bpy.data.collections if c.name.startswith('frontage-')],key=lambda c:c.name)):
    owner=c;root=bpy.data.objects[c.name+'-placement'];inv=root.matrix_world.inverted()
    walls=next(o for o in c.objects if o.name.endswith('-walls'));vs=[inv@walls.matrix_world@v.co for v in walls.data.vertices]
    x0,x1=min(v.x for v in vs),max(v.x for v in vs);y0,y1=min(v.y for v in vs),max(v.y for v in vs);x=(x0+x1)/2;w=x1-x0;h=max(v.z for v in vs)
    extension=[.76,.89,.82][index%3];front=y1+extension;bottom=h*.53;top=h+.04;window_z=h*.77;lo=window_z-.70;hi=window_z+.70
    # A real projecting envelope with two open window bays. Dark splayed
    # reveals sit behind it; trim projects beyond it and catches sunlight.
    windows=[x-w*.29,x+w*.29];last=x0-.115
    for j,xx in enumerate(windows):
        left,right=xx-.525,xx+.525
        box(c.name+'-pier-'+str(j),((last+left)/2,front,(bottom+top)/2),(left-last,.24,top-bottom),'plaster')
        box(c.name+'-window-base-'+str(j),(xx,front,(bottom+lo)/2),(1.05,.24,lo-bottom),'plaster')
        box(c.name+'-window-head-'+str(j),(xx,front,(hi+top)/2),(1.05,.24,top-hi),'plaster');last=right
    box(c.name+'-end-pier',((last+x1+.115)/2,front,(bottom+top)/2),(x1+.115-last,.24,top-bottom),'plaster')
    box(c.name+'-floor-soffit',(x,(y1+front)/2,bottom-.04),(w+.23,extension+.24,.18),'oak')
    box(c.name+'-floor-bressummer',(x,front+.04,bottom),(w+.39,.28,.26),'timber')
    for side in (-1,1):
        xx=x+side*(w/2+.115)
        box(c.name+'-return-'+str(side),(xx,(y1+front)/2,(bottom+top)/2),(.23,extension,top-bottom),'plaster')
        box(c.name+'-corner-post-'+str(side),(xx,front+.15,(bottom+top)/2),(.18,.20,top-bottom),'timber')
        beam(c.name+'-corner-brace-'+str(side),(xx-side*.06,front+.17,bottom+.26),(xx-side*min(.68,w*.12),front+.17,bottom+.98),.12)
    box(c.name+'-central-post',(x,front+.15,(bottom+top)/2),(.14,.18,top-bottom),'timber')
    # Four grounded brackets express the actual cantilever, not decorative
    # diagonals crossing window glass. They remain above pedestrian headroom.
    for j,t in enumerate([-.43,-.19,.19,.43]):
        xx=x+w*t
        beam(c.name+'-bracket-'+str(j),(xx,y1+.08,bottom-.68),(xx,front-.08,bottom-.09),.18,'oak')
    for o in list(c.objects):
        n=o.name
        if n.startswith('organic-v47-'+c.name) and any(t in n for t in ['upper-jetty','jetty-belt','jetty-corner']):o['render_visible']=False;o['shadow']=False
        if n.startswith('city-v48-'+c.name) and any(t in n for t in ['upper-brace','jetty-corbels']):o['render_visible']=False;o['shadow']=False
        if n.startswith('city-v48-'+c.name):
            delta=None
            if 'window-recess' in n or 'window-glass' in n or 'window-mullion' in n or 'window-transom' in n:delta=extension-.54
            elif 'window-jamb' in n or 'window-lintel' in n:delta=extension-.35
            elif 'shutter' in n:delta=extension-.21
            elif 'oriel' in n:delta=extension-.27
            if delta is not None:shift(o,lambda p,d=delta:p+Vector((0,d,0)))
        if n.startswith('organic-v47-'+c.name):
            if 'curved-roof' in n or 'deep-eave' in n:
                shift(o,lambda p:p+Vector((0,extension*max(0,min(1,(p.y-y0)/(y1-y0))),0)))
            elif any(t in n for t in ['shaped-gable','gable-kingpost','gable-brace','-verge-']):shift(o,lambda p:p+Vector((0,extension,0)))
    records.append({'owner':c.name,'upperFloorProjection':extension,'windowDepth':.135,'groundFootprintRetained':True})
scene['frontage_depth_version']=58;scene['frontage_depth_review_json']=json.dumps(records)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved',len(records),'jettied frontage envelopes and coordinated roof extensions',flush=True)
