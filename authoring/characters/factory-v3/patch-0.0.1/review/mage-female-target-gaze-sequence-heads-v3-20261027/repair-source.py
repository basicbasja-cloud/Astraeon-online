from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,sys,hashlib
sys.path.insert(0,'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/mage-female-single-frame-trace-20261027')
def author_mask(mask,index,recipe,fit,row):
 viewport=recipe['canonical_viewport768']if index in recipe['indices']else[224,224,576,576]
 image=Image.new('L',(768,768));image.paste(Image.fromarray(mask.astype('uint8')*255).resize((viewport[2]-viewport[0],viewport[3]-viewport[1]),Image.Resampling.NEAREST),tuple(viewport[:2]));scale=fit['shared_scale'];tx,ty=fit['shared_translation'];image=image.transform((768,768),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.NEAREST);registered=Image.new('L',(768,768));registered.paste(image,tuple(row['whole_frame_integer_translation']));return np.array(registered)>0

from scipy import ndimage
b=Path('authoring/characters/factory-v3/patch-0.0.1');src=b/'review/mage-female-target-gaze-sequence-heads-v2-20261027';out=b/'review/mage-female-target-gaze-sequence-heads-v3-20261027';out.mkdir(exist_ok=True);paint=b/'painted-candidates/mage-female-single-frame-trace-20261027';masters=b/'review/mage-female-single-frame-trace-20261027';receipt=json.loads((src/'receipt.json').read_text());fit=json.loads((masters/'receipt.json').read_text());recipe=json.loads((paint/'sequence-reference-recipe.json').read_text());contact=Image.new('RGBA',(1440,960),'#ddd')
for r in receipt['frames']:
 i=r['index'];raw=np.array(Image.open(paint/f'raw{i:03d}.png').convert('RGBA'));mask=np.array(Image.open(src/'RawMasks'/f'{i:03d}.png'))>0;old=mask.copy()
 if i!=0:
  yy,xx=np.indices(mask.shape);woodx=r['observed_jewel_center_raw'][0];corridor=abs(xx-woodx)<10*raw.shape[1]/1280
  fill=ndimage.binary_fill_holes(mask)&~mask;fill&=~corridor;mask|=fill&(raw[:,:,3]>128)
  labels,n=ndimage.label(mask,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());keep=sizes>=25;keep[0]=False;mask=keep[labels]
  # Recover source antialias pixels tightly adjacent to accepted visible head.
  edge=ndimage.binary_dilation(mask,iterations=1)&(raw[:,:,3]>0)&(raw[:,:,3]<128)&~corridor;mask|=edge
 (out/'RawMasks').mkdir(exist_ok=True);Image.fromarray(mask.astype('uint8')*255).save(out/'RawMasks'/f'{i:03d}.png');row=next(q for q in fit['frames']if q['index']==i);canonical=author_mask(mask,i,recipe,fit,row);master=np.array(Image.open(masters/'Master'/f'{i:03d}.png').convert('RGBA'));canonical&=master[:,:,3]>0;head=master.copy();head[~canonical]=0;rest=master.copy();rest[canonical]=0
 for name,a in [('HeadHair',head),('BodyRest',rest)]:
  (out/name).mkdir(exist_ok=True);Image.fromarray(a).save(out/name/f'{i:03d}.png')
 re=Image.new('RGBA',(768,768));re.alpha_composite(Image.fromarray(rest));re.alpha_composite(Image.fromarray(head));visible=master[:,:,3]>0;assert np.array_equal(np.array(re)[visible],master[visible]);assert np.array_equal(np.array(re)[:,:,3],master[:,:,3]);r['headband_internal_holes_restored_from_own_master_pixels']=int((mask&~old).sum());r['removed_small_disconnected_mask_pixels']=int((old&~mask).sum());r['semantic_approved']=False
 rawhead=raw.copy();rawhead[~mask]=0;im=Image.fromarray(rawhead);box=im.getbbox();cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2;side=max(box[2]-box[0],box[3]-box[1])+35;bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);tile=bg.crop((round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2))).resize((240,240),Image.Resampling.LANCZOS);contact.alpha_composite(tile,((i%6)*240,(i//6)*240));ImageDraw.Draw(contact).text(((i%6)*240+3,(i//6)*240+3),str(i),fill='black')
contact.convert('RGB').save(out/'head-contact.jpg',quality=98);receipt.update({'status':'24_SAME_FRAME_HEAD_PROPOSALS_WITH_SOURCE_HEADBAND_HOLES_RESTORED_NOT_RUNTIME_APPROVED','all24_masks_available':True,'raw_masters_modified':False,'runtime_admitted':False});(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'repair-source.py').write_bytes(Path(__file__).read_bytes())
