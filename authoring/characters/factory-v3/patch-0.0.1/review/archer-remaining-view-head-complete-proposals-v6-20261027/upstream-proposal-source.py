from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys
sys.path.append('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages')
from scipy import ndimage
import torch
sys.path.insert(0,'/workspace/.tools/SAM2')
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
torch.set_num_threads(3)
b=Path('authoring/characters/factory-v3/patch-0.0.1');o=b/'review/archer-remaining-view-head-complete-proposals-v4-20261027';o.mkdir(exist_ok=True);exceptions=json.loads((o/'native-exceptions.json').read_text())['frames'];guide=json.loads((b/'guides/2fed9f286cdd5c5ffbf4/manifest.json').read_text());cp=Path('/workspace/.tools/SAM2/sam2.1_hiera_tiny.pt');predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(cp),device='cpu',apply_postprocessing=False));records=[];contact=Image.new('RGBA',(1800,900),'#ddd')
for vindex,view in enumerate(['SW','NE','SE']):
 for sindex,sex in enumerate(['male','female']):
  for pindex,i in enumerate(range(16)):
   p=b/'review/archer-coherent-recovery-masters-v2-20261026'/sex/view/'Master'/f'{i:03d}.png'
   key=f'{sex}/{view}/{i:03d}'
   if key not in exceptions:
    import shutil
    previous=b/'review/archer-remaining-view-head-complete-proposals-v3-20261027';prior=json.loads((previous/'proposal-receipt.json').read_text());record=next(dict(r)for r in prior['frames']if(r['sex'],r['view'],r['index'])==(sex,view,i))
    if hashlib.sha256(p.read_bytes()).hexdigest()!=record['master_sha256']:raise ValueError('Reviewed mask master changed')
    dest=o/sex/view;dest.mkdir(parents=True,exist_ok=True);(dest/'BodyRest').mkdir(exist_ok=True);shutil.copy2(previous/sex/view/f'{i:03d}.png',dest/f'{i:03d}.png');shutil.copy2(previous/sex/view/'BodyRest'/f'{i:03d}.png',dest/'BodyRest'/f'{i:03d}.png');record['reused_identical_master_proposal']=True;record['previously_reviewed_key']=i in [0,8,15];records.append(record);continue
   im=Image.open(p).convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype(float);r,g,z=rgb.transpose((2,0,1));yy,xx=np.indices(a.shape[:2]);lm=guide['views'][view]['frames'][i]['landmarks'];hx,hy=(np.array(lm['head'])-np.array([360,440]))*.3925+np.array([99,80]);scope=(abs(xx-hx)<60)&(yy>hy-90)&(yy<hy+3)&(a[:,:,3]>64);warm=scope&(r>g*1.25)&(g>z*1.05)&(r>40);warm=ndimage.binary_opening(warm,structure=np.ones((3,3)));labels,n=ndimage.label(warm,structure=np.ones((3,3)));areas=np.bincount(labels.ravel());objects=ndimage.find_objects(labels);options=[k for k in range(1,n+1)if areas[k]>80];
   if not options:raise ValueError(f'Missing warm hair {sex} {view} {i}')
   k=max(options,key=lambda k:areas[k]);cy,cx=np.where(labels==k);bounds=[int(cx.min())-6,int(cy.min())-6,int(cx.max())+7,int(cy.max())+13];crop=[max(0,bounds[0]-20),max(0,bounds[1]-20),min(512,bounds[2]+20),min(512,bounds[3]+20)];core=ndimage.binary_erosion(labels==k,iterations=1)&(abs(xx-hx)<24)&(yy>hy-65)&(yy<hy-22);py,px=np.where(core);target=np.array([cx.mean(),cy.mean()]);index=np.argmin((px-target[0])**2+(py-target[1])**2);pos=[[int(px[index]),int(py[index])]]
   # Trusted upper hair seeds avoid brown neck/cloth becoming positive prompts.
   core&=yy<=int(cy.min()+.7*(cy.max()-cy.min()));py,px=np.where(core)
   candidates=np.stack([px,py],axis=1)
   for _ in range(2):
    distance=np.min(((candidates[:,None,:]-np.array(pos)[None,:,:])**2).sum(axis=2),axis=1);pos.append(candidates[int(distance.argmax())].tolist())
   neg=[]
   olive=scope&(yy>hy-8)&(yy<hy+3)&(g>r*1.02)&(g>z*1.3)&(g>25)
   oy,ox=np.where(olive)
   if len(ox):
    q=np.argmin((ox-hx)**2+(oy-hy)**2);neg.append([int(ox[q]),int(oy[q])])
   neg.append([int(round(hx)),int(round(hy+15))])
   if view in ['SW','SE']:
    # Face proposals follow actual painted hair, not a displaced guide neck point.
    skin=scope&(abs(xx-pos[0][0])<22)&(yy>pos[0][1]+4)&(yy<pos[0][1]+34)&(r>190)&(g>130)&(z>90)&(r>g*1.05)&(g>z*1.05)&((g-z)<65)&((r-g)<65)
    skin_labels,skin_count=ndimage.label(skin,structure=np.ones((3,3)));face_target=np.array(pos[0])+np.array([5 if view=='SW'else-5,18]);face_options=[]
    for label in range(1,skin_count+1):
     sy,sx=np.where(skin_labels==label)
     if len(sx)<6:continue
     centre=np.array([sx.mean(),sy.mean()]);value=min(len(sx),80)/(1+float(((centre-face_target)**2).sum())/36);face_options.append((value,label))
    if face_options:
     _,selected_skin=max(face_options);component=skin_labels==selected_skin;distance=ndimage.distance_transform_edt(component);sy,sx=np.where(distance>=max(1,float(distance.max())*.75));q=np.argmin((sx-face_target[0])**2+(sy-face_target[1])**2);pos.append([int(sx[q]),int(sy[q])])
   manual={('male','SW'):[[207,170],[224,177]],('female','SW'):[[195,155],[209,164]],('male','NE'):[[315,180],[330,187]],('female','NE'):[[334,186],[300,193]],('male','SE'):[[288,172],[303,169]],('female','SE'):[[317,183],[307,195],[298,190]]}
   reference={("male","SW"):[227,163],("female","SW"):[225,152],("male","NE"):[294,173],("female","NE"):[304,165],("male","SE"):[277,137],("female","SE"):[273,153]}
   shift=np.array(pos[0])-reference[sex,view]
   if i in [6,7,8,9]:neg+=[(np.array(q)+shift).tolist()for q in manual[sex,view]]
   if sex=='female'and view=='SW'and i in [6,7,8,9]:
    exclude=Image.new('L',(512,512));ImageDraw.Draw(exclude).polygon([tuple(np.array(q)+shift)for q in [(180,145),(208,150),(222,160),(217,172),(181,165)]],fill=255);core&=~(np.array(exclude)>0)
   spec=exceptions[key];pos=pos[:3]+([spec['face']]if spec['face']else[]);neg=spec['negative']
   bg=Image.new('RGBA',im.size,'#ddd');bg.alpha_composite(im);predictor.set_image(np.array(bg.crop(crop).convert('RGB')));pts=np.array(pos+neg,np.float32)-np.array(crop[:2]);masks,scores,_=predictor.predict(point_coords=pts,point_labels=np.array([1]*len(pos)+[0]*len(neg)),box=np.array(bounds)-np.array(crop[:2]*2),multimask_output=True);choice=[]
   for t,score in enumerate(scores):
    full=np.zeros((512,512),bool);full[crop[1]:crop[3],crop[0]:crop[2]]=masks[t];full=ndimage.binary_fill_holes(full)&(a[:,:,3]>0);(o/'Candidates').mkdir(exist_ok=True);Image.fromarray(full.astype('uint8')*255).save(o/'Candidates'/f'{sex}-{view}-{i:03d}-{t}.png');coverage=float((full&core).sum()/core.sum());area=int(full.sum());valid=coverage>.92 and 450<area<4000 and all(not full[q[1],q[0]]for q in neg) and all(full[q[1],q[0]]for q in pos);choice.append((float(score)if valid else-1,t,full,coverage,area))
   score,selected,head,cov,area=max(choice,key=lambda x:x[0]);record={'sex':sex,'view':view,'index':i,'master_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'box':bounds,'crop':crop,'positive':pos,'negative':neg,'scores':scores.tolist(),'selected':selected,'selected_score':score,'warm_hair_coverage':cov,'head_area':area,'semantic_approved':False,'coverage_scope':'trusted upper-hair seed only, not whole hair or semantic approval','face_point_basis':'painted-hair-relative skin component proposal'};records.append(record)
   if score<0:
    record['choices']=[{'score':float(scores[t]),'coverage':c,'area':ar,'included_positive':[bool(full[q[1],q[0]])for q in pos],'included_negative':[bool(full[q[1],q[0]])for q in neg]}for ss,t,full,c,ar in choice];(o/'failed-prompt.json').write_text(json.dumps(record,indent=2)+'\n');print(f'UNRESOLVED_HEAD {sex} {view} {i}',flush=True);continue
   head=ndimage.binary_fill_holes(head);head&=a[:,:,3]>0
   polygon=spec['exclude']
   if polygon:
    exclusion=Image.new('L',(512,512));ImageDraw.Draw(exclusion).polygon([tuple(q)for q in polygon],fill=255);head&=np.array(exclusion)==0
   record['native_annotation']=spec;record['annotation_template_reuse_disabled_for_this_frame']=True;record['candidate_holes_filled_before_prompt_validation']=True
   fragments,n=ndimage.label(head);sizes=np.bincount(fragments.ravel());sizes[0]=0;main=fragments==sizes.argmax();head&=ndimage.distance_transform_edt(~main)<=3
   d=o/sex/view;d.mkdir(parents=True,exist_ok=True);out=a.copy();out[~head]=0;Image.fromarray(out).save(d/f'{i:03d}.png')
   rest=a.copy();rest[head]=0;(d/'BodyRest').mkdir(exist_ok=True);Image.fromarray(rest).save(d/'BodyRest'/f'{i:03d}.png');combined=Image.new('RGBA',im.size);combined.alpha_composite(Image.fromarray(rest));combined.alpha_composite(Image.fromarray(out));visible=a[:,:,3]>0
   if not np.array_equal(np.array(combined)[visible],a[visible])or not np.array_equal(np.array(combined)[:,:,3],a[:,:,3]):raise ValueError('Master visible recomposition changed')
   record['visible_recomposition_mismatch_pixels']=0;record['master_modified']=False;print(json.dumps(record),flush=True)
(o/'proposal-receipt.json').write_text(json.dumps({'status':'COMPLETE_TIMELINE_PROPOSALS_REQUIRE_NATIVE_SEMANTIC_REVIEW','checkpoint_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'frames':records,'source_pixels_redrawn':False,'semantic_approved':False,'native_annotation_sha256':hashlib.sha256((o/'native-exceptions.json').read_bytes()).hexdigest(),'runtime_admitted':False},indent=2)+'\n')
(o/'proposal-source.py').write_bytes(Path(__file__).read_bytes())
