"""Single-frame CPU ControlNet experiment; never modifies source/master assets."""
import argparse, hashlib, json, time
from pathlib import Path
from PIL import Image

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--control',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--strength',type=float,default=.5);p.add_argument('--conditioning',type=float,default=.8);p.add_argument('--steps',type=int,default=12);a=p.parse_args()
 if a.output.exists() or a.output.is_symlink():raise ValueError('fresh output required')
 if not 0 < a.strength <= 1 or not 0 <= a.conditioning <= 2 or a.steps < 4 or int(a.steps*a.strength)<1:raise ValueError('invalid parameters')
 import torch
 from diffusers import StableDiffusionControlNetImg2ImgPipeline,ControlNetModel,UniPCMultistepScheduler
 torch.set_num_threads(4);start=time.monotonic()
 control=ControlNetModel.from_pretrained(a.control,torch_dtype=torch.float16,variant='fp16',local_files_only=True)
 pipe=StableDiffusionControlNetImg2ImgPipeline.from_pretrained(a.base,controlnet=control,torch_dtype=torch.float16,variant='fp16',safety_checker=None,feature_extractor=None,requires_safety_checker=False,local_files_only=True)
 pipe.scheduler=UniPCMultistepScheduler.from_config(pipe.scheduler.config);pipe.enable_attention_slicing();pipe.enable_vae_slicing();pipe=pipe.to('cpu')
 init=Image.open(a.inputs/'init.png').convert('RGB');edge=Image.open(a.inputs/'canny.png').convert('RGB')
 if init.size!=(512,512) or edge.size!=init.size:raise ValueError('expected aligned 512 inputs')
 prompt='full body fantasy swordsman, silver hair, gold scarf, bronze armor, dark navy tunic, cream tabard, brown boots, steel sword, illustrated game sprite, clean white background'
 negative='extra limbs, extra fingers, duplicate sword, cropped, blurry, bad anatomy, background, text'
 result=pipe(prompt=prompt,negative_prompt=negative,image=init,control_image=edge,strength=a.strength,controlnet_conditioning_scale=a.conditioning,num_inference_steps=a.steps,guidance_scale=5.0,generator=torch.Generator(device='cpu').manual_seed(20261104)).images[0]
 a.output.mkdir(parents=True);result.save(a.output/'result.png')
 (a.output/'receipt.json').write_text(json.dumps({'status':'SINGLE_FRAME_RESEARCH_NOT_ACCEPTED','base_revision':'451f4fe16113bff5a5d2269ed5ad43b0592e9a14','control_revision':'115a470d547982438f70198e353a921996e2e819','inputs':{x:digest(a.inputs/x) for x in ('init.png','guide.png','canny.png')},'script_sha256':digest(Path(__file__)),'output_sha256':digest(a.output/'result.png'),'seed':20261104,'strength':a.strength,'controlnet_conditioning_scale':a.conditioning,'num_inference_steps':a.steps,'guidance_scale':5.,'dtype':'float16','device':'cpu','seconds':round(time.monotonic()-start,2),'prompt':prompt,'negative_prompt':negative,'limitations':['Single image, not motion or temporal consistency.','Canny silhouette is not skeleton, grip or contact control.','No parts, variants or gameplay.']},indent=2)+'\n')
if __name__=='__main__':main()
