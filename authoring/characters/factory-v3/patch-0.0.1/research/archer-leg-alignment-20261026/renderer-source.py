"""Render whole-rig leg diagnostics with left/right colors, never final art."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['library','controls','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh diagnostic folder')
    data=json.loads(a.controls.read_text());a.output.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(a.library.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01']
    rig.animation_data_clear()
    for bone in rig.pose.bones:
        bone.matrix_basis=Matrix.Identity(4)
        for constraint in bone.constraints:constraint.influence=0
    body=bpy.data.objects['F01_BodyOutfit']
    for obj in scene.objects:
        if obj.type in ['MESH','CURVE']:obj.hide_render=obj.name not in ['F01_BodyOutfit','F01_HeadHair']
    colors=[(.3,.3,.3,1),(.04,.45,.55,1),(.05,.7,.8,1),(.35,.9,1,1),(.5,.05,.35,1),(.8,.06,.55,1),(1,.4,.8,1)]
    body.data.materials.clear()
    for i,color in enumerate(colors):
        mat=bpy.data.materials.new('LegAudit'+str(i));mat.diffuse_color=color;body.data.materials.append(mat)
    groups={g.index:g.name for g in body.vertex_groups}
    def material(vertex):
        g=max(vertex.groups,key=lambda x:x.weight)if vertex.groups else None
        name=groups[g.group]if g else ''
        for side,offset in [('L',0),('R',3)]:
            if name=='Thigh.'+side:return offset+1
            if name=='Shin.'+side:return offset+2
            if name in ['Foot.'+side,'Toe.'+side]:return offset+3
        return 0
    for face in body.data.polygons:
        choices=[material(body.data.vertices[i])for i in face.vertices]
        face.material_index=max(set(choices),key=choices.count)
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL'
    scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
    scene.render.resolution_x=scene.render.resolution_y=1536;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.display.render_aa='8';records=[]
    frames=data['views']['NW']['frames']
    for i in [0,8,12]:
        row=frames[i]
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
            if bone.name in row['world_matrices']:
                bone.matrix=rig.matrix_world.inverted()@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[name].matrix)[r][c]-matrix[r][c])for name,matrix in row['world_matrices'].items()for r in range(4)for c in range(4))
        if error>3e-5:raise ValueError('Diagnostic changed native pose: '+str(error))
        for direction in ['NW','NE','SE']:
            spec=data['available_cameras'][direction]
            camera=scene.camera;camera.location=spec['location'];camera.rotation_euler=spec['rotation'];camera.data.type='ORTHO';camera.data.ortho_scale=spec['ortho_scale']
            folder=a.output/direction;folder.mkdir(exist_ok=True);scene.render.filepath=str((folder/f'{i:03d}.png').resolve());bpy.ops.render.render(write_still=True)
            records.append({'direction':direction,'index':i,'maximum_native_matrix_error':error,'source_action':row['source_action'],'source_frame':row['source_frame']})
    (a.output/'receipt.json').write_text(json.dumps({'status':'WHOLE_RIG_LEFT_RIGHT_LEG_DIAGNOSTIC_NOT_FINAL_ART','left_leg':'cyan','right_leg':'magenta','source_controls_sha256':sha(a.controls),'library_sha256':sha(a.library),'source_pose_changed':False,'frames':records,'naturalness_approved':False,'runtime_admitted':False},indent=2)+'\n')


if __name__=='__main__':main()
