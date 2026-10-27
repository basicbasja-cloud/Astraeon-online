"""Render an isolated proportion profile on the original human motion guide."""
import ast,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def instrument(source):
    tree=ast.parse(source);found=0
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef)and node.name=='prop_pose':
            node.body.extend(ast.parse('from hero_fit_guide_study import apply_fit\napply_fit(rig,job)').body);found+=1
    if found!=1:raise ValueError('Expected one prop-pose boundary')
    tree.body=[n for n in tree.body if not(isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.left,ast.Name)and n.test.left.id=='__name__')]
    return ast.fix_missing_locations(tree)


def main():
    args=sys.argv[sys.argv.index('--')+1:];job=json.loads(Path(args[args.index('--job')+1]).read_text());out=Path(args[args.index('--output')+1]);helper=Path(__file__).with_name('hero_fit_guide_study.py');canonical=Path(__file__).with_name('render_patch001_guides.py')
    if job.get('hero_fit_study_renderer_sha256')!=sha(__file__)or job.get('hero_fit_study_helper_sha256')!=sha(helper):raise ValueError('Explicit pinned fit study required')
    if job.get('staff_grip_alignment_revision'):raise ValueError('Use the composed staff study for a staff job')
    import hero_fit_guide_study as fit
    from render_frozen_patch001_guides import run_capture
    scope={'__file__':str(canonical),'__name__':'isolated_original_hero_fit'};exec(compile(instrument(canonical.read_text()),str(canonical),'exec'),scope);run_capture(renderer_main=scope['main'])
    receipt={'status':'ISOLATED_GUIDE_PROPORTION_STUDY_NOT_ART_OR_MOTION_APPROVAL','profile':job['hero_fit_study'],'applications':fit.RECORDS,'renderer_sha256':sha(__file__),'helper_sha256':sha(helper),'source_glb_modified':False,'runtime_admitted':False}
    (out/'hero-fit-study-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'hero-fit-renderer-source.py').write_bytes(Path(__file__).read_bytes());(out/'hero-fit-helper-source.py').write_bytes(helper.read_bytes())


if __name__=='__main__':main()
