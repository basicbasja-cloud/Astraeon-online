"""Compose a guide-only proportion experiment with the pinned staff adapter."""
import ast,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());out=Path(args[args.index('--output')+1])
    helper=Path(__file__).with_name('hero_fit_guide_study.py')
    if job.get('hero_fit_study_renderer_sha256')!=sha(__file__) or job.get('hero_fit_study_helper_sha256')!=sha(helper):raise ValueError('Explicit pinned study required')
    import render_staff_grip_study as staff
    import hero_fit_guide_study as fit
    original=staff.instrument
    def instrument(source):
        tree=original(source);found=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef)and node.name=='prop_pose':
                node.body.extend(ast.parse('from hero_fit_guide_study import apply_fit\napply_fit(rig,job)').body);found.append(node)
        if len(found)!=1:raise ValueError('Expected one prop-pose boundary')
        return ast.fix_missing_locations(tree)
    staff.instrument=instrument
    staff.main()
    receipt={'status':'ISOLATED_GUIDE_PROPORTION_STUDY_NOT_ART_OR_MOTION_APPROVAL','profile':job['hero_fit_study'],'applications':fit.RECORDS,'renderer_sha256':sha(__file__),'helper_sha256':sha(helper),'source_glb_modified':False,'runtime_admitted':False}
    (out/'hero-fit-study-proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'hero-fit-renderer-source.py').write_bytes(Path(__file__).read_bytes());(out/'hero-fit-helper-source.py').write_bytes(helper.read_bytes())


if __name__=='__main__':main()
