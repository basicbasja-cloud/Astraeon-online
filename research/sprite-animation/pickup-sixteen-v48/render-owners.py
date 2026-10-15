"""Physical full-scene occlusion at the new times, no anatomical image inference."""
import bpy,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'source/parent-v45.blend'))
sc=bpy.context.scene;sc.camera=bpy.data.objects['N'];sc.cycles.samples=1
colors={'body':(.08,.08,.08),'left':(1,.3,.01),'right':(0,0,1),'head':(0,1,0),'item':(1,0,0)};mats={}
for key,color in colors.items():
 m=bpy.data.materials.new('v48_owner_'+key);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);mats[key]=m
for o in sc.objects:
 if o.type!='MESH':continue
 label='item' if o.name=='collectible' else 'head' if o.get('runtime_slot')=='complete_head' else 'right' if o.name.startswith('right.') else 'left' if o.name.startswith('left.') else 'body'
 o.data.materials.clear();o.data.materials.append(mats[label])
 for poly in o.data.polygons:poly.material_index=0
records=[]
for i,k in enumerate([.5,1.5,2.5,3.5,4.5,5.5,6+1/3,6+2/3]):
 tick=1+39*k/7;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick))
 folder=P/'source/raw-owners';folder.mkdir(parents=True,exist_ok=True);path=folder/f'{i:02}.png';sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 records.append({'index':i,'key_fraction':k,'path':str(path.relative_to(P)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(P/'source/owner-receipt.json').write_text(json.dumps({'frames':records,'scope':'Actual source surface ownership with physical occlusion; not painted pixels','production_pass':False},indent=2)+'\n')
