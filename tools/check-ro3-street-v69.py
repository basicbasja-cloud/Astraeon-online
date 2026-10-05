"""Read-only source checks for recessed side glazing and rooted groundcover."""
import json
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

scene=bpy.context.scene
assert scene.get('ro3_street_version')==69


def hull(points):
    p=sorted(set((round(v.x,5),round(v.y,5)) for v in points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def chain(seq):
        out=[]
        for v in seq:
            while len(out)>1 and cross(out[-2],out[-1],v)<=0:out.pop()
            out.append(v)
        return out
    return chain(p)[:-1]+chain(reversed(p))[:-1]


terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
vertices=[];triangles=[]
for obj in terrain.objects:
    if obj.type!='MESH' or obj.get('surface_role')=='water' or not obj.get('walkable',True):continue
    base=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    obj.data.calc_loop_triangles();triangles.extend(tuple(base+i for i in t.vertices) for t in obj.data.loop_triangles)
floor=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
violations=[];rays=0;windows=0;patches=0;ground_vertices=0
for collection in bpy.data.collections:
    glazing=[o for o in collection.objects if o.name.startswith('ro3-v69-') and o.name.endswith('-glass')]
    core=next((o for o in collection.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls'))),None)
    if core is None:continue
    root=core.parent;inv=root.matrix_world.inverted()
    outline=hull([inv@core.matrix_world@v.co for v in core.data.vertices])
    vertices=[];triangles=[];owners=[]
    for obj in collection.objects:
        if obj.type!='MESH' or not obj.get('render_visible',True) or obj.data.materials[0].name=='frontageGlazing':continue
        base=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        obj.data.calc_loop_triangles()
        for f in obj.data.loop_triangles:
            triangles.append(tuple(base+i for i in f.vertices));owners.append(obj.name)
    tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
    for obj in glazing:
        edge=int(re.search(r'-ground-side-(\d+)-\d+-glass$',obj.name)[1])
        a,b=outline[edge],outline[(edge+1)%len(outline)]
        tangent=Vector((b[0]-a[0],b[1]-a[1],0)).normalized()
        normal=Vector((tangent.y,-tangent.x,0));direction=(root.matrix_world.to_3x3()@normal).normalized()
        pts=[v.co for v in obj.data.vertices];center=sum(pts,Vector())/len(pts)
        width=max(v.dot(tangent) for v in pts)-min(v.dot(tangent) for v in pts)
        height=max(v.z for v in pts)-min(v.z for v in pts)
        for x in (-1,0,1):
            for y in (-1,0,1):
                p=root.matrix_world@(center+tangent*width*x/3+Vector((0,0,height*y/3)))+direction*.035
                hit,_,index,distance=tree.ray_cast(p,direction,.65);rays+=1
                if hit is not None:violations.append({'window':obj.name,'obstruction':owners[index],'distance':distance})
        windows+=1
    for obj in collection.objects:
        if not obj.get('street_v69_patch'):continue
        patches+=1
        for v in obj.data.vertices:
            p=obj.matrix_world@v.co;ground=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
            ground_vertices+=1
            if ground is None or abs(p.z-ground.z-.017)>.003:violations.append({'patch':obj.name,'contact':list(p)})
        if max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)>.13:violations.append({'patch':obj.name,'crossesStep':True})
clumps=0
for obj in bpy.data.objects:
    if not obj.get('street_v69_clump'):continue
    root=Vector(obj['street_v69_root_world']);ground=floor.ray_cast(Vector((root.x,root.y,100)),Vector((0,0,-1)),150)[0]
    if ground is None or abs(root.z-ground.z-.017)>.003:violations.append({'clump':obj.name,'contact':list(root)})
    clumps+=1
if scene.get('ro3_grass_life_version'):
    assert clumps==json.loads(scene['ro3_grass_life_review_json'])['rootedClumps']
report={'sourcePass':69,'sideWindows':windows,'paneRays':rays,'groundcoverPatches':patches,'rootedVertices':ground_vertices,'rootedClumps':clumps,'violations':violations}
path=Path(sys.argv[sys.argv.index('--')+1]);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n')
assert windows==148-len(json.loads(scene.get('ro3_junction_omissions_json','[]'))),windows
assert patches>150,patches
assert not violations,json.dumps(violations[:12])
print('PASS',windows,'new recessed windows;',rays,'clear pane rays;',patches,'rooted patches')
