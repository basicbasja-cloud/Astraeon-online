"""Cut a corrected same-frame underpaint, then compose an independent staff."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,hashlib
b=Path('authoring/characters/factory-v3/patch-0.0.1');trial=b/'review/mage-separate-staff-frame000-pilot-20261028';under=b/'review/mage-staff-body-underlay-pilot-v2-20261028/Master000-underpaint.png';src=b/'review/mage-neck-fragment-clean-review-20261028/HeadHair000-clean.png';out=b/'review/mage-frame000-four-visible-parts-v3-20261028';out.mkdir(exist_ok=False);a=np.array(Image.open(under).convert('RGBA'));headseed=np.array(Image.open(src).convert('RGBA'))[:,:,3]>0;hand=np.array(Image.open(trial/'WeaponHandOccluder.png').convert('RGBA'))[:,:,3]>0;yy,xx=np.indices(headseed.shape);r,g,z=a[:,:,:3].astype(float).transpose((2,0,1));warm=(a[:,:,3]>0)&(r>g*1.3)&(g>z*1.1)&((r-g)>1.8*(g-z))&(xx>=335)&(xx<412)&(yy>=310)&(yy<373);grow=ndimage.binary_dilation(headseed,iterations=5)&warm;headmask=(headseed|grow)&(a[:,:,3]>0)&~hand;hands=hand&(a[:,:,3]>0);bodymask=(a[:,:,3]>0)&~headmask&~hands
roles={}
for name,mask in [('BodyCostume',bodymask),('HeadHair',headmask),('WeaponHandOccluder',hands)]:
 z=a.copy();z[~mask]=0;roles[name]=Image.fromarray(z)
roles['Weapon']=Image.open(trial/'Weapon.png').convert('RGBA');restore=Image.new('RGBA',(768,768))
for role in ['BodyCostume','HeadHair','WeaponHandOccluder']:restore.alpha_composite(roles[role])
visible=a[:,:,3]>0;assert np.array_equal(np.array(restore)[visible],a[visible]);assert np.array_equal(np.array(restore)[:,:,3],a[:,:,3]);complete=Image.new('RGBA',(768,768))
for name in ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']:roles[name].save(out/(name+'.png'));complete.alpha_composite(roles[name])
complete.save(out/'Master000.png');canvas=Image.new('RGBA',(1200,540),'#ddd')
for j,name in enumerate(['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']):
 bg=Image.new('RGBA',(300,500),'#ddd');bg.alpha_composite(roles[name].crop((288,288,576,576)).resize((300,300),Image.Resampling.LANCZOS),(0,45));ImageDraw.Draw(bg).text((4,4),name,fill='black');canvas.alpha_composite(bg,(j*300,0))
canvas.crop((0,0,1200,345)).convert('RGB').save(out/'parts-review.jpg',quality=98);(out/'receipt.json').write_text(json.dumps({'status':'ONE_FRAME_OWN_UNDERPAINT_AND_SEPARATE_WEAPON_STUDY_NOT_RUNTIME_ACCEPTED','underpaint_master_sha256':hashlib.sha256(under.read_bytes()).hexdigest(),'new_hair_edge_pixels':int((grow&~headseed).sum()),'underpaint_visible_rgba_recomposition_mismatches':0,'render_order':['BodyCostume','HeadHair','Weapon','WeaponHandOccluder'],'single_frame_only':True,'head_mask_and_grip_require_native_semantic_review':True,'source_guide_grip_alignment_requires_review':True,'costume_or_hair_swaps_not_tested':True,'runtime_admitted':False},indent=2)+'\n');(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'same_frame_underpaint_mismatches':0,'new_hair_edge_pixels':int((grow&~headseed).sum())}))
