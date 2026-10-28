from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,hashlib,json
b=Path('authoring/characters/factory-v3/patch-0.0.1');o=b/'review/mage-frame001-separate-parts-study-20261028';o.mkdir(exist_ok=True)
src=b/'review/mage-staff-underlay-frame001-study-20261028/underpaint.png';source=Image.open(src).convert('RGBA');a=np.asarray(source);h=np.asarray(Image.open(b/'review/mage-underpaint001-head-sam-study-20261028/mask-2.png'))>0
h=ndimage.binary_fill_holes(h)&(a[:,:,3]>0);labels,n=ndimage.label(h,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0;h=labels==sizes.argmax();yy,xx=np.indices(h.shape);h=(h|(ndimage.binary_dilation(h,iterations=1)&(yy<373)&(a[:,:,3]>0)))
seed=np.asarray(Image.open(b/'review/mage-female-head-fringe-ownership-v7-20261027/HeadHair/001.png').convert('RGBA'))[:,:,3]>0
h |= seed & (yy<370) & (a[:,:,3]>0)
handmask=Image.new('L',(768,768));ImageDraw.Draw(handmask).polygon([(381,406),(401,406),(409,410),(409,420),(404,424),(384,423),(380,417)],fill=255);hand=np.asarray(handmask)>0;hand&=a[:,:,3]>0;h&=~hand;body=(a[:,:,3]>0)&~h&~hand
layers={}
for name,m in [('BodyCostume',body),('HeadHair',h),('WeaponHandOccluder',hand)]:
 z=a.copy();z[~m]=0;layers[name]=Image.fromarray(z)
asset=b/'painted-candidates/mage-staff-independent-pilot-20261028/staff-cutout.png';img=Image.open(asset).convert('RGBA');scale=207/(1479-8);sz=(round(img.width*scale),round(img.height*scale));weapon=Image.new('RGBA',(768,768));weapon.alpha_composite(img.convert('RGBa').resize(sz,Image.Resampling.LANCZOS).convert('RGBA'),(round(398-58*scale),round(323-8*scale)));layers['Weapon']=weapon
rest=Image.new('RGBA',source.size)
for name in ['BodyCostume','HeadHair','WeaponHandOccluder']:rest.alpha_composite(layers[name])
r=np.asarray(rest);visible=(a[:,:,3]>0)|(r[:,:,3]>0);assert np.array_equal(a[visible],r[visible]) and np.array_equal(a[:,:,3],r[:,:,3])
combined=Image.new('RGBA',source.size)
for name in ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']:layers[name].save(o/(name+'.png'));combined.alpha_composite(layers[name])
combined.save(o/'assembled.png');page=Image.new('RGBA',(1500,380),'#ddd')
for j,(name,im) in enumerate([('underpaint',source),*[(k,layers[k]) for k in ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']],('assembled',combined)]):
 tile=Image.new('RGBA',(250,300),'#ddd');tile.alpha_composite(im.crop((288,288,576,576)).resize((250,250),Image.Resampling.LANCZOS));ImageDraw.Draw(tile).text((4,255),name,fill='black');page.alpha_composite(tile,(j*250,0))
page.crop((0,0,1500,280)).convert('RGB').save(o/'parts-review.jpg',quality=98)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(o/'receipt.json').write_text(json.dumps({'status':'DRAFT_ONE_FRAME_SEMANTIC_AND_GRIP_REVIEW_REQUIRED','frame':1,'source_sha256':sha(src),'head_proposal_sha256':sha(b/'review/mage-underpaint001-head-sam-study-20261028/mask-2.png'),'source_head_seed_sha256':sha(b/'review/mage-female-head-fringe-ownership-v7-20261027/HeadHair/001.png'),'independent_staff_sha256':sha(asset),'estimated_staff_tip':[398,323],'estimated_staff_bottom':[398,530],'guide_hand_r_middle_01':[398.3,414.2],'base_recomposition_visible_rgba_mismatch':0,'weapon_grip_and_occlusion_reviewed':False,'runtime_admitted':False},indent=2)+'\n')
# Two still frames are shown only to review the registration, not as an animation approval.
frames=[]
for i,path in enumerate([b/'review/mage-frame000-four-visible-parts-v5-20261028/Master000.png',o/'assembled.png']):
 im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',(576,576),'#ddd');bg.alpha_composite(im.crop((288,288,576,576)).resize((576,576),Image.Resampling.LANCZOS));ImageDraw.Draw(bg).text((5,5),f'frame {i:03} - study',fill='black');frames.append(bg.convert('RGB'))
frames[0].save(o/'two-frame-study.gif',save_all=True,append_images=frames[1:],duration=[300,300],loop=0,disposal=2,optimize=False)
alt_path=b/'painted-candidates/mage-staff-alternate-pilot-20261028/staff-cutout.png';alt=Image.open(alt_path).convert('RGBA');scale_alt=207/(2135-8);size=(round(alt.width*scale_alt),round(alt.height*scale_alt));alt_weapon=Image.new('RGBA',(768,768));alt_weapon.alpha_composite(alt.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA'),(round(398-132*scale_alt),round(323-8*scale_alt)));alt_weapon.save(o/'Weapon-alternate.png');alternate=Image.new('RGBA',(768,768))
for layer in [layers['BodyCostume'],layers['HeadHair'],alt_weapon,layers['WeaponHandOccluder']]:alternate.alpha_composite(layer)
alternate.save(o/'assembled-alternate.png');change=np.any(np.asarray(combined)!=np.asarray(alternate),axis=2);allowed=(np.asarray(weapon)[:,:,3]>0)|(np.asarray(alt_weapon)[:,:,3]>0);assert not np.any(change&~allowed)
comparison=Image.new('RGBA',(768,384),'#ddd')
for j,im in enumerate([combined,alternate]):comparison.alpha_composite(im.crop((288,288,576,576)).resize((384,384),Image.Resampling.LANCZOS),(j*384,0))
comparison.convert('RGB').save(o/'weapon-swap-comparison.jpg',quality=98)
proof={'status':'ONE_FRAME_WEAPON_SWAP_DIAGNOSTIC','alternate_staff_sha256':sha(alt_path),'changed_pixels_outside_weapon_union':int(np.sum(change&~allowed)),'body_head_hand_files_unchanged':True,'hidden_surfaces_and_occlusion_approved':False,'runtime_admitted':False};(o/'weapon-swap-receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
