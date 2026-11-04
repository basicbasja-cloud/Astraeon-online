"""Measure actual canonical skin/prop displacement for optional study reuse.

This does not authorize an original-guide pose override or final-art admission.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def weapon_points(row):
    left=Vector(row['bow_grip_world']);nock=Vector(row['string_nock_world']);aim=(left-nock).normalized();up=Vector((0,0,1));up-=aim*up.dot(aim);up.normalize()
    points=[left+up*(.52*t)+aim*(-.22*t*t+.07*abs(t)**6)for t in [k/12-1 for k in range(25)]]
    return points+[nock,left+aim*.4]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['rig','controls','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--pairs',nargs='+',required=True);p.add_argument('--runtime-size',type=int,default=240);p.add_argument('--threshold',type=float,default=.5)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.output.exists():raise ValueError('Preserve previous measurements')
    data=json.loads(a.controls.read_text());rows=data['views']['NW']['frames'];bpy.ops.wm.open_mainfile(filepath=str(a.rig.resolve()))
    scene=bpy.context.scene;rig=bpy.data.objects['ARM_FantasyCharacter01'];rig.animation_data_clear();snapshots={}
    meshes=[bpy.data.objects[n]for n in ['F01_BodyOutfit','F01_HeadHair']]
    def snapshot(index):
        if index in snapshots:return snapshots[index]
        row=rows[index]
        for bone in sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive)):
            if bone.name in row['world_matrices']:
                bone.matrix=rig.matrix_world.inverted()@Matrix(row['world_matrices'][bone.name]);bpy.context.view_layer.update()
        error=max(abs((rig.matrix_world@rig.pose.bones[n].matrix)[r][c]-m[r][c])for n,m in row['world_matrices'].items()for r in range(4)for c in range(4))
        if error>3e-5:raise ValueError('Source matrix replay differs')
        graph=bpy.context.evaluated_depsgraph_get();result={}
        for obj in meshes:
            ev=obj.evaluated_get(graph);mesh=ev.to_mesh();result[obj.name]=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
        result['weapon']=weapon_points(row);snapshots[index]=result;return result
    result=[];ppm=a.runtime_size/data['available_cameras']['NW']['ortho_scale']
    for pair in a.pairs:
        first,last=[int(n)for n in pair.split(':')];before=snapshot(first);after=snapshot(last)
        bounds={name:max((x-y).length for x,y in zip(before[name],after[name]))*ppm for name in before}
        if any(len(before[name])!=len(after[name])for name in before):raise ValueError('Topology changed')
        same_arrow=rows[first]['arrow_visible']==rows[last]['arrow_visible'];eligible=[]
        if bounds['F01_BodyOutfit']<=a.threshold:eligible.append('BodyCostume')
        if bounds['F01_HeadHair']<=a.threshold:eligible.append('HeadHair')
        if bounds['weapon']<=a.threshold and same_arrow:eligible.append('Weapon')
        result.append({'from_index':first,'to_index':last,'conservative_runtime_pixel_bounds':bounds,'same_arrow_state':same_arrow,'study_eligible_roles':eligible,'same_source_action':rows[first]['source_action']==rows[last]['source_action']})
    a.output.write_text(json.dumps({'status':'CANONICAL_STUDY_REUSE_MEASUREMENTS_NOT_ORIGINAL_GUIDE_CERTIFICATES','source_sha256':{str(f):sha(f)for f in [a.rig,a.controls]},'implementation_sha256':sha(Path(__file__)),'runtime_size':a.runtime_size,'threshold_runtime_px':a.threshold,'pairs':result,'timing_changed':False,'source_images_modified':False,'runtime_admitted':False},indent=2)+'\n')
    print('CANONICAL_REUSE_BOUNDS '+json.dumps(result))


if __name__=='__main__':main()
