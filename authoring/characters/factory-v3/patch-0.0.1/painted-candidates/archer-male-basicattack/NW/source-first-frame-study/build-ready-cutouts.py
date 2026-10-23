from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import binary_dilation,label
p=Path('authoring/characters/factory-v3/patch-0.0.1/painted-candidates/archer-male-basicattack/NW/source-first-frame-study');out=p/'ready-cutout-study';out.mkdir(exist_ok=True)
a=np.array(Image.open(p/'sequence/detail/000.png').convert('RGBA'));h,w=a.shape[:2];yy,xx=np.indices((h,w));base=np.array(Image.open(p/'weapon-seed-proposals/Weapon-1.png'))[:,:,3]>0
# Manual review coordinates are in the shared 768px detail viewport.
mask=binary_dilation(base,iterations=3)&((yy<291)|(yy>355))
mask|=base
reg=Image.new('L',(w,h));d=ImageDraw.Draw(reg)
# Bowstring and nocked arrow, excluding visible hands and sleeves below.
d.line([(473,132),(418,342),(397,434)],fill=255,width=5)
mask|=np.array(reg)>0
protect=Image.new('L',(w,h));d=ImageDraw.Draw(protect)
# Far gripping glove stays with the character; near draw glove covers the string.
d.polygon([(425,305),(437,301),(449,299),(459,304),(460,309),(468,311),(470,316),(466,324),(461,331),(451,337),(443,335),(439,328),(426,327)],fill=255)
d.polygon([(398,339),(410,334),(420,334),(428,338),(434,343),(436,350),(432,357),(425,361),(414,364),(399,357)],fill=255)
mask&=np.array(protect)==0
# Bow-only ownership remains separate from the nocked arrow.
bow_mask=mask.copy()
# The pale shaft visibly passes in front of the far glove.
shaft=Image.new('L',(w,h));sd=ImageDraw.Draw(shaft);sd.line([(477,292),(423,339)],fill=255,width=3)
# Pale feather pixels in this bounded region; exclude the brown draw glove.
r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);feather=(xx>=419)&(xx<=442)&(yy>=326)&(yy<=346)&(r>150)&(g>125)&(b>95)&(r-g<45)&(g-b<55)
arrow_mask=(np.array(shaft)>0)|binary_dilation(feather,iterations=1);mask|=arrow_mask
# Detached fragments in the reviewed bow region belong to the weapon.
remaining=(a[:,:,3]>8)&~mask;labs,n=label(remaining);sizes=np.bincount(labs.ravel());sizes[0]=0;largest=sizes.argmax();isolated=(labs!=largest)&(labs>0)&(xx>390)&(xx<492)&(yy>120)&(yy<450);mask|=binary_dilation(isolated,iterations=1)&(a[:,:,3]>0)&(np.array(protect)==0)
mask&=a[:,:,3]>0
Image.fromarray((mask*255).astype('uint8')).save(out/'weapon-ownership.png')
donor_image=Image.open(p/'weaponless-donor/detail.png').convert('RGBA')
grip_donor=p/'weaponless-grip-donor/second-pass.png'
if grip_donor.exists():
 crop=json.loads((grip_donor.parent/'crop.json').read_text())['shared_detail_box'];x0,y0,x1,y1=crop;donor_image.paste(Image.open(grip_donor).convert('RGBa').resize((x1-x0,y1-y0),Image.Resampling.LANCZOS).convert('RGBA'),(x0,y0))
donor_image.save(out/'bounded-hidden-donor.png');donor=np.array(donor_image);rows=[]
for i in [0,15]:
 master_path=p/'sequence/detail'/f'{i:03d}.png';src=np.array(Image.open(master_path).convert('RGBA'));hm=np.array(Image.open(p/'manual-head-seeds/HeadHair/000.png'))[:,:,3]>0
 wm=(mask if i==0 else bow_mask)&(src[:,:,3]>0)
 # Frame15 has no arrow; never assign its reconstructed glove pixels to Weapon.
 rem=(src[:,:,3]>8)&~wm;labs,n=label(rem);sizes=np.bincount(labs.ravel());sizes[0]=0;largest=sizes.argmax();isolated=(labs!=largest)&(labs>0)&(xx>390)&(xx<492)&(yy>120)&(yy<450);wm|=binary_dilation(isolated,iterations=1)&(src[:,:,3]>0)&(np.array(protect)==0)
 weapon=src.copy();weapon[~wm]=0
 head=src.copy();head[~hm]=0
 body=src.copy();body[wm|hm]=0
 # Preserve donor only under fully opaque weapon pixels. Translucent edge pixels
 # retain exclusive ownership so the assembled master remains byte-identical.
 hidden=wm&(src[:,:,3]==255)&(donor[:,:,3]>0)
 body[hidden]=donor[hidden]
 for role,arr in [('HeadHair',head),('BodyCostume',body),('Weapon',weapon)]:
  folder=out/role;folder.mkdir(exist_ok=True);Image.fromarray(arr).save(folder/f'{i:03d}.png')
 comp=Image.alpha_composite(Image.alpha_composite(Image.fromarray(body),Image.fromarray(weapon)),Image.fromarray(head));comp.save(out/f'composed-{i:03d}.png');actual=np.array(comp);visible=src[:,:,3]>0
 changed=int(np.any(actual!=src,2)[visible].sum());assert changed==0,changed
 rows.append({'index':i,'master_sha256':hashlib.sha256(master_path.read_bytes()).hexdigest(),'weapon_visible_pixels':int(wm.sum()),'hidden_body_pixels':int(hidden.sum()),'visible_recomposition_changed_pixels':changed,'body_pixels_outside_weapon_and_head_changed':0})
review=Image.new('RGBA',(1440,768),'#e8e8e8');d=ImageDraw.Draw(review)
for j,(role,label)in enumerate([('HeadHair','Head + hair'),('BodyCostume','Body: hidden surfaces retained'),('Weapon','Bow + arrow'),(None,'Same-frame assembly')]):
 im=Image.open(out/role/'000.png')if role else Image.open(out/'composed-000.png');review.alpha_composite(im.crop((270,110,510,700)).resize((300,738)),(j*360,30));d.text((j*360+8,8),label,fill='black')
review.save(out/'review.png')
(out/'receipt.json').write_text(json.dumps({'status':'SAME_FRAME_READY_CUTOUT_STUDY_REQUIRES_EDGE_REVIEW','frames':rows,'same_frame_pixel_partition':True,'body_donor_limited_to_opaque_weapon_coverage':True,'original_hand_pixels_preserved':True,'new_playable_packages':0,'owner_approved':False,'runtime_admitted':False},indent=2)+'\n')
print(json.dumps(rows))
