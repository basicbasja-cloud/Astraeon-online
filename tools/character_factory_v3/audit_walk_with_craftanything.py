import argparse,hashlib,json,subprocess,pathlib
from PIL import Image
parser=argparse.ArgumentParser(description='Craft Anything pixel audit; not animation approval')
parser.add_argument('--cli',type=pathlib.Path,required=True)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
cli=str(args.cli.resolve())
if hashlib.sha256(pathlib.Path(cli).read_bytes()).hexdigest()!='4db1afe78c0365f1192de776edf3a66a3e5c26fdc78f4b9d63128bf3d6d609eb':raise ValueError('Expected official v0.3.0 Linux x86_64 CLI')
root=pathlib.Path(__file__).resolve().parents[2]
out=args.output.resolve()
if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
out.mkdir(parents=True);frames=out/'frames';frames.mkdir()
a=Image.open(root/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104/generated-sheet.png').convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS)
b=Image.open(root/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk234-bounded-20261104/review-sheet.png').convert('RGB')
rows=[]
for i in range(16):
 box=(i%4*384,i//4*384,(i%4+1)*384,(i//4+1)*384)
 for tag,sheet in [('before',a),('after',b)]:sheet.crop(box).save(frames/f'{tag}{i:02}.png')
 params={'before':{'path':str(frames/f'before{i:02}.png')},'after':{'path':str(frames/f'after{i:02}.png')},'tolerance':0}
 f=out/'params.json';f.write_text(json.dumps(params))
 r=json.loads(subprocess.check_output([cli,'--deep','--project',str(out/'audit.cany'),'web-pixels-compare','@'+str(f)]))
 (out/f'frame{i:02}.json').write_text(json.dumps(r,indent=2)+'\n')
 assert r['result']['identical']==(i not in (2,3,4))
 rows.append({'frame':i,**r['result']})
(out/'summary.json').write_text(json.dumps({'status':'PIXEL_SCOPE_VERIFIED_NOT_ANIMATION_APPROVAL','cli_sha256':hashlib.sha256(pathlib.Path(cli).read_bytes()).hexdigest(),'frames':rows},indent=2)+'\n')
print(json.dumps([{'frame':r['frame'],'differing_pixels':r['differing_pixels'],'bbox':r['changed_bounding_box']} for r in rows],indent=2))
