"""Propose same-frame HeadHair/BodyCostume masks; never certify semantic quality."""
import argparse,json,hashlib,sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frames',type=Path,required=True);p.add_argument('--annotations',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--model-root',type=Path,default=Path('/workspace/.tools/MobileSAM'));a=p.parse_args()
    import torch
    torch.set_num_threads(2);sys.path.insert(0,str(a.model_root))
    from mobile_sam import sam_model_registry,SamPredictor
    cp=a.model_root/'weights/mobile_sam.pt';model=sam_model_registry['vit_t'](checkpoint=None);model.load_state_dict(torch.load(cp,map_location='cpu',weights_only=True));model.eval();predictor=SamPredictor(model)
    annotations=json.loads(a.annotations.read_text());records=[];a.output.mkdir(parents=True,exist_ok=True);contact=Image.new('RGBA',(1536,1536),'#353b45')
    for item in annotations['frames']:
        i=item['index'];im=Image.open(a.frames/f'{i:03d}.png').convert('RGBA');pixels=np.array(im);scale=im.width/annotations['canvas'];box=np.array(item['box'],float)*scale
        backdrop=Image.new('RGBA',im.size,'white');backdrop.alpha_composite(im);predictor.set_image(np.array(backdrop.convert('RGB')))
        points=np.array(item['positive']+item['negative'],np.float32)*scale;labels=np.array([1]*len(item['positive'])+[0]*len(item['negative']))
        masks,scores,_=predictor.predict(point_coords=points,point_labels=labels,box=box,multimask_output=True)
        yy,xx=np.indices(pixels.shape[:2]);x0,y0,x1,y1=box;scope=(xx>=x0-4)&(xx<=x1+4)&(yy>=y0-4)&(yy<=y1+4)&(pixels[:,:,3]>0);candidates=[]
        for mask,score in zip(masks,scores):
            mask=mask&scope
            valid=all(mask[min(im.height-1,round(pt[1])),min(im.width-1,round(pt[0]))] for pt in points[:len(item['positive'])])
            candidates.append((float(score) if valid else -1,mask))
        score,head=max(candidates,key=lambda r:r[0])
        # Bounded warm-color prior separates this brown-haired identity from green
        # hood and ivory sleeves. This is identity-specific, not a general model.
        if annotations.get('warm_head_prior'):
            rgb=pixels[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
            warm=(r>g*1.18)&(g>b*1.08)&(r>35)&scope
            warm=cv2.morphologyEx(warm.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8),iterations=2)>0
            warm=(cv2.dilate(warm.astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)>0)&scope
            head &= warm
            count,components=cv2.connectedComponents(head.astype(np.uint8))
            hair=points[0];seed=components[round(hair[1]),round(hair[0])]
            if seed:head=components==seed
            else:raise ValueError(f'Head prior lost hair seed in frame {i}')
        if item.get('manual_neckline'):
            # Explicit source-frame neckline overrides model spill into hood/sleeve.
            boundary=np.array(item['manual_neckline'])*scale
            right=[tuple(np.array(pt)*scale) for pt in item.get('manual_right_profile',[])]
            polygon=[(x0-4,y0-4),(x1+4,y0-4),*right,(boundary[-1][0],boundary[-1][1]),*reversed([tuple(pt) for pt in boundary]),(x0-4,boundary[0][1])]
            clip=Image.new('L',im.size);ImageDraw.Draw(clip).polygon(polygon,fill=255)
            head=(np.array(clip)>0)&scope
            count,components=cv2.connectedComponents(head.astype(np.uint8))
            hair=points[0];seed=components[round(hair[1]),round(hair[0])]
            if seed:head=components==seed
        if score<0:raise ValueError(f'No proposal includes all head positives in frame {i}')
        h=pixels.copy();h[~head]=0;b=pixels.copy();b[head]=0
        for role,array in [('HeadHair',h),('BodyCostume',b)]:
            d=a.output/role;d.mkdir(exist_ok=True);Image.fromarray(array).save(d/f'{i:03d}.png')
        recomposed=Image.alpha_composite(Image.fromarray(b),Image.fromarray(h));different=int(np.any(np.array(recomposed)!=pixels,axis=2).sum())
        if different:raise ValueError(f'Pixel recomposition changed {different} pixels')
        preview=Image.new('RGBA',im.size,'#353b45');preview.alpha_composite(Image.fromarray(h));contact.alpha_composite(preview.resize((384,384)),((i%4)*384,(i//4)*384))
        rec={'index':i,'proposal_score':score,'source_sha256':hashlib.sha256((a.frames/f'{i:03d}.png').read_bytes()).hexdigest(),'head_pixels':int(head.sum()),'recomposition_mismatch_pixels':different};records.append(rec);print(json.dumps(rec),flush=True)
    contact.save(a.output/'heads-contact.png')
    (a.output/'receipt.json').write_text(json.dumps({'status':'HEAD_MASK_PROPOSALS_REQUIRE_BOUNDARY_REVIEW','roles':['HeadHair','BodyCostume'],'weapon_separated':False,'bodycostume_note':'Contains weapon until separate same-frame mask is authored; not an importable layer package.','checkpoint_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'source_pixels_redrawn':False,'source_pose_registered':False,'frames':records,'owner_approved':False,'runtime_admitted':False},indent=2)+'\n')

if __name__=='__main__':main()
