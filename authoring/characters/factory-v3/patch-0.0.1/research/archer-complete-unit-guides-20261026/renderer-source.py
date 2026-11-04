"""Render complete BodyCostume and HeadHair guides from the same actual pose.

No limb templates are created. Per-unit source viewports are recorded editing
crops; native camera, pixels-per-meter and full-canvas registration stay fixed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rig','controls','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--indices',nargs='+',type=int,required=True)
    p.add_argument('--directions',nargs='+',default=['NW'])
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh guide set')
    data=json.loads(a.controls.read_text());rows=data['views']['NW']['frames']
    if len(a.indices)!=len(set(a.indices))or any(i<0 or i>=len(rows)for i in a.indices):raise ValueError('Invalid source indices')
    if any(d not in data['available_cameras']for d in a.directions):raise ValueError('Unknown real camera')
    a.output.mkdir(parents=True);bpy.ops.wm.open_mainfile(filepath=str(a.rig.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01'];rig.animation_data_clear()
    source_objects=[bpy.data.objects[n]for n in ['F01_BodyOutfit','F01_HeadHair']]
    for obj in scene.objects:
        if obj.type in ['MESH','CURVE']:obj.hide_render=True
    palette={'coat':(.11,.16,.07,1),'cream':(.78,.70,.53,1),'leather':(.28,.13,.055,1),'pants':(.16,.17,.09,1),'skin':(.73,.48,.30,1),'hair':(.27,.10,.035,1)};materials={}
    for role,color in palette.items():
        mat=bpy.data.materials.new('UnitGuide_'+role);mat.diffuse_color=color;materials[role]=mat
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
    scene.render.resolution_x=scene.render.resolution_y=1536;scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.display.render_aa='8';records=[]
    for index in a.indices:
        row=rows[index]
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
            if bone.name in row['world_matrices']:
                bone.matrix=rig.matrix_world.inverted()@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[n].matrix)[r][c]-m[r][c])for n,m in row['world_matrices'].items()for r in range(4)for c in range(4))
        if error>3e-5:raise ValueError('Source pose replay differs')
        objects=[]
        for unit in ['BodyCostume','HeadHair']:
            verts=[];faces=[];labels=[];graph=bpy.context.evaluated_depsgraph_get()
            for source in source_objects:
                evaluated=source.evaluated_get(graph);mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=graph);offset=len(verts);verts.extend(tuple(evaluated.matrix_world@v.co)for v in mesh.vertices);names={g.index:g.name for g in source.vertex_groups}
                weights=[{names[g.group]:g.weight for g in vertex.groups}for vertex in mesh.vertices]
                for face in mesh.polygons:
                    head=source.name=='F01_HeadHair'or sum(weights[i].get('Head',0)for i in face.vertices)/len(face.vertices)>.5
                    if head!=(unit=='HeadHair'):continue
                    faces.append(tuple(offset+i for i in face.vertices))
                    if head:role='hair'if source.name=='F01_HeadHair'else'skin'
                    else:
                        influences={}
                        for i in face.vertices:
                            for name,value in weights[i].items():influences[name]=influences.get(name,0)+value
                        name=max(influences,key=influences.get)
                        role='skin'if name.startswith('Neck')else'leather'if name.startswith(('Hand','Index','Middle','Ring','Pinky','Thumb','Foot','Toe'))else'cream'if name.startswith(('UpperArm','Forearm'))else'pants'if name.startswith(('Thigh','Shin'))else'coat'
                    labels.append(role)
                evaluated.to_mesh_clear()
            mesh=bpy.data.meshes.new(unit+'_actual_pose');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(obj)
            keys=list(materials)
            for mat in materials.values():mesh.materials.append(mat)
            for face,label in zip(mesh.polygons,labels):face.material_index=keys.index(label)
            obj.hide_render=True;objects.append((unit,obj))
        for direction in a.directions:
            spec=data['available_cameras'][direction];camera=scene.camera;camera.location=spec['location'];camera.rotation_euler=spec['rotation'];camera.data.ortho_scale=spec['ortho_scale'];bpy.context.view_layer.update()
            for unit,obj in objects:
                obj.hide_render=False;folder=a.output/direction/unit;folder.mkdir(parents=True,exist_ok=True);path=folder/f'{index:03d}.png';scene.render.filepath=str(path.resolve());bpy.ops.render.render(write_still=True);obj.hide_render=True
                records.append({'direction':direction,'unit':unit,'source_index':index,'native_file':str(path),'sha256':sha(path),'maximum_matrix_error':error})
        for _,obj in objects:
            mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    (a.output/'receipt.json').write_text(json.dumps({'status':'COMPLETE_UNIT_NATIVE_GUIDES_NOT_FINISHED_ART','units':['BodyCostume','HeadHair'],'frames':records,'native_canvas':[1536,1536],'source_sha256':{str(f):sha(f)for f in [a.rig,a.controls]},'implementation_sha256':sha(Path(__file__)),'camera_changed':False,'limb_templates_created':False,'runtime_admitted':False},indent=2)+'\n');(a.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':main()
