"""Same-frame head cutout study; no master painting or runtime admission."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
import torch
from PIL import Image,ImageDraw
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
from scipy import ndimage
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def component(mask,minimum=1):
 labels,count=ndimage.label(mask,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0
 if count==0 or sizes.max()<minimum:raise ValueError('No sufficiently clear foreground component')
 return labels==sizes.argmax()

def author_mask(mask,index,recipe,fit,row):
 viewport=recipe['canonical_viewport768']if index in recipe['indices']else[224,224,576,576]
 image=Image.new('L',(768,768));image.paste(Image.fromarray(mask.astype('uint8')*255).resize((viewport[2]-viewport[0],viewport[3]-viewport[1]),Image.Resampling.NEAREST),tuple(viewport[:2]));scale=fit['shared_scale'];tx,ty=fit['shared_translation'];image=image.transform((768,768),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.NEAREST);registered=Image.new('L',(768,768));registered.paste(image,tuple(row['whole_frame_integer_translation']));return np.array(registered)>0

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();out=args.output
 if out.exists():raise ValueError('Use a fresh cutout output')
 base=Path('authoring/characters/factory-v3/patch-0.0.1');paint=base/'painted-candidates/mage-female-single-frame-trace-20261027';masters=base/'review/mage-female-single-frame-trace-20261027';recipe=json.loads((paint/'sequence-reference-recipe.json').read_text());fit=json.loads((masters/'receipt.json').read_text());family=json.loads((base/'research/target-facing-mage-gaze-20261027/head-pose-family-study.json').read_text());view=next(v for v in family['families']if v['direction']=='SW');checkpoint=Path('/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt')
 if len(fit['frames'])!=24 or any(not(paint/f'raw{i:03d}.png').exists()for i in range(24)):raise ValueError('All24 actual source-frame paintings and registrations required')
 torch.set_num_threads(3);predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False));out.mkdir(parents=True);records=[];errors=[];contact=Image.new('RGBA',(1440,960),'#ddd')
 for index in range(24):
  row=next(r for r in fit['frames']if r['index']==index);rawpath=paint/f'raw{index:03d}.png';raw=Image.open(rawpath).convert('RGBA');a=np.array(raw);r,g,b=a[:,:,:3].astype(float).transpose((2,0,1));yy,xx=np.indices(r.shape);unit=raw.width/1280;source_anchor=np.asarray(view['members'][index]['head_anchor_author768']);vp=recipe['canonical_viewport768']if index in recipe['indices']else[224,224,576,576];total_scale=(vp[2]-vp[0])/raw.width*fit['shared_scale'];translation=np.array(vp[:2])*fit['shared_scale']+np.array(fit['shared_translation'])+row['whole_frame_integer_translation'];expected=(source_anchor-translation)/total_scale
  record={'index':index,'raw_sha256':digest(rawpath),'master_sha256':digest(masters/'Master'/f'{index:03d}.png'),'semantic_approved':False,'expected_head_anchor_raw':expected.tolist()};records.append(record)
  try:
   crystal=(a[:,:,3]>128)&(g>r*1.2)&(b>r*1.2)&(g>70)&(b>80)&(yy<expected[1]-90*unit)&(abs(xx-expected[0])<300*unit)
   jewel=component(crystal,20*unit*unit);jy,jx=np.where(jewel);jcx=float(jx.mean());jcy=float(jy.mean())
   warm=(a[:,:,3]>128)&(abs(xx-expected[0])<260*unit)&(yy>expected[1]-300*unit)&(yy<expected[1]+80*unit)&(r>g*1.35)&(g>b*1.1)&((r-g)>1.8*(g-b));warm&=~((abs(xx-jcx)<10*unit)&(yy>jy.min()-20*unit));warm=ndimage.binary_opening(warm,structure=np.ones((3,3)));mainhair=component(warm,1000*unit*unit);hy,hx=np.where(mainhair);distance=ndimage.distance_transform_edt(~mainhair);near=warm&(distance<65*unit);hy,hx=np.where(near);bounds=[max(0,int(hx.min()-15*unit)),max(0,int(hy.min()-10*unit)),min(raw.width,int(hx.max()+21*unit)),min(raw.height,int(hy.max()+71*unit))];crop=[max(0,bounds[0]-30),max(0,bounds[1]-30),min(raw.width,bounds[2]+30),min(raw.height,bounds[3]+80)]
   if bounds[2]-bounds[0]>400*unit or bounds[3]-bounds[1]>430*unit:raise ValueError('Head proposal region includes ambiguous non-head material')
   core=ndimage.binary_erosion(mainhair,iterations=2);py,px=np.where(core);target=np.array([hx.mean(),hy.mean()]);q=np.argmin((px-target[0])**2+(py-target[1])**2);positive=[[int(px[q]),int(py[q])]];points=np.stack([px,py],axis=1)
   for _ in range(2):
    distances=np.min(((points[:,None,:]-np.array(positive)[None,:,:])**2).sum(axis=2),axis=1);positive.append(points[int(distances.argmax())].tolist())
   face_target=np.array([hx.min()+.72*(hx.max()-hx.min()),hy.min()+.92*(hy.max()-hy.min())]);skin=(a[:,:,3]>128)&(xx>bounds[0])&(xx<bounds[2])&(yy>hy.min()+.4*(hy.max()-hy.min()))&(yy<bounds[3])&(r>180)&(g>120)&(b>80)&(r>g*1.03)&(g>b*1.03)&((r-g)<85)&((g-b)<85);labels,count=ndimage.label(skin,structure=np.ones((3,3)));options=[]
   for label in range(1,count+1):
    sy,sx=np.where(labels==label)
    if len(sx)<30*unit*unit:continue
    centre=np.array([sx.mean(),sy.mean()]);score=min(len(sx),3000*unit*unit)/(1+float(((centre-face_target)**2).sum())/(40*unit)**2);options.append((score,label))
   if not options:raise ValueError('No unambiguous visible face proposal')
   _,label=max(options);d=ndimage.distance_transform_edt(labels==label);sy,sx=np.where(d>=max(1,float(d.max())*.75));q=np.argmin((sx-face_target[0])**2+(sy-face_target[1])**2);positive.append([int(sx[q]),int(sy[q])]);negative=[]
   proposed_negative=[[round(jcx),round(jcy)],[round(expected[0]),int(hy.max()+85*unit)],[int(hx.min()+25*unit),int(hy.max()+45*unit)]]
   wood=(a[:,:,3]>128)&(abs(xx-jcx)<10*unit)&(abs(yy-float(hy.mean()))<25*unit)&(r>g)&(g>b)&((r-g)<2.4*(g-b))&(r<150)&(g<120);wy,wx=np.where(wood)
   if len(wx):q=np.argmin((wx-jcx)**2+(wy-float(hy.mean()))**2);proposed_negative.append([int(wx[q]),int(wy[q])])
   for x,y in proposed_negative:
    if crop[0]<=x<crop[2]and crop[1]<=y<crop[3]and a[y,x,3]>128:negative.append([x,y])
   # Foreground prompts stay in the visible painted head; gold cloth is not a hair seed.
   centre=np.asarray(positive[0]);face_target=centre+np.array([20,80])*unit
   skin=(a[:,:,3]>128)&(abs(xx-face_target[0])<65*unit)&(yy>centre[1]+40*unit)&(yy<centre[1]+115*unit)&(r>180)&(g>120)&(b>75)&(r>g*1.03)&(g>b*1.03)&((r-g)<85)&((g-b)<85)
   labels,count=ndimage.label(skin,structure=np.ones((3,3)));options=[]
   for lab in range(1,count+1):
    sy,sx=np.where(labels==lab)
    if len(sx)<40*unit*unit:continue
    c=np.array([sx.mean(),sy.mean()]);options.append((float(((c-face_target)**2).sum())/max(1,min(len(sx),1000*unit*unit))**.25,lab))
   if not options:raise ValueError('No visible face inside head-only region')
   lab=min(options)[1];dist=ndimage.distance_transform_edt(labels==lab);sy,sx=np.where(dist>=max(1,float(dist.max())*.7));q=np.argmin((sx-face_target[0])**2+(sy-face_target[1])**2);face=[int(sx[q]),int(sy[q])];positive=[centre.astype(int).tolist(),face];negative=[]
   # Fixed head-only crop and actual collar points, with the staff kept separate.
   bounds=[int(centre[0]-170*unit),int(centre[1]-160*unit),int(centre[0]+115*unit),int(centre[1]+125*unit)];crop=[max(0,bounds[0]-25),max(0,bounds[1]-25),min(raw.width,bounds[2]+25),min(raw.height,bounds[3]+60)]
   for x,y in [[int(centre[0]),int(centre[1]+145*unit)],[int(centre[0]+85*unit),int(centre[1]+140*unit)],[round(jcx),round(jcy)]]:
    if crop[0]<=x<crop[2]and crop[1]<=y<crop[3]and a[y,x,3]>128:negative.append([x,y])
   if len(wx):
    q=np.argmin((wx-jcx)**2+(wy-float(centre[1]))**2);x,y=int(wx[q]),int(wy[q])
    if abs(x-face[0])>30*unit:negative.append([x,y])
   record.update({'box':bounds,'crop':crop,'positive':positive,'negative':negative})
   if index==0:
    selected=np.array(Image.open(base/'review/mage-female-target-gaze-head-asset-selected-20261027/selected-raw-mask.png'))>0;record['reused_same_input_reviewed_reference_mask']=True;choices=[]
   else:
    bg=Image.new('RGBA',raw.size,'#ddd');bg.alpha_composite(raw);predictor.set_image(np.array(bg.crop(crop).convert('RGB')));masks,scores,_=predictor.predict(point_coords=np.asarray(positive+negative)-np.asarray(crop[:2]),point_labels=np.array([1]*len(positive)+[0]*len(negative)),box=np.asarray(bounds)-np.asarray(crop[:2]*2),multimask_output=True);choices=[]
    for k,score in enumerate(scores):
     full=np.zeros(raw.size[::-1],bool);full[crop[1]:crop[3],crop[0]:crop[2]]=masks[k];full&=a[:,:,3]>128;area=int(full.sum());valid=5000*unit*unit<area<60000*unit*unit and all(full[y,x]for x,y in positive)and all(not full[y,x]for x,y in negative);choices.append((float(score)if valid else-1,k,full,area));folder=out/'Candidates';folder.mkdir(exist_ok=True);Image.fromarray(full.astype('uint8')*255).save(folder/f'{index:03d}-{k}.png')
    score,k,selected,area=max(choices,key=lambda item:item[0]);record['proposal_scores']=[{'index':q,'score':float(scores[q]),'valid':s>=0,'area':n}for s,q,full,n in choices]
    if score<0:raise ValueError('No head mask satisfies the actual foreground prompts')
    record['selected_proposal']=k
   record.update({'box':bounds,'crop':crop,'positive':positive,'negative':negative,'observed_jewel_center_raw':[jcx,jcy],'raw_head_bbox':Image.fromarray(selected.astype('uint8')*255).getbbox()});(out/'RawMasks').mkdir(exist_ok=True);Image.fromarray(selected.astype('uint8')*255).save(out/'RawMasks'/f'{index:03d}.png');canonical=author_mask(selected,index,recipe,fit,row);master=Image.open(masters/'Master'/f'{index:03d}.png').convert('RGBA');pixels=np.array(master);canonical&=pixels[:,:,3]>0;head=pixels.copy();head[~canonical]=0;rest=pixels.copy();rest[canonical]=0
   for role,array in [('HeadHair',head),('BodyRest',rest)]:
    (out/role).mkdir(exist_ok=True);Image.fromarray(array).save(out/role/f'{index:03d}.png')
   recomposed=Image.new('RGBA',master.size);recomposed.alpha_composite(Image.fromarray(rest));recomposed.alpha_composite(Image.fromarray(head));visible=pixels[:,:,3]>0
   if not np.array_equal(np.array(recomposed)[visible],pixels[visible])or not np.array_equal(np.array(recomposed)[:,:,3],pixels[:,:,3]):raise ValueError('Same-frame visible recomposition changed')
   record['visible_recomposition_mismatch_pixels']=0;record['master_pixels_modified']=False;rawhead=a.copy();rawhead[~selected]=0;bg=Image.new('RGBA',raw.size,'#ddd');bg.alpha_composite(Image.fromarray(rawhead));box=Image.fromarray(selected.astype('uint8')*255).getbbox();cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2;side=max(box[2]-box[0],box[3]-box[1])+35;tile=bg.crop((round(cx-side/2),round(cy-side/2),round(cx+side/2),round(cy+side/2))).resize((240,240),Image.Resampling.LANCZOS);contact.alpha_composite(tile,((index%6)*240,(index//6)*240));ImageDraw.Draw(contact).text(((index%6)*240+3,(index//6)*240+3),str(index),fill='black');print('HEAD_PROPOSED',index,flush=True)
  except ValueError as error:
   record['unresolved']=str(error);errors.append(index);ImageDraw.Draw(contact).rectangle(((index%6)*240,(index//6)*240,(index%6+1)*240-1,(index//6+1)*240-1),fill='#f99');ImageDraw.Draw(contact).text(((index%6)*240+3,(index//6)*240+3),f'{index}: unresolved',fill='black');print('HEAD_UNRESOLVED',index,str(error),flush=True)
 contact.convert('RGB').save(out/'head-contact.jpg',quality=98);(out/'receipt.json').write_text(json.dumps({'status':'SAME_FRAME_HEAD_CUTOUT_PROPOSALS_NOT_FULL_HEAD_REUSE_APPROVAL','checkpoint_sha256':digest(checkpoint),'input_fit_sha256':digest(masters/'receipt.json'),'pose_family_sha256':digest(base/'research/target-facing-mage-gaze-20261027/head-pose-family-study.json'),'frames':records,'unresolved_indices':errors,'full24_recomposition_completed':not errors,'BodyRest_contains_weapon':True,'neck_backfill_authored':False,'runtime_admitted':False},indent=2)+'\n');(out/'segmentation-source.py').write_bytes(Path(__file__).read_bytes())

if __name__=='__main__':main()
