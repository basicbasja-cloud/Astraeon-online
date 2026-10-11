"""Reproducible local factory: source receipt -> rig -> audit -> sprites -> pack.

No network, provider jobs, imported archive scripts, runtime admission or upload.
Native plus exporter digests make incomplete bake caches safe to resume.
"""
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['inspect','build','audit','bake','pack','variants','runtime','refresh','all']);parser.add_argument('--actions',default='all')
parser.add_argument('--recipe',type=Path,default=ROOT/'authoring/characters/swordsman-production/fantasy-base-01/factory/recipe.json')
parser.add_argument('--blender',type=Path,default=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'))
parser.add_argument('--partial',action='store_true');args=parser.parse_args()
recipe=json.loads(args.recipe.read_text(encoding='utf-8'));out=ROOT/recipe['output'];native=ROOT/recipe['productionNative'];cache=ROOT/recipe['cache'];cache.mkdir(parents=True,exist_ok=True)
if args.mode=='refresh':
    for mode in ['audit','bake','pack','variants','runtime']:
        subprocess.run([sys.executable,str(Path(__file__).resolve()),mode,'--recipe',str(args.recipe),'--blender',str(args.blender)],cwd=ROOT,check=True)
    for script in ['verify-fantasy-delivery.py','verify-fantasy-runtime.py']:
        subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,check=True)
    sys.exit(0)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(Path(recipe['sourceArchive']))==recipe['sourceArchiveSHA256'],'Source changed; inspect the new base before fitting.'
assert digest(ROOT/recipe['approvedConcept'])==recipe['approvedConceptSHA256'],'Approved design changed.'
with zipfile.ZipFile(recipe['sourceArchive']) as archive:
    for entry in archive.infolist():
        target=(cache/entry.filename).resolve()
        assert target.is_relative_to(cache.resolve()),'Unsafe archive entry'
        if entry.is_dir():target.mkdir(parents=True,exist_ok=True);continue
        original=archive.read(entry)
        if target.exists():assert hashlib.sha256(original).hexdigest()==digest(target),'Cached source changed'
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
def blender(job,options):
    path=ROOT/'.character-tools'/('fantasy-'+job+'.log')
    with path.open('w',encoding='utf-8') as handle:
        result=subprocess.run([str(args.blender),'--background','--python-exit-code','1',*options],cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{job} failed; inspect {path}')
    print('FACTORY_COMPLETE '+job,flush=True)
if args.mode in ['inspect','all']:
    blender('inspect',['--factory-startup','--python',str(ROOT/'tools/inspect-fantasy-base.py'),'--','--workspace',str(ROOT)])
if args.mode in ['build','all']:
    options=[str(ROOT/recipe['inspectionNative'])]
    for script in recipe['buildScripts']:options.extend(['--python',str(ROOT/'tools'/script)])
    blender('build',options)
if args.mode in ['audit','bake','pack','variants','runtime','all']:
    assert native.is_file(),'Build the source first.'
if args.mode in ['audit','all']:
    blender('audit',[str(native),'--python',str(ROOT/'tools'/recipe['auditScript'])])
    audit=json.loads((out/'factory/source-audit.json').read_text())
    assert audit['technicalVerdict']=='PASS',audit['issues']
if args.mode in ['bake','all']:
    audit=json.loads((out/'factory/source-audit.json').read_text())
    assert audit['nativeSHA256']==digest(native) and audit['technicalVerdict']=='PASS','Audit this native before baking.'
    matrix=json.loads((ROOT/'docs/character-factory/new-production-matrix.json').read_text())
    actions=[c['action'] for c in matrix['actions'] if c['swordsmanContract']!='excluded'] if args.actions=='all' else args.actions.split(',')
    for action in actions:
        print('FACTORY_START '+action,flush=True)
        blender('bake-'+action,[str(native),'--python',str(ROOT/'tools'/recipe['bakeScript']),'--','--action',action])
if args.mode in ['pack','all']:
    subprocess.run([sys.executable,str(ROOT/'tools'/recipe['packScript']),'--native',str(native),'--output',str(out),*(['--partial'] if args.partial else [])],cwd=ROOT,check=True)
if args.mode in ['variants','all']:
    bank=ROOT/'.character-tools/checkpoints/fantasy-swap-bank.blend';receipt_path=out/'factory/swap-bank.json'
    receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if not(bank.exists() and receipt.get('baseNativeSHA256')==digest(native) and receipt.get('builderSHA256')==digest(ROOT/'tools/build-fantasy-swap-bank.py') and receipt.get('bankSHA256')==digest(bank)):
        blender('swap-build',[str(native),'--python',str(ROOT/'tools/build-fantasy-swap-bank.py')])
    clips=json.loads((out/'clips.json').read_text())['clips']
    for clip in clips:
        if args.actions!='all' and clip['name'] not in args.actions.split(','):continue
        print('FACTORY_SWAP_START '+clip['name'],flush=True)
        blender('swap-'+clip['name'],[str(bank),'--python',str(ROOT/'tools/bake-fantasy-swap-bank.py'),'--','--action',clip['name']])
if args.mode in ['runtime','all']:
    subprocess.run([sys.executable,str(ROOT/'tools/compile-fantasy-runtime.py')],cwd=ROOT,check=True)
