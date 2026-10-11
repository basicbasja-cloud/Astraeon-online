"""Bake independently complete 2D modules plus normalized per-pixel depth.

Each pose is evaluated once, then rendered into five orthographic cells in one
batch: native composite, body/outfit, head/hair, weapon, cape. Cell copies share
UVs and a world-normal paint shader, so translation changes neither scale nor
color. Covered hilt pixels belong to the actual holding hand. No 3D runtime.
"""
import argparse,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Matrix

parser=argparse.ArgumentParser();parser.add_argument('--action',default='Idle');parser.add_argument('--frames');parser.add_argument('--directions',default='S,SW,W,NW,N,NE,E,SE')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
base=Path(__file__).resolve().parents[1];s=bpy.context.scene
native=Path(bpy.data.filepath);source_hash=hashlib.sha256(native.read_bytes()).hexdigest()
exporter_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
key=hashlib.sha256((source_hash+exporter_hash).encode()).hexdigest()[:16]
out=base/'.character-tools/sprite-bakes'/key/args.action;out.mkdir(parents=True,exist_ok=True)
rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
clip=next(c for c in json.loads(s['clips']) if c['name']==args.action)
rig.animation_data.action=bpy.data.actions[clip['action']]
source_objects=[o for o in s.objects if o.get('spriteModule') and not o.hide_render]
assert all(sl.material.get('factoryPaintShader') for o in source_objects for sl in o.material_slots if sl.material),'Use the reproducible source paint shader.'
modules=['Composite','BodyOutfit','HeadHair','Weapon','Cape','Headgear']
original_cam=s.camera;span=original_cam.data.ortho_scale
body=next(o for o in source_objects if o.get('spriteModule')=='BodyOutfit')
hand=body.copy();hand.data=body.data.copy();hand.name='BAKE_HoldingHand';s.collection.objects.link(hand)
bm=bmesh.new();bm.from_mesh(hand.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if not all(v.co.x<-.397 and v.co.z>.675 for v in f.verts)],context='FACES')
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(hand.data);bm.free();hand.hide_render=True
holdout=bpy.data.materials.new('BAKE_HandHoldout');holdout.use_nodes=True;holdout.node_tree.nodes.clear()
a=holdout.node_tree.nodes.new('ShaderNodeHoldout');b=holdout.node_tree.nodes.new('ShaderNodeOutputMaterial');holdout.node_tree.links.new(a.outputs[0],b.inputs['Surface'])
render=bpy.data.scenes.new('ASTRAEON_SPRITE_BATCH');render.render.engine='BLENDER_EEVEE';render.render.film_transparent=True
render.render.resolution_x=320*len(modules);render.render.resolution_y=320;render.render.resolution_percentage=100
render.render.image_settings.file_format='PNG';render.render.image_settings.color_mode='RGBA'
render.view_settings.view_transform='Standard';render.view_settings.look='None';render.view_layers[0].use_pass_z=True
cam=original_cam.copy();cam.data=original_cam.data.copy();render.collection.objects.link(cam);render.camera=cam
cam.location.x+=span*(len(modules)-1)/2;cam.data.ortho_scale=span*len(modules)
tree=bpy.data.node_groups.new('SpriteLinearDepth','CompositorNodeTree');render.compositing_node_group=tree
layer=tree.nodes.new('CompositorNodeRLayers');layer.scene=render
mapping=tree.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=0;mapping.inputs['From Max'].default_value=10;mapping.inputs['To Min'].default_value=0;mapping.inputs['To Max'].default_value=1;mapping.clamp=True
tree.links.new(layer.outputs['Depth'],mapping.inputs['Value'])
depth=tree.nodes.new('CompositorNodeOutputFile');depth.format.media_type='IMAGE';depth.format.file_format='PNG';depth.format.color_mode='BW';depth.format.color_depth='16'
depth.directory=str(out);depth.file_output_items.new('RGBA','');tree.links.new(mapping.outputs[0],depth.inputs[0])
directions=[(d,y) for d,y in json.loads(s['directions']) if d in args.directions.split(',')]
frames=[int(f) for f in args.frames.split(',')] if args.frames else list(range(1,clip['frames']+1))
assert all(1<=f<=clip['frames'] for f in frames)
for direction,yaw in directions:
    root.rotation_euler.z=math.radians(yaw)
    for frame in frames:
        prefix=direction+'-'+str(frame).zfill(3)
        color_path=out/(prefix+'-tile.png');depth_path=out/(prefix+'-depth.png')
        if color_path.is_file() and depth_path.is_file():continue
        bpy.context.window.scene=s;s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        posed=[];objects=[]
        for original in source_objects:
            mesh=bpy.data.meshes.new_from_object(original.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);posed.append(mesh)
            for cell,module in enumerate(modules):
                if module!='Composite' and original['spriteModule']!=module:continue
                obj=bpy.data.objects.new('TILE_'+module+'_'+original.name,mesh);render.collection.objects.link(obj)
                obj.matrix_world=Matrix.Translation((cell*span,0,0))@original.matrix_world;objects.append(obj)
        mesh=bpy.data.meshes.new_from_object(hand.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
        mesh.materials.clear();mesh.materials.append(holdout)
        for p in mesh.polygons:p.material_index=0
        obj=bpy.data.objects.new('TILE_WeaponGripMask',mesh);render.collection.objects.link(obj)
        obj.matrix_world=Matrix.Translation((modules.index('Weapon')*span,0,0))@hand.matrix_world;objects.append(obj);posed.append(mesh)
        bpy.context.window.scene=render;depth.file_name=prefix+'-depth';render.render.filepath=str(color_path)
        bpy.ops.render.render(write_still=True)
        for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
        for mesh in posed:bpy.data.meshes.remove(mesh)
        print('SPRITE_BAKED '+args.action+' '+direction+' '+str(frame),flush=True)
receipt={**clip,'nativeSHA256':source_hash,'exporterSHA256':exporter_hash,'cacheKey':key,'directions':[d for d,y in directions],'bakedFrames':frames,
         'canvas':[320,320],'root':[160,264],'tileCells':modules,'depthRange':[0,10],
         'kind':'independent_complete_modules_with_depth','gripMask':'actual right holding-hand holdout in weapon cell',
         'ownerApproved':False,'runtimeAdmitted':False}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('SPRITE_BAKE_COMPLETE '+str(out),flush=True)
