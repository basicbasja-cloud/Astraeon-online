"""Propose head cuts from coherent full-body masters; never move body pixels."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['masters', 'controls', 'checkpoint', 'output']:
        p.add_argument('--'+key, type=Path, required=True)
    p.add_argument('--direction', required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError('Choose a fresh proposal folder')
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4)
    if sha(a.checkpoint) != '7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':
        raise ValueError('Unexpected segmentation checkpoint')
    predictor = SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml', str(a.checkpoint), device='cpu', apply_postprocessing=False))
    controls = json.loads(a.controls.read_text())
    a.output.mkdir(parents=True)
    records = []
    for frame in controls['views'][a.direction]['frames']:
        i = frame['index']; source = a.masters/f'{i:03d}.png'
        im = Image.open(source).convert('RGBA'); pixels = np.array(im)
        hx, hy = frame['landmarks']['Head']; nx, ny = frame['landmarks']['Neck']
        yy, xx = np.indices(pixels.shape[:2]); rgb = pixels[:, :, :3].astype(float)
        region = (abs(xx-hx)<108)&(yy>hy-155)&(yy<ny+8)
        warm = (rgb[:, :, 0]>1.12*rgb[:, :, 1])&(rgb[:, :, 1]>1.05*rgb[:, :, 2])
        observed = region&warm&(pixels[:, :, 3]>96)
        opened = cv2.morphologyEx(observed.astype('uint8'), cv2.MORPH_OPEN, np.ones((7, 7), 'uint8'))
        count, labels, stats, centers = cv2.connectedComponentsWithStats(opened, 8)
        candidates = [k for k in range(1, count) if stats[k, cv2.CC_STAT_AREA]>100]
        if not candidates:
            raise ValueError('No observed chestnut hair component')
        selected = max(candidates, key=lambda k: stats[k, cv2.CC_STAT_AREA]); core = labels==selected
        ys, xs = np.where(core); center = centers[selected]
        n = np.argmin((xs-center[0])**2+(ys-center[1])**2); seed = [int(xs[n]), int(ys[n])]
        box = [int(xs.min())-8, int(ys.min())-8, int(xs.max())+18, min(int(ys.max())+16, round(ny+8))]
        crop = [max(0,box[0]-50),max(0,box[1]-50),min(im.width,box[2]+50),min(im.height,box[3]+50)]
        bg = Image.new('RGBA', im.size, '#ddd'); bg.alpha_composite(im)
        predictor.set_image(np.array(bg.crop(crop).convert('RGB')))
        points = np.array([seed,[nx,ny+27],[box[0]+3,ny+20]],np.float32)-np.array(crop[:2],np.float32)
        cb = np.array(box,np.float32)-np.array(crop[:2]*2,np.float32)
        masks, scores, _ = predictor.predict(point_coords=points, point_labels=np.array([1,0,0]),box=cb,multimask_output=True)
        proposals=[]
        for mask, score in zip(masks,scores):
            full = np.zeros(pixels.shape[:2],bool);full[crop[1]:crop[3],crop[0]:crop[2]]=mask
            full &= region&(pixels[:,:,3]>0)
            coverage = float((full&core).sum()/core.sum())
            proposals.append((float(score) if coverage>.95 else -1,full,coverage))
        score, mask, coverage=max(proposals,key=lambda item:item[0])
        if score<0:
            raise ValueError('No proposal covers observed hair: '+str(i))
        parts={}
        for role, selection in [('HeadHair',mask),('BodyCostume',~mask)]:
            data=pixels.copy();data[~selection]=0;part=Image.fromarray(data);parts[role]=part
            folder=a.output/role;folder.mkdir(exist_ok=True);part.save(folder/f'{i:03d}.png')
        reconstructed=Image.alpha_composite(parts['BodyCostume'],parts['HeadHair'])
        if reconstructed.tobytes()!=im.tobytes():
            raise ValueError('Same-frame pixel recomposition failed')
        records.append({'index':i,'source_sha256':sha(source),'seed':seed,'box':box,'sam_score':score,'observed_hair_coverage':coverage,'master_pixel_changes':0})
        print('COHERENT_HEAD_PROPOSAL',i,flush=True)
    (a.output/'receipt.json').write_text(json.dumps({'status':'HEAD_MASK_PROPOSALS_NOT_APPROVED','frames':records,'controls_sha256':sha(a.controls),'checkpoint_sha256':sha(a.checkpoint),'body_includes_weapon':True,'body_pose_changed':False,'limbs_separately_generated_or_assembled':False,'hidden_surfaces_authored':False,'runtime_admitted':False},indent=2)+'\n')


if __name__=='__main__':
    main()
