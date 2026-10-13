"""Actual Flare swing keys 13..16, their evaluated hand/weapon, unmodified camera."""
import bpy,json,sys,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]);out=Path(args[1]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False)
scene=bpy.context.scene;arm=bpy.data.objects['MaleArm'];sword=bpy.data.objects['Shortsword'];human=bpy.data.objects['HumanMale']
scene.camera=bpy.data.objects['Camera'];scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world=bpy.data.worlds.new('Study light');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
for o in bpy.data.objects:
    if o.type=='MESH':o.hide_render=o not in [human,sword]
for o,color in [(human,(.62,.67,.74,1)),(sword,(.9,.67,.2,1))]:
    mat=bpy.data.materials.new('Study '+o.name);mat.diffuse_color=color;mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color
    o.data.materials.clear();o.data.materials.append(mat)
data={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_frames':[13,14,15,16],
      'clock':'Source descriptor swing position12/4keys/400ms; key13..16 correspondence assumes one-based blend frame matching descriptor zero-based columns.',
      'camera_matrix':[list(row) for row in scene.camera.matrix_world], 'resolution':[512,512],
      'weapon_parent':[sword.parent.name,sword.parent_bone], 'weapon_local_vertices':[list(v.co) for v in sword.data.vertices],
      'frames':[],'dense':[],'scope':'Third-party actual source, no original-character retarget or naturalness acceptance.'}
def sample(frame):
    scene.frame_set(int(frame),subframe=frame-int(frame));dg=bpy.context.evaluated_depsgraph_get();dg.update();ea=arm.evaluated_get(dg);es=sword.evaluated_get(dg)
    bones={b.name: {'head':list(ea.matrix_world@b.head),'tail':list(ea.matrix_world@b.tail), 'matrix_world':[list(r) for r in ea.matrix_world@b.matrix]} for b in ea.pose.bones}
    verts=[list(es.matrix_world@v.co) for v in es.data.vertices]
    def px(v):
        p=world_to_camera_view(scene,scene.camera,Vector(v));return [512*p.x,512*(1-p.y),p.z]
    return {'source_frame':frame,'joints_world':bones,'joints_px':{n:{k:px(b[k]) for k in ['head','tail']} for n,b in bones.items()},
            'weapon_matrix_world':[list(r) for r in es.matrix_world], 'weapon_vertices_world':verts,'weapon_vertices_px':[px(v) for v in verts]}
for i in range(25):data['dense'].append(sample(13+i/8))
for i,f in enumerate([13,14,15,16]):
    item=sample(f);scene.render.filepath=str(out/f'{i:02}.png');bpy.ops.render.render(write_still=True)
    item.update(path=str(Path(scene.render.filepath)),sha256=hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest(),time_ms=i*100,duration_ms=100);data['frames'].append(item)
(out/'source-motion.json').write_text(json.dumps(data,indent=2));print('FLARE_ATTACK_SAMPLED',len(data['dense']),data['weapon_parent'])
