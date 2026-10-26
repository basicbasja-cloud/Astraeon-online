"""Author explicit 3D boot contact IK on a derived Archer pose copy.

Keeps upper-body matrices, foot orientation and camera unchanged. Foot XY is
retained by default or fixed to an explicitly supplied authored support plan.
Never modifies the source rig, original captures or drawings.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['library','controls','donor','output']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--support-anchors',type=Path)
    p.add_argument('--weapon',choices=['none','bow'],default='none')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh contact adaptation')
    original=json.loads(a.controls.read_text());donor=json.loads(a.donor.read_text())
    anchors=json.loads(a.support_anchors.read_text())['feet']if a.support_anchors else None
    if anchors and not all(anchors[s]['solver_success']for s in ['L','R']):raise ValueError('Support plan did not solve')
    # This grounded action's toe heads never rise above their ready-pose
    # reference. Foot roll can lower a toe head, so equal head heights are not
    # a contact test. Do not flatten a source-authored positive toe lift.
    baseline={side:donor['frames'][0]['bones']['ball_'+side]['head'][2]for side in ['l','r']}
    for row in donor['frames']:
        if any(row['bones']['ball_'+side]['head'][2]>baseline[side]+.001 for side in baseline):
            raise ValueError('Donor includes a toe lift; support phases need explicit authoring')
    a.output.mkdir(parents=True);bpy.ops.wm.open_mainfile(filepath=str(a.library.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01'];rig.animation_data_clear()
    for bone in rig.pose.bones:
        bone.matrix_basis=Matrix.Identity(4)
        for constraint in bone.constraints:constraint.influence=0
    body=bpy.data.objects['F01_BodyOutfit']
    for obj in scene.objects:
        if obj.type in ['MESH','CURVE']:obj.hide_render=obj.name not in ['F01_BodyOutfit','F01_HeadHair']
    props={}
    if a.weapon=='bow':
        for name,radius,color in [('bow',.018,(.3,.15,.06,1)),('string',.003,(.8,.8,.75,1)),('arrow',.006,(.55,.4,.15,1))]:
            curve=bpy.data.curves.new('ContactGuide_'+name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius
            obj=bpy.data.objects.new(curve.name,curve);scene.collection.objects.link(obj)
            mat=bpy.data.materials.new(curve.name);mat.diffuse_color=color;curve.materials.append(mat);props[name]=obj
    groups={s:{body.vertex_groups[n+'.'+s].index for n in ['Foot','Toe']}for s in ['L','R']}
    def world(name):return rig.matrix_world@rig.pose.bones[name].matrix
    def point(name):return world(name).translation.copy()
    def soles():
        graph=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(graph);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=graph)
        result={s:min((ev.matrix_world@v.co).z for v in mesh.vertices if sum(g.weight for g in v.groups if g.group in ids)>.5)for s,ids in groups.items()}
        ev.to_mesh_clear();return result
    def solve(side,goal):
        upper,lower,foot=['Thigh.'+side,'Shin.'+side,'Foot.'+side]
        hip,knee,ankle=[point(n)for n in [upper,lower,foot]];foot_matrix=world(foot).copy()
        u=(knee-hip).length;l=(ankle-knee).length;axis=goal-hip;distance=axis.length
        if not abs(u-l)+1e-5<distance<u+l-1e-5:
            raise ValueError('Foot contact would require stretching or pelvis movement')
        axis.normalize();along=(u*u-l*l+distance*distance)/(2*distance)
        # Preserve the original anatomical bend plane. Projecting the old
        # knee directly against a displaced ankle axis can reverse the pole
        # when the source leg is almost straight.
        old_axis=(ankle-hip).normalized()
        pole=knee-hip;pole-=old_axis*pole.dot(old_axis)
        if pole.length<1e-5:raise ValueError('Knee pole is ambiguous')
        pole=old_axis.rotation_difference(axis)@pole
        pole-=axis*pole.dot(axis)
        pole.normalize();new_knee=hip+axis*along+pole*math.sqrt(max(0,u*u-along*along))
        for name,end in [(upper,new_knee),(lower,goal)]:
            bone=rig.pose.bones[name];matrix=world(name)
            current=rig.matrix_world@bone.tail-matrix.translation;desired=end-matrix.translation
            rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
            bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
        foot_matrix.translation=point(foot);rig.pose.bones[foot].matrix=rig.matrix_world.inverted()@foot_matrix;bpy.context.view_layer.update()
        if (point(foot)-goal).length>3e-5:raise ValueError('IK ankle goal not reached')
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.display.shading.light='STUDIO';scene.display.shading.show_cavity=True
    scene.render.resolution_x=scene.render.resolution_y=1536;scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.display.render_aa='8'
    derived=copy.deepcopy(original);derived['views']={};records=[]
    directions=['SW','NW','NE','SE']
    for direction in directions:derived['views'][direction]={'camera':original['available_cameras'][direction],'frames':[]}
    for row in original['views']['NW']['frames']:
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
            if bone.name in row['world_matrices']:
                bone.matrix=rig.matrix_world.inverted()@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
        before=soles();old={n:world(n).copy()for n in row['world_matrices']}
        if anchors:
            for side in ['L','R']:
                goal=point('Foot.'+side);goal.x,goal.y=anchors[side]['ankle_xy_world_m'];solve(side,goal)
        for iteration in range(4):
            heights=soles()
            if max(abs(z)for z in heights.values())<1e-5:break
            for side,height in heights.items():
                if abs(height)>1e-5:
                    goal=point('Foot.'+side);goal.z-=height;solve(side,goal)
        after=soles()
        if max(abs(z)for z in after.values())>1e-4:raise ValueError('Actual boot geometry did not contact floor')
        unchanged=[n for n in old if not n.startswith(('Thigh.','Shin.','Foot.','Toe.'))]
        upper_error=max(abs(world(n)[r][c]-old[n][r][c])for n in unchanged for r in range(4)for c in range(4))
        if upper_error>3e-5:raise ValueError('Foot repair moved upper body')
        for side in ['L','R']:
            n='Foot.'+side
            expected=Vector(anchors[side]['ankle_xy_world_m'])if anchors else old[n].translation.xy
            if (world(n).translation.xy-expected).length>3e-5:raise ValueError('Foot missed intended XY support')
            if world(n).to_quaternion().rotation_difference(old[n].to_quaternion()).angle>1e-4:raise ValueError('Foot orientation changed')
        matrices={n:[list(r)for r in world(n)]for n in row['world_matrices']}
        records.append({'index':row['index'],'before_sole_z_m':before,'after_sole_z_m':after,'upper_body_maximum_matrix_error':upper_error,'foot_xy_changed':bool(anchors),'foot_rotation_changed':False,'reach_clamped':False,'ankle_world_positions':{s:list(point('Foot.'+s))for s in ['L','R']}})
        if props:
            left=Vector(row['bow_grip_world']);nock=Vector(row['string_nock_world']);aim=(left-nock).normalized();up=Vector((0,0,1));up-=aim*up.dot(aim);up.normalize()
            ends=[left+up*(.52*t)+aim*(-.22*t*t+.07*abs(t)**6)for t in [k/12-1 for k in range(25)]]
            for name,points in [('bow',ends),('string',[ends[0],nock,ends[-1]]),('arrow',[nock,left+aim*.4])]:
                curve=props[name].data;curve.splines.clear();line=curve.splines.new('POLY');line.points.add(len(points)-1)
                for curve_point,value in zip(line.points,points):curve_point.co=(*value,1)
            props['arrow'].hide_render=not row['arrow_visible']
        for direction in directions:
            spec=original['available_cameras'][direction];camera=scene.camera;camera.location=spec['location'];camera.rotation_euler=spec['rotation'];camera.data.ortho_scale=spec['ortho_scale'];bpy.context.view_layer.update()
            new=copy.deepcopy(row);new['world_matrices']=matrices;new['landmarks']={}
            for name in matrices:
                projected=world_to_camera_view(scene,camera,point(name));new['landmarks'][name]=[projected.x*1536,(1-projected.y)*1536]
            new['contact_adaptation']='anchored-support-boot-IK-v2'if anchors else'paired-boot-sole-IK-v1';derived['views'][direction]['frames'].append(new)
            folder=a.output/direction;folder.mkdir(exist_ok=True);scene.render.filepath=str((folder/f'{row["index"]:03d}.png').resolve());bpy.ops.render.render(write_still=True)
        print('PAIRED_BOOT_CONTACT_REPAIRED',row['index'],after,flush=True)
    derived.update({'parent_controls_sha256':sha(a.controls),'parent_canonical_implementation_sha256':original['canonical_implementation_sha256'],'canonical_implementation_sha256':sha(Path(__file__)),'implementation_sha256':sha(Path(__file__)),'contact_adaptation':'anchored-support-boot-IK-v2'if anchors else'paired-boot-sole-IK-v1','original_source_motion_unchanged':False,'adaptation_note':'Explicit target-rig leg IK preserves upper body and foot orientation. Support XY is fixed to the separate authored plan when supplied; otherwise source XY is retained. Actual weighted boot soles match the support plane.','runtime_admitted':False})
    (a.output/'pose-controls.json').write_text(json.dumps(derived,indent=2)+'\n')
    inputs=[a.library,a.controls,a.donor]+([a.support_anchors]if a.support_anchors else[])
    (a.output/'contact-repair-receipt.json').write_text(json.dumps({'status':'DERIVED_3D_FOOT_CONTACT_REPAIR_REQUIRES_MOTION_AND_ART_REVIEW','frames':records,'actual_captures':64,'input_sha256':{str(f):sha(f)for f in inputs},'implementation_sha256':sha(Path(__file__)),'source_files_modified':False,'camera_changed':False,'support_anchors_authored':bool(anchors),'guide_weapon':a.weapon,'naturalness_approved':False,'runtime_admitted':False},indent=2)+'\n')
    (a.output/'repair-source.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':main()
