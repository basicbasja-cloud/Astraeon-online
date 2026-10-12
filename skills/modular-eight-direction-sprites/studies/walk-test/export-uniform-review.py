"""Re-expose unchanged masters on one exact GIF/APNG/WebP review clock."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
def main():
 p=argparse.ArgumentParser();p.add_argument('--frames',type=Path,required=True);p.add_argument('--palette-gif',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--frame-ms',type=int,default=50);a=p.parse_args()
 if a.output.exists() or a.frame_ms<=0 or a.frame_ms%10:raise ValueError('Fresh output and GIF-exact multiple-of10ms required')
 files=sorted(a.frames.glob('*.png'));frames=[Image.open(f).convert('RGBA') for f in files]
 if not frames or len({f.size for f in frames})!=1:raise ValueError('Consistent master canvas required')
 palette=Image.open(a.palette_gif);palette.seek(0);palette=palette.copy();gif=[]
 for f in frames:
  bg=Image.new('RGBA',f.size,'#272727');bg.alpha_composite(f);gif.append(bg.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))
 a.output.mkdir(parents=True);delays=[a.frame_ms]*len(frames);stem='walk-uniform-'+str(sum(delays))+'ms'
 for ext in ['png','webp']:
  options={'disposal':0,'blend':0} if ext=='png' else {'lossless':True,'quality':100,'method':6,'exact':True}
  frames[0].save(a.output/(stem+'.'+ext),save_all=True,append_images=frames[1:],duration=delays,loop=0,**options)
 gif[0].save(a.output/(stem+'.gif'),save_all=True,append_images=gif[1:],duration=delays,loop=0,disposal=2,optimize=False)
 (a.output/'manifest.json').write_text(json.dumps({'schema':'uniform-review-clock-v1','source_frames':[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'delays_ms':delays,'duration_ms':sum(delays),'art_pixels_modified':False,'source_time_remapped_to_playback':True,'game_speed_contact_verified':False,'anatomy_accepted':False,'production_ready':False},indent=2)+'\n');print('UNIFORM_REVIEW',len(frames),'frames',sum(delays),'ms')
if __name__=='__main__':main()
