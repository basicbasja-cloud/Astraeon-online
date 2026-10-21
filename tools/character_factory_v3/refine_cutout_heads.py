"""Free MobileSAM-assisted visible head cutouts from manual same-frame boxes.

Run in the isolated CPU environment. Model scores are proposal scores, never
semantic accuracy or art approval. Original painted pixels remain unchanged.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw


def refine(folder,model_root,limit):
    import torch
    torch.set_num_threads(2)
    sys.path.insert(0,str(model_root))
    from mobile_sam import sam_model_registry,SamPredictor
    checkpoint=model_root/'weights/mobile_sam.pt';model=sam_model_registry['vit_t'](checkpoint=None)
    model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True));model.eval();predictor=SamPredictor(model)
    annotation=json.loads((folder/'cutout-annotations.json').read_text());scale=512/annotation['annotation_canvas_per_cell'];out=folder/'sam-head-study';out.mkdir(exist_ok=True);records=[]
    contact=Image.new('RGB',(1024,256*((min(limit,len(annotation['frames']))+3)//4)),(44,48,60))
    for record in annotation['frames'][:limit]:
        i=record['index'];start=time.monotonic();original=Image.open(folder/'cutout-study/Master'/f'{i:03d}.png').convert('RGBA');a=np.array(original);visible=a[:,:,3]>0
        rgb=Image.new('RGBA',original.size,'white');rgb.alpha_composite(original);predictor.set_image(np.array(rgb.convert('RGB')))
        box=np.array(record['head_ellipse'],float)*scale;x0,y0,x1,y1=box;cx=(x0+x1)/2;cy=(y0+y1)/2
        colors=np.array(rgb.convert('RGB')).astype(float);rr,gg,bb=colors[:,:,0],colors[:,:,1],colors[:,:,2];yy0,xx0=np.indices(rr.shape)
        skin=(rr>80)&(rr>gg*1.12)&(gg>bb*1.08)&(bb>rr*.42)&(xx0>=x0)&(xx0<=x1)&(yy0>=cy)&(yy0<=y1)
        candidates=np.argwhere(skin)
        if len(candidates):
            yface,xface=min(candidates,key=lambda p:(p[1]-cx)**2+(p[0]-(y0+.85*(y1-y0)))**2)
        else:xface,yface=cx,y1-8
        points=np.array([[cx,y0+.3*(y1-y0)],[xface,yface],[cx,y1+12]],dtype=np.float32);labels=np.array([1,1,0])
        masks,scores,_=predictor.predict(point_coords=points,point_labels=labels,box=box,multimask_output=True)
        yy,xx=np.indices(visible.shape);scope=(xx>=x0-6)&(xx<=x1+6)&(yy>=y0-6)&(yy<=y1+6)
        choices=[]
        for index,(mask,score)in enumerate(zip(masks,scores)):
            m=mask&visible&scope;area=int(m.sum());ratio=area/max(1,(x1-x0)*(y1-y0));contains=all(m[round(p[1]),round(p[0])]for p in points[:2])
            choices.append((float(score)if .15<ratio<1.3 and contains else-10,index,m,ratio))
        score,index,head,ratio=max(choices,key=lambda c:c[0])
        if score<0:raise ValueError(f'No plausible bounded head proposal for frame {i}')
        weapon=np.array(Image.open(folder/'cutout-study/Weapon'/f'{i:03d}.png').convert('RGBA'))[:,:,3]>0
        head &= ~weapon
        head_pixels=a.copy();head_pixels[~head]=0;body_pixels=a.copy();body_pixels[head|weapon]=0
        parts={'HeadHair':Image.fromarray(head_pixels),'BodyCostume':Image.fromarray(body_pixels),'Weapon':Image.open(folder/'cutout-study/Weapon'/f'{i:03d}.png').convert('RGBA')}
        merged=Image.new('RGBA',(512,512))
        for role in ['BodyCostume','HeadHair','Weapon']:
            target=out/role/f'{i:03d}.png';target.parent.mkdir(exist_ok=True);parts[role].save(target);merged.alpha_composite(parts[role])
        mismatch=int(np.any(np.array(merged)!=a,axis=2).sum())
        if mismatch:raise ValueError('Source pixel recomposition differs')
        preview=Image.new('RGBA',(512,512),(44,48,60,255));preview.alpha_composite(parts['HeadHair']);contact.paste(preview.resize((256,256)).convert('RGB'),(i%4*256,i//4*256))
        records.append({'frame':i,'proposal_score':float(scores[index]),'mask_to_box_area_ratio':ratio,'head_visible_pixels':int(head.sum()),'recomposition_mismatch_pixels':mismatch,'seconds':round(time.monotonic()-start,3),'semantic_boundary_review_required':True})
        print(json.dumps(records[-1]),flush=True)
    contact.save(out/'HeadHair-contact.png')
    (out/'receipt.json').write_text(json.dumps({'status':'SEGMENTATION_PROPOSALS_NOT_APPROVED_CUTOUTS','checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'checkpoint_license':'Apache-2.0; official MobileSAM repository','source_pixels_redrawn':False,'frames':records,'owner_approved':False,'runtime_admitted':False},indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--model-root',type=Path,default=Path('/workspace/.tools/MobileSAM'));p.add_argument('--limit',type=int,default=16);a=p.parse_args();refine(a.folder,a.model_root,a.limit)
