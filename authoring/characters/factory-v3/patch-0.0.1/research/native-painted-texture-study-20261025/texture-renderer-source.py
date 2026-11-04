"""Inspect existing packed painted textures on the unchanged native rig.

Replays the frozen canonical guide implementation. Only display materials change;
source cameras and projected joint/prop data must match their retained captures.
This is a material/geometry study, not admitted character artwork.
"""
import argparse
import ast
import json
from pathlib import Path
import sys

import bpy


def sha(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def enable_textures(scene,records):
    scene.display.shading.color_type='TEXTURE'
    scene.display.shading.light='FLAT'
    scene.display.shading.show_cavity=False
    scene.display.shading.show_shadows=False
    for material in bpy.data.materials:
        if not material.use_nodes:continue
        textures=[n for n in material.node_tree.nodes if n.type=='TEX_IMAGE'and n.image]
        color=[n for n in textures if 'basecolor'in n.image.name.lower()or n.image.name.endswith('_0')]
        if color:
            material.node_tree.nodes.active=color[0]
            records.append({'material':material.name,'image':color[0].image.name,'size':list(color[0].image.size),'packed':bool(color[0].image.packed_file)})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['skeleton','rig','canonical-guide','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--directions',nargs='+',default=['SW','NW','NE','SE'])
    parser.add_argument('--indices',type=int,nargs='+',default=[0])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Choose a fresh texture study')
    reference=json.loads((args.canonical_guide/'pilot-receipt.json').read_text())
    source=args.canonical_guide/'renderer-source.py'
    if sha(source)!=reference['implementation_sha256']or sha(args.skeleton)!=reference['source_skeleton_sha256']:
        raise ValueError('Frozen canonical source changed')
    if len(set(args.directions))!=len(args.directions)or set(args.directions)-set(reference['views']):raise ValueError('Unknown native cameras')
    if args.indices!=sorted(set(args.indices))or any(i<0 or i>=len(reference['views'][args.directions[0]]['frames'])for i in args.indices):raise ValueError('Invalid native pose selection')
    tree=ast.parse(source.read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
    inserted=[];records=[]
    class Inject(ast.NodeTransformer):
        def visit_Assign(self,node):
            if len(node.targets)==1:
                target=ast.unparse(node.targets[0])
                if target=='donor':
                    inserted.append('poses');return[node,ast.parse('_select_poses(donor)').body[0]]
                if target=='scene.render.image_settings.color_depth':
                    inserted.append('materials');return[node,ast.parse('_enable_textures(scene)').body[0]]
            return self.generic_visit(node)
    tree=ast.fix_missing_locations(Inject().visit(tree))
    if sorted(inserted)!=['materials','poses']:raise ValueError('Canonical material boundaries changed')
    def select(donor):donor['frames']=[row for row in donor['frames']if row['index']in args.indices]
    scope={'__name__':'native_texture_study','__file__':str(source),'_select_poses':select,'_enable_textures':lambda scene:enable_textures(scene,records)}
    exec(compile(tree,str(source),'exec'),scope)
    sys.argv=[sys.argv[0],'--','--skeleton',str(args.skeleton),'--rig',str(args.rig),'--output',str(args.output),'--directions',*args.directions,'--weapon',reference['weapon']]
    scope['main']()
    generated=json.loads((args.output/'pilot-receipt.json').read_text());checks=[]
    for direction in args.directions:
        before=reference['views'][direction];after=generated['views'][direction]
        if before['camera']!=after['camera']:raise ValueError('Native camera changed')
        for row in after['frames']:
            original=before['frames'][row['index']]
            if any(row[k]!=original[k]for k in ['landmarks','grip_world','staff_tip_world']):raise ValueError('Native geometry or prop data changed')
            checks.append({'direction':direction,'index':row['index'],'projected_pose_changed':False})
    report={'status':'EXISTING_PAINTED_TEXTURE_MATERIAL_STUDY_NOT_ADMITTED','canonical_receipt_sha256':sha(args.canonical_guide/'pilot-receipt.json'),'implementation_sha256':sha(__file__),'texture_bindings':records,'checks':checks,'geometry_changed':False,'camera_changed':False,'runtime_admitted':False}
    (args.output/'texture-study.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.output/'texture-renderer-source.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':main()
