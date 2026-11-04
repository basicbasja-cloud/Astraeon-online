"""Fetch pinned public SD1.5 anime weights and convert safely with bounded RAM."""
import argparse,hashlib,json,pathlib,subprocess,sys,urllib.request,shutil,time
REPO='stablediffusionapi/anything-v5';REV='095f2abb647d239d7988e34ea236d20153f11573'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--download-dir',type=pathlib.Path,required=True);a=p.parse_args()
 for path in (a.output,a.download_dir):
  if path.exists() or path.is_symlink():raise ValueError('Choose fresh temporary directories')
 meta=json.load(urllib.request.urlopen(f'https://huggingface.co/api/models/{REPO}/revision/{REV}?blobs=true',timeout=30));assert meta['sha']==REV
 records=[];a.output.mkdir(parents=True);a.download_dir.mkdir(parents=True)
 def fetch(path,dest,expected=None):
  dest.parent.mkdir(parents=True,exist_ok=True)
  with urllib.request.urlopen(f'https://huggingface.co/{REPO}/resolve/{REV}/{path}',timeout=90) as r,dest.open('xb') as f:
   done=0;threshold=256*1024*1024
   while True:
    b=r.read(4*1024*1024)
    if not b:break
    f.write(b);done+=len(b)
    if done>=threshold:print(path,done,'bytes',flush=True);threshold+=256*1024*1024
  digest=sha(dest)
  if expected and digest!=expected:raise ValueError('Source checksum mismatch')
  return digest
 small=[r['rfilename'] for r in meta['siblings'] if r['rfilename']=='model_index.json' or r['rfilename'].startswith(('tokenizer/','scheduler/')) or r['rfilename'] in ('text_encoder/config.json','unet/config.json','vae/config.json','README.md')]
 for path in small:records.append({'source':path,'sha256':fetch(path,a.output/path)})
 unet=json.loads((a.output/'unet/config.json').read_text())
 if unet['in_channels']!=4 or unet['cross_attention_dim']!=768:raise ValueError('Expected SD1.5 architecture')
 for sub,filename,target in [('unet','diffusion_pytorch_model.safetensors','diffusion_pytorch_model.fp16.safetensors'),('text_encoder','model.safetensors','model.fp16.safetensors'),('vae','diffusion_pytorch_model.safetensors','diffusion_pytorch_model.fp16.safetensors')]:
  path=sub+'/'+filename;source=next(r for r in meta['siblings'] if r['rfilename']==path);size=source['lfs']['size']
  if shutil.disk_usage(a.download_dir).free<size+64*1024*1024:raise ValueError('Not enough temporary download storage')
  temp=a.download_dir/'source.safetensors';digest=fetch(path,temp,source['lfs']['sha256']);dest=a.output/sub/target
  subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('convert_safetensors_fp32_to_fp16.py')),str(temp),str(dest)],check=True)
  records.append({'source':path,'bytes':size,'source_sha256':digest,'converted_file':sub+'/'+target,'converted_sha256':sha(dest)});temp.unlink()
 (a.output/'setup-receipt.json').write_text(json.dumps({'status':'TEMPORARY_MODEL_SETUP_NOT_ASSET_ACCEPTANCE','repo':REPO,'revision':REV,'license':meta.get('cardData',{}).get('license'),'records':records,'script_sha256':sha(pathlib.Path(__file__))},indent=2)+'\n');print('MODEL_SETUP_COMPLETED',flush=True)
if __name__=='__main__':main()
