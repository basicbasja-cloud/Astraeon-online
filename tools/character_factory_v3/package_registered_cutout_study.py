"""Package manually annotated visible cutouts without moving or repainting pixels.

This produces an editable study, not hidden surfaces or a complete outfit rig.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw
from assemble_mesh2motion_paint_review import cut_white


def png_bytes(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('annotation', type=Path)
    args = parser.parse_args()
    specification = json.loads(args.annotation.read_text())
    root = args.annotation.parent
    source = root / specification['image']
    master, matte = cut_white(Image.open(source))
    if list(master.size) != specification['canvas']:
        raise ValueError('Annotation canvas differs from source; refusing implicit fit')
    output = root / 'editable-cutouts'
    output.mkdir(exist_ok=True)
    rgba = np.asarray(master)
    assigned = np.zeros(rgba.shape[:2], dtype=bool)
    layers = []
    for entry in specification['layers']:
        mask = Image.new('1', master.size)
        draw = ImageDraw.Draw(mask)
        for polygon in entry['polygons']:
            draw.polygon([tuple(point) for point in polygon], fill=1)
        selected = np.asarray(mask, dtype=bool) & ~assigned & (rgba[:, :, 3] > 0)
        pixels = np.zeros_like(rgba)
        pixels[selected] = rgba[selected]
        assigned |= selected
        layers.append((entry['name'], Image.fromarray(pixels)))
    rest = np.zeros_like(rgba)
    rest[~assigned] = rgba[~assigned]
    layers.append(('BodyOutfit_UNSEPARATED', Image.fromarray(rest)))
    composition = Image.new('RGBA', master.size)
    for name, layer in reversed(layers):
        composition.alpha_composite(layer)
        layer.save(output / (name + '.png'))
    mismatch = int(np.any(np.asarray(composition) != rgba, axis=2).sum())
    if mismatch:
        raise ValueError(f'Cutout reconstruction differs by {mismatch} pixels')
    master.save(output / 'master-transparent.png')
    image_xml = ET.Element('image', {'w': str(master.width), 'h': str(master.height), 'name': 'No-cloak visible-cutout STUDY'})
    stack = ET.SubElement(image_xml, 'stack')
    with zipfile.ZipFile(output / 'swordsman-no-cloak-study.ora', 'w') as archive:
        archive.writestr('mimetype', 'image/openraster', compress_type=zipfile.ZIP_STORED)
        for index, (name, layer) in enumerate(layers):
            filename = f'data/layer{index}.png'
            ET.SubElement(stack, 'layer', {'name': name, 'src': filename, 'opacity': '1.0', 'visibility': 'visible', 'composite-op': 'svg:src-over', 'x': '0', 'y': '0'})
            archive.writestr(filename, png_bytes(layer), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('stack.xml', ET.tostring(image_xml), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('mergedimage.png', png_bytes(composition), compress_type=zipfile.ZIP_DEFLATED)
    sheet = Image.new('RGB', (384 * len(layers), 420), '#ececec')
    draw = ImageDraw.Draw(sheet)
    for index, (name, layer) in enumerate(layers):
        thumb = layer.convert('RGBa').resize((384, 384), Image.Resampling.LANCZOS).convert('RGBA')
        sheet.paste(thumb, (384 * index, 30), thumb)
        draw.text((384 * index + 5, 8), name, fill='black')
    sheet.save(output / 'layer-review.png')
    report = {'status': 'EDITABLE_STUDY_NOT_MOTION_REGISTERED', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'canvas': list(master.size), 'layers': [name for name, _ in layers], 'recomposition_mismatched_pixels': mismatch, 'pixel_transform': 'none; disjoint original visible pixels on identical full canvases', 'matte': matte, 'limitations': ['Manual semantic boundaries require visual review.', 'Body and outfit remain combined, not independently replaceable.', 'No hidden surfaces have been invented.', 'Pose registration and animated continuity have not passed.']}
    (output / 'cutout-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
