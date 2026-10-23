"""Map retained Swordsman art through its documented cameras and root tracks.

One isotropic camera scale per action; frame translations use source root travel,
never painted figure bounds. All core pixels are sampled once from the master.
This retains an explicit legacy source contract, not current paint-job coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial.transform import Rotation
from scipy.ndimage import binary_dilation

from build_fixed_grid_sequence_review import gif

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'authoring/characters/factory-v3/patch-0.0.1'
CATALOG = ROOT/'authoring/characters/factory-v3/configs/layered_action_catalog.json'
ROLES = ['BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']


def camera_mapping(source_ortho, source_root, target_ortho, target_root,
                   source_size=512, target_size=768, root_delta=(0., 0.)):
    scale = source_ortho*target_size/(target_ortho*source_size)
    if not np.isfinite(scale) or scale <= 0: raise ValueError('Invalid camera scale')
    offset = np.asarray(target_root)-scale*(np.asarray(source_root)+np.asarray(root_delta))
    return scale, offset


def root_screen_delta(world_delta, camera_rotation, ppm):
    rotation = Rotation.from_euler('xyz', camera_rotation).as_matrix()
    delta = np.asarray(world_delta)
    return np.array([delta@rotation[:,0], -delta@rotation[:,1]])*ppm


def transform(image, scale, offset, size=768, resample=Image.Resampling.BICUBIC):
    inverse = (1/scale, 0., -offset[0]/scale, 0., 1/scale, -offset[1]/scale)
    if image.mode == 'RGBA':
        out = image.convert('RGBa').transform((size,size), Image.Transform.AFFINE, inverse,
                                            resample).convert('RGBA')
        pixels = np.array(out); pixels[pixels[:,:,3] == 0] = 0
        return Image.fromarray(pixels)
    return image.transform((size,size), Image.Transform.AFFINE, inverse, resample)


def refine_blade_ownership(master, coverage, annotation):
    """Propose missed blade-outline ownership near existing manual blade pixels.

    Existing head and gripping glove are protected. This changes labels only;
    source artwork remains identical. A visual boundary review is still needed.
    """
    tip=np.array(annotation['weapon_tip'],dtype=float);guard=np.array(annotation['weapon_guard'],dtype=float)
    grip=np.array(annotation['weapon_grip'],dtype=float);axis=tip-guard;length=np.linalg.norm(axis)
    if length<8: return coverage,0
    axis/=length;yy,xx=np.indices((master.height,master.width));dx=xx-guard[0];dy=yy-guard[1]
    along=dx*axis[0]+dy*axis[1];across=np.abs(dx*axis[1]-dy*axis[0])
    scope=(along>=-2)&(along<=length+3)&(across<=max(4,min(9,length*.085)))
    weapon=np.array(coverage[2])>0;head=np.array(coverage[1])>0;body=np.array(coverage[0])>0
    protected=(xx-grip[0])**2+(yy-grip[1])**2<=9**2
    additions=binary_dilation(weapon,iterations=3)&scope&body&~head&~protected
    alpha=np.array(master.getchannel('A'));updated=list(coverage)
    w=np.array(updated[2]);w[additions]=alpha[additions];b=np.array(updated[0]);b[additions]=0
    updated[0]=Image.fromarray(b);updated[2]=Image.fromarray(w)
    return updated,int(additions.sum())


def register(cleaned, output, verify_existing=False):
    if output.exists() and not verify_existing: raise ValueError('Choose a fresh destination')
    if verify_existing and not (output/'receipt.json').is_file(): raise ValueError('No complete existing review to verify')
    config = json.loads((BASE/'factory.json').read_text())
    catalog = json.loads(CATALOG.read_text())
    ledger=json.loads((BASE/'ledger.json').read_text())
    target=ledger['guide_jobs'][ledger['action_guide_bindings']['Swordsman/BasicAttack']]
    author = config['canvas']['authoring'][0]; root = config['canvas']['authoring_root']
    receipt = json.loads((cleaned/'receipt.json').read_text())
    for relative, digest in receipt['baseline_files'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != digest:
            raise ValueError('Preserved baseline changed: '+relative)
    target_capture = json.loads((BASE/'guides'/target['id']/'manifest.json').read_text())
    if hashlib.sha256((ROOT/catalog['source_path']).read_bytes()).hexdigest() != catalog['source_sha256']:
        raise ValueError('Preserved motion source differs')
    output.mkdir(parents=True,exist_ok=verify_existing); records = []; verified_images=0
    for name, spec in catalog['actions'].items():
        original = ROOT/spec['directory']; source = cleaned/name
        timing = json.loads((original/'assembly-audit.json').read_text())['durations_ms']
        if name == 'BasicAttack':
            guide = json.loads((original/'source-guides/manifest.json').read_text())
            clips = {c['clip']: c for c in guide['clips']}
        view_previews = {}
        for direction in catalog['directions']:
            annotations=json.loads((original/direction/'annotations.generated.json').read_text())['frames']
            if name == 'BasicAttack':
                clip = clips[direction]; camera = clip['camera']; ortho = camera['ortho_scale']
                native_root = np.array(clip['frames'][0]['landmarks']['root'])*.5
                rotation = guide['camera']['rotation']
                # Rotation in the old top-level manifest is its final SE view;
                # per-view yaw and the common six-metre camera radius define
                # each actual source camera, rather than reusing SE elsewhere.
                rotation = [np.arctan2(6.,3.1), 0., np.deg2rad(camera['yaw_degrees'])]
                # BasicAttack records have zero source root travel in all views.
                root_tracks = [np.zeros(2) for _ in range(16)]
                source_records = clip['frames']
                if any(np.linalg.norm(np.array(r['landmarks']['root'])*.5-native_root) > .001 for r in source_records):
                    raise ValueError('BasicAttack has unhandled source root travel')
            else:
                g = json.loads((ROOT/spec['guides']/direction/'manifest.json').read_text())
                camera = g['camera']; ortho = camera['scale']; rotation = camera['rotation']
                native_root = np.array(camera['initial_root_pixel'])*.5
                packing = json.loads((original/direction/'assembly.json').read_text())['frames']
                source_records = [g['frames'][p['source_frame']] for p in packing]
                root_tracks = [root_screen_delta(r['root_motion_delta'], rotation, 512/ortho) for r in source_records]
            target_rotation = target_capture['views'][direction]['camera']['rotation']
            orientation_error = np.abs(Rotation.from_euler('xyz',rotation).as_matrix()-Rotation.from_euler('xyz',target_rotation).as_matrix()).max()
            if orientation_error > 1e-5: raise ValueError('Camera orientations differ; a 2D viewport transform is insufficient')
            previews = []; entries = []
            for i in range(16):
                scale, offset = camera_mapping(ortho, native_root, target['ortho_scale'], root,
                                               target_size=author, root_delta=root_tracks[i])
                master = Image.open(source/direction/'Master'/f'{i:03d}.png').convert('RGBA')
                bounds = master.getbbox()
                corners = np.array([[bounds[0],bounds[1]],[bounds[2],bounds[3]]])*scale+offset
                if corners.min() < 2 or corners.max() > author-2: raise ValueError('Mapped source artwork would clip')
                canonical = transform(master, scale, offset, author)
                coverage = [Image.open(source/direction/r/f'{i:03d}.png').getchannel('A') for r in ROLES[:3]]
                coverage,weapon_refinement=refine_blade_ownership(master,coverage,annotations[i])
                hand = np.array(Image.open(original/direction/'WeaponHandOccluder'/f'{i:03d}.png').getchannel('A'))>0
                body = np.array(coverage[0]); hand &= body>0
                hand_alpha = np.where(hand, body, 0).astype(np.uint8)
                body[hand] = 0; coverage[0] = Image.fromarray(body); coverage.append(Image.fromarray(hand_alpha))
                weights = np.stack([np.array(transform(c, scale, offset, author)) for c in coverage])
                owner = weights.argmax(axis=0); pixels = np.array(canonical); parts = {}
                for j, role in enumerate(ROLES):
                    part = pixels.copy(); part[owner != j] = 0; parts[role] = Image.fromarray(part)
                composed = Image.new('RGBA', canonical.size)
                for role in ROLES: composed.alpha_composite(parts[role])
                if composed.tobytes() != canonical.tobytes(): raise ValueError('Canonical recomposition differs')
                for role in ['WeaponLightBack','WeaponLightFront']:
                    parts[role] = transform(Image.open(original/direction/role/f'{i:03d}.png').convert('RGBA'), scale, offset, author)
                for role, image in {'Master': canonical, **parts}.items():
                    folder = output/name/direction/role; folder.mkdir(parents=True,exist_ok=True)
                    path=folder/f'{i:03d}.png'
                    if verify_existing:
                        if not path.is_file() or Image.open(path).convert('RGBA').tobytes()!=image.tobytes():
                            raise ValueError('Existing review differs from recomputed source transform: '+str(path))
                        verified_images+=1
                    else:image.save(path)
                full = Image.new('RGBA', canonical.size)
                for role in ['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon']:
                    full.alpha_composite(parts[role])
                previews.append(full.resize((240,240),Image.Resampling.LANCZOS))
                mapped_root = scale*(native_root+root_tracks[i])+offset
                entries.append({'index': i, 'source_action': source_records[i].get('action',source_records[i].get('segment')),
                                'source_frame': source_records[i]['source_frame'], 'camera_scale': scale,
                                'source_root_screen_delta': root_tracks[i].tolist(), 'canvas_translation': offset.tolist(),
                                'blade_outline_pixels_reassigned_to_weapon':weapon_refinement,
                                'mapped_root': mapped_root.tolist(), 'root_error_px': float(np.linalg.norm(mapped_root-root)),
                                'recomposition_mismatch_pixels': 0})
            view_previews[direction] = previews
            if not verify_existing:
                gif(previews, output/name/f'{direction}-normal-with-trail.gif', timing)
                gif(previews, output/name/f'{direction}-slow-with-trail.gif', [t*3 for t in timing])
            records.append({'action': name, 'direction': direction, 'source_camera': camera,
                            'source_target_orientation_matrix_max_error': float(orientation_error),
                            'source_root_at_native_512': native_root.tolist(), 'frames': entries})
        combined = []
        for i in range(16):
            image = Image.new('RGBA',(960,240))
            for j,d in enumerate(catalog['directions']): image.alpha_composite(view_previews[d][i],(j*240,0))
            combined.append(image)
        if not verify_existing:gif(combined, output/name/'four-directions-with-trail.gif', timing)
    report = {'status': 'PRESERVED_ART_CANONICAL_SOURCE_CAMERA_REVIEW_NOT_RUNTIME_ADMISSION',
              'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'canonical_canvas': [author,author], 'canonical_root': root,
              'target_ortho_scale': target['ortho_scale'], 'frames': records,
              'root_policy': 'Remove only recorded source root travel; all body articulation and all layers share the same source-derived transform.',
              'pose_bbox_fitting': False, 'anatomical_warp': False,
              'independent_part_color_resampling': False, 'semantic_mask_review_required': True,
              'source_sampling_matches_current_patch_jobs': False, 'patch_coverage_increment': 0,
              'source_art_overwritten': False, 'runtime_admitted': False}
    if verify_existing:
        report['verified_existing_images']=verified_images
        report['original_receipt_sha256']=hashlib.sha256((output/'receipt.json').read_bytes()).hexdigest()
    (output/('verification-receipt.json'if verify_existing else'receipt.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cleaned',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    p.add_argument('--verify-existing',action='store_true')
    a = p.parse_args(); r = register(a.cleaned,a.output,a.verify_existing)
    print(json.dumps({'views':len(r['frames']), 'poses':sum(len(v['frames']) for v in r['frames']),
                      'max_root_error_px':max(f['root_error_px']for v in r['frames']for f in v['frames'])}))
