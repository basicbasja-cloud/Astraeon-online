"""Ground complete inherited plant groups against the current native floor.

Old separately fitted petals/stems survived several placement passes above
their planting surfaces. Translate each complete group once, keeping all
relative flower geometry, then add rooted broad leaves. No bitmap edits.
"""
import bpy,bmesh,json,re,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('market_court_version')==63
PREFIX='flora-v64-';owner=bpy.data.collections['wayfarer-v44-detail']
for o in list(bpy.data.objects):
    if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
terrain=bpy.data.collections['court-terrain'];vs=[];fs=[]
for o in terrain.objects:
    if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
    offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
    fs.extend([offset+i for i in p.vertices] for p in o.data.polygons)
floor=BVHTree.FromPolygons(vs,fs)
def height(x,y):
    hit=floor.ray_cast(Vector((x,y,50)),Vector((0,0,-1)),100)
    assert hit[0] is not None,(x,y)
    return hit[0].z
def mesh(name,vs,fs,mat,shadow=True):
    d=bpy.data.meshes.new(PREFIX+name);d.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free()
    d.materials.append(bpy.data.materials[mat]);d.uv_layers.new(name='PhysicalUV')
    for f in d.polygons:
        for li in f.loop_indices:
            p=d.vertices[d.loops[li].vertex_index].co;d.uv_layers.active.data[li].uv=(p.x/3,p.y/3)
    o=bpy.data.objects.new(PREFIX+name,d);owner.objects.link(o);o['role']='decorative';o['shadow']=shadow
    return o
groups={}
for o in owner.objects:
    m=re.match(r'detail-v44-flower-(\d+)-',o.name)
    if m and o.type=='MESH' and o.get('render_visible',True):groups.setdefault(int(m[1]),[]).append(o)
records=[]
for k,parts in sorted(groups.items()):
    stems=[o for o in parts if o.name.endswith('-stem')]
    if not stems:continue
    pts=[o.matrix_world@v.co for o in stems for v in o.data.vertices];x=sum(v.x for v in pts)/len(pts);y=sum(v.y for v in pts)/len(pts)
    ground=height(x,y);baseline=min(p.z for p in pts)
    # Store a source datum so repeat runs never compound offsets.
    if 'flora_v64_base_z' not in stems[0]:stems[0]['flora_v64_base_z']=baseline
    dz=ground+.20-stems[0]['flora_v64_base_z']
    for o in parts:
        if 'flora_v64_original_matrix_z' not in o:o['flora_v64_original_matrix_z']=o.matrix_world.translation.z
        m=o.matrix_world.copy();m.translation.z=o['flora_v64_original_matrix_z']+dz;o.matrix_world=m
    # A low soil mound and lance-shaped leaves visibly join stems to the floor.
    ring=[(x+math.cos(j*math.tau/12)*.29,y+math.sin(j*math.tau/12)*.25,ground+.054) for j in range(12)]
    mesh(str(k)+'-soil',[(x,y,ground+.10)]+ring,[[0,j+1,(j+1)%12+1] for j in range(12)],'soil',False)
    for j in range(6):
        a=j*math.tau/6+.3;u=Vector((math.cos(a),math.sin(a),0));v=Vector((-u.y,u.x,0));c=Vector((x,y,ground+.08))
        middle=c+u*.16+Vector((0,0,.12));tip=c+u*.30+Vector((0,0,.16+.035*(j%2)))
        mesh(str(k)+'-leaf-'+str(j),[tuple(c),tuple(middle+v*.10),tuple(tip),tuple(middle-v*.10),tuple(middle+Vector((0,0,.025)))],[[0,1,4],[1,2,4],[2,3,4],[3,0,4]],'produceGreen' if j%2 else 'leaf')
    records.append({'group':k,'ground':round(ground,5),'oldStemBase':round(stems[0]['flora_v64_base_z'],5),'newStemBase':round(ground+.20,5),'parts':len(parts)})
scene['street_flora_ground_version']=64;scene['street_flora_ground_review_json']=json.dumps(records)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Grounded',len(records),'whole inherited plant groups against current native floors; both bakes required',flush=True)
