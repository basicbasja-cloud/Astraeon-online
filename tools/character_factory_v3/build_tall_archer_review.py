"""Extract the eight coherent Archer sheets into reproducible review frames.

This does not register anatomy, assign semantic parts, or admit runtime art.
All frames use the same recorded viewport, with no individual figure fitting.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from normalize_fixed_viewport_batch import normalize_batch


VIEWS = ['SW', 'NW', 'NE', 'SE']
SEXES = ['male', 'female']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(source, output):
    if output.exists():
        raise ValueError('Use a fresh review destination')
    recipe_path = source/'extraction-recipe.json'
    recipe = json.loads(recipe_path.read_text())
    if recipe['source_pose_indices'] != list(range(16)):
        raise ValueError('Expected sixteen actual source poses')
    output.mkdir(parents=True)
    groups, records = {}, []
    for sex in SEXES:
        for view in VIEWS:
            raw = source/f'{sex}-{view}-raw.png'
            frames, receipt = normalize_batch(Image.open(raw), recipe,
                                               white_edge_unmatting=True)
            if receipt['production_blockers']:
                raise ValueError(f'{sex}/{view} touches the fixed viewport')
            directory = output/sex/view/'Master'
            directory.mkdir(parents=True)
            for index, frame in enumerate(frames):
                frame.save(directory/f'{index:03d}.png')
            request = source/f'generation-request-{sex}-{view}.json'
            receipt.update({'source_sha256': sha(raw),
                            'generation_request_sha256': sha(request),
                            'recipe_sha256': sha(recipe_path),
                            'complete_painted_body_preserved': True,
                            'independent_limb_assembly': False})
            (directory.parent/'extraction-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
            groups[sex, view] = frames
            records.append({'sex': sex, 'view': view, 'raw': str(raw),
                            'source_sha256': sha(raw), 'request_sha256': sha(request),
                            'frames': [{'index': i, 'sha256': sha(directory/f'{i:03d}.png')}
                                       for i in range(16)]})
    left, top, right, bottom = recipe['viewport']
    width, height = right-left, bottom-top
    for sex in SEXES:
        animation = []
        for i in range(16):
            canvas = Image.new('RGB', (width*4, height+28), '#dcdcd8')
            draw = ImageDraw.Draw(canvas)
            for column, view in enumerate(VIEWS):
                frame = groups[sex, view][i].crop((left, top, right, bottom))
                canvas.paste(frame, (column*width, 28), frame)
                draw.text((column*width+8, 8), f'{sex} {view} | {i:02d} | DRAFT', fill='#222222')
            animation.append(canvas)
        for name, speed in [('normal', 1), ('slow', 3)]:
            animation[0].save(output/f'{sex}-four-views-{name}.gif', save_all=True,
                append_images=animation[1:], duration=[80*speed]*15+[240*speed],
                loop=0, disposal=2)
        contact = Image.new('RGB', (width*4, (height+28)*4), '#dcdcd8')
        for row, i in enumerate([0, 6, 10, 15]):
            contact.paste(animation[i], (0, row*(height+28)))
        contact.save(output/f'{sex}-key-poses.jpg', quality=95)
    manifest = {'status': 'COHERENT_TALL_PAINT_REVIEW_NOT_RUNTIME_ADMITTED',
                'sheets': 8, 'frames': 128, 'views': VIEWS, 'sexes': SEXES,
                'source_pose_registered': False, 'semantic_cutouts_approved': False,
                'smoothness_approved': False, 'complete_characters': 0,
                'uniform_review_sample_duration_ms': 80,
                'terminal_review_hold_ms': 240,
                'preview_note': 'Repeated one-shot review; not a certified seamless loop.',
                'blockers': ['Painted root placement and source joint correspondence need correction.',
                             'Release pose 10 foreshortening needs local whole-frame repair.',
                             'First/last body art differs despite matching source body poses.',
                             'Head/weapon/hand boundaries and hidden surfaces are not approved.'],
                'implementation_sha256': sha(Path(__file__)), 'records': records}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (output/'extraction-recipe.json').write_bytes(recipe_path.read_bytes())
    (output/'review-builder-source.py').write_bytes(Path(__file__).read_bytes())
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = build(args.source, args.output)
    print(json.dumps({key: report[key] for key in ['status', 'sheets', 'frames']}))


if __name__ == '__main__':
    main()
