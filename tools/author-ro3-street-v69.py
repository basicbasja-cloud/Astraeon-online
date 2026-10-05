"""Saved-source migration: crisp paving, rooted verge grass and pierced GF shells.

Retain every collision core, actor, service and native floor. Decorative shells
replace visible closed ground-floor walls; source UVs, openings and placements
remain editable. Run after source68, then bake both lighting passes sequentially.
"""
import json
import math
import random
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
assert scene.get('ro3_facade_version') == 68
assert not scene.get('ro3_street_version'), 'Source migration already applied'
art = json.loads((ROOT/'authoring/materials/wayfarer-street-v69.json').read_text())['materials']
Kit = runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
rng = random.Random(69045)
PREFIX = 'ro3-v69-'


def material(name, color, spec):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    c = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    m.diffuse_color = tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1,)
    m['texture_json'] = json.dumps(spec)
    return name


BRICK = material('streetBrickLime', '#c2b194', art['brick']['texture'])
GREEN = material('vergeGroundcover', '#81974c', art['groundcover']['texture'])
SAGE = material('vergeGroundcoverShade', '#6d8844', art['groundcover']['texture'])
for name in ('paving', 'cityPaving', 'avenuePaving'):
    bpy.data.materials[name]['texture_json'] = json.dumps(art['paving']['texture'])
    if name != 'paving':
        bpy.data.materials[name].diffuse_color = (.60,.545,.435,1)

# Shared world-space stone registration across every paving surface and stair.
# Keep other limestone walls/trim on their existing authored stone atlas.
stone_uvs = 0
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.materials:
        continue
    if o.data.materials[0].name in ('paving','cityPaving','avenuePaving'):
        uv=o.data.uv_layers.active or o.data.uv_layers.new(name='PhysicalUV')
        for f in o.data.polygons:
            for li in f.loop_indices:
                p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                uv.data[li].uv=(p.x/8,p.y/8) if abs(f.normal.z)>.65 else (p.x/8,p.z/8)
        stone_uvs += 1

terrain = next(c for c in bpy.data.collections if c.get('family')=='terrain')
vs, fs = [], []
for o in terrain.objects:
    if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
    base=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
    o.data.calc_loop_triangles();fs.extend(tuple(base+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)


def height(x,y):
    p=floor.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),150)[0]
    return p.z if p else None


def hull(points):
    points=sorted(set((round(p.x,5),round(p.y,5)) for p in points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def chain(seq):
        out=[]
        for p in seq:
            while len(out)>1 and cross(out[-2],out[-1],p)<=0:out.pop()
            out.append(p)
        return out
    return chain(points)[:-1]+chain(reversed(points))[:-1]


def fit(objects,a,t,n):
    for o in objects:
        for v in o.data.vertices:
            p=v.co.copy();v.co=Vector((a.x,a.y,0))+t*p.x+n*p.y+Vector((0,0,p.z))
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()


records=[];patches=[]
for c in sorted(bpy.data.collections,key=lambda c:c.name):
    core=next((o for o in c.objects if o.type=='MESH' and
        (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls'))),None)
    if core is None:continue
    root=core.parent
    assert root,c.name
    inv=root.matrix_world.inverted()
    points=[inv@core.matrix_world@v.co for v in core.data.vertices]
    outline=hull(points);top=max(p.z for p in points);base=.44
    core['render_visible']=False;core['shadow']=False
    kit=Kit(c,root);kit.prefix=PREFIX
    # Gather old ground glazing. Its reveal/mullions move into the new genuine
    # openings; the collision core remains hidden and keeps its old footprint.
    frontwindows=[o for o in c.objects if o.name.startswith('ro3-v68-') and '-ground-window-' in o.name and o.name.endswith('-glass')]
    face_records=[]
    for edge,(aa,bb) in enumerate(zip(outline,outline[1:]+outline[:1])):
        a,b=Vector((*aa,0)),Vector((*bb,0));length=(b-a).length;t=(b-a).normalized();n=Vector((t.y,-t.x,0))
        front=n.y>.98
        openings=[]
        if front:
            for window in frontwindows:
                pts=[inv@window.matrix_world@v.co for v in window.data.vertices]
                xs=[(p-a).dot(t) for p in pts];zs=[p.z for p in pts]
                if min(xs)<.08 or max(xs)>length-.08:continue
                openings.append((min(xs)-.09,max(xs)+.09,min(zs)-.09,max(zs)+.09))
                stem=window.name[:-6]
                for part in [o for o in c.objects if o.type=='MESH' and o.name.startswith(stem)]:
                    if any(s in part.name for s in ('-glass','-mullion','-transom')):
                        for v in part.data.vertices:v.co.y-=.145
                    elif part.name.endswith('-reveal'):
                        old_inner=min(v.co.y for v in part.data.vertices)
                        for v in part.data.vertices:
                            if abs(v.co.y-old_inner)<.001:v.co.y-=.145
        elif length>=2.6:
            centers=[length*.32,length*.68] if length>5 else [length*.50]
            # Do not place new glazing into attached wings or retained furniture.
            blockers=[];tri=[]
            for ob in c.objects:
                if ob==core or ob.type!='MESH' or not ob.get('render_visible',True):continue
                if ob.data.materials[0].name=='frontageGlazing':continue
                off=len(blockers);blockers.extend(ob.matrix_world@v.co for v in ob.data.vertices)
                ob.data.calc_loop_triangles();tri.extend(tuple(off+i for i in f.vertices) for f in ob.data.loop_triangles)
            tree=BVHTree.FromPolygons(blockers,tri,all_triangles=True)
            for j,s in enumerate(centers):
                z=2.02;ww=1.04;hh=1.32
                direction=(root.matrix_world.to_3x3()@n).normalized()
                if any(tree.ray_cast(root.matrix_world@(a+t*(s+dx)+n*(-.075)+Vector((0,0,z+dz))),direction,.40)[0] is not None
                       for dx in (-.35,0,.35) for dz in (-.45,0,.45)):continue
                openings.append((s-ww/2,s+ww/2,z-hh/2,z+hh/2))
                old=set(c.objects)
                kit.window(c.name+'-ground-side-'+str(edge)+'-'+str(j),s,0,z,ww,hh,
                           recess=.115,low=True)
                # Paired slatted shutters lie close to masonry; sill and upper
                # lintel relief catch baked light without obstructing a street.
                for side in (-1,1):
                    sx=s+side*(ww/2+.18)
                    kit.box(c.name+f'-shutter-{edge}-{j}-{side}',(sx,.055,z),(.25,.09,hh),'oak')
                    for k in range(5):
                        kit.box(c.name+f'-shutter-slat-{edge}-{j}-{side}-{k}',(sx,.107,z-hh*.38+k*hh*.19),(.23,.022,.045),'timber',False)
                fit(set(c.objects)-old,a,t,n)
        xs=sorted({0,length,*[v for h in openings for v in h[:2]]})
        zs=sorted({base,top,*[v for h in openings for v in h[2:]]})
        for xi,(l,r) in enumerate(zip(xs,xs[1:])):
            for zi,(lo,hi) in enumerate(zip(zs,zs[1:])):
                if hi<=base or lo>=top:continue
                if any(h[0]<(l+r)/2<h[1] and h[2]<(lo+hi)/2<h[3] for h in openings):continue
                o=kit.box(c.name+f'-brick-panel-{edge}-{xi}-{zi}',((l+r)/2,-.10,(lo+hi)/2),(r-l,.20,hi-lo),BRICK)
                # UVs run along the native face, continuous across hole cuts.
                for f in o.data.polygons:
                    for li in f.loop_indices:
                        p=o.data.vertices[o.data.loops[li].vertex_index].co
                        o.data.uv_layers.active.data[li].uv=(p.x/2.4,p.z/2.4)
                fit([o],a,t,n)
        # Side/rear framing and projecting masonry datum give formerly blank
        # walls the same structural depth as the detailed street front.
        if not front:
            old=set(c.objects)
            for j,s in enumerate([.12,length-.12]+[length/2] if length>4 else [.12,length-.12]):
                if any(h[0]-.14<s<h[1]+.14 for h in openings):continue
                kit.box(c.name+f'-ground-post-{edge}-{j}',(s,.045,(base+top)/2),(.20,.09,top-base),'timber')
            kit.box(c.name+f'-ground-lintel-{edge}',(length/2,.06,top-.14),(length,.12,.22),'timber')
            kit.box(c.name+f'-ground-dado-{edge}',(length/2,.04,.76),(length,.08,.14),'stoneLight')
            fit(set(c.objects)-old,a,t,n)
        face_records.append({'edge':edge,'front':front,'length':round(length,4),'openings':len(openings)})
        # Uneven, discontinuous green wedges by the foundation. Breaks preserve
        # door thresholds and make planting follow the building, rather than a
        # row of disconnected round blobs. These are decorative, never floors.
        for j in range(max(2,int(length/1.4))):
            s=length*(j+.5)/max(2,int(length/1.4))
            if front and abs(s-length/2)<1.0:continue
            if rng.random()<.22:continue
            span=rng.uniform(.65,1.35);depth=rng.uniform(.30,.72)
            patch_points=[]
            for xx,yy in [(s-span*.5,.14),(s-span*.25,.14+depth*.8),
                          (s+.05,.14+depth),(s+span*.45,.14+depth*.45),
                          (s+span*.5,.14)]:
                p=root.matrix_world@(a+t*xx+n*yy);z=height(p.x,p.y)
                if z is None:break
                patch_points.append((p.x,p.y,z+.017))
            if len(patch_points)!=5:continue
            if max(p[2] for p in patch_points)-min(p[2] for p in patch_points)>.13:continue
            name=c.name+f'-foundation-green-{edge}-{j}'
            # Native placement ownership: author world vertices back into this
            # house frame so later building moves carry the rooted planting.
            pp=[tuple(inv@Vector(p)) for p in patch_points]
            o=kit.mesh(name,pp,[[0,1,2],[0,2,3],[0,3,4]],GREEN if j%2 else SAGE,False)
            o['street_v69_patch']=True
            for f in o.data.polygons:
                for li in f.loop_indices:
                    p=o.data.vertices[o.data.loops[li].vertex_index].co
                    pts=[v.co for v in o.data.vertices];u=(pts[-1]-pts[0]).normalized();v=Vector((-u.y,u.x,0));us=[q.dot(u) for q in pts];vs=[q.dot(v) for q in pts]
                    o.data.uv_layers.active.data[li].uv=((p.dot(u)-min(us))/(max(us)-min(us)),(p.dot(v)-min(vs))/(max(vs)-min(vs)))
            # A few low physical blades, rooted to exactly the same floor.
            for blade in range(4):
                s2=s+rng.uniform(-span*.32,span*.32);p=root.matrix_world@(a+t*s2+n*(.19+depth*.3))
                z=height(p.x,p.y);q=inv@Vector((p.x,p.y,z+.022))
                tip=q+Vector((rng.uniform(-.035,.035),rng.uniform(-.035,.035),rng.uniform(.09,.18)))
                w=t*.025
                blade_obj=kit.mesh(name+'-blade-'+str(blade),[tuple(q-w),tuple(q+w),tuple(tip)],[[0,1,2]],'grass',False)
                blade_obj['street_v69_blade']=True
            patches.append({'id':o.name,'owner':c.name,'vertices':patch_points})
    records.append({'owner':c.name,'hiddenCore':core.name,'faces':face_records})
    print('Source69 masonry/openings/verge:',c.name,flush=True)

assert len(records)==37,len(records)
scene['ro3_street_version']=69
scene['ro3_street_review_json']=json.dumps({'buildings':records,'patches':patches,'pavingUVObjects':stone_uvs})
scene['concept_architecture_version']=69
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved source69:',len(records),'ground facades;',len(patches),'rooted patches;',stone_uvs,'paving UV meshes; bake required')
