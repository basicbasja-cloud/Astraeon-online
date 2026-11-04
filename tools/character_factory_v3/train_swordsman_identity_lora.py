"""CPU identity LoRA study using protected Swordsman artwork; never art approval."""
import argparse,hashlib,json,time,random,gc
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'
PROMPT='astraeon swordsman, full body illustrated fantasy game character, silver lavender hair, golden scarf, bronze armor and gauntlets, dark navy sleeves, cream tabard with gold borders, olive trousers, brown leather boots, steel sword, white background'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--steps',type=int,default=80);p.add_argument('--save-every',type=int,default=20);p.add_argument('--resume',type=Path);a=p.parse_args()
 if a.output.exists() or a.output.is_symlink():raise ValueError('Choose a fresh output')
 if not 1<=a.steps<=200 or a.save_every<1:raise ValueError('Bounded study only')
 import numpy as np,torch
 from PIL import Image
 from diffusers import AutoencoderKL,UNet2DConditionModel,DDPMScheduler,StableDiffusionPipeline
 from diffusers.utils import convert_state_dict_to_diffusers
 from peft import LoraConfig,get_peft_model_state_dict
 from transformers import CLIPTextModel,CLIPTokenizer
 torch.set_num_threads(4);torch.manual_seed(20261104);random.seed(20261104);start=time.monotonic();a.output.mkdir(parents=True)
 sources=[];tensors=[]
 for d in ('SW','NW','NE','SE'):
  for i in (0,4,8,15):
   path=SOURCE/d/'Master'/f'{i:03}.png';im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);im=bg.crop((68,40,452,424)).convert('RGB')
   sources.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path),'direction':d,'index':i});tensors.append(torch.from_numpy(np.asarray(im).copy()).permute(2,0,1).float()/127.5-1)
 # One fixed crop for all identity training images. This is not a runtime transform.
 (a.output/'study.json').write_text(json.dumps({'status':'IDENTITY_TRAINING_STUDY_NOT_PRODUCTION_ART','base_revision':'a7e52b98680b1ba8ff7bce97c7f9f2e2e5337917','base_repo':'Lykon/dreamshaper-8','base_license':'CreativeML OpenRAIL-M','prompt':PROMPT,'sources':sources,'crop':[68,40,452,424],'resolution':384,'seed':20261104,'rank':8,'learning_rate':1e-4,'steps':a.steps,'script_sha256':sha(Path(__file__)),'resume':str(a.resume) if a.resume else None},indent=2)+'\n')
 print('ENCODING',len(tensors),'protected source references',flush=True)
 vae=AutoencoderKL.from_pretrained(a.base,subfolder='vae',variant='fp16',torch_dtype=torch.float16,local_files_only=True).eval();vae.requires_grad_(False)
 generator=torch.Generator().manual_seed(20261104)
 with torch.no_grad():latents=torch.cat([vae.encode(t[None].half()).latent_dist.sample(generator=generator)*vae.config.scaling_factor for t in tensors])
 del vae,tensors;gc.collect()
 encoder=CLIPTextModel.from_pretrained(a.base,subfolder='text_encoder',variant='fp16',torch_dtype=torch.float16,local_files_only=True).eval();encoder.requires_grad_(False);tokenizer=CLIPTokenizer.from_pretrained(a.base,subfolder='tokenizer',local_files_only=True)
 with torch.no_grad():embedding=encoder(tokenizer(PROMPT,padding='max_length',max_length=tokenizer.model_max_length,truncation=True,return_tensors='pt').input_ids)[0]
 del encoder,tokenizer;gc.collect()
 unet=UNet2DConditionModel.from_pretrained(a.base,subfolder='unet',variant='fp16',torch_dtype=torch.float16,local_files_only=True);unet.requires_grad_(False)
 unet.add_adapter(LoraConfig(r=8,lora_alpha=8,init_lora_weights='gaussian',target_modules=['to_q','to_k','to_v','to_out.0']))
 for parameter in unet.parameters():
  if parameter.requires_grad:parameter.data=parameter.data.float()
 if a.resume:
  from safetensors.torch import load_file
  from peft import set_peft_model_state_dict
  from diffusers.utils import convert_unet_state_dict_to_peft
  weights=load_file(str(a.resume));weights={k.removeprefix('unet.'):v for k,v in weights.items()};set_peft_model_state_dict(unet,convert_unet_state_dict_to_peft(weights),adapter_name='default')
 unet.enable_gradient_checkpointing();unet.train();params=[q for q in unet.parameters() if q.requires_grad];optim=torch.optim.AdamW(params,lr=1e-4,eps=1e-8);scheduler=DDPMScheduler.from_pretrained(a.base,subfolder='scheduler',local_files_only=True)
 print('TRAINABLE',sum(q.numel() for q in params),'parameters',flush=True);losses=[]
 for step in range(1,a.steps+1):
  tick=time.monotonic();latent=latents[(step-1)%len(latents)][None];noise=torch.randn(latent.shape,generator=generator,dtype=latent.dtype);t=torch.randint(0,scheduler.config.num_train_timesteps,(1,),generator=generator).long();noisy=scheduler.add_noise(latent,noise,t)
  prediction=unet(noisy,t,encoder_hidden_states=embedding).sample
  target=scheduler.get_velocity(latent,noise,t) if scheduler.config.prediction_type=='v_prediction' else noise
  loss=torch.nn.functional.mse_loss(prediction.float(),target.float());loss.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.0)
  if not torch.isfinite(loss) or not torch.isfinite(norm):raise RuntimeError('Nonfinite training signal; study stops')
  optim.step();optim.zero_grad(set_to_none=True);row={'step':step,'loss':float(loss.detach()),'grad_norm':float(norm),'seconds':round(time.monotonic()-tick,3)};losses.append(row)
  with (a.output/'progress.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps(row),flush=True)
  if step%a.save_every==0 or step==a.steps:
   weights=convert_state_dict_to_diffusers(get_peft_model_state_dict(unet));name=f'identity-{step:03}.safetensors';StableDiffusionPipeline.save_lora_weights(a.output,unet_lora_layers=weights,weight_name=name)
   (a.output/(name+'.json')).write_text(json.dumps({'status':'ADAPTER_CHECKPOINT_NOT_CHARACTER_ACCEPTANCE','step':step,'weights_sha256':sha(a.output/name),'study_sha256':sha(a.output/'study.json'),'seconds':round(time.monotonic()-start,2)},indent=2)+'\n')
 print('TRAINING_COMPLETED',round(time.monotonic()-start,2),flush=True)
if __name__=='__main__':main()
