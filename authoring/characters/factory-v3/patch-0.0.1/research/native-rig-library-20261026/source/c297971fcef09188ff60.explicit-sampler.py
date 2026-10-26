"""Render the retained native pose sampling through the unchanged capture code.

The version-pinned entrypoint replaces only the local sample list immediately
before pose evaluation. The canonical renderer file and other cached guide jobs
remain byte-identical. Every override and lossless PNG normalization is recorded.
"""
import ast
import hashlib
import json
import math
import sys
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def explicit_samples(job,static=False):
    values=job.get('explicit_source_samples');actions=job.get('source_actions',[])
    if not isinstance(values,list)or len(values)!=job['frames']or len(actions)!=1:raise ValueError('Explicit sampling requires one complete native action')
    if job.get('entry_transition')or job.get('exit_transition')or job.get('loop'):raise ValueError('Explicit retained sampling has no implicit transitions or loop substitution')
    if any(isinstance(f,bool)or not isinstance(f,(int,float))or not math.isfinite(f)or not 0<=f<=39 for f in values)or any(b<=a for a,b in zip(values,values[1:])):raise ValueError('Native sample frames must increase within the retained 0..39 range')
    if actions!=['Sword_Attack']:raise ValueError('Only the retained Sword_Attack sampling is implemented')
    return [{'action':actions[0],'source_frame':float(f),'segment_phase':float(f)/39}for f in (values[:1]if static else values)]


def instrument(source):
    tree=ast.parse(source);mains=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main']
    if len(mains)!=1:raise ValueError('Canonical capture entrypoint differs')
    main=mains[0];positions=[i for i,n in enumerate(main.body)if isinstance(n,ast.FunctionDef)and n.name=='evaluate']
    if len(positions)!=1:raise ValueError('Canonical pose evaluation boundary differs')
    override=ast.parse("samples = _explicit_pose_samples(job, args.static)").body[0]
    main.body.insert(positions[0],override)
    # The canonical file's CLI guard is replaced by the checked wrapper call.
    tree.body=[n for n in tree.body if not(isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='__name__')]
    return ast.fix_missing_locations(tree)


def run():
    args=sys.argv[sys.argv.index('--')+1:];job_path=Path(args[args.index('--job')+1]);output=Path(args[args.index('--output')+1])
    job=json.loads(job_path.read_text());explicit_samples(job)
    canonical=Path(__file__).with_name('render_patch001_guides.py');png_helper=Path(__file__).with_name('render_frozen_patch001_guides.py')
    if job.get('explicit_sampling_implementation_sha256')!=sha(__file__)or job.get('explicit_capture_png_sha256')!=sha(png_helper)or job.get('renderer_sha256')!=sha(canonical):raise ValueError('Planned capture implementation changed')
    scope={'__file__':str(canonical),'__name__':'explicit_patch001_capture','_explicit_pose_samples':explicit_samples}
    exec(compile(instrument(canonical.read_text()),str(canonical),'exec'),scope)
    scope['IMPLEMENTATION_DIGESTS'][Path(__file__).name]=sha(__file__)
    scope['IMPLEMENTATION_DIGESTS'][png_helper.name]=sha(png_helper)
    scope['main']()
    from render_frozen_patch001_guides import compact_capture
    manifest_path=output/'manifest.json';manifest=json.loads(manifest_path.read_text());rows=[]
    for direction,view in manifest['views'].items():
        expected=explicit_samples(job,'--static'in args)
        if [(f['action'],f['source_frame'])for f in view['frames']]!=[(f['action'],f['source_frame'])for f in expected]:raise ValueError('Captured source sampling differs')
        for i in range(len(expected)):
            path=output/direction/f'{i:03d}.png';row=compact_capture(path);row['image']=str(path.relative_to(output));rows.append(row)
    manifest['sampling_override']={'implementation_sha256':sha(__file__),'canonical_source_sha256':sha(canonical),'explicit_source_samples':job['explicit_source_samples'],'body_or_prop_geometry_overridden':False}
    manifest['png_normalization']={'implementation_sha256':sha(png_helper),'frames':rows}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':run()
