"""Package a native guide replay without volatile PNG render metadata.

The input capture remains untouched. All decoded RGBA bytes, including RGB
under zero alpha, must survive. This is a reproducibility step, not art approval.
"""
import argparse
import hashlib
import io
import json
import shutil
from pathlib import Path

from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize_png(path):
    with Image.open(path) as image:
        if image.mode != 'RGBA':
            raise ValueError('Expected native RGBA guide frame')
        image.load()
        pixels = image.tobytes()
        size = image.size
    output = io.BytesIO()
    Image.frombytes('RGBA', size, pixels).save(output, format='PNG', compress_level=6)
    encoded = output.getvalue()
    with Image.open(io.BytesIO(encoded)) as restored:
        if restored.mode != 'RGBA' or restored.size != size or restored.tobytes() != pixels:
            raise ValueError('Guide packaging changed decoded RGBA bytes')
    return encoded, sha(pixels), list(size)


def seal(source, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output; no existing capture is overwritten')
    manifest_path = source / 'manifest.json'
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    count = manifest['frame_count']
    resolution = manifest['job']['resolution']
    if type(count) is not int or count < 1 or type(resolution) is not int or resolution < 1:
        raise ValueError('Invalid guide dimensions or coverage')
    if set(manifest['views']) != set(manifest['job']['directions']):
        raise ValueError('View coverage differs from the source job')
    paths = []
    for direction, view in manifest['views'].items():
        if direction not in {'S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE'}:
            raise ValueError('Unexpected guide direction')
        if len(view['frames']) != count:
            raise ValueError('Incomplete guide timeline')
        for index, record in enumerate(view['frames']):
            relative = f'{direction}/{index:03}.png'
            if record['frame'] != index or record['image'] != relative:
                raise ValueError('Guide frame/image mapping changed')
            path = source / relative
            if path.is_symlink():
                raise ValueError('Source frame must not be a symlink')
            # Validate every input before creating a destination.
            with Image.open(path) as image:
                image.load()
                if image.mode != 'RGBA' or image.size != (resolution, resolution):
                    raise ValueError('Source frame canvas changed')
                pixel_hash = sha(image.tobytes())
            paths.append((relative, path, pixel_hash))
    output.mkdir(parents=True, exist_ok=False)
    try:
        records = []
        for relative, path, expected_pixels in paths:
            encoded, pixel_hash, size = normalize_png(path)
            if pixel_hash != expected_pixels or size != [resolution, resolution]:
                raise ValueError('Source frame changed during packaging')
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encoded)
            records.append({'image': relative, 'rgba_sha256': pixel_hash,
                            'png_sha256': sha(encoded), 'canvas': size})
        if manifest_path.read_bytes() != manifest_bytes:
            raise ValueError('Source manifest changed during packaging')
        (output / 'manifest.json').write_bytes(manifest_bytes)
        receipt = {
            'status': 'REPRODUCIBLE_SOURCE_GUIDE_PACKAGE_NOT_ART_APPROVAL',
            'implementation_sha256': sha(Path(__file__).read_bytes()),
            'manifest_sha256': sha(manifest_bytes),
            'source_glb_sha256': manifest['job']['source_sha256'],
            'views': list(manifest['views']), 'frames': records,
            'decoded_rgba_changed': False, 'source_capture_modified': False,
            'world_pose_or_camera_changed': False, 'runtime_admitted': False,
            'policy': 'Remove PNG metadata only; preserve every RGBA byte, including hidden RGB.',
        }
        (output / 'capture-seal.json').write_text(json.dumps(receipt, indent=2) + '\n')
    except BaseException:
        # Only this exclusively created output is owned by the failed operation.
        shutil.rmtree(output)
        raise
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = seal(args.source, args.output)
    print(json.dumps({'status': result['status'], 'frames': len(result['frames'])}))
