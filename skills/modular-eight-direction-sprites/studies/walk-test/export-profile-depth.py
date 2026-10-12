"""Actual profile pelvis/thigh surface visibility and metric depth, no pose edits."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.output.exists():raise ValueError('Fresh output required')
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene;cam=scene.camera
motion=json.loads((a.blend.parent/'motion.json').read_text());pivot=bpy.data.objects['facing.pivot']
rig=next(o for o in scene.objects if o.type=='ARMATURE');meshes=[o for o in scene.objects if o.type=='MESH']
owners={};mats={}
for name,color in [('r',(.03,.35,1,1)),('l',(1,.35,.02,1)),('pelvis',(.56,.53,.58,1)),('other',(.26,.28,.3,1))]:
    mat=bpy.data.materials.new('profile-depth.'+name);mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=color;node.inputs['Roughness'].default_value=.85;mats[name]=mat
for o in meshes:
    groups={g.name for g in o.vertex_groups}
    sides=[s for s in ['r','l'] if groups.intersection({n+'_'+s for n in ['thigh','calf','foot','ball','ball_leaf']})]
    if len(sides)>1:raise ValueError('Mixed side mesh')
    owner=sides[0] if sides else 'pelvis' if o.name=='body.complete.torso' else 'other'
    owners[o.name]={'owner':owner,'slot':o.get('slot'),'bone_groups':sorted(groups)}
    o.pass_index={'r':1,'l':2,'pelvis':3,'other':4}[owner]
    o.data.materials.clear();o.data.materials.append(mats[owner])
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False
scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
layer=scene.view_layers[0];layer.use_pass_object_index=True;layer.use_pass_z=True
scene.use_nodes=True;nodes=scene.node_tree.nodes;nodes.clear();rl=nodes.new('CompositorNodeRLayers');comp=nodes.new('CompositorNodeComposite');scene.node_tree.links.new(rl.outputs['Image'],comp.inputs[0])
outputs={}
for name,socket in [('id','IndexOB'),('depth','Depth')]:
    node=nodes.new('CompositorNodeOutputFile');node.format.file_format='OPEN_EXR';node.format.color_depth='32';node.file_slots[0].path=name+'_';scene.node_tree.links.new(rl.outputs[socket],node.inputs[0]);outputs[name]=node
a.output.mkdir(parents=True);samples=[]
for view,angle in [('E',90),('W',270)]:
    pivot.rotation_euler.z=math.radians(angle)
    for k,index in enumerate([0,10,20,30]):
        t=motion['frames'][index]['time_seconds'];pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos));bpy.context.view_layer.update()
        bones={}
        for n in ['pelvis','thigh_r','calf_r','foot_r','thigh_l','calf_l','foot_l']:
            point=rig.matrix_world@rig.pose.bones[n].head;uv=world_to_camera_view(scene,cam,point);local=cam.matrix_world.inverted()@point
            bones[n]={'world':list(point),'xy':[uv.x*512,(1-uv.y)*512],'camera_axis_depth':-local.z}
        dr=a.output/view/f'{k:02}';dr.mkdir(parents=True)
        for mode in ['dressed','cutaway','right-amodal','left-amodal','pelvis-amodal']:
            for o in meshes:
                owner=owners[o.name]['owner'];alt=o.get('slot')=='hair.auburn'
                include=not alt if mode=='dressed' else owner in ['r','l','pelvis'] if mode=='cutaway' else owner=={'right-amodal':'r','left-amodal':'l','pelvis-amodal':'pelvis'}[mode]
                o.hide_render=not include;o.visible_camera=True
            for node in outputs.values():node.base_path=str(dr.resolve())
            scene.render.filepath=str((dr/(mode+'.png')).resolve());bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
            for name in outputs:
                files=list(dr.glob(name+'_*.exr'))
                if len(files)!=1:raise ValueError('EXR ambiguity')
                files[0].rename(dr/(mode+'-'+name+'.exr'))
        samples.append({'view':view,'key':k,'source_index':index,'time_seconds':t,'bones':bones})
receipt={'schema':'profile-source-depth-v1','blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),'motion_sha256':hashlib.sha256((a.blend.parent/'motion.json').read_bytes()).hexdigest(),
 'blender':bpy.app.version_string,'canvas':[512,512],'camera_matrix_world':[list(row) for row in cam.matrix_world],'camera_ortho_scale':cam.data.ortho_scale,
 'depth_encoding':'Raw Cycles Z pass, scene units; smaller surface depth is nearer. No per-frame normalization. Background excluded by integer owner ID.',
 'fixed_display_depth_range':[3.6,5.4],'owners':owners,'samples':samples,'render_passes':40,'source_pose_edited':False,
 'scope':'Cutaway removes other meshes to expose actual original pelvis and weighted leg meshes. It is a diagnostic source pass, not recovered anatomy of generated art.'}
(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PROFILE_DEPTH',len(samples),'poses / 40 passes')
