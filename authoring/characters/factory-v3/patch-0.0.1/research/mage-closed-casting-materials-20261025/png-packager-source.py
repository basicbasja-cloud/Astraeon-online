"""Losslessly package an unpublished pilot capture with stable pose/pixel ID.

Only untracked research captures are accepted. Preserve every alpha, visible
RGB and non-IDAT PNG chunk. Clear only RGB beneath alpha zero. Archive the raw
capture receipt and record every old/new image digest before publishing recipes.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from compact_unused_guide_cache import repack


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(receipt, pixels):
    keys = ['rig_sha256','source_skeleton_sha256','implementation_sha256','actor_scale','leg_scale','bone_map','weapon']
    result = {key:receipt[key] for key in keys}
    result['views'] = {}
    for direction, view in receipt['views'].items():
        result['views'][direction] = {'camera':view['camera'],'frames':[
            {'pose':{key:value for key,value in row.items() if key!='image_sha256'},
             'visible_rgba_sha256':pixels[direction,row['index']]}
            for row in view['frames']]}
    return sha(json.dumps(result,sort_keys=True,separators=(',',':')).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide',type=Path,required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    guide = args.guide.resolve()
    relative = guide.relative_to(root/'authoring/characters/factory-v3/patch-0.0.1/research')
    tracked = subprocess.check_output(['git','ls-files','--',str(guide.relative_to(root))],cwd=root,text=True)
    if tracked.strip():
        raise ValueError('Refuse to repackage a published/tracked capture')
    path = guide/'pilot-receipt.json'
    raw_receipt = path.read_bytes()
    receipt = json.loads(raw_receipt)
    if receipt.get('png_packaging') or (guide/'capture-before-png-packaging.json').exists():
        raise ValueError('Capture has already entered PNG packaging')
    if receipt['implementation_sha256']!=sha((guide/'renderer-source.py').read_bytes()):
        raise ValueError('Capture implementation snapshot differs')
    original = copy.deepcopy(receipt)
    for direction,view in receipt['views'].items():
        for row in view['frames']:
            image = guide/direction/f"{row['index']:03d}.png"
            if sha(image.read_bytes())!=row['image_sha256']:
                raise ValueError('Capture changed before packaging')
    (guide/'capture-before-png-packaging.json').write_bytes(raw_receipt)
    records,pixels = [],{}
    for direction,view in receipt['views'].items():
        for row in view['frames']:
            image = guide/direction/f"{row['index']:03d}.png"
            raw = image.read_bytes()
            packed,proof = repack(raw)
            after = np.array(Image.open(io.BytesIO(packed)).convert('RGBA'))
            after[after[:,:,3]==0] = 0
            pixel_hash = sha(after.tobytes())
            if pixel_hash!=proof['canonical_pixel_sha256']:
                raise ValueError('Visible capture identity changed')
            if packed!=raw:
                temporary = image.with_suffix('.packing.tmp')
                temporary.write_bytes(packed)
                temporary.replace(image)
            records.append({'image':str(image.relative_to(guide)),
                            'before_sha256':sha(raw),'after_sha256':sha(packed),
                            'bytes_before':len(raw),'bytes_after':len(packed),**proof})
            row['image_sha256'] = sha(packed)
            pixels[direction,row['index']] = pixel_hash
            (guide/'png-packaging-progress.json').write_text(json.dumps(records,indent=2)+'\n')
    before_id,after_id = identity(original,pixels),identity(receipt,pixels)
    if before_id!=after_id:
        raise ValueError('Pose/camera identity changed')
    result = {'status':'EXACT_POSE_VISIBLE_RGBA_ALPHA_AND_PNG_METADATA',
              'implementation_sha256':sha(Path(__file__).read_bytes()),
              'png_codec_sha256':sha(Path(__file__).with_name('compact_unused_guide_cache.py').read_bytes()),
              'original_receipt_sha256':sha(raw_receipt),'stable_pose_visible_identity':before_id,
              'files':records,'bytes_before':sum(r['bytes_before']for r in records),
              'bytes_after':sum(r['bytes_after']for r in records),
              'published_captures_modified':False,'visible_rgb_or_alpha_changed':False,
              'non_idat_metadata_changed':False}
    (guide/'png-packaging.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt['png_packaging'] = {key:value for key,value in result.items() if key!='files'}
    temporary = path.with_suffix('.packing.tmp')
    temporary.write_text(json.dumps(receipt,indent=2)+'\n')
    temporary.replace(path)
    (guide/'png-packager-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'capture':str(relative),'images':len(records),
                      'saved_bytes':result['bytes_before']-result['bytes_after'],
                      'pose_and_visible_pixels_unchanged':True}))


if __name__=='__main__':
    main()
