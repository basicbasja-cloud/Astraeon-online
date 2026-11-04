"""Single-frame CPU pose+reference experiment; not production art."""
import argparse, hashlib,json,time
from pathlib import Path
from PIL import Image

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
SCRIPT_SHA=sha(Path(__file__))
def main():
 p=argparse.ArgumentParser()
 for flag in ('base','control','adapter','embedding','inputs','output'):p.add_argument('--'+flag,type=Path,required=True)
 p.add_argument('--adapter-file',choices=('ip-adapter_sd15.safetensors','ip-adapter-plus_sd15.safetensors'),default='ip-adapter_sd15.safetensors');p.add_argument('--strength',type=float,default=.25);p.add_argument('--steps',type=int,default=20);p.add_argument('--ip-scale',type=float,default=.7);p.add_argument('--pose-scale',type=float,default=.7);a=p.parse_args()
 if not 0<a.strength<=1 or not 0<=a.ip_scale<=2 or not 0<=a.pose_scale<=2 or a.steps<4 or int(a.strength*a.steps)<1:raise ValueError('invalid generation parameters')
 if a.output.exists() or a.output.is_symlink():raise ValueError('fresh output required')
 import torch
 from diffusers import StableDiffusionControlNetImg2ImgPipeline,ControlNetModel,UniPCMultistepScheduler
 torch.set_num_threads(4);start=time.monotonic()
 c=ControlNetModel.from_pretrained(a.control,torch_dtype=torch.float16,variant='fp16',local_files_only=True)
 pipe=StableDiffusionControlNetImg2ImgPipeline.from_pretrained(a.base,controlnet=c,torch_dtype=torch.float16,variant='fp16',safety_checker=None,feature_extractor=None,requires_safety_checker=False,local_files_only=True)
 pipe.scheduler=UniPCMultistepScheduler.from_config(pipe.scheduler.config);pipe.vae.enable_slicing();pipe=pipe.to('cpu')
 pipe.load_ip_adapter(a.adapter,subfolder='models',weight_name=a.adapter_file,image_encoder_folder=None,local_files_only=True);pipe.set_ip_adapter_scale(a.ip_scale)
 init=Image.open(a.inputs/'init.png').convert('RGB');pose=Image.open(a.inputs/'openpose.png').convert('RGB');emb=torch.load(a.embedding,map_location='cpu',weights_only=True)
 if init.size!=(512,512) or pose.size!=init.size or tuple(emb.shape)!=((2,1,257,1280) if a.adapter_file=='ip-adapter-plus_sd15.safetensors' else (2,1,1024)) or not torch.isfinite(emb).all():raise ValueError('invalid aligned inputs or embeddings')
 prompt='full body fantasy swordsman, silver hair, gold scarf, bronze armor, dark navy tunic, cream tabard, brown boots, steel sword, illustrated game sprite, clean white background'
 negative='extra limbs, extra fingers, duplicate sword, cropped, blurry, bad anatomy, background, text'
 result=pipe(prompt=prompt,negative_prompt=negative,image=init,control_image=pose,ip_adapter_image_embeds=[emb],strength=a.strength,controlnet_conditioning_scale=a.pose_scale,num_inference_steps=a.steps,guidance_scale=5.,generator=torch.Generator(device='cpu').manual_seed(20261104)).images[0]
 a.output.mkdir(parents=True);result.save(a.output/'result.png')
 (a.output/'receipt.json').write_text(json.dumps({'status':'SINGLE_FRAME_RESEARCH_NOT_ACCEPTED','base_revision':'a7e52b98680b1ba8ff7bce97c7f9f2e2e5337917','control_revision':'9ae9f970358db89e211b87c915f9535c6686d5ba','ip_adapter_revision':'018e402774aeeddd60609b4ecdb7e298259dc729','adapter_sha256':sha(a.adapter/'models'/a.adapter_file),'embedding_sha256':sha(a.embedding),'inputs':{x:sha(a.inputs/x) for x in ('init.png','guide.png','openpose.png')},'script_sha256':SCRIPT_SHA,'output_sha256':sha(a.output/'result.png'),'seed':20261104,'strength':a.strength,'controlnet_conditioning_scale':a.pose_scale,'ip_adapter_scale':a.ip_scale,'num_inference_steps':a.steps,'guidance_scale':5.,'dtype':'float16','device':'cpu','seconds':round(time.monotonic()-start,2),'prompt':prompt,'negative_prompt':negative,'limitations':['Single pose, not an animation.','Projected skeleton omits weapon/fingers and does not guarantee contact.','No cutouts, variants or gameplay.']},indent=2)+'\n')
if __name__=='__main__':main()
