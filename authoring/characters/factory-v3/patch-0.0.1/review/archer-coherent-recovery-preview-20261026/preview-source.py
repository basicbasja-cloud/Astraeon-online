"""Render a fixed-viewport review from existing complete painted masters.

No asset fitting, interpolation, mask inference, or acceptance is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(masters, recipe, output):
    if output.exists():
        raise ValueError('Use a fresh review output')
    expected = tuple(recipe['source_size'])
    left, top, right, bottom = recipe['viewport']
    if not (0 <= left < right <= expected[0] and 0 <= top < bottom <= expected[1]):
        raise ValueError('Review viewport is outside the source canvas')
    if recipe['frame_count'] < 2 or recipe['sample_ms'] <= 0:
        raise ValueError('Invalid review sample count or timing')
    width, height = right-left, bottom-top
    output.mkdir(parents=True)
    records = []
    for identity in recipe['identities']:
        previews = []
        for index in range(recipe['frame_count']):
            canvas = Image.new('RGB', (width*len(recipe['directions']), height+28), '#dcdcd8')
            draw = ImageDraw.Draw(canvas)
            for column, view in enumerate(recipe['directions']):
                path = masters/identity/view/'Master'/f'{index:03d}.png'
                image = Image.open(path).convert('RGBA')
                if image.size != expected:
                    raise ValueError('Mixed source canvases are forbidden')
                cropped = image.crop((left, top, right, bottom))
                canvas.paste(cropped, (column*width, 28), cropped)
                draw.text((column*width+5, 8), f'{identity} {view} | {index:02d} | DRAFT', fill='#222')
                records.append({'identity': identity, 'direction': view, 'index': index,
                                'source_sha256': sha(path)})
            previews.append(canvas)
        for suffix, multiplier in [('normal', 1), ('slow', 3)]:
            timings = [recipe['sample_ms']*multiplier]*(len(previews)-1)+[recipe['terminal_hold_ms']*multiplier]
            previews[0].save(output/f'{identity}-{suffix}.gif', save_all=True,
                             append_images=previews[1:], duration=timings, loop=0, disposal=2)
        rows = recipe['contact_indices']
        contact = Image.new('RGB', (previews[0].width, previews[0].height*len(rows)))
        for row, index in enumerate(rows):
            contact.paste(previews[index], (0, row*previews[0].height))
        contact.save(output/f'{identity}-key-poses.jpg', quality=97)
    receipt = {'status': 'FIXED_VIEWPORT_REVIEW_NOT_ANIMATION_ACCEPTANCE',
               'recipe': recipe, 'frames': records, 'source_pixels_moved_or_fitted': False,
               'implementation_sha256': sha(Path(__file__)),
               'note': 'GIF repeats a one-shot with an inspection hold; not a certified seamless cycle.'}
    (output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (output/'preview-source.py').write_bytes(Path(__file__).read_bytes())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--masters', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = render(args.masters, json.loads(args.recipe.read_text()), args.output)
    print(json.dumps({'status': receipt['status'], 'frames': len(receipt['frames'])}))


if __name__ == '__main__':
    main()
