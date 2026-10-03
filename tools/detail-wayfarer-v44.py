"""Playable-scale lanterns, blooms and river strata, authored as real meshes."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene;assert scene['town_plan_version']==44
prefix='detail-v44-'
for o in list(bpy.data.objects):
    if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
owner=bpy.data.collections.get('wayfarer-v44-detail')
if owner is None:owner=bpy.data.collections.new('wayfarer-v44-detail');scene.collection.children.link(owner)
owner['family']='civic'
def mesh(name,vs,fs,mat,role='decorative',shadow=False):
    data=bpy.data.meshes.new(prefix+name);data.from_pydata(vs,[],fs)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='WorldUV')
    spec=json.loads(bpy.data.materials[mat].get('texture_json','{}'));size=spec.get('worldSize',2.4)
    for face in data.polygons:
        n=face.normal;axes=(0,1) if abs(n.z)>.65 else (0,2) if abs(n.y)>abs(n.x) else (1,2)
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co;data.uv_layers.active.data[li].uv=(p[axes[0]]/size,p[axes[1]]/size)
    o=bpy.data.objects.new(prefix+name,data);owner.objects.link(o);o['role']=role;o['shadow']=shadow;return o
def ring(name,x,y,z,r1,r2,height,mat,sides=8):
    vs=[(x+r*math.cos(i*math.tau/sides),y+r*math.sin(i*math.tau/sides),zz) for r,zz in ((r1,z),(r2,z+height)) for i in range(sides)]
    return mesh(name,vs,[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[i,(i+1)%sides,(i+1)%sides+sides,i+sides] for i in range(sides)],mat,shadow=True)
for name,color in [('lanternGlow',(.95,.76,.37,1)),('flowerIvory',(.95,.86,.57,1)),('flowerRose',(.72,.34,.40,1))]:
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=color
for o in bpy.data.collections['wayfarer-street-furniture'].objects:
    if 'lamp-' in o.name:o['render_visible']=False;o['role']='decorative';o['shadow']=False
lamps=[(49.2,65),(58.8,65),(49.2,77),(58.8,77),(49.2,86),(58.8,86),(49,36),(59,36),(34,45),(38,53),(73,50),(84,58),(23,43),(30,75),(75,76),(87,70)]
for i,(x,y) in enumerate(lamps):
    ring(f'lantern-{i}-foot',x,y,0,.30,.22,.24,'stoneLight')
    ring(f'lantern-{i}-plinth',x,y,.24,.19,.12,.38,'iron')
    ring(f'lantern-{i}-shaft',x,y,.62,.095,.075,2.50,'iron')
    ring(f'lantern-{i}-collar',x,y,2.97,.16,.22,.13,'gold')
    ring(f'lantern-{i}-glass',x,y,3.13,.22,.28,.57,'lanternGlow',4)
    for j in range(4):
        a=j*math.pi/2;ring(f'lantern-{i}-mullion-{j}',x+.22*math.cos(a),y+.22*math.sin(a),3.1,.025,.025,.65,'iron',4)
    ring(f'lantern-{i}-hood',x,y,3.70,.36,.10,.22,'iron')
    ring(f'lantern-{i}-finial',x,y,3.92,.06,.005,.20,'gold')
# Replace visible geometric flower cubes with a cluster of petalled blossoms.
flower_positions=[]
for o in bpy.data.objects:
    if o.type=='MESH' and (o.get('render_visible',True) or o.get('bloom_replaced_v44')) and o.data.materials and o.data.materials[0].name=='flowers':
        pts=[o.matrix_world@v.co for v in o.data.vertices];center=sum(pts,Vector())/len(pts)
        flower_positions.append(center);o['render_visible']=False;o['role']='decorative';o['shadow']=False;o['bloom_replaced_v44']=True
for i,p in enumerate(flower_positions):
    for j in range(3):
        x=p.x+.11*math.cos(j*2.3+i);y=p.y+.11*math.sin(j*2.3+i);z=p.z+.10+(j%2)*.08;r=.10
        ring(f'flower-{i}-{j}-stem',x,y,z-.18,.013,.01,.18,'leaf',4)
        vs=[(x,y,z+.025)]+[(x+r*(1 if k%2==0 else .55)*math.cos(k*math.tau/10),y+r*(1 if k%2==0 else .55)*math.sin(k*math.tau/10),z) for k in range(10)]
        mesh(f'flower-{i}-{j}-petals',vs,[[0,k+1,(k+1)%10+1] for k in range(10)],'flowerRose' if i%3 else 'flowerIvory')
# Rocky strata follow the entire shoreline with small irregular facets. This
# removes enlarged repeating triangular outcrops from the previous scale pass.
for o in bpy.data.objects:
    if o.name.startswith(('district-v4-rock-bank-','bank-v4-')):o['render_visible']=False;o['role']='decorative';o['shadow']=False
ground=next(o for o in bpy.data.collections['court-terrain'].objects if o.type=='MESH' and not o.get('surface_role'))
outline=[ground.matrix_world@ground.data.vertices[i].co for i in json.loads(ground['outline_vertex_indices'])]
for i,(a,b) in enumerate(zip(outline,outline[1:]+outline[:1])):
    delta=b-a;length=math.hypot(delta.x,delta.y);count=max(2,math.ceil(length/1.7));nx,ny=delta.y/length,-delta.x/length
    for j in range(count):
        p=a+delta*j/count;q=a+delta*(j+1)/count
        spread=1.1+.35*math.sin(i*13+j*2.7);midz=-1.35+.22*math.sin(i+j*1.4)
        vs=[(p.x,p.y,0),(q.x,q.y,0),(p.x+nx*.6,p.y+ny*.6,midz),(q.x+nx*.8,q.y+ny*.8,midz-.15),(p.x+nx*spread,p.y+ny*spread,-3.08),(q.x+nx*(spread+.25),q.y+ny*(spread+.25),-3.08)]
        mesh(f'bank-{i}-{j}',vs,[[0,1,3],[0,3,2],[2,3,5],[2,5,4]],'bankStone' if j%3 else 'bankStoneLight')
# Original heraldic cloth surface on banner meshes only; awnings keep woven cloth.
banner=bpy.data.materials.get('bannerSilk') or bpy.data.materials.new('bannerSilk');banner.diffuse_color=(.2,.35,.48,1);banner['texture_json']=json.dumps({'file':'assets/wayfarer-banner-v44.svg','grid':[1,1],'tile':0,'worldSize':2})
for o in bpy.data.objects:
    if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='clothBlue' and any(s in o.name for s in ('banner','flag')):
        o.data.materials[0]=banner
        if not o.data.uv_layers.active:o.data.uv_layers.new(name='BannerUV')
        for face in o.data.polygons:
            pts=[o.data.vertices[o.data.loops[li].vertex_index].co for li in face.loop_indices];axes=(0,2) if abs(face.normal.y)>.5 else (1,2);lo=[min(p[k] for p in pts) for k in axes];hi=[max(p[k] for p in pts) for k in axes]
            for li,p in zip(face.loop_indices,pts):o.data.uv_layers.active.data[li].uv=tuple((p[k]-lo[j])/max(.001,hi[j]-lo[j]) for j,k in enumerate(axes))
# New architectural detail swatches are separate from paving/roof repeat lengths.
for name,tile,size in [('glass',0,1.2),('civicGlass',0,1.2),('civicGlassLight',0,1.2),('timber',1,2.4),('oak',1,2.4),('wood',1,2.4),('stone',2,4),('stoneLight',2,4),('civicIvory',2,4),('civicShadow',2,4),('wallStone',2,4),('wallCap',2,4),('clothBlue',3,2.5)]:
    if name in bpy.data.materials:bpy.data.materials[name]['texture_json']=json.dumps({'file':'assets/wayfarer-details-v44.webp','grid':[2,2],'tile':tile,'worldSize':size})
scene['detail_authoring_version']=44;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'))
print('Saved detailed lanterns,',len(flower_positions),'flower clusters, river strata and original heraldic banners')
