"""Propose narrower head ownership and return old collar/arm pixels to body.

Run with the retained SAM2 environment. No painted color, alpha, body geometry,
weapon, or hand pixels are repainted. Exact replay is not semantic approval.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from track_visible_cutouts import pin_inputs,verify_inputs,sha


def transfer(master,body,head,mask):
    a,b,h=[np.array(im.convert('RGBA'))for im in [master,body,head]]
    if a.shape!=b.shape or a.shape!=h.shape or mask.shape!=a.shape[:2]:raise ValueError('Cutout canvases differ')
    release=(h[:,:,3]>0)&~mask;b[release]=a[release];h[release]=0
    return Image.fromarray(b),Image.fromarray(h),int(release.sum())


def head_prompt(image):
    import cv2
    a=np.array(image);rgb=a[:,:,:3].astype(float);hi=rgb.max(2);lo=rgb.min(2)
    gray=(a[:,:,3]>32)&(hi>80)&((hi-lo)<.28*np.maximum(hi,1))&(rgb[:,:,2]>.78*rgb[:,:,1])
    grown=cv2.morphologyEx(gray.astype('uint8'),cv2.MORPH_CLOSE,np.ones((5,5),'uint8'))
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(grown,8)
    if count<2:raise ValueError('No observed silver hair component')
    largest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));scope=(labels==largest)&gray
    yy,xx=np.where(scope);center=np.array([xx.mean(),yy.mean()]);index=np.argmin((xx-center[0])**2+(yy-center[1])**2);positive=[[int(xx[index]),int(yy[index])]]
    skin=(a[:,:,3]>64)&(rgb[:,:,0]>rgb[:,:,1]*1.15)&(rgb[:,:,1]>rgb[:,:,2]*1.1)&((hi-lo)/np.maximum(hi,1)<.64)
    sy,sx=np.where(skin&((np.indices(skin.shape)[1]-center[0])**2+(np.indices(skin.shape)[0]-center[1])**2<32**2))
    if len(sx):
        index=np.argmin((sx-center[0])**2+(sy-center[1])**2);positive.append([int(sx[index]),int(sy[index])])
    box=[max(0,int(xx.min())-12),max(0,int(yy.min())-12),min(a.shape[1]-1,int(xx.max())+12),min(a.shape[0]-1,int(yy.max())+28)]
    return {'positive':positive,'box':box},scope


def build(source,checkpoint,output):
    if output.exists():raise ValueError('Choose a new proposal directory')
    if sha(checkpoint)!='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':raise ValueError('Unexpected SAM2 checkpoint')
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4);predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(checkpoint),device='cpu',apply_postprocessing=False))
    directions=['SW','NW','NE','SE'];roles=['Master','BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront']
    pins=pin_inputs([Path(__file__),checkpoint,*[source/d/r/f'{i:03d}.png'for d in directions for r in roles for i in range(16)]])
    output.mkdir(parents=True);rows=[]
    for d in directions:
        for i in range(16):
            master=Image.open(source/d/'Master'/f'{i:03d}.png').convert('RGBA');head=Image.open(source/d/'HeadHair'/f'{i:03d}.png').convert('RGBA');body=Image.open(source/d/'BodyCostume'/f'{i:03d}.png').convert('RGBA')
            prompt,hair=head_prompt(head);bg=Image.new('RGBA',master.size,'#eee');bg.alpha_composite(master);predictor.set_image(np.array(bg.convert('RGB')))
            with torch.inference_mode():masks,scores,raw=predictor.predict(point_coords=np.array(prompt['positive'],np.float32),point_labels=np.ones(len(prompt['positive']),dtype=np.int32),box=np.array(prompt['box'],np.float32),multimask_output=True,return_logits=True)
            valid=[]
            for n in range(len(scores)):
                candidate=masks[n]>0
                if all(candidate[y,x]for x,y in prompt['positive']) and (candidate&hair).sum()/hair.sum()>=.90:valid.append(n)
            hair_only_retry=False
            if not valid and len(prompt['positive'])>1:
                # A warm pixel near hair may be an overlapping glove rather
                # than a visible face. Retry only the observed hair seed;
                # retain the same complete-hair constraint and review status.
                with torch.inference_mode():masks,scores,raw=predictor.predict(point_coords=np.array(prompt['positive'][:1],np.float32),point_labels=np.ones(1,dtype=np.int32),box=np.array(prompt['box'],np.float32),multimask_output=True,return_logits=True)
                for n in range(len(scores)):
                    candidate=masks[n]>0
                    if candidate[prompt['positive'][0][1],prompt['positive'][0][0]] and (candidate&hair).sum()/hair.sum()>=.90:valid.append(n)
                hair_only_retry=True
            if not valid:raise ValueError(f'No complete hair/face proposal {d}/{i}')
            selected=max(valid,key=lambda n:float(scores[n]));mask=masks[selected]>0
            newbody,newhead,released=transfer(master,body,head,mask)
            composed=Image.new('RGBA',master.size)
            parts={'BodyCostume':newbody,'HeadHair':newhead,'Weapon':Image.open(source/d/'Weapon'/f'{i:03d}.png').convert('RGBA'),'WeaponHandOccluder':Image.open(source/d/'WeaponHandOccluder'/f'{i:03d}.png').convert('RGBA')}
            for part in parts.values():composed.alpha_composite(part)
            if composed.tobytes()!=master.tobytes():raise ValueError('Master reconstruction changed')
            for role in roles:
                dest=output/d/role;dest.mkdir(parents=True,exist_ok=True)
                if role in ['BodyCostume','HeadHair']:parts[role].save(dest/f'{i:03d}.png')
                else:shutil.copy2(source/d/role/f'{i:03d}.png',dest/f'{i:03d}.png')
            label=(np.array(newhead.getchannel('A'))>0).astype('uint8');dest=output/d/'head-labels';dest.mkdir(exist_ok=True);Image.fromarray(label).save(dest/f'{i:03d}.png')
            rows.append({'direction':d,'index':i,'body_reassigned_pixels':released,'head_pixels':int(label.sum()),'confidence':float(scores[selected]),'prompt':prompt,'hair_only_prompt_retry':hair_only_retry,'master_reconstruction_changed_pixels':0})
            (output/'progress.json').write_text(json.dumps({'status':'PARTIAL_UNREVIEWED_PROPOSALS','frames':rows},indent=2)+'\n')
            print(d,i,released,flush=True)
    verify_inputs(pins);receipt={'status':'REFINED_HEAD_OWNERSHIP_PROPOSAL_NOT_SEMANTIC_APPROVAL','frames':rows,'source_pins':pins,'painted_rgba_modified':False,'hidden_surfaces_authored':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','checkpoint','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.source,a.checkpoint,a.output)
