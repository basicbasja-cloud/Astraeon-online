"""SAM2 visible-part proposals for the bounded NE mage casting pilot.

Every output pixel belongs to exactly one slot and recomposes exactly. Semantic
ownership, hidden anatomy and swapping are separate reviews, never inferred
from that equality or the segmentation model's confidence.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def component(mask, minimum=12):
    count, labels, stats, centers = cv2.connectedComponentsWithStats(mask.astype('uint8'), 8)
    options = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= minimum]
    if not options:
        raise ValueError('Missing observed component')
    index = max(options, key=lambda i: stats[i, cv2.CC_STAT_AREA])
    selected = labels == index
    yy, xx = np.where(selected)
    middle = centers[index]
    nearest = np.argmin((xx-middle[0])**2+(yy-middle[1])**2)
    return selected, [int(xx[nearest]), int(yy[nearest])], [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())]


def attached_foreground(mask, alpha, seed):
    """Drop disconnected cuff/prop fragments while keeping nearby hair edges."""
    count, labels = cv2.connectedComponents((mask & (alpha > 32)).astype('uint8'), 8)
    label = int(labels[seed[1], seed[0]])
    if not label:
        raise ValueError('Observed hair seed was not retained')
    core = labels == label
    distance = cv2.distanceTransform((~core).astype('uint8'), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return mask & (alpha > 0) & (distance <= 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'guide', 'checkpoint', 'output']:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--masters',type=Path,help='Explicit registered master directory; default is source/frames/Master')
    parser.add_argument('--indices',type=int,nargs='+',help='Bounded diagnostic poses; incomplete exports cannot be packaged as a full sequence')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a new proposal output')
    if sha(args.checkpoint) != '7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':
        raise ValueError('Unexpected SAM2 model')
    implementation = sha(__file__)
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(4)
    predictor = SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml', str(args.checkpoint), device='cpu', apply_postprocessing=False))
    guide = json.loads((args.guide / 'pilot-receipt.json').read_text())
    rows = guide['views']['NE']['frames']
    if args.indices is not None:
        if len(set(args.indices))!=len(args.indices) or not set(args.indices).issubset({r['index'] for r in rows}):
            raise ValueError('Diagnostic indices must be unique captured poses')
        rows = [row for row in rows if row['index'] in args.indices]
    args.output.mkdir(parents=True)
    records = []
    for row in rows:
        index = row['index']
        master_directory = args.masters if args.masters is not None else args.source/'frames/Master'
        path = master_directory/f'{index:03d}.png'
        digest = sha(path)
        master = Image.open(path).convert('RGBA')
        a = np.array(master)
        rgb = a[:, :, :3].astype(float)
        yy, xx = np.indices(a.shape[:2])
        hx, hy = row['landmarks']['Head']
        region = (abs(xx-hx)<115) & (yy>hy-170) & (yy<hy+12)
        auburn_core = (rgb[:,:,0]-rgb[:,:,1])>1.8*(rgb[:,:,1]-rgb[:,:,2])
        observed = (a[:, :, 3]>64) & region & (rgb[:, :, 0]>1.45*rgb[:, :, 1]) & (rgb[:, :, 1]>1.1*rgb[:, :, 2]) & auburn_core
        # The brown staff can touch the auburn hair in the illustration. Break
        # thin shaft bridges before locating head positives; otherwise the
        # crystal/shaft negatives contradict positive "hair" shaft pixels.
        opened = cv2.morphologyEx(observed.astype('uint8'),cv2.MORPH_OPEN,np.ones((9,9),'uint8'))>0
        solid_hair, seed, _ = component(opened,50)
        hair_distance = cv2.distanceTransform((~solid_hair).astype('uint8'),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
        hair = observed & (hair_distance<=4)
        hair_y,hair_x = np.where(hair)
        bounds = [int(hair_x.min()),int(hair_y.min()),int(hair_x.max()),int(hair_y.max())]
        canvas = Image.new('RGBA', master.size, '#eee')
        canvas.alpha_composite(master)
        predictor.set_image(np.array(canvas.convert('RGB')))
        box = [bounds[0]-12, bounds[1]-12, bounds[2]+12, bounds[3]+12]
        cyan = (a[:, :, 3]>64) & (rgb[:, :, 1]>90) & (rgb[:, :, 2]>110) & (rgb[:, :, 2]>1.5*rgb[:, :, 0]) & (rgb[:, :, 1]>1.3*rgb[:, :, 0]) & (yy<hy-50)
        crystal, crystal_seed, crystal_bounds = component(cyan)
        staff_region = (abs(xx-crystal_seed[0])<12) & (yy>crystal_bounds[3]+10) & (yy<crystal_bounds[3]+55) & (a[:, :, 3]>128)
        staff_y, staff_x = np.where(staff_region)
        if not len(staff_x):
            raise ValueError('Missing observed shaft negative seed')
        middle = len(staff_x)//2
        negatives = [[hx, bounds[3]+30], crystal_seed, [int(staff_x[middle]), int(staff_y[middle])]]
        cuff = (a[:, :, 3]>128) & (xx>hx+25) & (xx<hx+130) & (abs(yy-hy)<50) & (rgb[:, :, 1]>.55*rgb[:, :, 0]) & (rgb[:, :, 1]>1.5*rgb[:, :, 2]) & (rgb[:, :, 0]>110)
        cuff_y, cuff_x = np.where(cuff)
        if len(cuff_x):
            center = np.array([cuff_x.mean(), cuff_y.mean()])
            selected_cuff = np.argmin((cuff_x-center[0])**2+(cuff_y-center[1])**2)
            negatives.append([int(cuff_x[selected_cuff]), int(cuff_y[selected_cuff])])
        # Several observed interior hair positives prevent a single point from
        # selecting only a curl. Keep the existing coverage and area gates.
        interior = cv2.erode(hair.astype('uint8'),np.ones((5,5),'uint8'))>0
        iy,ix = np.where(interior & ((xx-seed[0])**2+(yy-seed[1])**2<90**2))
        candidates = np.stack([ix,iy],axis=1)
        positives = [seed]
        for _ in range(4):
            if not len(candidates):
                break
            distances = np.min(np.sum((candidates[:,None,:]-np.array(positives)[None,:,:])**2,axis=2),axis=1)
            selected_point = int(np.argmax(distances))
            if distances[selected_point]<100:
                break
            positives.append(candidates[selected_point].tolist())
        points = np.array([*positives, *negatives], np.float32)
        with torch.inference_mode():
            masks, scores, _ = predictor.predict(point_coords=points, point_labels=np.array([1]*len(positives)+[0]*len(negatives)), box=np.array(box, np.float32), multimask_output=True, return_logits=True)
        core = hair & ((xx-hx)**2+(yy-(hy-70))**2<55**2)
        if not core.any():
            raise ValueError('Missing observed hair core')
        # Scale the lower area bound from observed hair, rather than the pixel
        # area of the older larger pilot. Require both independent observed
        # auburn coverage and central-core coverage; keep the body-area cap.
        lower_area = max(1000,.9*hair.sum())
        upper_area = min(35000,4*hair.sum())
        choices = [i for i in range(len(scores)) if ((masks[i]>0)&core).sum()/core.sum()>.95
                   and ((masks[i]>0)&hair).sum()/hair.sum()>.95
                   and lower_area<(masks[i]>0).sum()<upper_area]
        if not choices:
            (args.output/'proposal-failure.json').write_text(json.dumps({'index':index,
                'observed_hair_pixels':int(hair.sum()),'core_pixels':int(core.sum()),
                'prompt_points':points.tolist(),'positive_count':len(positives),'observed_hair_bounds':bounds,
                'candidates':[{'area':int((mask>0).sum()),'core_coverage':float(((mask>0)&core).sum()/core.sum()),
                               'observed_hair_coverage':float(((mask>0)&hair).sum()/hair.sum()),'score':float(score)}
                              for mask,score in zip(masks,scores)],'runtime_admitted':False},indent=2)+'\n')
            raise ValueError('No bounded complete hair proposal ' + str(index))
        selected = max(choices, key=lambda i: float(scores[i]))
        head = attached_foreground(masks[selected]>0, a[:, :, 3], seed)
        sx = crystal_seed[0]
        box = [sx-50, crystal_bounds[1]-18, sx+50, min(980, int(hy+230))]
        weapon_points = [crystal_seed, seed]
        if len(cuff_x):
            weapon_points.append(negatives[-1])
        with torch.inference_mode():
            masks, weapon_scores, _ = predictor.predict(point_coords=np.array(weapon_points, np.float32), point_labels=np.array([1]+[0]*(len(weapon_points)-1)), box=np.array(box, np.float32), multimask_output=True, return_logits=True)
        choices = [i for i in range(len(weapon_scores)) if ((masks[i]>0)&crystal).sum()/crystal.sum()>.70 and (masks[i]>0).sum()<18000]
        if not choices:
            raise ValueError('No bounded staff proposal ' + str(index))
        chosen = max(choices, key=lambda i: float(weapon_scores[i]))
        raw_weapon = (masks[chosen]>0) & (a[:, :, 3]>0)
        weapon = raw_weapon & ~head
        hand = np.zeros(head.shape, bool)
        if len(cuff_x):
            cuff_seed = negatives[-1]
            hand_box = [cuff_seed[0]-40, cuff_seed[1]-40, cuff_seed[0]+40, cuff_seed[1]+40]
            with torch.inference_mode():
                hand_masks, hand_scores, _ = predictor.predict(point_coords=np.array([cuff_seed, seed, crystal_seed], np.float32), point_labels=np.array([1, 0, 0]), box=np.array(hand_box, np.float32), multimask_output=True, return_logits=True)
            hand_choices = [k for k in range(len(hand_scores)) if hand_masks[k][cuff_seed[1], cuff_seed[0]]>0 and 100<(hand_masks[k]>0).sum()<6000]
            if hand_choices:
                k = max(hand_choices, key=lambda n: float(hand_scores[n]))
                hand = (hand_masks[k]>0) & (a[:, :, 3]>0)
                hand &= (xx-cuff_seed[0])**2+(yy-cuff_seed[1])**2<45**2
        # Resolve touching visible surfaces using both the observed auburn
        # palette and the independently prompted cuff. Otherwise SAM can join
        # a wrist touching the hair into one connected head component.
        auburn = (rgb[:, :, 0]>1.45*rgb[:, :, 1]) & ((rgb[:, :, 0]-rgb[:, :, 1])>1.8*(rgb[:, :, 1]-rgb[:, :, 2]))
        hand &= ~(head & auburn)
        head &= ~hand
        head &= ~(raw_weapon & ~auburn)
        weapon = raw_weapon & ~head & ~hand
        labels = np.zeros(a.shape[:2], 'uint8')
        labels[head] = 1
        labels[weapon] = 2
        labels[hand] = 3
        parts = {}
        for value, role in enumerate(['BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']):
            pixels = np.zeros_like(a)
            pixels[labels==value] = a[labels==value]
            parts[role] = Image.fromarray(pixels)
        combined = Image.new('RGBA', master.size)
        for part in parts.values():
            combined.alpha_composite(part)
        if combined.tobytes() != master.tobytes() or sha(path) != digest:
            raise ValueError('Visible source pixels changed')
        for role, part in parts.items():
            folder = args.output / role
            folder.mkdir(exist_ok=True)
            part.save(folder / f'{index:03d}.png')
        (args.output / 'labels').mkdir(exist_ok=True)
        Image.fromarray(labels).save(args.output / 'labels' / f'{index:03d}.png')
        records.append({'index': index, 'master_sha256': digest, 'head_confidence': float(scores[selected]),
                        'weapon_confidence': float(weapon_scores[chosen]), 'recomposition_changed_pixels': 0,
                        'head_prompt': points.tolist(), 'crystal_seed': crystal_seed,
                        'head_ownership_bound': 'observed hair-core positives; observed shaft/crystal/cuff and collar negatives; back view only',
                        'semantic_approval': False})
        (args.output / 'progress.json').write_text(json.dumps(records, indent=2) + '\n')
        print('MAGE_VISIBLE_CUTOUT_PROPOSAL', index, flush=True)
    if sha(__file__) != implementation:
        raise ValueError('Proposal implementation changed during execution')
    (args.output / 'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    (args.output / 'receipt.json').write_text(json.dumps({'status': 'VISIBLE_OWNERSHIP_PROPOSALS_NOT_SWAP_READY',
        'implementation_sha256': sha(__file__), 'checkpoint_sha256': sha(args.checkpoint),
        'frames': records, 'hidden_anatomy_reconstructed': False,
        'hand_occluder_authored': 'VISIBLE_PROPOSAL_ONLY', 'runtime_admitted': False}, indent=2) + '\n')


if __name__ == '__main__':
    main()
