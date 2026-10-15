#!/usr/bin/env python3
"""Bounded image-surface audit and lossless review exports. Never edits input art.

Fixed ROIs were visually selected on this rear-camera bank. They are visible
boot surfaces, NOT semantic leg tracking or inferred anatomical joint labels.
Diagnostic exit 0 means report built; --require-production remains strict.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageSequence
from scipy import ndimage

P = Path(__file__).resolve().parent
CLOCK = [190,180,190,180,190,180,190,600]
WINDOWS = {'screen_left_boot': (164,460,215,493), 'screen_right_boot': (233,460,280,493)}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cells(path):
    im=Image.open(path).convert('RGBA')
    if im.size != (1536,1024): raise ValueError('Exact 4x2 plate required; no fitting')
    return [im.crop((k%4*384,k//4*512,k%4*384+384,k//4*512+512)) for k in range(8)]
def component(im):
    a=np.asarray(im)[:,:,3]>=128
    labels,n=ndimage.label(a)
    if not n: raise ValueError('Empty foreground')
    counts=np.bincount(labels.ravel());counts[0]=0
    y,x=np.where(labels==counts.argmax())
    return {'bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
            'height':int(y.max()-y.min()+1), 'component_bottom_proxy':int(y.max()),
            'cell_edge_pixels':int(a[0].sum()+a[-1].sum()+a[:,0].sum()+a[:,-1].sum())}
def boot(im,box):
    # Fixed window below the trouser/cape, selected from actual visible boots.
    x0,y0,x1,y1=box;a=np.asarray(im)[:,:,3]>=128
    y,x=np.where(a[y0:y1,x0:x1])
    if not len(x): return {'status':'UNKNOWN_EMPTY'}
    touches=bool((x==0).any() or (x==x1-x0-1).any() or (y==y1-y0-1).any())
    # Only distal band supplies x extent; the top of the window is not an ankle.
    yy,xx=np.where(a[460:y1,x0:x1])
    if not len(xx): return {'status':'UNKNOWN_NO_DISTAL_SURFACE'}
    return {'status':'UNKNOWN_WINDOW_CUT' if touches else 'VISIBLE_SURFACE_ONLY',
            'bottom_y':int(y.max()+y0),'distal_left_x':int(xx.min()+x0),
            'distal_right_x':int(xx.max()+x0),'not_anatomical_joint_tracking':True}
def measure(path):
    seq=cells(path);obs=[component(im) for im in seq]
    surface={name:[boot(im,box) for im in seq] for name,box in WINDOWS.items()}
    ranges={}
    for name,values in surface.items():
        valid=all(v['status']=='VISIBLE_SURFACE_ONLY' for v in values)
        spans={field:max(v[field] for v in values)-min(v[field] for v in values)
               for field in ['bottom_y','distal_left_x','distal_right_x']} if valid else None
        ranges[name]={'covered_all_keys':valid,'ranges_px':spans,
                      'bounded_6px_surface_stability':bool(valid and max(spans.values())<=6)}
    return {'sha256':sha(path),'components':obs,'surface_windows':WINDOWS,
            'visible_surface_observations':surface,'surface_summary':ranges,
            'neutral_return_height_delta':obs[7]['height']-obs[0]['height'],
            'height_vs_accepted_one_view_399px':obs[0]['height']-399,
            'same_view_family_proportions':'UNKNOWN: v39 is another facing; 18-dimension protocol not completed',
            'component_bottom_proxy_range':max(o['component_bottom_proxy'] for o in obs)-min(o['component_bottom_proxy'] for o in obs)}
def write_json(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def build():
    (P/'frames').mkdir(exist_ok=True);(P/'previews').mkdir(exist_ok=True)
    candidates={f'attempt{i}':measure(P/'raw'/f'N-attempt{i}.png') for i in range(1,4)}
    before=measure(P/'inputs'/'N-before-reconstructed.png')
    chosen=cells(P/'raw'/'N-attempt3.png');old=cells(P/'inputs'/'N-before-reconstructed.png')
    source=cells(P/'inputs'/'N-source.png')
    exports=[]; comparisons=[]
    for k,im in enumerate(chosen):
        f=P/'frames'/f'{k:02}.png';im.save(f)
        assert np.array_equal(np.asarray(Image.open(f)),np.asarray(im))
        bg=Image.new('RGBA',im.size,'#292b30');bg.alpha_composite(im);exports.append(bg.convert('RGB'))
        pair=Image.new('RGBA',(1152,512),'#292b30')
        for j,s in enumerate([source[k],old[k],im]):pair.alpha_composite(s,(j*384,0))
        comparisons.append(pair.convert('RGB'))
    for name,seq in [('N-candidate',exports),('source-before-after',comparisons)]:
        path=P/'previews'/f'{name}.gif'
        seq[0].save(path,save_all=True,append_images=seq[1:],duration=CLOCK,loop=0,disposal=2)
        decoded=Image.open(path)
        assert [f.info['duration'] for f in ImageSequence.Iterator(decoded)]==CLOCK
    report={'production_pass':False,'status':'REVIEW_CANDIDATE_REMAINS_BLOCKED',
      'selected_attempt':3,'clock_ms':CLOCK,'total_ms':sum(CLOCK),'before':before,'candidates':candidates,
      'review_authority':'Fixed visible pixel windows, component measurements and separate SHA-bound manual review',
      'blockers':['Full source-to-painted grip/contact continuity is occluded or untraced at keys2..4',
                  '18-dimension family proportion contract/head socket and complete_head separation unverified',
                  '399px accepted one-view size reference not yet reconciled; no per-frame fitting allowed',
                  'No head-swap, target-engine one-shot/event or other-facing approval'],
      'exports':{'lossless_cells':8,'decoded_gif_clocks_checked':2,'no_pixel_reposition_or_cleanup':True},
      'limitations':['Sole surface windows are not hips/knees/ankles/toes or semantic owner tracking',
                     'Component bottom never certifies anatomical floor contact',
                     'Looping GIF is review only; pickup gameplay is a one-shot',
                     'No source rig/export receipts transfer to generated pixels']}
    write_json(P/'review.json',report)
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--require-production',action='store_true');args=ap.parse_args()
    result=build();print(json.dumps({'production_pass':result['production_pass'],
       'visible_surface_summary':result['candidates']['attempt3']['surface_summary'],
       'neutral_return_height_delta':result['candidates']['attempt3']['neutral_return_height_delta'],
       'neutral_height':result['candidates']['attempt3']['components'][0]['height']}))
    raise SystemExit(1 if args.require_production and not result['production_pass'] else 0)
