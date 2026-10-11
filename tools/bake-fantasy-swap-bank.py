"""Render replacement parts and real pose sockets without regenerating motion."""
import argparse,bpy,bmesh,json,math,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
base=Path(__file__).resolve().parents[1];s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
parser=argparse.ArgumentParser();parser.add_argument('--action',default='Idle');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
clip=next(c for c in json.loads(s['clips']) if c['name']==args.action);rig.animation_data.action=bpy.data.actions[clip['action']]
bankhash=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();script_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();key=hashlib.sha256((bankhash+script_hash).encode()).hexdigest()[:16]
out=base/'.character-tools/swap-bakes'/key/args.action;out.mkdir(parents=True,exist_ok=True)
modules=['BodyAlt','WeaponAlt','Headgear','Offhand','WeaponUnmasked','GripHand'];span=s.camera.data.ortho_scale;original_cam=s.camera
source=[o for o in s.objects if o.get('swapModule')]
body=bpy.data.objects['F01_BodyOutfit'];hand=body.copy();hand.data=body.data.copy();s.collection.objects.link(hand)
bm=bmesh.new();bm.from_mesh(hand.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if not all(v.co.x<-.397 and v.co.z>.675 for v in f.verts)],context='FACES');bm.to_mesh(hand.data);bm.free()
hold=bpy.data.materials.new('SWAP_Holdout');hold.use_nodes=True;n=hold.node_tree.nodes;n.clear();h=n.new('ShaderNodeHoldout');output=n.new('ShaderNodeOutputMaterial');hold.node_tree.links.new(h.outputs[0],output.inputs['Surface'])
render=bpy.data.scenes.new('SWAP_BATCH');render.render.engine='BLENDER_EEVEE';render.render.film_transparent=True;render.render.resolution_x=320*len(modules);render.render.resolution_y=320;render.render.resolution_percentage=100;render.render.image_settings.file_format='PNG';render.render.image_settings.color_mode='RGBA';render.view_settings.view_transform='Standard';render.view_settings.look='None';render.view_layers[0].use_pass_z=True
cam=original_cam.copy();cam.data=original_cam.data.copy();render.collection.objects.link(cam);render.camera=cam;cam.location.x+=span*(len(modules)-1)/2;cam.data.ortho_scale=span*len(modules)
tree=bpy.data.node_groups.new('SwapDepth','CompositorNodeTree');render.compositing_node_group=tree;rl=tree.nodes.new('CompositorNodeRLayers');rl.scene=render;mapping=tree.nodes.new('ShaderNodeMapRange');mapping.inputs['From Min'].default_value=0;mapping.inputs['From Max'].default_value=10;mapping.inputs['To Min'].default_value=0;mapping.inputs['To Max'].default_value=1;mapping.clamp=True;tree.links.new(rl.outputs['Depth'],mapping.inputs['Value'])
depth=tree.nodes.new('CompositorNodeOutputFile');depth.format.media_type='IMAGE';depth.format.file_format='PNG';depth.format.color_mode='BW';depth.format.color_depth='16';depth.directory=str(out);depth.file_output_items.new('RGBA','');tree.links.new(mapping.outputs[0],depth.inputs[0]);poses={}
for direction,yaw in json.loads(s['directions']):
    root.rotation_euler.z=math.radians(yaw)
    for frame in range(1,clip['frames']+1):
        prefix=f'{direction}-{frame:03}';color=out/(prefix+'-tile.png');zpath=out/(prefix+'-depth.png')
        bpy.context.window.scene=s;s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
        contact=json.loads(s['swordContact']);p=rig.pose.bones['Hand.R'];grip=rig.matrix_world@(p.matrix@p.bone.matrix_local.inverted()@Vector(contact['centerModel']))
        points={'root':None,'head':rig.matrix_world@((rig.pose.bones['Head'].head+rig.pose.bones['Head'].tail)/2),'hand_R':grip,'hand_L':rig.matrix_world@((rig.pose.bones['Hand.L'].head+rig.pose.bones['Hand.L'].tail)/2),'back':rig.matrix_world@rig.pose.bones['Cape0'].head,'waist':rig.matrix_world@rig.pose.bones['Hips'].head}
        sockets={}
        for name,point in points.items():
            if point is None:sockets[name]=[160,264];continue
            q=original_cam.matrix_world.inverted()@point;sockets[name]=[160+q.x*320/span,160-q.y*320/span]
        poses[prefix]=sockets
        if color.exists() and zpath.exists():continue
        objects=[];meshes=[]
        def copy(obj,cell,mask=False):
            me=bpy.data.meshes.new_from_object(obj.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);meshes.append(me)
            if mask:
                me.materials.clear();me.materials.append(hold)
                for polygon in me.polygons:polygon.material_index=0
            new=bpy.data.objects.new('SWAP_TILE',me);render.collection.objects.link(new);new.matrix_world=Matrix.Translation((cell*span,0,0))@obj.matrix_world;objects.append(new)
        for obj in source:copy(obj,modules.index(obj['swapModule']))
        for obj in s.objects:
            if obj.get('spriteModule')=='Weapon' and not obj.get('swapModule'):copy(obj,4)
        copy(hand,1,True);copy(hand,5)
        bpy.context.window.scene=render;depth.file_name=prefix+'-depth';render.render.filepath=str(color);bpy.ops.render.render(write_still=True)
        for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
        for me in meshes:bpy.data.meshes.remove(me)
        print('SWAP_BAKED '+args.action+' '+prefix,flush=True)
receipt={**clip,'baseNativeSHA256':s['baseNativeSHA256'],'bankSHA256':bankhash,'exporterSHA256':script_hash,'key':key,'modules':modules,'sockets':poses,'proof':json.loads(s['swapProof'])}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SWAP_COMPLETE '+args.action,flush=True)
