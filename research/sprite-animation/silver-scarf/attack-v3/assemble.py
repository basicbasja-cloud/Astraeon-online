"""Register a coherent full-body clip and compose its separate weapon trail.

No body repainting, pose tweening, per-pose scaling or frozen-leg substitution.
"""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

OUT=Path(__file__).parent
SIZE=256
SCALE=.5
SUPPORT_TOE=np.array([182,208])
DELAYS=[80,100,100,60,60,120,140,140]
PHASES=['ready','load','coil','drive','cut','follow_through','recover','ready']
BG=(25,33,46,255)

def toe_marker(rgba,mask,bottom):
    yy,xx=np.indices(mask.shape)
    warm=mask&(yy>bottom-125)
    warm &= rgba[:,:,0].astype(float)>rgba[:,:,1]*1.20
    warm &= rgba[:,:,1].astype(float)>rgba[:,:,2]*1.08
    labels,_=ndimage.label(warm);sizes=np.bincount(labels.ravel());sizes[0]=0
    candidates=[]
    for k in np.argsort(sizes)[-5:]:
        if sizes[k]<1500:continue
        y,x=np.where(labels==k);candidates.append((float(x.mean()),k))
    assert len(candidates)>=2, candidates
    _,front=max(candidates)
    y,x=np.where(labels==front);floor=int(y.max())
    # Toe, not the changing ankle/shin/whole-figure bounds: the rightmost
    # contour in the lower forefoot portion of the supporting boot.
    region=(labels==front)&(yy>=floor-28)
    y,x=np.where(region);edge=int(x.max());near_edge=region&(xx>=edge-3)
    y,x=np.where(near_edge)
    return np.array([edge+1,float(np.median(y))]), {'front_boot_area':int(sizes[front]),'toe_band_bottom':floor}

def opaque(frame):
    bg=Image.new('RGBA',frame.size,BG);bg.alpha_composite(frame);return bg.convert('RGB')

def gif(name,frames,multiplier=1):
    rgb=[opaque(f) for f in frames];sheet=Image.new('RGB',(SIZE*4,SIZE*2),BG[:3])
    for i,f in enumerate(rgb):sheet.paste(f,(i%4*SIZE,i//4*SIZE))
    palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    converted=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in rgb]
    converted[0].save(OUT/name,save_all=True,append_images=converted[1:],duration=[d*multiplier for d in DELAYS],loop=0,disposal=2,optimize=False)

def main():
    for d in ['body-frames','trail-frames','composite-frames']:(OUT/d).mkdir(exist_ok=True)
    a=np.array(Image.open(OUT/'source-art.png').convert('RGBA'))
    labels,_=ndimage.label(a[:,:,3]>=120);sizes=np.bincount(labels.ravel());objects=[]
    for k in range(1,len(sizes)):
        if sizes[k]<20000:continue
        y,x=np.where(labels==k)
        objects.append({'label':k,'center':[float(x.mean()),float(y.mean())],
                        'box':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]})
    assert len(objects)==8, ('Figure count/overlap',len(objects))
    rows=sorted(objects,key=lambda o:o['center'][1]);ordered=[]
    for r in range(2):ordered.extend(sorted(rows[r*4:(r+1)*4],key=lambda o:o['center'][0]))
    foreground=np.isin(labels,[o['label'] for o in ordered])
    distance,nearest=ndimage.distance_transform_edt(~foreground,return_indices=True)
    owners=labels[tuple(nearest)]
    frames,records=[],[]
    for i,o in enumerate(ordered):
        mask=labels==o['label'];x0,y0,x1,y1=o['box']
        assert x0>0 and y0>0 and x1<a.shape[1] and y1<a.shape[0],('Source clipping',i,o['box'])
        toe,diagnostic=toe_marker(a,mask,y1-1)
        x0=max(0,x0-6);y0=max(0,y0-6);x1=min(a.shape[1],x1+6);y1=min(a.shape[0],y1+6)
        pixels=a[y0:y1,x0:x1].copy()
        owned=(owners[y0:y1,x0:x1]==o['label'])&(distance[y0:y1,x0:x1]<=4)
        pixels[:,:,3]=np.where(owned&(pixels[:,:,3]>=16),pixels[:,:,3],0)
        assert pixels.shape[0]<=512 and pixels.shape[1]<=512
        # A common 512-square source workspace ensures exactly the same .5
        # scale, independent of the figure's changing visible bounding box.
        stage=Image.new('RGBA',(512,512));stage.alpha_composite(Image.fromarray(pixels))
        stage=stage.resize((256,256),Image.Resampling.LANCZOS)
        placement=np.rint(SUPPORT_TOE-(toe-np.array([x0,y0]))*SCALE).astype(int)
        normalized=toe_marker_point=(toe-np.array([x0,y0]))*SCALE+placement
        frame=Image.new('RGBA',(SIZE,SIZE));frame.alpha_composite(stage,tuple(placement))
        solid=np.array(frame.getchannel('A'))>=80;y,x=np.where(solid)
        bounds=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
        assert min(bounds[:2])>=3 and max(bounds[2:])<=SIZE-3,('Export clipping',i,bounds)
        frames.append(frame)
        records.append({'index':i,'phase':PHASES[i],'duration_ms':DELAYS[i],
                        'source_box':[x0,y0,x1,y1],'source_support_toe':toe.tolist(),
                        'normalized_support_toe':normalized.tolist(),'placement':placement.tolist(),
                        'scale':SCALE,'visible_bounds_alpha80':bounds,'boot_marker_diagnostic':diagnostic,
                        'contact_policy':'front/left toe registered; rear foot allowed to pivot/step'})
    frames[-1]=frames[0].copy();records[-1]['image_alias']=0
    for key in ['source_box','source_support_toe','normalized_support_toe','placement',
                'visible_bounds_alpha80','boot_marker_diagnostic']:
        records[-1][key]=records[0][key]
    # Artist-authored landmarks identify the actual blade, not a generic effect
    # centered on the character. They are source-sheet pixels, not painted edits.
    landmarks={3:{'grip':[1396,286],'tip':[1515,300],'opacity':.66},
               4:{'grip':[298,812],'tip':[395,898],'opacity':.94},
               5:{'grip':[699,850],'tip':[785,924],'opacity':.32}}
    effect=Image.open(OUT/'source-trail.png').convert('RGBA')
    effect_pivot=np.array([312.,688.]);effect_tip=np.array([986.,1146.]);vector=effect_tip-effect_pivot
    trails=[Image.new('RGBA',(SIZE,SIZE)) for _ in frames]
    effect_records={}
    for i,lm in landmarks.items():
        record=records[i];origin=np.array(record['source_box'][:2]);placement=np.array(record['placement'])
        grip=(np.array(lm['grip'])-origin)*SCALE+placement
        tip=(np.array(lm['tip'])-origin)*SCALE+placement
        delta=tip-grip;fx_scale=float(np.linalg.norm(delta)/np.linalg.norm(vector))
        angle=math.degrees(math.atan2(vector[1],vector[0])-math.atan2(delta[1],delta[0]))
        scaled=effect.resize((round(effect.width*fx_scale),round(effect.height*fx_scale)),Image.Resampling.LANCZOS)
        stage=Image.new('RGBA',(SIZE,SIZE))
        fx_place=np.rint(grip-effect_pivot*fx_scale).astype(int)
        stage.alpha_composite(scaled,tuple(fx_place));stage=stage.rotate(angle,Image.Resampling.BICUBIC,center=tuple(grip))
        alpha=np.array(stage.getchannel('A'),dtype=float)
        stage.putalpha(Image.fromarray(np.rint(alpha*lm['opacity']).astype('uint8')))
        trails[i]=stage
        effect_records[i]={'source_grip':lm['grip'],'source_blade_tip':lm['tip'],
                           'normalized_grip':grip.tolist(),'normalized_blade_tip':tip.tolist(),
                           'effect_scale_for_projected_blade':fx_scale,'rotation_degrees':angle,'opacity':lm['opacity']}
    composites=[]
    for i,(body,trail) in enumerate(zip(frames,trails)):
        body.save(OUT/'body-frames'/f'{i:02}.png');trail.save(OUT/'trail-frames'/f'{i:02}.png')
        composed=trail.copy();composed.alpha_composite(body)
        composed.save(OUT/'composite-frames'/f'{i:02}.png');composites.append(composed)
    gif('attack-full-body.gif',composites)
    gif('attack-full-body-slow.gif',composites,4)
    gif('attack-body-only.gif',frames)
    composites[0].save(OUT/'attack-transparent.png',save_all=True,append_images=composites[1:],duration=DELAYS,loop=0,disposal=0,blend=0)
    for folder in ['body-frames','trail-frames','composite-frames']:
        strip=Image.new('RGBA',(SIZE*8,SIZE))
        for i in range(8):strip.alpha_composite(Image.open(OUT/folder/f'{i:02}.png'),(i*SIZE,0))
        strip.save(OUT/f'{folder}-strip.png')
    contact=Image.new('RGB',(SIZE*4,SIZE*2),BG[:3])
    for i,f in enumerate(composites):contact.paste(opaque(f),(i%4*SIZE,i//4*SIZE))
    contact.save(OUT/'attack-contact-sheet.png')
    report={'version':3,'acceptance':'CANDIDATE_USER_REVIEW_PENDING','direction':'SE/front-right only',
            'canvas':[256,256],'frame_delays_ms':DELAYS,'duration_ms':800,'average_timeline_pose_fps':10,
            'logical_frames':8,'distinct_body_images':7,'ground_root':[128,208],
            'contact_anchor':{'kind':'front/left toe','position':SUPPORT_TOE.tolist()},
            'maximum_support_marker_registration_error_px':max(float(np.linalg.norm(np.array(r['normalized_support_toe'])-SUPPORT_TOE)) for r in records),
            'render_order':['trail','body'],'trail_active_indices':list(landmarks),
            'loop_endpoint_RGBA_identical':True,'frames':records,'trail':effect_records,
            'source_files':['source-art.png','source-trail.png'],
            'limitations':['One facing; other painted attack directions are not authored',
                           'Separate trail only: body/clothes/head/weapon are still a flattened layer',
                           'Art does not reproduce every rig target exactly: rear foot performs authored-looking step/heel release',
                           'Registration markers do not prove zero silhouette boiling or correct weight dynamics',
                           'Interactive preview is separate from the actual game; gameplay validation pending']}
    (OUT/'attack-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    with Image.open(OUT/'attack-full-body.gif') as g:
        assert g.n_frames==8;durations=[];decoded=[]
        for i in range(g.n_frames):g.seek(i);durations.append(g.info['duration']);decoded.append(g.convert('RGB').tobytes())
        assert durations==DELAYS and sum(durations)==800 and decoded[0]==decoded[-1]
    assert np.array_equal(np.array(composites[0]),np.array(composites[-1]))
    for i in [0,1,2,6,7]:assert trails[i].getchannel('A').getbbox() is None
    assert report['maximum_support_marker_registration_error_px']<.8
    print(json.dumps({k:v for k,v in report.items() if k not in ['frames','trail']},indent=2))

if __name__=='__main__':main()
