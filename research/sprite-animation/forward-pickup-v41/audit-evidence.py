"""Verify bounded source success and painted failure without promoting either."""
import hashlib,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageSequence
P=Path(__file__).resolve().parent;ROOT=P.parents[2];checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,ok):
    checks.append(dict(name=name,pass_=bool(ok)))
    if not ok:raise AssertionError(name)
def module(name):
    s=importlib.util.spec_from_file_location(name,ROOT/'skills/modular-eight-direction-sprites/scripts'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
for folder in ['joint-tracking-ro-v30','pickup-pilot-v31','pickup-modular-v32','hair-swap-v33','pickup-view-v34','body-outfit-v35','neck-motion-v36','proportion-audit-v37','coherent-motion-v38','recovery-key-v39','rear-motion-v40']:
    manifest=json.loads((P.parent/folder/'evidence-manifest.json').read_text());check(folder+' exact frozen evidence unchanged',all(sha(ROOT/r['path'])==r['sha256'] for r in manifest['files']))
w=json.loads((P.parent/'joint-tracking-ro-v30/protected-W.json').read_text());check('13 exact protected W files',len(w['files'])==13 and all(sha(ROOT/r['path'])==r['expected_sha256'] for r in w['files']))
check('same sole research branch',subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/modular-sprites-full-body-2026-10-11')
refs=json.loads((P/'approved-gif-reference.json').read_text())['references'];valid=True
for r in refs:
    valid &= sha(ROOT/r['approved_gif_path'])==r['approved_gif_sha256']
    with Image.open(ROOT/r['approved_gif_path']) as im:
        fs=[f.convert('RGBA').copy() for f in ImageSequence.Iterator(im)]
        ds=[]
        for i in range(im.n_frames):im.seek(i);ds.append(im.info['duration'])
    valid &= len(fs)==8 and ds==[f['duration_ms'] for f in r['frames']] and sum(ds)==r['total_ms']
    for a,b in zip(fs,r['frames']):valid &= sha(ROOT/b['decoded_path'])==b['decoded_sha256'] and np.array_equal(np.array(a),np.array(Image.open(ROOT/b['decoded_path']).convert('RGBA')))
check('two exact approved GIFs and16 actual decoded exposures/clocks',valid)
ledger=json.loads((P/'generation-ledger.json').read_text());bindings=[b for j in ledger['jobs'] for b in [j['prompt'],j['output']]+j['inputs']]
check('8retained genuine still outputs with exact direct inputs',len(ledger['jobs'])==ledger['retained_completed_still_outputs']==8 and all(sha(ROOT/b['path'])==b['sha256'] for b in bindings))
check('no provider video MiniMax or old own attacks',not any(ledger[k] for k in ['generated_video','minimax_called','old_own_attack_used']))
repro=json.loads((P/'guide-reproduction.json').read_text());check('6exact authoring-guide reproductions',repro['exact'] and len(repro['files'])==6 and all(r['expected']==r['reproduced']==sha(P/r['file']) for r in repro['files']))
action=module('pickup-source-action');source=json.loads((P/'source/source.json').read_text());q=action.audit(source,P)
check('14actual source action/pixel/hash/projection checks reproduced',q==json.loads((P/'source-action-qa.json').read_text()) and q['source_action_pass'] and len(q['checks'])==14)
full=json.loads((P/'source-full-owner/source.json').read_text());check('full owner bank keeps exact168point records and2cameras',source['cameras']==full['cameras'] and all(a['points']==b['points'] for a,b in zip(source['frames'],full['frames'])))
check('full owner actual rendered capture hashes also pass',action.audit(full,P)['source_action_pass'])
replay=json.loads((P/'source-bone-replay.json').read_text());check('actual saved Blender bone replay bound',replay['pass_'] and replay['blend_sha256']==sha(P/'source/authoring-rig.blend') and len(replay['frames'])==8 and max(r['maximum_endpoint_error'] for r in replay['frames'])<1e-5)
g=json.loads((P/'goal-normalization.json').read_text());raw=Image.open(P/'goal-attempt1-raw.png').convert('RGBA');check('goal guide known-plate inverse independently reproduced',sha(P/'goal-attempt1-raw.png')==g['raw_sha256'] and np.array_equal(np.array(raw.transform((384,512),Image.Transform.AFFINE,tuple(g['inverse']),Image.Resampling.BICUBIC)),np.array(Image.open(P/'goal-attempt1.png'))))
play=json.loads((P/'source-gif-receipt.json').read_text());valid=True
for name,r in play.items():
    with Image.open(P/name) as im:
        ds=[]
        for i in range(im.n_frames):im.seek(i);ds.append(im.info['duration'])
    valid &= sha(P/name)==r['sha256'] and ds==r['decoded_durations_ms'] and len(ds)==8
check('4actual source-only GIFs keep approved exposure clocks',len(play)==4 and valid)
floor=module('visible-floor-surfaces');compare=module('approved-gif-compare');B=P/'attempt6-review';d=json.loads((B/'review-data.json').read_text());native=Image.open(P/'attempt6-raw.png').convert('RGBA');inverse=d['normalization']['inverse'];valid=True
for i,f in enumerate(d['candidate_frames']):
    crop=native.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));render=crop.transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC)
    valid &= sha(ROOT/f['path'])==f['sha256'] and np.array_equal(np.array(render),np.array(Image.open(ROOT/f['path'])))
check('all8native crops and one uniform bank transform reproduce exactly',valid and d['normalization']['display_matrix']==[.87,0,0,.87,24.96,50])
for attempt,expected in [(6,{'near':[12,1],'far':[23,3]}),(7,{'near':[17,5],'far':[32,8]})]:
    b=P/f'attempt{attempt}-review';r=json.loads((b/'floor-qa.json').read_text());windows={k:dict(roi=v['observations'][0]['window'],edge=v['observations'][0]['edge']) for k,v in r['raster']['tracks'].items()};actual=floor.run([Image.open(b/f'{i:02}.png') for i in range(8)],windows,6,1)
    check(f'native{attempt} actual raster feet still FAIL unchanged6px',actual==r['raster'] and not r['surface_checks_pass'] and {k:v['range_display_px'] for k,v in actual['tracks'].items()}==expected)
for clock in ['source','game']:
    c=json.loads((B/f'{clock}-comparison-contract.json').read_text())
    with tempfile.TemporaryDirectory() as td:r=compare.run(c,ROOT,td)
    check(clock+' approved GIF comparison independently reproduces numeric failure',json.loads(json.dumps(r))==json.loads((B/clock/'approved-gif-qa.json').read_text()) and not r['comparison_checks_pass'] and not r['checks']['support_near'] and not r['checks']['support_far'] and r['checks']['immutable_user_acceptance_binding'])
cmd=[sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/approved-gif-compare.py'),'--contract',str(B/'source-comparison-contract.json'),'--root',str(ROOT),'--out-dir','/tmp/astraeon-v41-strict','--require-checks'];s=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT)
(P/'strict-gate-receipt.json').write_text(json.dumps(dict(returncode=s.returncode,expected_returncode=1,stdout=s.stdout,stderr=s.stderr,reason='Current painted surface drift and unapproved action must not pass'),indent=2)+'\n');check('actual strict CLI refuses current painting exit1',s.returncode==1)
alpha=module('coherent-strip-alpha');a=json.loads((P/'native-alpha-qa.json').read_text());alpha_valid=True
for i in range(1,8):
    result=alpha.audit_sheet(P/f'attempt{i}-raw.png');alpha_valid &= Path(result['path'])==(ROOT/a[str(i)]['path']).resolve();result['path']=a[str(i)]['path'];alpha_valid &= result==a[str(i)]
check('7original native alpha results preserved/reproducible',alpha_valid and not a['7']['empty_patch_pass'])
t=json.loads((P/'test-receipt.json').read_text());check('28actual source/GIF/pixel negative checks',len(t['checks'])==28 and all(r['pass_'] for r in t['checks']))
b=json.loads((P/'browser-qa.json').read_text());check('31actual Canvas browser checks',len(b['checks'])==31 and all(r['pass'] for r in b['checks']) and not b['errors'])
size=module('character-size-audit');sq=json.loads((P/'size-locked-qa.json').read_text());sc=json.loads((P/'size-locked-contract.json').read_text());actual=size.run(sc,ROOT)
check('newsize399calibration does not approve clipped420pxheld-out return',actual==sq and actual['neutral_comparison'][0]['pass_'] and actual['neutral_comparison'][0]['observed_height_px']==399 and actual['neutral_comparison'][1]['observed_height_px']==420 and not actual['neutral_comparison'][1]['raw_complete_silhouette'] and not actual['character_size_pass'])
check('head/body proportions remain unknown despite whole-height match',not actual['checks']['head_body_family_review_bound'])
parts=module('part-proportion-audit');pq=parts.run(json.loads((P/'part-proportion-contract.json').read_text()),ROOT)
check('all18part-size requirements and actual visible measurements reproduce',pq==json.loads((P/'part-proportion-qa.json').read_text()) and len(pq['required_metrics'])==18 and not pq['part_proportion_pass'] and not actual['checks']['part_dimensions_and_ratios'])
check('same-view native boot grows21.56percent despiteheight calibration',any(r['frames']==['candidate0','candidate7'] and r['metric']=='boot_length' and r['status']=='FAIL' and 1.21<r['projected_ratio']<1.22 for r in pq['comparisons']))
pt=json.loads((P/'part-test-receipt.json').read_text());check('15part-size positive/negative/unknown controls',len(pt['checks'])==15 and all(r['pass_'] for r in pt['checks']))
oldsize=size.run(json.loads((P/'before-size-contract.json').read_text()),ROOT);check('before-size416pxnegative remains reproducible',oldsize==json.loads((P/'before-size-qa.json').read_text()) and oldsize['neutral_comparison'][0]['height_error_px']==17)
profile=json.loads((P/'character-size-profile.json').read_text());check('neutral-only scale derived from exact approved/native extents',profile['matrix']==[398/477,0,0,398/477,192-(398/477)*192,82-(398/477)*24] and profile['reference_visible_extent']['height']==399)
new=P/'size-locked-review';nd=json.loads((new/'review-data.json').read_text());valid=True
for i,f in enumerate(nd['candidate_frames']):
    crop=native.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));valid &= np.array_equal(np.array(crop.transform((384,512),Image.Transform.AFFINE,tuple(nd['normalization']['inverse']),Image.Resampling.BICUBIC)),np.array(Image.open(ROOT/f['path'])))
check('new size uses one same uniform transform for all8 unchanged nativecrops',valid and nd['normalization']['display_matrix']==profile['matrix'])
nq=json.loads((new/'floor-qa.json').read_text());nw=dict(near=dict(roi=[85,460,225,490],edge='min',material='foreground'),far=dict(roi=[236,440,308,488],edge='max',material='foreground'));nf=floor.run([Image.open(ROOT/f['path']) for f in nd['candidate_frames']],nw,6,1)
check('actual reviewed outline observer FAILS10and25px aftersize lock',nf==nq['raster'] and nf['tracks']['near']['range_display_px']==[10,1] and nf['tracks']['far']['range_display_px']==[25,3] and not nf['surface_checks_pass'])
st=json.loads((P/'size-test-receipt.json').read_text());check('13additional size/outline controls',len(st['checks'])==13 and all(r['pass_'] for r in st['checks']))
display=json.loads((P/'source-display-normalization.json').read_text());dm=display['matrix'];valid=True
for i,f in enumerate(display['frames']):
    im=Image.open(P/f'source/rear/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,(1/dm[0],0,-dm[4]/dm[0],0,1/dm[0],-dm[5]/dm[0]),Image.Resampling.BICUBIC);valid &= sha(ROOT/f['path'])==f['sha256'] and np.array_equal(np.array(im),np.array(Image.open(ROOT/f['path'])))
check('source panel has one separate disclosed neutral display transform',valid and size.extent(ROOT/display['frames'][0]['path'])['height']==399)
commands=[('current-painted-GIF',[sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/approved-gif-compare.py'),'--contract',str(new/'source-comparison-contract.json'),'--root',str(ROOT),'--out-dir','/tmp/astraeon-v41-current-strict','--require-checks']),('size',[sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/character-size-audit.py'),'--contract',str(P/'size-locked-contract.json'),'--root',str(ROOT),'--out','/tmp/astraeon-v41-current-size.json','--require-size'])]
commands.append(('part-proportions',[sys.executable,str(ROOT/'skills/modular-eight-direction-sprites/scripts/part-proportion-audit.py'),'--contract',str(P/'part-proportion-contract.json'),'--root',str(ROOT),'--out','/tmp/astraeon-v41-current-parts.json','--require-proportions']))
strict=[]
for name,cmd in commands:
    s=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT);strict.append(dict(name=name,returncode=s.returncode,stdout=s.stdout,stderr=s.stderr))
(P/'current-strict-gate-receipt.json').write_text(json.dumps(dict(commands=strict,all_refused_current_painting=all(r['returncode']==1 for r in strict)),indent=2)+'\n');check('current GIF size and part-size strict CLIs actually exit1',all(r['returncode']==1 for r in strict))
v=json.loads((P/'visual-review.json').read_text());check('explicit exact-image rejection never becomes art approval',not v['agent_motion_pass'] and all(sha(ROOT/b['path'])==b['sha256'] for b in v['inspected']))
decision=json.loads((P/'review-decision.json').read_text());check('source pass and painted/production failures remain separate',decision['source_action_pass'] and decision['approved_gif_reference_used'] and not any(decision[k] for k in ['painted_motion_pass','user_new_art_approved','complete_modular_bank','production_pass']))
bad=[]
for file in [P/'README.md',P/'KNOW-HOW.md',P/'RESEARCH.md',ROOT/'skills/modular-eight-direction-sprites/references/approved-gif-and-target-pickup.md']:
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        resolved=file.parent/target.split('#')[0]
        if '://' not in target and not target.startswith('#') and not resolved.exists() and resolved!=P/'audit-report.json':bad.append([str(file),target])
check('new durable documentation links resolve',not bad)
(P/'audit-report.json').write_text(json.dumps(dict(checks=checks,passed_checks=len(checks),decision=decision['decision'],agent_motion_pass=False,production_pass=False),indent=2)+'\n');print(json.dumps(dict(checks=len(checks),decision=decision['decision'])))
