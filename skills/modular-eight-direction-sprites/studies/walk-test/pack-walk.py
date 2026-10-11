"""Fixed-canvas native frames, depth-aware part preview and actual motion GIFs."""
import argparse,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import OpenEXR

p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--renders',type=Path,required=True)
p.add_argument('--parts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise ValueError('Use a fresh package directory')
m=json.loads((a.build/'motion.json').read_text());a.output.mkdir(parents=True)
DIRS=['S','SE','E','NE','N','NW','W','SW'];KEYS=m['selected_source_indices'];N=128
times=[m['frames'][i]['time_seconds']*1000 for i in KEYS]+[m['duration_seconds']*1000]
apng_delays=[round(times[i+1])-round(times[i]) for i in range(8)]
gif_delays=[(round(times[i+1]/10)-round(times[i]/10))*10 for i in range(8)]
elevation=math.atan2(2.92-.64,4);scale=N/1.58
def proj(p,view=1):
    x,y,z=p;th=view*math.pi/4;x,y=x*math.cos(th)-y*math.sin(th),x*math.sin(th)+y*math.cos(th)
    return (64+x*scale,64-(y*math.sin(elevation)+(z-.64)*math.cos(elevation))*scale)
def stage(im,k,view=1):
    bg=Image.new('RGBA',(N,N),'#dce0df');ground=Image.new('RGBA',(N,N));d=ImageDraw.Draw(ground)
    d.ellipse((6,88,122,127),fill='#c9cecd');travel=m['frames'][KEYS[k]]['root_world'];pitch=abs(m['frames'][-1]['root_world'][1])/4
    for x in np.arange(-.8,.9,pitch):
        for y in np.arange(-1.2,1.3,pitch):
            if (round(x/pitch)+round(y/pitch))%2:continue
            corners=[proj((xx,yy-travel[1],0),view) for xx,yy in [(x,y),(x+pitch,y),(x+pitch,y+pitch),(x,y+pitch)]]
            d.polygon(corners,fill='#c0c6c4')
    mask=Image.new('L',(N,N));ImageDraw.Draw(mask).ellipse((6,88,122,127),fill=255)
    bg.paste(ground,(0,0),mask)
    shadow=Image.new('RGBA',(N,N));ImageDraw.Draw(shadow).ellipse((43,105,86,116),fill=(54,61,60,36));bg.alpha_composite(shadow);bg.alpha_composite(im)
    return bg.convert('RGB')
def write_gif(images,path,magnify=1):
    palette_canvas=Image.new('RGB',(images[0].width*len(images),images[0].height))
    for i,im in enumerate(images):palette_canvas.paste(im,(i*im.width,0))
    palette=palette_canvas.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    fs=[im.quantize(palette=palette,dither=Image.Dither.NONE).resize((im.width*magnify,im.height*magnify),Image.Resampling.NEAREST) for im in images]
    fs[0].save(path,save_all=True,append_images=fs[1:],duration=gif_delays,loop=0,disposal=2,optimize=False)
def native(path):
    im=Image.open(path).convert('RGBA')
    if im.size!=(256,256):raise ValueError('Unexpected logical canvas')
    alpha=np.asarray(im)[:,:,3]
    if alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any():raise ValueError('Frame clipped at canvas edge')
    return im.resize((N,N),Image.Resampling.LANCZOS)

whole={};native_dir=a.output/'frames';native_dir.mkdir()
for view in DIRS:
    dr=native_dir/view;dr.mkdir();whole[view]=[]
    for k in range(8):
        im=native(a.renders/view/'composite'/f'{k:02}.png');im.save(dr/f'{k:02}.png');whole[view].append(im)
cards=[stage(im,k) for k,im in enumerate(whole['SE'])]
write_gif(cards,a.output/'walk-SE.gif',4)
whole['SE'][0].save(a.output/'walk-SE.png',save_all=True,append_images=whole['SE'][1:],duration=apng_delays,loop=0,disposal=0,blend=0)
sheet=Image.new('RGBA',(N*8,N))
for k,im in enumerate(whole['SE']):sheet.paste(im,(k*N,0))
sheet.save(a.output/'walk-SE-strip.png')
all_views=[]
for k in range(8):
    b=Image.new('RGB',(N*4,148*2),'#e7e9e8');d=ImageDraw.Draw(b)
    for i,view in enumerate(DIRS):
        x,y=i%4*N,i//4*148;b.paste(stage(whole[view][k],k,i),(x,y+20));d.text((x+5,y+3),view,fill='#263238')
    all_views.append(b)
write_gif(all_views,a.output/'walk-eight-directions.gif',2)
board=Image.new('RGB',(N*8,148*8),'#e7e9e8');d=ImageDraw.Draw(board)
for row,view in enumerate(DIRS):
    for k in range(8):board.paste(stage(whole[view][k],k,row),(k*N,row*148+20));d.text((k*N+4,row*148+3),f'{view} #{k}',fill='#263238')
board.save(a.output/'walk-eight-directions.png')

# Complete isolated item renders include other selected meshes as shadow casters.
# RGB24 stores camera depth / 8 units; ffffff is background. Native depth uses
# nearest sample, shared RGBA scale uses Lanczos: this is a bounded preview policy.
slots=m['parts'];arrays={};depths={};part_dir=a.output/'parts'/'SE';part_dir.mkdir(parents=True)
for slot in slots:
    dr=part_dir/slot;dr.mkdir();arrays[slot]=[];depths[slot]=[]
    for k in range(8):
        im=native(a.parts/'SE'/slot/f'{k:02}.png');im.save(dr/f'{k:02}.png');arr=np.asarray(im).copy()
        with OpenEXR.File(str(a.parts/'SE'/slot/f'{k:02}-depth.exr')) as ex:
            ch=ex.channels()
            z=ch['RGBA'].pixels[:,:,0] if 'RGBA' in ch else ch['RGB'].pixels[:,:,0] if 'RGB' in ch else ch['R'].pixels
        if z.shape!=(256,256):raise ValueError('Depth registration mismatch')
        z=np.asarray(Image.fromarray(z).resize((N,N),Image.Resampling.NEAREST))
        valid=(arr[:,:,3]>0)&np.isfinite(z)&(z>0)&(z<8)
        packed=np.full((N,N),0xffffff,dtype=np.uint32);packed[valid]=np.rint(z[valid]/8*0xfffffe).astype(np.uint32)
        rgb=np.stack([(packed>>16)&255,(packed>>8)&255,packed&255],axis=2).astype(np.uint8)
        Image.fromarray(rgb).save(dr/f'{k:02}-depth.png');arrays[slot].append(arr);depths[slot].append(packed)

def composite(k,hair='silver',cape=True):
    chosen=[n for n in slots if n!='hair.'+('auburn' if hair=='silver' else 'silver') and (cape or n!='cape')]
    rgba=np.stack([arrays[n][k] for n in chosen])/255;z=np.stack([depths[n][k] for n in chosen]);order=np.argsort(z,axis=0)[::-1]
    rgba=np.take_along_axis(rgba,order[:,:,:,None],axis=0);out=np.zeros((N,N,4))
    for row in rgba:
        aa=row[:,:,3:4];out[:,:,:3]=row[:,:,:3]*aa+out[:,:,:3]*(1-aa);out[:,:,3:4]=aa+out[:,:,3:4]*(1-aa)
    out[:,:,:3]/=np.maximum(out[:,:,3:4],1e-10)
    return Image.fromarray(np.rint(np.clip(out,0,1)*255).astype(np.uint8))
layer_dir=a.output/'layer-preview';layer_dir.mkdir();layer_frames={};max_rgb=0;mean_rgb=[];lower_changes=[]
for hair in ['silver','auburn']:
    layer_frames[hair]=[]
    for k in range(8):
        im=composite(k,hair);im.save(layer_dir/f'{hair}-{k:02}.png');layer_frames[hair].append(im)
        if hair=='silver':
            diff=np.abs(np.asarray(im).astype(float)-np.asarray(whole['SE'][k]).astype(float));max_rgb=max(max_rgb,int(diff[:,:,:3].max()));mean_rgb.append(float(diff[:,:,:3].mean()))
for k in range(8):
    silver=np.asarray(layer_frames['silver'][k]);auburn=np.asarray(layer_frames['auburn'][k]);lower_changes.append(int(np.count_nonzero(np.any(silver[65:]!=auburn[65:],axis=2))))
swaps=[]
for k in range(8):
    b=Image.new('RGB',(N*2,148),'#e7e9e8');d=ImageDraw.Draw(b)
    for i,hair in enumerate(['silver','auburn']):b.paste(stage(layer_frames[hair][k],k),(i*N,20));d.text((i*N+4,3),hair+' / same motion',fill='#263238')
    swaps.append(b)
write_gif(swaps,a.output/'walk-hair-swap.gif',3)
rows=['body','hair.silver','torso','pants','boots','gloves','armor','scarf','cape','belt','sash']
b=Image.new('RGB',(N*8,148*len(rows)),'#e7e9e8');d=ImageDraw.Draw(b)
for row,slot in enumerate(rows):
    for k in range(8):
        bg=Image.new('RGBA',(N,N),'#dce0df');bg.alpha_composite(Image.fromarray(arrays[slot][k]));b.paste(bg.convert('RGB'),(k*N,row*148+20));d.text((k*N+3,row*148+3),slot+f' #{k}',fill='#263238')
b.save(a.output/'complete-parts.png')

guide_frames=[]
parents={n:v['parent'] for n,v in json.loads(__import__('gzip').decompress(Path('research/sprite-animation/preset-retarget-v8/source-transforms.json.gz').read_bytes()))['rest_bones'].items()}
for k in range(8):
    im=Image.new('RGB',(N,N),'#26313a');d=ImageDraw.Draw(im);j=m['frames'][KEYS[k]]['in_place_joints'];pts={n:proj(v) for n,v in j.items()}
    for n,parent in parents.items():
        if parent and parent!='root':d.line([pts[n],pts[parent]],fill='#4ba0ff' if n.endswith('_r') else '#ff9740' if n.endswith('_l') else '#eff1f3',width=1)
    b=Image.new('RGB',(N*2,148),'#e7e9e8');d=ImageDraw.Draw(b);b.paste(cards[k],(0,20));b.paste(im,(N,20));d.text((4,3),'Original / actual baked rig',fill='#263238');guide_frames.append(b)
write_gif(guide_frames,a.output/'walk-rig-comparison.gif',3)
receipt={'schema':'walk-native-package-v1','native_canvas':[128,128],'render_canvas':[256,256],'shared_scale':.5,'registration':'Fixed source camera/root; no bbox fitting','body_exposures':8,'apng_delays_ms':apng_delays,'apng_cycle_ms':sum(apng_delays),'gif_delays_ms':gif_delays,'gif_cycle_ms':sum(gif_delays),'source_duration_ms':m['duration_seconds']*1000,'gif_timing':'10ms container quantization, cumulative boundaries; 3.333ms shorter than source cycle','views':DIRS,'complete_part_view_coverage':['SE'],'slots':slots,'depth_encoding':'RGB24 fixed 0..8 camera units; ffffff background; nearest native sample','layer_comparison':{'exact_color_pass':max_rgb==0,'maximum_rgb_difference':max_rgb,'mean_rgb_difference_per_key':mean_rgb,'scope':'Separate shaded passes + native alpha/depth sample policy; no exact compositing claim if differences remain'},'hair_swap_lower_body_changed_pixels_per_key':lower_changes,'release_ready':False}
(a.output/'package.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PACKED_WALK',receipt['layer_comparison'],'lower changes',lower_changes)
