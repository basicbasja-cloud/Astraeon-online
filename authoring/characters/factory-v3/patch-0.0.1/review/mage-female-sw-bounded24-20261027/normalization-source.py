from pathlib import Path
from PIL import Image
from scipy import ndimage
import numpy as np,json,sys,hashlib,ast,shutil
sys.path.insert(0,'tools/character_factory_v3')
from normalize_fixed_viewport_batch import normalize_batch
from register_planted_foot_masters import observed_sole,rigid_translation
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'painted-candidates/mage-female-sw-bounded24-20261027';o=b/'review/mage-female-sw-bounded24-20261027';(o/'Repaint').mkdir(parents=True,exist_ok=True)
src=b/'review/mage-female-sw-masked-six-v2-20261027/assembly-source.py';tree=ast.parse(src.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)];exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(src),'exec'))
frames=[];inputs=[]
for batch in range(4):
 d=p/f'batch-{batch:02d}';recipe=json.loads((d/'recipe.json').read_text());raw=d/'arm-raw.png';fs,proof=normalize_batch(Image.open(raw),{'grid':[3,2],'source_size':[768,768],'viewport':recipe['viewport'],'source_pose_indices':recipe['indices']});frames+=fs;inputs.append({'batch':batch,'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'normalization':proof})
original0=Image.open(b/'review/mage-female-sw-canonical-pilot-20261027/Master/000.png').convert('RGBA');old_a=np.array(original0);new_a=np.array(frames[0]);old_h=hair_extent(original0);new_h=hair_extent(frames[0]);old_ground=np.where(old_a[:,:,3]>200)[0].max();new_ground=np.where(new_a[:,:,3]>200)[0].max();scale=float((old_ground-old_h[1])/(new_ground-new_h[1]));old_contacts=np.array([x['point']for x in observed_sole(original0)[1]]);new_contacts=np.array([x['point']for x in observed_sole(frames[0])[1]]);tx=float(old_contacts[:,0].mean()-scale*new_contacts[:,0].mean());ty=float(old_ground-scale*new_ground);records=[]
for i,repaint in enumerate(frames):
 repaint=repaint.convert('RGBa').transform((768,768),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC).convert('RGBA');original=Image.open(b/'review/mage-female-sw-canonical-pilot-20261027/Master'/f'{i:03d}.png').convert('RGBA');delta=np.rint(hair_core_center(original)-hair_core_center(repaint)).astype(int);repaint=rigid_translation(repaint,delta);repaint.save(o/'Repaint'/f'{i:03d}.png');cx,cy,cb=crystal(repaint);records.append({'index':i,'whole_repaint_integer_registration':delta.tolist(),'crystal_center':[cx,cy],'crystal_bbox':cb})
proof={'status':'REGISTERED_COMPLETE_REPAINTS_FOR_BOUNDED_CORRECTION_ONLY','shared_scale':scale,'shared_translation':[tx,ty],'fit_basis':'single first-frame crown/ground/sole mean, then whole-frame integer hair-core registration only','per_frame_scale_or_limb_warp':False,'registration_is_not_anatomical_acceptance':True,'frames':records,'inputs':inputs,'art_approved':False,'runtime_admitted':False};(o/'normalization.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copy2(__file__,o/'normalization-source.py');print('24 complete repaints, sharedscale',scale,'range registration',[min(r['whole_repaint_integer_registration'][1]for r in records),max(r['whole_repaint_integer_registration'][1]for r in records)])
