"""Actual deformed-mesh leg ownership, visible vs amodal, with integer IndexOB."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--views',default='S,SE,E,NE,N,NW,W,SW');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
if a.output.exists():raise ValueError('Use fresh owner render output')
bpy.ops.wm.open_mainfile(filepath=str(a.blend));scene=bpy.context.scene
motion=json.loads((a.blend.parent/'motion.json').read_text());pivot=bpy.data.objects['facing.pivot'];directions=['S','SE','E','NE','N','NW','W','SW']
objects=[o for o in scene.objects if o.type=='MESH'];owners={};materials={}
for owner,color in [('r',(.025,.30,1,1)),('l',(1,.28,.01,1)),('other',(.22,.24,.27,1))]:
    m=bpy.data.materials.new('diagnostic.owner.'+owner);m.use_nodes=True;m.node_tree.nodes.clear()
    e=m.node_tree.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=color;e.inputs['Strength'].default_value=1
    out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);materials[owner]=m
for o in objects:
    groups={g.name for g in o.vertex_groups};hits=[]
    for side in ['r','l']:
        if groups.intersection({n+'_'+side for n in ['thigh','calf','foot','ball','ball_leaf']}):hits.append(side)
    if len(hits)>1:raise ValueError('Mixed anatomical owner '+o.name)
    owner=hits[0] if hits else 'other';owners[o.name]={'owner':owner,'bone_groups':sorted(groups)}
    o.pass_index={'r':1,'l':2,'other':3}[owner];o.data.materials.clear();o.data.materials.append(materials[owner])
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False
scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.view_layers[0].use_pass_object_index=True;scene.use_nodes=True;n=scene.node_tree.nodes;n.clear()
rl=n.new('CompositorNodeRLayers');comp=n.new('CompositorNodeComposite');scene.node_tree.links.new(rl.outputs['Image'],comp.inputs[0])
raw=n.new('CompositorNodeOutputFile');raw.format.file_format='OPEN_EXR';raw.format.color_depth='32';raw.file_slots[0].path='owner_'
scene.node_tree.links.new(rl.outputs['IndexOB'],raw.inputs[0]);a.output.mkdir(parents=True);records=[]
for view in a.views.split(','):
    if view not in directions:raise ValueError('Bad view')
    pivot.rotation_euler.z=directions.index(view)*math.pi/4
    for k,index in enumerate([0,10,20,30]):
        t=motion['frames'][index]['time_seconds'];pos=t*1000;scene.frame_set(math.floor(pos),subframe=pos-math.floor(pos))
        dr=a.output/view/f'{k:02}';dr.mkdir(parents=True)
        for mode in ['visible','right-amodal','left-amodal']:
            for o in objects:
                owner=owners[o.name]['owner'];alternate=o.get('slot')=='hair.auburn'
                o.hide_render=alternate or (mode=='right-amodal' and owner!='r') or (mode=='left-amodal' and owner!='l')
                o.visible_camera=True
            raw.base_path=str(dr.resolve());scene.render.filepath=str((dr/(mode+'.png')).resolve())
            bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
            files=list(dr.glob('owner_*.exr'))
            if len(files)!=1:raise ValueError('Owner output ambiguity')
            files[0].rename(dr/(mode+'.exr'))
        records.append({'view':view,'key':k,'source_index':index,'time_seconds':t})
(a.output/'owner-receipt.json').write_text(json.dumps({'schema':'actual-leg-owner-v1','blend_sha256':hashlib.sha256(a.blend.read_bytes()).hexdigest(),
 'motion_sha256':hashlib.sha256((a.blend.parent/'motion.json').read_bytes()).hexdigest(),'blender':bpy.app.version_string,
 'canvas':[512,512],'id_values':{'background':0,'anatomical_right_leg':1,'anatomical_left_leg':2,'other_occluders':3},
 'owners':owners,'samples':records,'scope':'Actual mesh weights and depth visibility, not guessed generated-art labels; amodal isolation removes other meshes; IndexOB is non-antialiased'},indent=2)+'\n')
print('OWNER_RENDERED',len(records),'poses,',len(records)*3,'actual visibility/isolation passes')
