"""Encode a reference image for the SD1.5 IP-Adapter on CPU."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
SCRIPT_SHA=sha(Path(__file__))
def main():
 p=argparse.ArgumentParser();p.add_argument('--encoder',type=Path,required=True);p.add_argument('--image',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists() or a.output.is_symlink():raise ValueError('fresh output required')
 import torch
 from transformers import CLIPVisionModelWithProjection,CLIPImageProcessor
 torch.set_num_threads(4);enc=CLIPVisionModelWithProjection.from_pretrained(a.encoder,torch_dtype=torch.float16,local_files_only=True).eval();proc=CLIPImageProcessor(size=224,crop_size=224)
 with Image.open(a.image) as im:pixels=proc(im.convert('RGB'),return_tensors='pt').pixel_values.to(dtype=torch.float16)
 with torch.inference_mode():emb=enc(pixels).image_embeds
 result=torch.cat((torch.zeros_like(emb)[None,:],emb[None,:]),dim=0)
 if tuple(result.shape)!=(2,1,1024) or not torch.isfinite(result).all():raise ValueError('invalid embedding')
 a.output.mkdir(parents=True);torch.save(result,a.output/'embedding.pt')
 (a.output/'receipt.json').write_text(json.dumps({'status':'REFERENCE_EMBEDDING_NOT_ART','encoder_sha256':sha(a.encoder/'model.safetensors'),'encoder_config_sha256':sha(a.encoder/'config.json'),'image_sha256':sha(a.image),'embedding_sha256':sha(a.output/'embedding.pt'),'script_sha256':SCRIPT_SHA,'dtype':'float16','device':'cpu','limits':['CLIP embedding alone cannot establish character identity, pose, or animation quality.']},indent=2)+'\n')
if __name__=='__main__':main()
