"""Convert F32 safetensors to F16 while copying other dtypes, bounded RAM."""
import sys,json,struct,numpy as np,os
src,dst=sys.argv[1:]
if os.path.exists(dst):raise ValueError('fresh destination required')
with open(src,'rb') as f:
 size=struct.unpack('<Q',f.read(8))[0];header=json.loads(f.read(size));data_start=8+size
 specs=[];pos=0
 for name,item in header.items():
  if name=='__metadata__':continue
  dtype=item['dtype'];a,b=item['data_offsets'];length=b-a
  if dtype=='F32':
   if length%4:raise ValueError('unaligned tensor')
   newlen=length//2;item['dtype']='F16'
  else:newlen=length
  specs.append((name,dtype,a,b));item['data_offsets']=[pos,pos+newlen];pos+=newlen
 raw=json.dumps(header,separators=(',',':')).encode();raw+=b' '*((-len(raw))%8)
 with open(dst,'xb') as out:
  out.write(struct.pack('<Q',len(raw)));out.write(raw)
  for name,dtype,a,b in specs:
   f.seek(data_start+a);remaining=b-a
   while remaining:
    take=min(remaining,4*2**20);buf=f.read(take)
    if len(buf)!=take:raise ValueError('truncated tensor '+name)
    out.write(np.frombuffer(buf,dtype='<f4').astype('<f2').tobytes() if dtype=='F32' else buf);remaining-=take
print('converted',len(specs),'tensors')
