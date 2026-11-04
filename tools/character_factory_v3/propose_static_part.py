"""Propose a static semantic cutout with recorded points and a pinned SAM2 model.

This preserves source RGBA exactly; confidence never grants art approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','recipe','checkpoint','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh static mask proposal')
    if sha(a.checkpoint)!='7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':raise ValueError('Unexpected model checkpoint')
    frozen={str(f):sha(f)for f in [a.source,a.recipe,a.checkpoint]}
    recipe=json.loads(a.recipe.read_text());image=Image.open(a.source).convert('RGBA');values=np.array(image)
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4)
    predictor=SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml',str(a.checkpoint),device='cpu',apply_postprocessing=False))
    bg=Image.new('RGBA',image.size,'#aaa');bg.alpha_composite(image);predictor.set_image(np.array(bg.convert('RGB')))
    positive=recipe['positive'];negative=recipe['negative'];points=np.array(positive+negative,dtype=np.float32);labels=np.array([1]*len(positive)+[0]*len(negative))
    with torch.inference_mode():masks,scores,_=predictor.predict(point_coords=points,point_labels=labels,box=np.array(recipe['box'],np.float32),multimask_output=True,return_logits=True)
    valid=[]
    for i,mask in enumerate(masks):
        if all(bool(mask[int(y),int(x)]>0)==bool(label)for(x,y),label in zip(points,labels)):valid.append(i)
    if not valid:
        a.output.mkdir(parents=True)
        details=[]
        for i,mask in enumerate(masks):
            wrong=[{'point':[float(x),float(y)],'expected':int(label),'observed':bool(mask[int(y),int(x)]>0)}for(x,y),label in zip(points,labels)if bool(mask[int(y),int(x)]>0)!=bool(label)]
            details.append({'candidate':i,'score':float(scores[i]),'violations':wrong})
        (a.output/'failure.json').write_text(json.dumps({'status':'REJECTED_SEMANTIC_PROMPTS','input_sha256':frozen,'candidates':details},indent=2)+'\n')
        raise ValueError('No static mask respects all semantic annotations')
    selected=max(valid,key=lambda i:scores[i]);mask=(masks[selected]>0)&(values[:,:,3]>0)
    yy,xx=np.indices(mask.shape);x0,y0,x1,y1=recipe['box'];mask&=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
    kept=np.zeros_like(values);kept[mask]=values[mask];removed=values.copy();removed[mask]=0
    a.output.mkdir(parents=True);Image.fromarray(kept).save(a.output/'part.png');Image.fromarray(removed).save(a.output/'excluded.png');Image.fromarray(mask.astype('uint8')*255).save(a.output/'mask.png')
    if any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Static semantic input changed')
    (a.output/'receipt.json').write_text(json.dumps({'status':'STATIC_SEMANTIC_PROPOSAL_NOT_APPROVED','input_sha256':frozen,'recipe':recipe,'selected_candidate':selected,'scores':[float(s)for s in scores],'kept_pixels':int(mask.sum()),'implementation_sha256':sha(__file__),'source_rgba_changed':False,'runtime_admitted':False},indent=2)+'\n')
    shutil.copyfile(__file__,a.output/'renderer-source.py')
    print(json.dumps({'kept_pixels':int(mask.sum()),'candidate':selected,'runtime_admitted':False}))

if __name__=='__main__':main()
