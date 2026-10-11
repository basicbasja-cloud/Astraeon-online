"""Validate independent parts against full-scene renders; package the rig study.

Host Python needs Pillow, numpy and OpenEXR. This performs mechanical visibility
composition and export, not image synthesis or painting. No external art inputs.
"""
import hashlib, itertools, json, sys, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import OpenEXR

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[3]/'research/sprite-animation/silver-scarf/rig-proof-v4'
M=json.loads((OUT/'rig-manifest.json').read_text())
DIRS=M['directions']; TIMES=[0,80,180,280,340,400,520,660]
MAX_CODE=16777214; Z_RANGE=8.0
CACHE={}

def load(part,d,i):
    key=(part,d,i)
    if key not in CACHE:
        path=OUT/'parts'/part/d/f'{i:02}.png'
        rgba=np.array(Image.open(path).convert('RGBA'))
        z=OpenEXR.File(str(path.with_name(f'{i:02}-depth-{TIMES[i]+1:04}.exr'))).channels()['RGBA'].pixels[:,:,0].copy()
        valid=(rgba[:,:,3]>0)&(z<Z_RANGE)
        code=np.full(z.shape,16777215,dtype=np.uint32)
        code[valid]=np.rint(z[valid]/Z_RANGE*MAX_CODE).astype(np.uint32)
        encoded=np.stack([(code>>16)&255,(code>>8)&255,code&255],axis=-1).astype(np.uint8)
        CACHE[key]=(rgba,z,code,encoded)
    return CACHE[key]

def compose(parts,d,i,fx=False,packed=False,owners=False,fx_gain=1):
    result=np.zeros((256,256,4),dtype=np.uint8)
    nearest=np.full((256,256),np.inf)
    owner=np.zeros((256,256),dtype=np.uint8)
    for part in parts:
        rgba,z,code,_=load(part,d,i)
        if packed:z=np.where(code==16777215,np.inf,code.astype(float)/MAX_CODE*Z_RANGE)
        visible=(rgba[:,:,3]>0)&(z<nearest)
        result[visible]=rgba[visible];nearest[visible]=z[visible]
        owner[visible]=list(M['parts']).index(part)+1
    if fx and fx_gain>0:
        weapon=next(p for p in parts if p.startswith('weapon.'))
        rgba,z,code,_=load(weapon.replace('weapon.','trail.'),d,i)
        if packed:z=np.where(code==16777215,np.inf,code.astype(float)/MAX_CODE*Z_RANGE)
        alpha=rgba[:,:,3].astype(float)/255*fx_gain
        alpha=np.where(z<nearest,alpha,0)
        # Straight-alpha over, including translucent ribbon outside the body.
        base_alpha=result[:,:,3].astype(float)/255
        out_alpha=alpha+base_alpha*(1-alpha)
        premul=rgba[:,:,:3]*alpha[:,:,None]+result[:,:,:3]*base_alpha[:,:,None]*(1-alpha[:,:,None])
        result[:,:,:3]=np.rint(premul/np.maximum(out_alpha[:,:,None],1e-9)).clip(0,255).astype(np.uint8)
        result[:,:,3]=np.rint(out_alpha*255).astype(np.uint8)
    return (result,owner) if owners else result

def native(rgba):
    return Image.fromarray(rgba).resize((128,128),Image.Resampling.BOX)

def coverage(parts):
    return [p for p in parts if not(p.startswith('hair.') and 'headgear.helm' in parts)]

def export():
    start=time.perf_counter();report={'acceptance':'TECHNICAL_CHECKS_ONLY_ART_AND_FX_UNAPPROVED','reference_checks':[]}
    variants={'default':M['default'],'alternate':M['alternate'],'helmet':coverage(M['default']+['headgear.helm'])}
    worst=0;total=0;packed_total=0;owner_total=0;alpha_total=0;alpha_counts={}
    for d in DIRS:
        for i in range(8):
            for part in M['parts']:
                rgba,z,code,encoded=load(part,d,i)
                alpha_counts[part]=sorted(set(alpha_counts.get(part,[]))|set(np.unique(rgba[:,:,3]).tolist()))
                Image.fromarray(encoded).save(OUT/'parts'/part/d/f'{i:02}.depth.png')
            if i in [0,2,4,5]:
                for name,parts in variants.items():
                    assembled,owner=compose(parts,d,i,owners=True)
                    ref=np.array(Image.open(OUT/'references'/name/d/f'{i:02}.png').convert('RGBA'))
                    # RGB of transparent pixels is unspecified; canonicalize both.
                    ref[ref[:,:,3]==0]=0;assembled[assembled[:,:,3]==0]=0
                    diff=np.abs(assembled.astype(int)-ref.astype(int))
                    count=int(np.count_nonzero(np.any(diff,axis=2)))
                    owner_ref=np.rint(OpenEXR.File(str(OUT/'references'/name/d/f'{i:02}-owner-{TIMES[i]+1:04}.exr')).channels()['RGBA'].pixels[:,:,0]).astype(np.uint8)
                    owner_count=int(np.count_nonzero(owner!=owner_ref))
                    alpha_count=int(np.count_nonzero(assembled[:,:,3]!=ref[:,:,3]))
                    Image.fromarray(owner_ref).save(OUT/'references'/name/d/f'{i:02}.owner.png')
                    packed=compose(parts,d,i,packed=True);packed[packed[:,:,3]==0]=0
                    packed_count=int(np.count_nonzero(np.any(packed!=assembled,axis=2)))
                    total+=count;packed_total+=packed_count;owner_total+=owner_count;alpha_total+=alpha_count;worst=max(worst,int(diff.max()))
                    report['reference_checks'].append({'variant':name,'direction':d,'key':i,'differing_source_pixels':count,'maximum_channel_error':int(diff.max()),'packed_depth_differing_pixels':packed_count,'differing_part_owner_pixels':owner_count,'differing_alpha_pixels':alpha_count})
                    (OUT/'composites'/name/d).mkdir(parents=True,exist_ok=True)
                    native(assembled).save(OUT/'composites'/name/d/f'{i:02}.png')
        # Bound runtime assets to one facing per strip; don't preload all views.
        for part in M['parts']:
            color=Image.new('RGBA',(2048,256));depth=Image.new('RGB',(2048,256))
            for i in range(8):
                rgba,_,_,encoded=load(part,d,i)
                color.paste(Image.fromarray(rgba),(i*256,0));depth.paste(Image.fromarray(encoded),(i*256,0))
            dest=OUT/'strips'/part;dest.mkdir(parents=True,exist_ok=True)
            color.save(dest/f'{d}.png');depth.save(dest/f'{d}.depth.png')
        # Release a whole facing, keeping host memory bounded.
        CACHE.clear()
    report.update({'independent_full_scene_comparisons':len(report['reference_checks']),'total_differing_source_pixels':total,'maximum_channel_error':worst,'total_packed_depth_differing_pixels':packed_total,'total_differing_part_owner_pixels':owner_total,'total_differing_alpha_pixels':alpha_total,'exact_color_reference_status':'PASS' if total==0 else 'FAIL: preserved shader/intersection color differences; no pixel patches or tolerance substitution','visibility_reference_status':'PASS' if owner_total==0 and alpha_total==0 else 'FAIL','opaque_source_alpha_values':{p:v for p,v in alpha_counts.items() if not p.startswith('trail.')},'trail_source_alpha_values':{p:v for p,v in alpha_counts.items() if p.startswith('trail.')},'comparison_scope':'Opaque part ownership and alpha checked independently; exact color differences separately reported. Translucent FX composition is an unapproved experiment.'})
    # Explicit supported loadouts; each resolves every pose without fallback.
    loadouts=[]
    fixed=[p for p in M['default'] if not p.startswith(('hair.','torso.','cape.','weapon.'))]
    for hair,torso,cape,weapon,helmet in itertools.product(M['slots']['hair'],M['slots']['torso'],M['slots']['cape'],M['slots']['weapon'],M['slots']['headgear']):
        parts=coverage(fixed+[p for p in [hair,torso,cape,weapon,helmet] if p])
        loadouts.append(parts)
        for d in DIRS:
            for i in range(8):
                for p in parts:assert (OUT/'parts'/p/d/f'{i:02}.png').exists(),(p,d,i)
                assert len([p for p in parts if p.startswith('weapon.')])==1
                assert not(helmet and any(p.startswith('hair.') for p in parts))
    report['loadout_coverage']={'logical_loadouts':len(loadouts),'poses_each':64,'resolved_combinations':len(loadouts)*64,'scope':'Coverage and slot rules, not exhaustive visual approval or reference renders for every loadout.'}
    report['timing']={'durations_ms':M['clips']['attack']['frame_delays_ms'],'total_ms':sum(M['clips']['attack']['frame_delays_ms'])}
    report['maximum_source_grip_error_world']=M['maximum_right_grip_error_world']
    bounds=[];blank_trail=[]
    # Source bounds test includes complete hidden geometry and FX.
    for d in DIRS:
        for i in range(8):
            for p in M['parts']:
                rgba=load(p,d,i)[0];a=rgba[:,:,3]>0
                if a[0].any() or a[-1].any() or a[:,0].any() or a[:,-1].any():bounds.append([p,d,i])
                if p.startswith('trail.') and i not in [3,4,5] and a.any():blank_trail.append([p,d,i])
        CACHE.clear()
    report['canvas_edge_contacts']=bounds;report['unexpected_trail_frames']=blank_trail
    report['runtime_memory_contract']={'cache':'At most one facing of all 17 part strips; clear before changing facing; retain current displayed bitmap during staged loading','decoded_color_and_depth_bytes_upper_bound':17*2048*256*4*2,'additional_source_framebuffers_bytes':256*256*(4+4),'native_output_bytes':128*128*4,'excludes':'Browser image decode/canvas overhead and temporarily staged loads. This is an array bound, not measured GPU memory.'}
    # Preview GIFs use a solid backdrop to avoid GIF transparency trails.
    def background(im):
        bg=Image.new('RGBA',im.size,(32,39,49,255));bg.alpha_composite(im);return bg.convert('RGB')
    def save_gif(name,parts,fx=False,slow=1,allviews=False):
        frames=[]
        # Body keys stay sparse; effect exposure can end inside a held body key.
        display_times=sorted(set(TIMES+([410,420,430] if fx else [])))
        expiry=round((M['trail']['emitting_seconds'][1]+M['trail']['lifetime_seconds'])*1000)
        fade_start=max(M['trail']['emitting_seconds'][1]*1000,TIMES[max(M['trail']['active_key_indices'])])
        for ms in display_times:
            i=max(n for n,start in enumerate(TIMES) if start<=ms)
            gain=0 if ms>=expiry else 1 if ms<fade_start else (expiry-ms)/(expiry-fade_start)
            if allviews:
                panel=Image.new('RGB',(4*192,2*176),(32,39,49));draw=ImageDraw.Draw(panel)
                for n,d in enumerate(DIRS):
                    im=background(native(compose(parts,d,i,fx,fx_gain=gain))).resize((160,160),Image.Resampling.NEAREST)
                    x=(n%4)*192+16;y=(n//4)*176+16;panel.paste(im,(x,y));draw.text((x,y-13),d,fill='white')
                frames.append(panel)
            else:frames.append(background(native(compose(parts,'SE',i,fx,fx_gain=gain))).resize((384,384),Image.Resampling.NEAREST))
        delays=[b-a for a,b in zip(display_times,display_times[1:]+[800])]
        frames[0].save(OUT/name,save_all=True,append_images=frames[1:],duration=[x*slow for x in delays],loop=0,disposal=2,optimize=False)
        CACHE.clear()
    save_gif('attack-SE.gif',M['default'],True)
    save_gif('attack-eight-directions.gif',M['default'],True,allviews=True)
    save_gif('attack-quarter-speed.gif',M['default'],True,slow=4)
    save_gif('attack-body-only.gif',[p for p in M['default'] if not p.startswith('weapon.')])
    save_gif('attack-alternate.gif',M['alternate'],True)
    paired={'S':'SW','SW':'SW','W':'NW','NW':'NW','N':'NE','NE':'NE','E':'SE','SE':'SE'}
    frames=[]
    paired_times=sorted(set(TIMES+[410,420,430]))
    for ms in paired_times:
        i=max(n for n,start in enumerate(TIMES) if start<=ms)
        gain=0 if ms>=430 else 1 if ms<400 else (430-ms)/30
        panel=Image.new('RGB',(4*192,176),(32,39,49));draw=ImageDraw.Draw(panel)
        for n,d in enumerate(['SW','NW','NE','SE']):
            im=background(native(compose(M['default'],d,i,True,fx_gain=gain))).resize((160,160),Image.Resampling.NEAREST)
            x=n*192+16;panel.paste(im,(x,16));draw.text((x,2),d,fill='white')
        frames.append(panel)
    frames[0].save(OUT/'attack-four-diagonals.gif',save_all=True,append_images=frames[1:],duration=[b-a for a,b in zip(paired_times,paired_times[1:]+[800])],loop=0,disposal=2,optimize=False)
    CACHE.clear()
    report['paired_attack_view_policy']={'map':paired,'scope':'Optional study policy based on the observed Swordman block; not a universal rule for all RO actions or an approved game contract','no_image_flip':True}
    report['effect_exposure']={'emission_end_ms':360,'lifetime_ms':70,'expires_ms':430,'body_key_5_hold_ms':[400,520],'final_decay_samples_ms':[400,410,420,430],'body_pose_keys_unchanged':8,'scope':'Scalar fade and expiry of the baked ribbon; no continuous geometric re-sampling or artistic approval.'}
    sheet=Image.new('RGB',(4*192,4*174),(32,39,49));draw=ImageDraw.Draw(sheet)
    for n,part in enumerate(p for p in M['parts'] if not p.startswith('trail.')):
        im=background(native(load(part,'SE',0)[0])).resize((156,156),Image.Resampling.NEAREST)
        x=n%4*192+18;y=n//4*174+18;sheet.paste(im,(x,y));draw.text((x,y-15),part,fill='white')
    sheet.save(OUT/'separate-parts.png');CACHE.clear()
    report['compose_and_package_seconds']=round(time.perf_counter()-start,3)
    (OUT/'quality-report.json').write_text(json.dumps(report,indent=2)+'\n')
    # Hash actual shipping files, not self-reported provider status.
    files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.suffix in ['.png','.gif','.blend','.mjs','.html'] and 'blocking-review' not in p.parts and not('parts' in p.relative_to(OUT).parts and p.name.endswith('.depth.png'))}
    (OUT/'asset-hashes.json').write_text(json.dumps(files,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['independent_full_scene_comparisons','total_differing_source_pixels','maximum_channel_error','total_differing_part_owner_pixels','total_differing_alpha_pixels','exact_color_reference_status','visibility_reference_status','total_packed_depth_differing_pixels','loadout_coverage','canvas_edge_contacts','unexpected_trail_frames','compose_and_package_seconds']},indent=2))
    # Fail honestly; a rendered scene is independent from the exported compositor.
    # Ownership and alpha are the visibility test; exact color remains separately
    # failed whenever it differs. Never relabel that result as a full-color pass.
    assert owner_total==0 and alpha_total==0,'Full-scene visibility reconstruction failed; inspect reference_checks'
    assert packed_total==0,'Packed depth changed visibility; inspect reference_checks'
    assert not bounds,'Source geometry reaches canvas edge'
    assert not blank_trail,'Trail persists outside its declared phases'

if __name__=='__main__':export()
