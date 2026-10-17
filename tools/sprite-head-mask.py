"""Local CPU MobileSAM ownership extraction; never paints or registers source pixels.

Run using the free-mask-model virtualenv. Prompts must be manually reviewed for
the actual source image. Model confidence is not semantic or head-swap approval.
"""
from pathlib import Path
import argparse, hashlib, json, time
import numpy as np
from PIL import Image

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inputs(path, checkpoint):
    path=Path(path).resolve(); data=json.loads(path.read_text())
    if sha(checkpoint)!=data['checkpoint_sha256']:
        raise ValueError('Checkpoint digest mismatch')
    if not data['frames']:
        raise ValueError('Empty frame list')
    for row in data['frames']:
        image=path.parent/row['path']
        if sha(image)!=row['sha256']:
            raise ValueError('Stale source image')
        w,h=Image.open(image).size
        points=row['points']; labels=row['labels']; box=row['box']
        if len(points)!=len(labels) or not points or set(labels)!={0,1}:
            raise ValueError('Explicit positive head and negative clothing prompts required')
        if any(type(v) is not int or v not in [0,1]for v in labels):
            raise ValueError('Binary integer labels required')
        for p in points:
            if len(p)!=2 or any(type(v) is not int for v in p) or not(0<=p[0]<w and 0<=p[1]<h):
                raise ValueError('Prompt point outside image or invalid')
        if len(box)!=4 or not(0<=box[0]<box[2]<=w and 0<=box[1]<box[3]<=h):
            raise ValueError('Invalid head prompt box')
        context=row.get('context_box',[0,0,w,h])
        if len(context)!=4 or any(type(v) is not int for v in context) or not(0<=context[0]<context[2]<=w and 0<=context[1]<context[3]<=h):
            raise ValueError('Invalid inference context crop')
        if any(not(context[0]<=x<context[2] and context[1]<=y<context[3])for x,y in points):
            raise ValueError('All prompt points must lie inside inference context')
        if not(context[0]<=box[0]<box[2]<=context[2] and context[1]<=box[1]<box[3]<=context[3]):
            raise ValueError('Head prompt box outside inference context')
    return path,data

def extract(prompt_file,checkpoint,out):
    # Preflight before importing models or creating output. No code evaluation
    # from the checkpoint; load tensor-only state with PyTorch weights_only.
    prompt_file,data=inputs(prompt_file,checkpoint)
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    import torch
    from scipy.ndimage import binary_fill_holes,label
    from mobile_sam import sam_model_registry,SamPredictor
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    model=sam_model_registry['vit_t'](checkpoint=None)
    model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=True),strict=True)
    model.eval();predictor=SamPredictor(model);results=[]
    for i,row in enumerate(data['frames']):
        source=prompt_file.parent/row['path']; full=Image.open(source).convert('RGBA')
        bg=Image.new('RGBA',full.size,'#343941');bg.alpha_composite(full)
        context=row.get('context_box',[0,0,*full.size]);x0,y0,x1,y1=context
        offset=np.array([x0,y0]);points=np.array(row['points'])-offset
        box=np.array(row['box'])-np.array([x0,y0,x0,y0])
        # Crop is for segmentation context ONLY. The output ownership mask is
        # placed at its original integer origin on the full unchanged canvas.
        started=time.perf_counter();predictor.set_image(np.array(bg.convert('RGB').crop(tuple(context))))
        masks,scores,_=predictor.predict(point_coords=points,
            point_labels=np.array(row['labels']),box=box,multimask_output=True)
        options=[]
        owner=next(p for p,v in zip(points,row['labels']) if v==1)
        for j,mask in enumerate(masks):
            # Mask edits affect ownership only. Keep the component at the
            # manually identified hair point; disconnected gold fragments go
            # back to the body. All positive/negative prompts must still agree.
            filled=binary_fill_holes(mask);components,_=label(filled)
            value=components[owner[1],owner[0]]
            candidate=(components==value) if value else np.zeros_like(filled)
            violations=sum(bool(candidate[y,x])!=bool(v)for (x,y),v in zip(points,row['labels']))
            options.append((violations,-float(scores[j]),j,candidate))
        violations,_,selected,mask=min(options,key=lambda x:x[:3])
        full_mask=np.zeros((full.height,full.width),dtype='uint8')
        full_mask[y0:y1,x0:x1]=mask.astype('uint8')*255
        bitmap=Image.fromarray(full_mask)
        empty=Image.new('RGBA',full.size)
        head=Image.composite(full,empty,bitmap);body=Image.composite(empty,full,bitmap)
        recomposed=Image.alpha_composite(body,head);a=np.array(full);b=np.array(recomposed)
        assert np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0])
        assert not np.any((np.array(head)[:,:,3]>0)&(np.array(body)[:,:,3]>0))
        for name,image in [('head',head),('body',body),('mask',bitmap)]:
            dest=out/name/f'{i:02}.png';dest.parent.mkdir(exist_ok=True);image.save(dest)
        results.append({'index':i,'source_sha256':row['sha256'],'selected_candidate':selected,
            'model_scores':scores.tolist(),'prompt_violations':violations,
            'inference_context_box':context,'final_image_transform':'identity; no pixel translation, scaling or warp',
            'head_sha256':sha(out/'head'/f'{i:02}.png'),'body_sha256':sha(out/'body'/f'{i:02}.png'),
            'exact_visible_RGBA_recomposition':True,'disjoint_visible_ownership':True,
            'seconds':time.perf_counter()-started,'semantic_head_review':'pending'})
        print(f'{i+1}/{len(data["frames"])}: prompt violations={violations}',flush=True)
    report={'technical_partition_pass':all(r['prompt_violations']==0 for r in results),
            'checkpoint_sha256':sha(checkpoint),'prompt_file_sha256':sha(prompt_file),
            'tool_sha256':sha(Path(__file__).resolve()),
            'source_pixels_transformed':False,'new_drawings':0,'provider_calls':0,
            'semantic_head_approval_granted':False,'head_swap_pass':False,
            'production_pass':False,'frames':results}
    (out/'extraction-review.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prompts',type=Path);parser.add_argument('--checkpoint',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    result=extract(args.prompts,args.checkpoint,args.out)
    raise SystemExit(0 if result['technical_partition_pass'] else 1)
