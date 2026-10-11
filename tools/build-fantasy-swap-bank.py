"""Bounded equipment proof using the existing fitted source and motion library.

No bone, pose, camera or base-body sequence is regenerated. The alternate
outfit adds a fitted crimson cuirass to the recolored supplied garment.
"""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1];s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']]
s['baseNativeSHA256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
body=bpy.data.objects['F01_BodyOutfit'];alt=body.copy();alt.data=body.data.copy();alt.name='SWAP_CrimsonOutfit';s.collection.objects.link(alt);alt['swapModule']='BodyAlt';alt.hide_render=False
original=body.data.materials[0];mat=original.copy();mat.name='SWAP_CrimsonCloth';nodes=mat.node_tree.nodes;links=mat.node_tree.links
out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');emission=out.inputs['Surface'].links[0].from_node
old=emission.inputs['Color'].links[0].from_socket;links.remove(emission.inputs['Color'].links[0])
mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='COLOR';mix.inputs[0].default_value=.8;mix.inputs[2].default_value=(.20,.025,.048,1)
links.new(old,mix.inputs[1]);links.new(mix.outputs[0],emission.inputs['Color']);alt.data.materials.append(mat);index=len(alt.data.materials)-1
for p in alt.data.polygons:
    co=sum((alt.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
    if p.material_index==0 and .34<co.z<.64 and abs(co.x)<.17:p.material_index=index
contact=json.loads(s['swordContact']);guard=Vector(contact['centerModel'])+Vector(contact['axisModel'])*.05
for obj in list(s.objects):
    if obj.get('spriteModule')!='Weapon':continue
    new=obj.copy();new.data=obj.data.copy();new.name='SWAP_Alt_'+obj.name;s.collection.objects.link(new);new['swapModule']='WeaponAlt'
    if obj.name.endswith('Blade'):
        basis=Vector((0,-1,0)).rotation_difference(Vector(contact['axisModel']))
        for v in new.data.vertices:
            delta=basis.inverted()@(v.co-guard);delta.x*=1.22;delta.y*=.8;delta.z*=1.2;v.co=guard+basis@delta
def material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);l.new(em.outputs[0],out.inputs['Surface']);m['factoryPaintShader']=True;return m
bronze=material('SWAP_Gold',(.46,.29,.11));navy=material('SWAP_Navy',(.025,.08,.13));highlight=material('SWAP_GoldLight',(.64,.46,.20))
def mesh(name,vertices,faces,mat,module,bone):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();data.materials.append(mat)
    obj=bpy.data.objects.new(name,data);s.collection.objects.link(obj);obj.parent=rig;obj['swapModule']=module;obj['spriteModule']=module
    g=obj.vertex_groups.new(name=bone);g.add(list(range(len(vertices))),1,'REPLACE');mod=obj.modifiers.new('ExistingRigAttachment','ARMATURE');mod.object=rig
    assert min(p.area for p in data.polygons)>1e-10
    return obj
crimson=material('SWAP_CrimsonArmor',(.19,.023,.038))
# Closed fitted breastplate, matching the supplied torso's measured front
# surface. It is an actual garment surface, not a palette-only costume claim.
profile=[(-.09,.720),(.09,.720),(.112,.689),(.100,.636),(.071,.606),(-.071,.606),(-.100,.636),(-.112,.689)]
def front(z):return -.023-(.72-z)*.17
verts=[(x,front(z)+offset,z) for offset in [0,.007] for x,z in profile]
center=(0,-.048,.666);verts.append(center);n=len(profile)
faces=[(i,(i+1)%n,2*n) for i in range(n)]+[tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh('SWAP_CrimsonCuirass',verts,faces,crimson,'BodyAlt','Chest')
# Raised bronze perimeter follows the cuirass rather than original body paint.
inner=[(x*.935,.666+(z-.666)*.925) for x,z in profile]
verts=[(x,front(z)-.002,z) for x,z in profile]+[(x,front(z)-.006,z) for x,z in inner]
mesh('SWAP_CuirassBronzeBorder',verts,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],bronze,'BodyAlt','Chest')
segments=32
# Gold circlet fitted around the enlarged hair mass; it can be unequipped.
verts=[]
for z,rx,ry in [(.925,.152,.137),(.939,.152,.137),(.925,.145,.130),(.939,.145,.130)]:
    verts.extend([(rx*math.cos(i*math.tau/segments),.075+ry*math.sin(i*math.tau/segments),z) for i in range(segments)])
faces=[]
for ring1,ring2 in [(0,1),(1,3),(3,2),(2,0)]:
    faces.extend([(ring1*segments+i,ring1*segments+(i+1)%segments,ring2*segments+(i+1)%segments,ring2*segments+i) for i in range(segments)])
mesh('SWAP_Circlet',verts,faces,bronze,'Headgear','Head')
verts=[(-.018,-.065,.932),(0,-.067,.967),(.018,-.065,.932),(0,-.068,.917),(-.018,-.060,.932),(0,-.062,.967),(.018,-.060,.932),(0,-.063,.917)]
mesh('SWAP_CircletCrest',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],highlight,'Headgear','Head')
# An arm-strapped buckler: attachment is forearm, not an invented palm grip.
c=Vector((.347,.066,.786));verts=[tuple(c+Vector((.073*math.cos(i*math.tau/segments),.055*math.sin(i*math.tau/segments),z))) for z in [-.009,0] for i in range(segments)]
faces=[tuple(range(segments-1,-1,-1)),tuple(range(segments,2*segments))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
mesh('SWAP_BucklerRim',verts,faces,bronze,'Offhand','Forearm.L')
verts=[tuple(c+Vector((.060*math.cos(i*math.tau/segments),.043*math.sin(i*math.tau/segments),.001))) for i in range(segments)]
mesh('SWAP_BucklerFace',verts,[tuple(range(segments))],navy,'Offhand','Forearm.L')
verts=[tuple(c+Vector(v)) for v in [(-.017,0,.002),(0,-.020,.002),(.017,0,.002),(0,.020,.002),(0,0,.014)]]
mesh('SWAP_BucklerBoss',verts,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],highlight,'Offhand','Forearm.L')
s['swapProof']=json.dumps({'BodyAlt':'Crimson garment recolor plus fitted closed cuirass and bronze border; original body/rig retained','WeaponAlt':'Wider shorter blade; same hilt and Hand.R','Headgear':'Gold circlet; Head','Offhand':'Arm-strapped buckler; Forearm.L','motionReauthored':False,'cameraChanged':False,'ownerApproved':False})
bpy.ops.wm.save_as_mainfile(filepath=str(base/'.character-tools/checkpoints/fantasy-swap-bank.blend'))
(base/'authoring/characters/swordsman-production/fantasy-base-01/factory/swap-bank.json').write_text(json.dumps({'baseNativeSHA256':s['baseNativeSHA256'],'bankSHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'builderSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'proof':json.loads(s['swapProof']),'ownerApproved':False},indent=2)+'\n')
print('FANTASY_SWAP_BANK_CREATED',flush=True)
