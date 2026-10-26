"""Reuse one illustrated cutout pose for a bounded native breathing/hold loop.

Native projected joints drive one shared inverse deformation field. No camera,
silhouette fitting, frame-wise image generation, or crossfading. This is limited
to small motions and refuses folds, excessive deformation, bent staff axes and
bad native loop seams. Exact visible composition is not hidden-surface approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.interpolate import RBFInterpolator
from scipy.spatial.transform import Rotation

ROLES = ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']
JOINTS = ['Hips','Chest','Head']+[
    name+'.'+side for side in ['L','R']
    for name in ['UpperArm','Forearm','Hand','Shin','Foot','Toe']
    if name!='Hand' or side!='R']
SIZE = 1536
SPACING = 8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def project(point,camera):
    local = Rotation.from_euler('xyz',camera['rotation']).as_matrix().T@(np.asarray(point)-camera['location'])
    return (local[:2]/camera['ortho_scale']*np.array([1,-1])+.5)*SIZE


def controls(row,camera):
    palm,tip = [project(row[key],camera) for key in ['grip_world','staff_tip_world']]
    boundary = [[0,0],[768,0],[1536,0],[0,768],[1536,768],[0,1536],[768,1536],[1536,1536]]
    return np.vstack([[row['landmarks'][key] for key in JOINTS],
                      [(1-t)*palm+t*tip for t in np.linspace(0,1,9)],boundary])


def inverse_field(source,target,size=SIZE,spacing=SPACING):
    if source.shape!=target.shape or source.ndim!=2 or source.shape[1]!=2 or not np.isfinite([source,target]).all():
        raise ValueError('Finite matching anatomical controls required')
    if size%spacing:
        raise ValueError('Grid must divide the canvas')
    interpolator = RBFInterpolator(target/size,(source-target)/size,kernel='thin_plate_spline',degree=1)
    yy,xx = np.mgrid[0:size+1:spacing,0:size+1:spacing]
    grid = np.stack([xx,yy],axis=-1)
    field = interpolator(grid.reshape(-1,2)/size).reshape(grid.shape)*size
    dxdy,dxdx = np.gradient(field[:,:,0],spacing)
    dydy,dydx = np.gradient(field[:,:,1],spacing)
    determinant = (1+dxdx)*(1+dydy)-dxdy*dydx
    sampled = np.stack([ndimage.map_coordinates(field[:,:,axis],
                       [target[:,1]/spacing,target[:,0]/spacing],order=1) for axis in range(2)],axis=1)
    return field,{'maximum_inverse_displacement_px':float(np.linalg.norm(field,axis=2).max()),
                  'minimum_jacobian':float(determinant.min()),'maximum_jacobian':float(determinant.max()),
                  'maximum_control_interpolation_error_px':float(np.linalg.norm(target+sampled-source,axis=1).max())},interpolator


def resample_rgba(image,source_y,source_x):
    pixels = np.array(image.convert('RGBA')).astype(np.float32)
    pixels[:,:,:3] *= pixels[:,:,3:4]/255
    sampled = np.stack([ndimage.map_coordinates(pixels[:,:,c],[source_y,source_x],order=1,mode='constant',cval=0,prefilter=False)
                        for c in range(4)],axis=-1)
    alpha = sampled[:,:,3:4]
    sampled[:,:,:3] = np.divide(sampled[:,:,:3]*255,alpha,out=np.zeros_like(sampled[:,:,:3]),where=alpha>0)
    values = np.rint(np.clip(sampled,0,255)).astype('uint8')
    values[values[:,:,3]==0] = 0
    return Image.fromarray(values)


def partition(master,part_alphas,source_y,source_x):
    scores = np.stack([ndimage.map_coordinates(alpha,[source_y,source_x],order=1,mode='constant',cval=0,prefilter=False)
                       for alpha in part_alphas])
    owner = scores.argmax(axis=0)
    pixels = np.array(master)
    parts = []
    for role in range(len(part_alphas)):
        result = np.zeros_like(pixels)
        result[owner==role] = pixels[owner==role]
        parts.append(Image.fromarray(result))
    combined = Image.new('RGBA',master.size)
    for part in parts:
        combined.alpha_composite(part)
    if combined.tobytes()!=master.tobytes():
        raise ValueError('Derived parts do not reconstruct master')
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['master','parts','base-guide','target-guide','target-skeleton','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--base-index',type=int,default=0)
    parser.add_argument('--direction',default='NE')
    parser.add_argument('--repository-root',type=Path,default=Path.cwd())
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new bounded reuse output')
    root = args.repository_root.resolve()
    base = json.loads((args.base_guide/'pilot-receipt.json').read_text())
    target = json.loads((args.target_guide/'pilot-receipt.json').read_text())
    for key in ['rig_sha256','bone_map','actor_scale','leg_scale','weapon']:
        if base[key]!=target[key]:
            raise ValueError('Incompatible canonical rigs/scale/prop: '+key)
    if target['weapon']!='staff' or target['source_skeleton_sha256']!=sha(args.target_skeleton):
        raise ValueError('Expected the verified native held-staff skeleton')
    skeleton = json.loads(args.target_skeleton.read_text())
    manifest_path = root/'authoring/characters/factory-v3/patch-0.0.1/guides'/skeleton['source_job']/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if sha(manifest_path)!=skeleton['source_manifest_sha256'] or not manifest['job']['loop']:
        raise ValueError('Target is not a pinned native cyclic action')
    a,b = [capture['views'][args.direction] for capture in [base,target]]
    if a['camera']!=b['camera']:
        raise ValueError('Camera/framing changes are not supported')
    base_row = a['frames'][args.base_index]
    source = controls(base_row,a['camera'])
    master = Image.open(args.master).convert('RGBA')
    if master.size!=(SIZE,SIZE):
        raise ValueError('Expected the native 1536px illustrated canvas')
    paths = {role:args.parts/role/f'{args.base_index:03d}.png' for role in ROLES}
    images = [Image.open(path).convert('RGBA') for path in paths.values()]
    combined = Image.new('RGBA',master.size)
    for part in images:
        combined.alpha_composite(part)
    if combined.tobytes()!=master.tobytes():
        raise ValueError('Base cutouts do not exactly reconstruct the illustration')
    inputs = {str(path):sha(path) for path in [args.master,*paths.values(),
              args.base_guide/'pilot-receipt.json',args.target_guide/'pilot-receipt.json',args.target_skeleton,manifest_path]}
    args.output.mkdir(parents=True)
    records,fields,preview = [],[],[]
    yy,xx = np.mgrid[:SIZE,:SIZE].astype(np.float32)
    part_alphas = [np.array(im.getchannel('A')).astype(np.float32) for im in images]
    for row in b['frames']:
        index = row['index']
        destination = controls(row,b['camera'])
        field,diagnostic,interpolator = inverse_field(source,destination)
        palm,tip = [project(row[key],b['camera']) for key in ['grip_world','staff_tip_world']]
        bp,bt = [project(base_row[key],a['camera']) for key in ['grip_world','staff_tip_world']]
        t = np.linspace(0,1,101)[:,None]
        axis = (1-t)*palm+t*tip
        expected = (1-t)*bp+t*bt
        staff_error = float(np.linalg.norm(axis+interpolator(axis/SIZE)*SIZE-expected,axis=1).max())
        if (diagnostic['maximum_inverse_displacement_px']>32 or diagnostic['minimum_jacobian']<.75
            or diagnostic['maximum_jacobian']>1.35 or diagnostic['maximum_control_interpolation_error_px']>.75
            or staff_error>.75):
            raise ValueError('Native action exceeds bounded hold deformation: '+json.dumps(diagnostic))
        fields.append(field)
        dx,dy = [ndimage.map_coordinates(field[:,:,axis],[((yy+.5)/SPACING),((xx+.5)/SPACING)],order=1,prefilter=False).astype(np.float32)
                 for axis in range(2)]
        source_x,source_y = xx+dx,yy+dy
        derived = resample_rgba(master,source_y,source_x)
        parts = partition(derived,part_alphas,source_y,source_x)
        hashes = {}
        for role,image in zip(['Master',*ROLES],[derived,*parts]):
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            path = folder/f'{index:03d}.png'
            image.save(path)
            hashes[role] = sha(path)
        bg = Image.new('RGBA',master.size,'#eee');bg.alpha_composite(derived)
        preview.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
        records.append({'index':index,'source_action':row['source_action'],'source_frame':row['source_frame'],
                        'master_sha256':hashes.pop('Master'),'part_sha256':hashes,
                        'deformation':diagnostic,'maximum_staff_axis_inverse_error_px':staff_error,
                        'recomposition_changed_pixels':0})
        print('BOUNDED_NATIVE_HOLD_POSE',index,flush=True)
    seam = float(np.linalg.norm(fields[-1]-fields[0],axis=2).max())
    adjacent = max(float(np.linalg.norm(x-y,axis=2).max()) for x,y in zip(fields,fields[1:]))
    if seam>1.25*adjacent+1e-6:
        raise ValueError('Native cyclic seam is larger than ordinary motion')
    if any(sha(path)!=digest for path,digest in inputs.items()):
        raise ValueError('Frozen reuse input changed during production')
    preview[0].save(args.output/'native-hold-loop-draft.gif',save_all=True,append_images=preview[1:],duration=80,loop=0)
    receipt = {'status':'BOUNDED_NATIVE_HOLD_REUSE_NOT_ADMITTED','implementation_sha256':sha(__file__),
               'direction':args.direction,'source_template_pose':args.base_index,'input_sha256':inputs,
               'one_illustrated_template':True,'per_frame_generation':False,'whole_character_bbox_fit':False,
               'deformation_policy':{'maximum_flow_native_px':32,'jacobian_range':[.75,1.35],
                                     'maximum_control_error_native_px':.75,'maximum_staff_error_native_px':.75},
               'loop_evidence':{'checked':True,'native_source_loop':True,'field_seam_max_px':seam,
                                'largest_adjacent_field_change_px':adjacent,'closing_pose_duplicated':False},
               'frames':records,'semantic_cutouts_approved':False,'hidden_surfaces_authored':False,
               'runtime_admitted':False,'full_character_complete':False}
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (args.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'poses':len(records),'native_loop_seam_px':seam,'largest_adjacent_motion_px':adjacent,'runtime_admitted':False}))


if __name__=='__main__':
    main()
