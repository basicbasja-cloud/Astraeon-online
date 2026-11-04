"""Replay frozen native retargeting and export canonical bone matrices only.

This creates no image captures and never counts as completed sprite/guide art.
The same rig, camera and retarget implementation drive later 2D part transforms.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

import bpy


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['skeleton','rig','reference-guide','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--directions',nargs='+',default=['NE'])
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Choose a fresh numeric pose replay output')
    reference=json.loads((args.reference_guide/'pilot-receipt.json').read_text())
    implementation=args.reference_guide/'renderer-source.py'
    if sha(implementation)!=reference['implementation_sha256']or sha(args.rig)!=reference['rig_sha256']:
        raise ValueError('Pinned canonical implementation/rig changed')
    if set(args.directions)-set(reference['views'])or len(set(args.directions))!=len(args.directions):raise ValueError('Unknown source camera')
    tree=ast.parse(implementation.read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
    boundaries=[];captures={};scope={}
    class Numeric(ast.NodeTransformer):
        def visit_Call(self,node):
            function=ast.unparse(node.func)
            if function=='bpy.ops.render.render':
                boundaries.append('render')
                return ast.Call(func=ast.Name(id='_capture_numeric',ctx=ast.Load()),args=[ast.Name(id=k,ctx=ast.Load())for k in ['scene','rig','camera','frame']],keywords=[])
            if function=='sha'and len(node.args)==1 and isinstance(node.args[0],ast.Name)and node.args[0].id=='path':
                boundaries.append('image-hash');return ast.Constant(value=None)
            return self.generic_visit(node)
    tree=ast.fix_missing_locations(Numeric().visit(tree))
    if sorted(boundaries)!=['image-hash','render']:raise ValueError('Frozen numeric capture boundaries changed')
    def capture(scene,rig,camera,frame):
        direction=next(d for d in args.directions if str(scene.render.filepath).endswith('/'+d+f"/{frame['index']:03d}.png"))
        matrices={name:[list(row)for row in rig.matrix_world@rig.pose.bones[name].matrix]for name in scope['MAP']}
        captures.setdefault(direction,[]).append({'index':frame['index'],'source_action':frame['action'],'source_frame':frame['source_frame'],'world_matrices':matrices})
    scope.update({'__name__':'numeric_canonical_replay','__file__':str(implementation),'_capture_numeric':capture})
    exec(compile(tree,str(implementation),'exec'),scope)
    sys.argv=[sys.argv[0],'--','--skeleton',str(args.skeleton),'--rig',str(args.rig),'--output',str(args.output),'--directions',*args.directions,'--weapon',reference['weapon']]
    scope['main']()
    internal=args.output/'pilot-receipt.json';replayed=json.loads(internal.read_text());views={}
    for direction in args.directions:
        view=replayed['views'][direction]
        if view['camera']!=reference['views'][direction]['camera']:raise ValueError('Numeric camera differs from pinned reference')
        if len(view['frames'])!=len(captures[direction]):raise ValueError('Incomplete numeric pose capture')
        frames=[]
        for row,matrices in zip(view['frames'],captures[direction],strict=True):
            if row['index']!=matrices['index']or row['image_sha256']is not None:raise ValueError('Numeric replay unexpectedly claims image capture')
            frames.append({**row,**matrices})
        views[direction]={'camera':view['camera'],'frames':frames}
    report={'status':'NUMERIC_CANONICAL_POSES_NOT_IMAGE_CAPTURE','image_captures':0,
            'source_skeleton_sha256':sha(args.skeleton),'rig_sha256':sha(args.rig),
            'reference_guide_receipt_sha256':sha(args.reference_guide/'pilot-receipt.json'),
            'canonical_implementation_sha256':sha(implementation),'implementation_sha256':sha(__file__),
            'actor_scale':replayed['actor_scale'],'leg_scale':replayed['leg_scale'],'bone_map':replayed['bone_map'],
            'weapon':replayed['weapon'],
            'available_cameras':{d:v['camera']for d,v in reference['views'].items()},
            'views':views,'old_actions_used':False,'runtime_admitted':False}
    (args.output/'pose-controls.json').write_text(json.dumps(report,indent=2)+'\n')
    internal.unlink()
    (args.output/'numeric-renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print('NUMERIC_CANONICAL_POSES',sum(len(v['frames'])for v in views.values()),'IMAGES',0,flush=True)


if __name__=='__main__':main()
