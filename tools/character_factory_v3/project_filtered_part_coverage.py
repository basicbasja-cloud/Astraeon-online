"""Project a raw part's alpha support through the exact fixed master filters.

Nearest-neighbour labels can leave the original part's filtered edge in the
remainder. This helper proposes ownership for every contributing source-part
pixel. Mixed material boundaries still require semantic review/underpainting.
It does not transform body parts independently or approve a runtime asset.
"""
import math
import numpy as np
from PIL import Image


def project_coverage(source, mask, viewport, scale, translation, integer_delta,
                     canvas_size=(768, 768)):
    source = source.convert('RGBA')
    mask = np.asarray(mask)
    if mask.shape != (source.height, source.width) or mask.dtype != np.bool_:
        raise ValueError('Expected a native boolean raw-part mask')
    if len(viewport) != 4 or any(not isinstance(v, int) for v in viewport):
        raise ValueError('Expected integer fixed viewport')
    left, top, right, bottom = viewport
    if not 0 <= left < right <= canvas_size[0] or not 0 <= top < bottom <= canvas_size[1]:
        raise ValueError('Viewport is outside the canonical canvas')
    if not math.isfinite(scale) or scale <= 0 or len(translation) != 2 or not np.isfinite(translation).all():
        raise ValueError('Invalid shared fit')
    delta = np.asarray(integer_delta, dtype=float)
    if delta.shape != (2,) or not np.isfinite(delta).all() or not np.equal(delta, np.rint(delta)).all():
        raise ValueError('Registration must be a whole-frame integer translation')
    pixels = np.array(source)
    if pixels[:, :, 3].min() == 255:
        raise ValueError('Opaque source requires the original matte preprocessing first')
    pixels[~mask] = 0
    part = Image.fromarray(pixels)
    # Same premultiplied EXTENT and AFFINE operations as fixed master normalization.
    cell = part.convert('RGBa').transform(
        (right - left, bottom - top), Image.Transform.EXTENT,
        (0, 0, source.width, source.height), Image.Resampling.BICUBIC).convert('RGBA')
    placed = Image.new('RGBA', canvas_size)
    placed.alpha_composite(cell, (left, top))
    tx, ty = translation
    py, px = np.nonzero(np.array(placed.getchannel('A')))
    if len(px):
        # Conservative cubic-filter support bounds; do not silently crop a part.
        bounds = [(px.min()-2)*scale+tx, (py.min()-2)*scale+ty,
                  (px.max()+2)*scale+tx, (py.max()+2)*scale+ty]
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] >= canvas_size[0] or bounds[3] >= canvas_size[1]:
            raise ValueError('Shared fit would clip filtered part support')
    fitted = placed.convert('RGBa').transform(
        canvas_size, Image.Transform.AFFINE,
        (1 / scale, 0, -tx / scale, 0, 1 / scale, -ty / scale),
        Image.Resampling.BICUBIC).convert('RGBA')
    alpha = np.array(fitted.getchannel('A'))
    ys, xs = np.nonzero(alpha)
    dx, dy = map(int, integer_delta)
    if len(xs) and ((xs + dx < 0).any() or (xs + dx >= canvas_size[0]).any()
                    or (ys + dy < 0).any() or (ys + dy >= canvas_size[1]).any()):
        raise ValueError('Registration would clip a visible filtered part')
    registered = Image.new('L', canvas_size)
    registered.paste(fitted.getchannel('A'), (dx, dy))
    return np.asarray(registered) > 0
