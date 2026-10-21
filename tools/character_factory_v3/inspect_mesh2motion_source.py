#!/usr/bin/env python3
"""Inspect source GLB animation endpoints and duplicate targets without importing it."""
import argparse,collections,hashlib,json,struct
from pathlib import Path


def inspect(path):
    data=path.read_bytes();magic,version,size=struct.unpack_from('<III',data)
    if magic!=0x46546c67 or version!=2 or size!=len(data):raise ValueError('Expected a complete GLB 2 file')
    length,kind=struct.unpack_from('<II',data,12);document=json.loads(data[20:20+length]);binary_start=20+length
    bin_length,bin_kind=struct.unpack_from('<II',data,binary_start);blob=data[binary_start+8:binary_start+8+bin_length]
    def accessor(index):
        a=document['accessors'][index];view=document['bufferViews'][a['bufferView']]
        if a['componentType']!=5126:raise ValueError('Animation audit expects float accessors')
        width={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];start=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',width*4)
        return [struct.unpack_from('<'+'f'*width,blob,start+i*stride) for i in range(a['count'])]
    actions=[]
    for animation in document['animations']:
        if not animation['name'].startswith('Sword'):continue
        same=0;end=0
        for sampler in animation['samplers']:
            values=accessor(sampler['output']);times=accessor(sampler['input']);end=max(end,times[-1][0]);same+=max(abs(x-y) for x,y in zip(values[0],values[-1]))<1e-5
        targets=collections.Counter((c['target']['node'],c['target']['path']) for c in animation['channels'])
        actions.append({'name':animation['name'],'duration_seconds':round(end,6),'last_key_at_24fps':round(end*24,5),'sampler_count':len(animation['samplers']),'samplers_repeating_first_at_terminal_key':same,'all_channels_repeat_first_at_terminal_key':same==len(animation['samplers']),'duplicate_channel_targets':sum(n-1 for n in targets.values())})
    return {'source':str(path),'source_sha256':hashlib.sha256(data).hexdigest(),'source_fps_for_review':24,'actions':actions,'interpretation':'Repeated terminal values and the interpolation leading into them need explicit handling for one-shot playback. They do not establish a natural recovery. Avoid C_RM duplicate-target import warnings; the unmodified C action has unique targets.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();r=inspect(args.source);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
