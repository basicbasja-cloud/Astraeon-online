"""Capture bow/arrow geometry and front/back ownership from actual rig poses.

The bow binds to the left grip/wrist; a loaded string follows the right nock.
The arrow has a fixed authored length and explicit nock/release states.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rig','controls','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--arrow-length',type=float,default=1.0)
    p.add_argument('--nock-index',type=int,default=5)
    p.add_argument('--release-index',type=int,default=10)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Choose a fresh geometry capture')
    if not .5<=a.arrow_length<=1.5:raise ValueError('Invalid authored arrow length')
    data=json.loads(a.controls.read_text());rows=data['views']['NW']['frames'];bpy.ops.wm.open_mainfile(filepath=str(a.rig.resolve()))
    if not 0<=a.nock_index<a.release_index<len(rows):raise ValueError('Author explicit nock/release indices')
    reference=rows[8];reference_hand=Matrix(reference['world_matrices']['Hand.L']).to_quaternion()
    reference_aim=(Vector(reference['bow_grip_world'])-Vector(reference['grip_world'])).normalized()
    reference_up=Vector((0,0,1));reference_up-=reference_aim*reference_up.dot(reference_aim);reference_up.normalize()
    local_aim=reference_hand.inverted()@reference_aim;local_up=reference_hand.inverted()@reference_up
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01'];rig.animation_data_clear()
    camera=scene.camera;captures=[]
    for row in rows:
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
            if bone.name in row['world_matrices']:
                bone.matrix=rig.matrix_world.inverted()@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[n].matrix)[r][c]-m[r][c])for n,m in row['world_matrices'].items()for r in range(4)for c in range(4))
        if error>3e-5:raise ValueError('Rig pose replay differs')
        verts=[];faces=[];graph=bpy.context.evaluated_depsgraph_get()
        for name in ['F01_BodyOutfit','F01_HeadHair']:
            obj=bpy.data.objects[name];evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh();offset=len(verts)
            verts.extend(evaluated.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(offset+i for i in face.vertices)for face in mesh.polygons);evaluated.to_mesh_clear()
        body=BVHTree.FromPolygons(verts,faces,all_triangles=False)
        grip=Vector(row['bow_grip_world']);right=Vector(row['grip_world']);hand=Matrix(row['world_matrices']['Hand.L']).to_quaternion();loaded=a.nock_index<=row['index']<a.release_index
        aim=(grip-right).normalized()if loaded else(hand@local_aim).normalized()
        up=hand@local_up;up-=aim*up.dot(aim)
        if up.length<1e-5:raise ValueError('Degenerate bow plane')
        up.normalize();side=aim.cross(up).normalized()
        nock=right if loaded else grip-aim*.15
        bow=[]
        for i in range(129):
            t=i/64-1;point=grip+up*(.52*t)+aim*(-.22*t*t+.07*abs(t)**6);bow.append((point,t))
        def line(start,end,count=65):return [(start.lerp(end,i/(count-1)),i/(count-1))for i in range(count)]
        paths=[('wood',bow),('string',line(bow[0][0],nock)+line(nock,bow[-1][0])[1:])]
        polygons=[]
        if loaded:
            arrow_rest=grip+up*.025;arrow_aim=(arrow_rest-nock).normalized()
            tip=nock+arrow_aim*a.arrow_length;neck=tip-arrow_aim*.055;tail=nock-arrow_aim*.025
            paths.append(('shaft',line(tail,neck,129)))
            ring=[neck+up*.014,neck+side*.014,neck-up*.014,neck-side*.014]
            polygons.extend(('steel'+str(i%2),[tip,ring[i],ring[(i+1)%4]])for i in range(4))
            for sign in [-1,1]:
                polygons.append(('feather',[nock+arrow_aim*.035,nock+arrow_aim*.14,nock+arrow_aim*.115+up*(.025*sign),nock+arrow_aim*.05+up*(.017*sign)]))
        for direction in ['SW','NW','NE','SE']:
            spec=data['available_cameras'][direction];camera.location=spec['location'];camera.rotation_euler=spec['rotation'];camera.data.ortho_scale=spec['ortho_scale'];bpy.context.view_layer.update()
            to_camera=camera.matrix_world.to_quaternion()@Vector((0,0,1));inverse=camera.matrix_world.inverted()
            def point_record(point,param=0):
                projected=world_to_camera_view(scene,camera,point)
                hit,normal,face,distance=body.ray_cast(point+to_camera*.0005,to_camera,100)
                return {'xy':[projected.x*1536,(1-projected.y)*1536],'world':list(point),'parameter':param,'behind_body':hit is not None,'camera_depth':-(inverse@point).z}
            rendered_paths=[{'material':name,'points':[point_record(point,t)for point,t in points]}for name,points in paths]
            rendered_polys=[]
            for material,points in polygons:
                center=sum(points,Vector())/len(points);owner=point_record(center)
                rendered_polys.append({'material':material,'points':[point_record(point)for point in points],'behind_body':owner['behind_body'],'camera_depth':owner['camera_depth']})
            captures.append({'direction':direction,'index':row['index'],'camera':spec,'paths':rendered_paths,'polygons':rendered_polys,'arrow_visible':loaded,'parent_diagnostic_arrow_visible':row['arrow_visible'],'bow_grip_world':list(grip),'right_nock_world':list(nock),'maximum_pose_matrix_error':error})
        print('RIG_WEAPON_GEOMETRY',row['index'],flush=True)
    result={'status':'RIG_BOUND_WEAPON_GEOMETRY_NOT_FINAL_ART_OR_GAMEPLAY_APPROVAL','canvas':[1536,1536],'frames':captures,'arrow_length_m':a.arrow_length,'authored_nock_index':a.nock_index,'authored_release_index':a.release_index,'arrow_rest_offset_m':.025,'unloaded_bow_binding':'left-hand world orientation calibrated at source pose8; never driven by the released right hand','source_sha256':{str(f):sha(f)for f in [a.rig,a.controls]},'implementation_sha256':sha(Path(__file__)),'occlusion':'actual posed reference-body/head BVH; painted silhouette/hand boundary review still required','camera_changed':False,'runtime_admitted':False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
