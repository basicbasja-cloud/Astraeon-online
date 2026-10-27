"""Fixed-camera guide-only cast gaze study, using pinned fit and staff hooks."""
import ast
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    args=sys.argv[sys.argv.index('--')+1:]
    job=json.loads(Path(args[args.index('--job')+1]).read_text())
    output=Path(args[args.index('--output')+1])
    helper=Path(__file__).with_name('target_gaze_guide_study.py')
    fit_helper=Path(__file__).with_name('hero_fit_guide_study.py')
    if job.get('target_gaze_study_renderer_sha256')!=sha(__file__)or job.get('target_gaze_study_helper_sha256')!=sha(helper)or job.get('hero_fit_study_helper_sha256')!=sha(fit_helper):
        raise ValueError('Explicit pinned gaze and anatomical fit study required')
    import render_staff_grip_study as staff
    import target_gaze_guide_study as gaze
    import hero_fit_guide_study as fit
    original=staff.instrument
    def instrument(source):
        tree=original(source);found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef)and node.name=='prop_pose':
                node.body.extend(ast.parse('from hero_fit_guide_study import apply_fit\napply_fit(rig,job)\nfrom target_gaze_guide_study import apply_target_gaze\napply_target_gaze(rig,job)').body)
                found.append(node)
        if len(found)!=1:raise ValueError('Expected one prop-pose boundary')
        return ast.fix_missing_locations(tree)
    staff.instrument=instrument
    staff.main()
    proof={'status':'AUTHORED_TARGET_FACING_CAST_GAZE_STUDY_NOT_UNCHANGED_MOCAP','profile':job['target_gaze_study'],'applications':gaze.RECORDS,'fit_applications':fit.RECORDS,'renderer_sha256':sha(__file__),'helper_sha256':sha(helper),'fit_helper_sha256':sha(fit_helper),'source_glb_modified':False,'production_profile_adopted':False,'sprite_head_reuse_approved':False,'runtime_admitted':False}
    (output/'target-gaze-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    for source,name in [(Path(__file__),'target-gaze-renderer-source.py'),(helper,'target-gaze-helper-source.py'),(fit_helper,'hero-fit-helper-source.py')]:
        (output/name).write_bytes(source.read_bytes())

if __name__=='__main__':main()
