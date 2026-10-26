"""Export retained Swordsman sampling without replacing it by uniform frames."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import export_evaluated_guide_skeleton as base
import render_explicit_patch001_guides as explicit


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-guide',type=Path,required=True)
    parser.add_argument('--direction',default='NE')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    manifest=json.loads((args.source_guide/'manifest.json').read_text());job=manifest['job']
    helper=Path(explicit.__file__)
    if job.get('explicit_sampling_implementation_sha256')!=sha(helper):
        raise ValueError('Retained explicit sampling implementation changed')
    expected=explicit.explicit_samples(job)
    original=base.instrument
    class BoundSampler(ast.NodeTransformer):
        def visit_Name(self,node):
            if node.id=='_explicit_pose_samples':
                return ast.copy_location(ast.Attribute(value=ast.Call(func=ast.Name(id='__import__',ctx=ast.Load()),args=[ast.Constant('render_explicit_patch001_guides')],keywords=[]),attr='explicit_samples',ctx=ast.Load()),node)
            return node
    def instrument(source):
        tree=BoundSampler().visit(explicit.instrument(source))
        return original(ast.unparse(ast.fix_missing_locations(tree)))
    base.instrument=instrument
    base.main()
    data=json.loads(args.output.read_text())
    if [(f['action'],f['source_frame'])for f in data['frames']]!=[(f['action'],f['source_frame'])for f in expected]:
        raise ValueError('Exported explicit source sample list differs')
    data['explicit_sampling']={'wrapper_sha256':sha(__file__),'sampler_sha256':sha(helper),
                               'base_exporter_sha256':sha(Path(base.__file__)),
                               'source_frames':[f['source_frame']for f in expected],
                               'uniform_sampling_substituted':False}
    args.output.write_text(json.dumps(data,indent=2)+'\n')
    args.output.with_suffix('.explicit-wrapper.py').write_bytes(Path(__file__).read_bytes())
    args.output.with_suffix('.explicit-sampler.py').write_bytes(helper.read_bytes())
    print('EXPLICIT_NATIVE_SOURCE_EXPORT_PASS',len(expected),flush=True)


if __name__=='__main__':main()
