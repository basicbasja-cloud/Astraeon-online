"""Compare painted staff motion with the captured native staff projection.

One frame-zero offset allows a different decorative crystal position. It is
fixed for the whole sequence. No per-frame fitting or image modification.
This is a motion diagnostic, not a grip/occlusion or final-art certificate.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial.transform import Rotation


def project(point,camera,size=1536):
    rotation = Rotation.from_euler('xyz',camera['rotation']).as_matrix()
    local = rotation.T@(np.asarray(point)-camera['location'])
    return (local[:2]/camera['ortho_scale']*np.array([1,-1])+.5)*size


def observed_crystal(image,head_y):
    pixels = np.array(image.convert('RGBA'))
    r,g,b = np.moveaxis(pixels[:,:,:3].astype(float),-1,0)
    yy,xx = np.indices(r.shape)
    mask = (pixels[:,:,3]>64)&(g>90)&(b>110)&(b>1.5*r)&(g>1.3*r)&(yy<head_y-50)
    labels,count = ndimage.label(mask,structure=np.ones((3,3)))
    if not count:
        raise ValueError('Missing observed staff crystal')
    areas = np.bincount(labels.ravel());areas[0]=0
    label = int(areas.argmax())
    if areas[label]<12:
        raise ValueError('Observed crystal too small')
    cy,cx = ndimage.center_of_mass(mask,labels,label)
    return np.array([cx,cy]),int(areas[label])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paint',type=Path,required=True)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--guide',type=Path)
    source.add_argument('--controls',type=Path,help='Canonical numeric pose export; does not claim image capture')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tolerance',type=float,default=12)
    args = parser.parse_args()
    source_path=args.controls if args.controls else args.guide/'pilot-receipt.json'
    capture = json.loads(source_path.read_text())
    if args.controls and capture.get('status')!='NUMERIC_CANONICAL_POSES_NOT_IMAGE_CAPTURE':
        raise ValueError('Expected frozen canonical numeric poses')
    if capture['weapon']!='staff' or args.tolerance<=0:
        raise ValueError('Staff capture and positive motion tolerance required')
    view = capture['views']['NE'];rows=[];offset=None
    for row in view['frames']:
        path = args.paint/f"{row['index']:03d}.png"
        with Image.open(path) as image:
            observed,area = observed_crystal(image,row['landmarks']['Head'][1])
        native = project(row['staff_tip_world'],view['camera'])
        if offset is None:
            offset = observed-native
        expected = native+offset
        error = float(np.linalg.norm(observed-expected))
        rows.append({'index':row['index'],'native_staff_tip':native.tolist(),
                     'observed_crystal':observed.tolist(),'crystal_pixels':area,
                     'expected_with_fixed_reference_offset':expected.tolist(),
                     'motion_error_native_px':error,'motion_gate_passed':error<=args.tolerance,
                     'paint_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {'status':'STAFF_MOTION_DIAGNOSTIC_NOT_GRIP_APPROVAL',
              'fixed_frame_zero_offset':offset.tolist(),'per_frame_fitting':False,
              'tolerance_native_px':args.tolerance,'frames':rows,
              'maximum_motion_error_native_px':max(r['motion_error_native_px'] for r in rows),
              'passed_poses':sum(r['motion_gate_passed'] for r in rows),
              'motion_gate_passed':all(r['motion_gate_passed'] for r in rows),
              'guide_receipt_sha256':None if args.controls else hashlib.sha256(source_path.read_bytes()).hexdigest(),
              'numeric_controls_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest()if args.controls else None,
              'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'runtime_admitted':False}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['motion_gate_passed','passed_poses','maximum_motion_error_native_px']}))


if __name__ == '__main__':
    main()
