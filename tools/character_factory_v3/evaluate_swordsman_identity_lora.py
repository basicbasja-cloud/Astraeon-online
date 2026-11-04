"""Matched-seed held-out Walk comparison; no runtime or animation approval."""
import argparse,hashlib,json,time
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104/generated-sheet.png'
GUIDE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104/guide-contact.png'
CONTROLS=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-sw-openpose-controls-20261104'
PROMPT='astraeon swordsman, full body illustrated fantasy game character, silver lavender hair, golden scarf, bronze armor and gauntlets, dark navy sleeves, cream tabard with gold borders, olive trousers, brown leather boots, steel sword, white background'
CLOTH_PROMPT='astraeon swordsman, hand-painted anime RPG sprite, silver hair, gold scarf, ivory cloth tunic, navy jacket, leather harness, bronze pauldrons and bracers, closed brown leather gloves, ivory tabard, olive trousers, brown boots, sword, white background'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SCRIPT_SHA=sha(Path(__file__))
def tile(path,i):
 with Image.open(path) as im:
  s=im.convert('RGB');w,h=s.size;return s.transform((512,512),Image.Transform.EXTENT,(i%4*w/4,i//4*h/4,(i%4+1)*w/4,(i//4+1)*h/4),Image.Resampling.BICUBIC)
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--base-repo',default='Lykon/dreamshaper-8');p.add_argument('--base-revision',default='a7e52b98680b1ba8ff7bce97c7f9f2e2e5337917');p.add_argument('--control',type=Path,required=True);p.add_argument('--lora',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--frames',type=int,nargs='+',default=[0,3,8,15]);p.add_argument('--strength',type=float,default=.3);p.add_argument('--lora-scale',type=float,default=.8);p.add_argument('--modes',choices=['base','identity'],nargs='+',default=['base','identity']);p.add_argument('--profile',choices=['original','cloth'],default='original');p.add_argument('--color-guide',type=Path);a=p.parse_args()
 prompt=CLOTH_PROMPT if a.profile=='cloth' else PROMPT
 negative='extra limbs, extra fingers, duplicate sword, cropped, blurry, bad anatomy, background, text, masked face'
 if a.profile=='cloth':negative+=', bare hands, exposed fingers, golden breastplate, metal chest plate, photorealistic, 3d render'
 if a.output.exists() or a.output.is_symlink():raise ValueError('Fresh output required')
 if any(not 0<=i<16 for i in a.frames) or not 0<a.strength<=1:raise ValueError('Invalid bounded evaluation')
 import torch
 from diffusers import StableDiffusionControlNetImg2ImgPipeline,ControlNetModel,UniPCMultistepScheduler
 from transformers import CLIPTokenizer
 from diffusion_caption_contract import validate_caption
 tokenizer=CLIPTokenizer.from_pretrained(a.base,subfolder='tokenizer',local_files_only=True);caption=validate_caption(tokenizer,prompt,negative)
 torch.set_num_threads(4);start=time.monotonic();control=ControlNetModel.from_pretrained(a.control,variant='fp16',torch_dtype=torch.float16,local_files_only=True)
 pipe=StableDiffusionControlNetImg2ImgPipeline.from_pretrained(a.base,controlnet=control,variant='fp16',torch_dtype=torch.float16,safety_checker=None,feature_extractor=None,requires_safety_checker=False,local_files_only=True)
 pipe.scheduler=UniPCMultistepScheduler.from_config(pipe.scheduler.config);pipe.vae.enable_slicing();pipe=pipe.to('cpu');pipe.load_lora_weights(a.lora.parent,weight_name=a.lora.name,adapter_name='swordsman',local_files_only=True);pipe.set_adapters('swordsman',adapter_weights=a.lora_scale)
 a.output.mkdir(parents=True);rows=[];board=Image.new('RGB',(512*(2+len(a.modes)),544*len(a.frames)),'white');draw=ImageDraw.Draw(board)
 for j,i in enumerate(a.frames):
  init=tile(ART,i);guide=tile(GUIDE,i)
  if a.color_guide:
   with Image.open(a.color_guide/'SW'/f'{i:03}.png') as raw:
    raw=raw.convert('RGBA').crop((420,520,1116,1216));white=Image.new('RGBA',raw.size,'white');white.alpha_composite(raw);init=white.convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
  pose=Image.open(CONTROLS/f'{i:03}.png').convert('RGB');init.save(a.output/f'input{i:02}.png');images=[guide,init]
  for mode in a.modes:
   if mode=='base':pipe.disable_lora()
   else:pipe.enable_lora()
   tick=time.monotonic();im=pipe(prompt=prompt,negative_prompt=negative,image=init,control_image=pose,strength=a.strength,controlnet_conditioning_scale=1.0,num_inference_steps=20,guidance_scale=5.,generator=torch.Generator().manual_seed(20261104+i)).images[0]
   path=a.output/f'{mode}{i:02}.png';im.save(path);rows.append({'frame':i,'mode':mode,'seed':20261104+i,'output_sha256':sha(path),'seconds':round(time.monotonic()-tick,2)});images.append(im);print(json.dumps(rows[-1]),flush=True)
  for col,(name,im) in enumerate(zip(['guide','initial draft']+[{'base':'base model','identity':'identity LoRA draft'}[m] for m in a.modes],images)):
   board.paste(im,(512*col,544*j+32));draw.text((512*col+5,544*j+5),f'{name} {i:02}',fill='black')
  board.save(a.output/'comparison.png')
 (a.output/'receipt.json').write_text(json.dumps({'status':'HELD_OUT_WALK_KEYPOSE_COMPARISON_NOT_ACCEPTED','lora_sha256':sha(a.lora),'script_sha256':SCRIPT_SHA,'art_sha256':sha(ART),'guide_sha256':sha(GUIDE),'base_repo':a.base_repo,'base_revision':a.base_revision,'base_setup_receipt_sha256':sha(a.base/'setup-receipt.json') if (a.base/'setup-receipt.json').exists() else None,'init_mode':'native_color_guide_fixed_crop' if a.color_guide else 'unapproved_painted_draft','init_crop':[420,520,1116,1216] if a.color_guide else None,'color_guide_proof_sha256':sha(a.color_guide/'color-control-proof.json') if a.color_guide else None,'control_revision':'9ae9f970358db89e211b87c915f9535c6686d5ba','prompt':prompt,'negative_prompt':negative,'profile':a.profile,'caption_tokens':caption,'modes':a.modes,'frames':rows,'lora_scale':a.lora_scale,'strength':a.strength,'steps':20,'seconds':round(time.monotonic()-start,2),'limitations':['Sparse key poses, not a full animation.','No geometry, identity or temporal pass is inferred.','Control omits blade, face and fingers; visible grip must be reviewed.','Training used original BasicAttack with DreamShaper; use on another compatible SD1.5 base is an unapproved transfer experiment.','This Walk motion was not in the training set.']},indent=2)+'\n')
if __name__=='__main__':main()
