#!/usr/bin/env python3
"""Export anatomy/shape/depth evidence from a verified rig build, outside that build.

This is the silver-scarf-A attack adapter, not an image-to-skeleton estimator.
Source technical proof and all resulting art/acting guides remain unapproved.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import shutil
import tempfile
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sprite_pipeline', HERE/'pipeline.py')
pipeline = importlib.util.module_from_spec(spec); spec.loader.exec_module(pipeline)


def export(root, output):
    root = root.resolve(); output = output.resolve()
    if output.exists() or output.is_relative_to(root): raise ValueError('Use a new output directory outside the immutable build root')
    source, receipt = pipeline.selected(root)
    manifest = pipeline.read(source/'rig-manifest.json'); guides = pipeline.read(source/'pose-guides.json')
    if manifest['rig_family'] != 'silver-scarf-A' or len(guides['poses']) != 64:
        raise ValueError('Unsupported rig adapter or incomplete guide matrix')
    output.parent.mkdir(parents=True,exist_ok=True); work = Path(tempfile.mkdtemp(prefix='.conditioning-',dir=output.parent))
    old = os.environ.get('SPRITE_OUTPUT_ROOT'); os.environ['SPRITE_OUTPUT_ROOT'] = str(source)
    try:
        comp = runpy.run_path(str(pipeline.ADAPTER/'compose-proof.py'))
        palette = [(0,0,0)] + [((i*73)%180+55,(i*113)%180+55,(i*157)%180+55) for i in range(1,len(manifest['parts'])+1)]
        entries = []; boards = []
        for direction in manifest['directions']:
            directory = work/direction; directory.mkdir()
            board = Image.new('RGB',(128*8,5*156),(27,32,40)); draw = ImageDraw.Draw(board)
            grip_board = Image.new('RGB',(128*8,160),(27,32,40)); grip_draw = ImageDraw.Draw(grip_board)
            poses = [p for p in guides['poses'] if p['direction'] == direction]
            for pose in poses:
                i = pose['index']; stem = f'{i:02}'
                rgba, owner = comp['compose'](manifest['default'],direction,i,packed=True,owners=True)
                active = rgba[:,:,3] > 0
                if not np.array_equal(owner > 0,active): raise ValueError('Owner/silhouette support mismatch')
                nearest = np.full((256,256),np.inf)
                for part in manifest['default']:
                    part_rgba,_,code,_ = comp['load'](part,direction,i)
                    z = np.where(code == 16777215,np.inf,code.astype(float)/16777214*8)
                    nearest = np.minimum(nearest,np.where(part_rgba[:,:,3] > 0,z,np.inf))
                if not np.array_equal(np.isfinite(nearest),active): raise ValueError('Depth/silhouette support mismatch')
                # Global camera-space range, constant for every key/view; 0 is background.
                depth = np.zeros((256,256),dtype=np.uint16)
                depth[active] = np.clip(np.rint((1-nearest[active]/8)*65534)+1,1,65535).astype(np.uint16)
                images = {'silhouette':Image.fromarray(active.astype(np.uint8)*255),
                          'part-ids':Image.fromarray(owner),'depth16':Image.fromarray(depth),
                          'composite':comp['native'](rgba)}
                skeleton = Image.open(source/'guides'/direction/f'{stem}-skeleton.png').convert('RGBA')
                images['skeleton'] = skeleton
                files = {}
                for kind, image in images.items():
                    name = f'{stem}-{kind}.png'; image.save(directory/name); files[kind] = f'{direction}/{name}'
                # Review colors are a separate derivative; categorical IDs remain integer labels.
                semantic = Image.fromarray(np.array(palette,dtype=np.uint8)[owner])
                depth_preview = Image.fromarray((depth//256).astype(np.uint8)).convert('RGB')
                for row,(label,image) in enumerate([('source FX off',images['composite']),('source-known joints',skeleton),
                                                     ('silhouette',images['silhouette']),('visible part IDs',semantic),('fixed-range depth',depth_preview)]):
                    image = image.resize((128,128),Image.Resampling.NEAREST)
                    cell = Image.new('RGBA',(128,128),(38,44,55,255)); cell.alpha_composite(image.convert('RGBA'))
                    board.paste(cell.convert('RGB'),(i*128,row*156+28)); draw.text((i*128+2,row*156+2),f'{direction} {i} {pose["time_ms"]}ms\n{label}',fill='white')
                # Zooms are inspection aids with recorded source rectangles, NEVER replacement frames.
                x,y = pose['joints_native_px']['right.wrist']; rect = [round(x)-12,round(y)-12,round(x)+12,round(y)+12]
                detail = Image.alpha_composite(images['composite'],skeleton).crop(tuple(rect))
                bg = Image.new('RGBA',(24,24),(38,44,55,255)); bg.alpha_composite(detail)
                zoom = bg.convert('RGB').resize((120,120),Image.Resampling.NEAREST)
                zoom.save(directory/f'{stem}-grip-inspection.png'); files['grip-inspection'] = f'{direction}/{stem}-grip-inspection.png'
                grip_board.paste(zoom,(i*128,30)); grip_draw.text((i*128+2,3),f'{direction} {i}\nFINGERS UNVERIFIED',fill='white')
                entries.append({'direction':direction,'index':i,'time_ms':pose['time_ms'],'duration_ms':pose['duration_ms'],
                                'weapon_owner':'anatomical_right','files':files,'grip_inspection_native_rect_xyxy':rect,
                                'finger_contact_verified':False})
            board.save(work/f'{direction}-conditioning-review.png'); grip_board.save(work/f'{direction}-grip-review.png')
            boards.extend([f'{direction}-conditioning-review.png',f'{direction}-grip-review.png']); comp['CACHE'].clear()
        shutil.copyfile(source/'pose-guides.json',work/'pose-guides.json')
        report = {'schema':'rig-conditioning-review-v1','status':'TECHNICAL_DIAGNOSTICS_SOURCE_POSES_REJECTED',
                  'source_build_fingerprint':receipt['fingerprint'],'source_receipt_sha256':pipeline.digest(source/'pipeline-receipt.json'),
                  'source_blend_sha256':pipeline.digest(source/'silver-scarf-modular-source.blend'),
                  'exporter_sha256':pipeline.digest(Path(__file__)),'frames':entries,'review_boards':boards,
                  'maps':{'skeleton':{'canvas':[128,128],'hidden_joints':'source known; not observed on visible artwork'},
                          'composite':{'canvas':[128,128],'FX':False,'source_color_reference':'six unresolved pixels; not exact-color approval'},
                          'silhouette':{'canvas':[256,256],'values':'0 background / 255 body+equipped weapon'},
                          'part-ids':{'canvas':[256,256],'values':{str(i+1):p for i,p in enumerate(manifest['parts'])},
                                      'limits':'Item render-piece ownership; paired gloves/body do NOT identify anatomical fingers or left/right surfaces'},
                          'depth16':{'canvas':[256,256],'range_camera_units':[0,8],'values':'background 0; valid round((1-z/8)*65534)+1; nearer = larger',
                                     'limits':'Packed source depth; no per-frame normalization; not a model-specific ControlNet encoding'}},
                  'registration':'Pose/skeleton/composite native128; source silhouette/part/depth256 share exact 2x coordinates. Full fixed canvases. Grip zoom has recorded source rect and is diagnostic only.',
                  'release_ready':False,'blockers':receipt['gates']['release_blockers']+['User rejected these original source poses as unnatural','No articulated finger/palm-to-hilt surface proof; wrist basis alone is insufficient'],
                  'artifacts':pipeline.inventory(work)}
        pipeline.atomic_json(work/'conditioning.json',report)
        # Verify immutability after reading source; a concurrent mutation must fail publication.
        pipeline.verify(source)
        os.rename(work,output); return report
    finally:
        if old is None: os.environ.pop('SPRITE_OUTPUT_ROOT',None)
        else: os.environ['SPRITE_OUTPUT_ROOT'] = old
        if work.exists(): shutil.rmtree(work)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--build-root',type=Path,required=True); parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        result = export(args.build_root,args.output)
        print(json.dumps({'output':str(args.output),'guide_keys':len(result['frames']),'release_ready':False}))
    except (ValueError,OSError,KeyError) as exc: parser.exit(2,'ERROR: '+str(exc)+'\n')
