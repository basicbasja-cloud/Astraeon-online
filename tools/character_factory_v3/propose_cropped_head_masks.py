"""Propose complete head masks at a local resolution, with measured skin seeds.

Actual source pixels are never moved. This is a semantic-review aid, not approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['frames', 'annotations', 'checkpoint', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--indices', type=int, nargs='+', required=True)
    args = parser.parse_args()
    import torch
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
    torch.set_num_threads(3)
    if args.output.exists():
        raise ValueError('Use a fresh mask proposal folder')
    checkpoint_sha = hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
    if checkpoint_sha != '7402e0d864fa82708a20fbd15bc84245c2f26dff0eb43a4b5b93452deb34be69':
        raise ValueError('Unexpected pinned segmentation checkpoint')
    predictor = SAM2ImagePredictor(build_sam2('configs/sam2.1/sam2.1_hiera_t.yaml', str(args.checkpoint), device='cpu', apply_postprocessing=False))
    data = json.loads(args.annotations.read_text())
    args.output.mkdir(parents=True)
    records = []
    for index in args.indices:
        annotation = next(r for r in data['frames'] if r['index'] == index)
        source = args.frames/f'{index:03d}.png'
        image = Image.open(source).convert('RGBA')
        rgba = np.array(image)
        rgb = rgba[:, :, :3].astype(float)
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        x0, y0, x1, y1 = np.array(annotation['box'])*image.width/data['canvas']
        yy, xx = np.indices(r.shape)
        scope = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & (rgba[:, :, 3] > 0)
        skin = scope & (r > 180) & (g > 125) & (b > 100) & (r > g*1.12) & (g > b*1.05) & (g-b < 65)
        count, components, stats, centers = cv2.connectedComponentsWithStats(skin.astype(np.uint8))
        candidates = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= 4]
        if not candidates:
            raise ValueError('No actual facial skin seed: '+str(index))
        selected = max(candidates, key=lambda i: stats[i, cv2.CC_STAT_AREA])
        ys, xs = np.nonzero(components == selected)
        center = centers[selected]
        closest = np.argmin((xs-center[0])**2+(ys-center[1])**2)
        face = np.array([xs[closest], ys[closest]], float)
        hair = np.array(annotation['positive'][0])*image.width/data['canvas']
        green = (rgba[:, :, 3] > 0) & (r < g*1.12) & (g > 30) & (yy > face[1]+4) & (yy < face[1]+40) & (abs(xx-face[0]) < 55)
        ys, xs = np.nonzero(green)
        if not len(xs):
            raise ValueError('No actual costume negative seed: '+str(index))
        target = face+[16, 22]
        closest = np.argmin((xs-target[0])**2+(ys-target[1])**2)
        negative = np.array([xs[closest], ys[closest]], float)
        padding = 24
        crop = [max(0, int(x0)-padding), max(0, int(y0)-padding), min(image.width, int(x1)+padding), min(image.height, int(y1)+padding)]
        backdrop = Image.new('RGBA', image.size, 'white')
        backdrop.alpha_composite(image)
        predictor.set_image(np.array(backdrop.crop(crop).convert('RGB')))
        points = np.array([hair, face, negative])-crop[:2]
        box = np.array([x0, y0, x1, y1])-np.array(crop[:2]*2)
        masks, scores, _ = predictor.predict(point_coords=points, point_labels=np.array([1, 1, 0]), box=box, multimask_output=True)
        proposals = []
        diagnostics = []
        for local, score in zip(masks, scores):
            mask = np.zeros(scope.shape, bool)
            mask[crop[1]:crop[3], crop[0]:crop[2]] = local
            mask &= scope
            valid = all(mask[round(point[1]), round(point[0])] for point in [hair, face]) and not mask[round(negative[1]), round(negative[0])]
            green_pixels = int((mask & green).sum())
            proposals.append((float(score)-green_pixels*.002 if valid else -1000, mask, float(score)))
            diagnostics.append({'score': float(score), 'valid': bool(valid),
                                'hair_included': bool(mask[round(hair[1]), round(hair[0])]),
                                'face_included': bool(mask[round(face[1]), round(face[0])]),
                                'negative_included': bool(mask[round(negative[1]), round(negative[0])])})
        metric, mask, score = max(proposals, key=lambda row: row[0])
        if metric <= -1000:
            (args.output/'failed-seeds.json').write_text(json.dumps({'index': index, 'hair': hair.tolist(), 'face': face.tolist(), 'negative': negative.tolist(), 'proposals': diagnostics}, indent=2)+'\n')
            raise ValueError('No proposal contains actual hair and face without the costume seed: '+str(index))
        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
        label = labels[round(face[1]), round(face[0])]
        if not label or labels[round(hair[1]), round(hair[0])] != label:
            raise ValueError('Head face and hair are disconnected: '+str(index))
        mask = labels == label
        for role, keep in [('HeadHair', mask), ('BodyCostume', ~mask)]:
            pixels = rgba.copy()
            pixels[~keep] = 0
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            Image.fromarray(pixels).save(folder/source.name)
        records.append({'index': index, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'hair_seed': hair.tolist(), 'face_seed': face.tolist(), 'costume_negative': negative.tolist(), 'score': score, 'head_pixels': int(mask.sum()), 'body_includes_weapon': True})
        (args.output/'progress.json').write_text(json.dumps({'status': 'CROPPED_HEAD_PROPOSALS_REQUIRE_VISUAL_REVIEW', 'checkpoint_sha256': checkpoint_sha, 'frames': records, 'runtime_admitted': False}, indent=2)+'\n')
        print('CROPPED_HEAD_PROPOSAL', index, score, flush=True)


if __name__ == '__main__':
    main()
