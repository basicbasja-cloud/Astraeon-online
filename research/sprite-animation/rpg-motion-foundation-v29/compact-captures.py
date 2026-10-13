#!/usr/bin/env python3
"""Lossless storage of real decoded frames, verified for every RGBA pixel.
Native timestamps/order/holds remain intact. Original PNGs are kept in ignored
local cache. This changes file encoding, never pose, scale, crop or clock.
"""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
records=[]
for folder in sorted((ROOT/'captures').glob('kaykit-preview-*')):
 report=json.loads((folder/'capture.json').read_text())
 if report.get('storage_encoding'):continue
 for frame in report['frames']:
  original=folder/frame['file'];webp=original.with_suffix('.webp')
  with Image.open(original) as image:
   rgba=image.convert('RGBA');pixels=rgba.tobytes();rgba.save(webp,format='WEBP',lossless=True,exact=True,method=6)
  with Image.open(webp) as decoded:
   if decoded.convert('RGBA').tobytes()!=pixels:raise ValueError('Lossless pixel mismatch')
  frame.update(original_decoded_png_sha256=frame['sha256'],rgba_pixels_sha256=hashlib.sha256(pixels).hexdigest(),sha256=hashlib.sha256(webp.read_bytes()).hexdigest(),file=webp.name)
  cache=ROOT/'local-cache'/'native-capture-png'/folder.name/original.name;cache.parent.mkdir(parents=True,exist_ok=True);original.rename(cache)
 report.update(storage_encoding='Lossless WebP, exact RGBA comparison against every original decoded PNG; no image transform',source_capture_tool='skills/modular-eight-direction-sprites/scripts/capture-reference.py')
 (folder/'capture.json').write_text(json.dumps(report,indent=2)+'\n')
 records.append({'capture':folder.name,'frames':len(report['frames']),'all_rgba_pixels_equal':True,'duration_ms':report['duration_ms'],'all_native_clocks_preserved':True})
(ROOT/'capture-storage-verification.json').write_text(json.dumps({'schema':'lossless-capture-storage-v1','captures':records},indent=2)+'\n')
print(json.dumps(records))
