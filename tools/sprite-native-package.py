"""Lossless four-slot .aseprite packaging + independent live SPA roundtrip.

Writes the public RGBA native file format, not new art. Linked cels encode exact
holds. Uses ordinary supported SPA inspection/validation/PNG sequence exports;
no Lua fallback, capability overrides, color conversion or pose fitting.
"""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,struct,zlib,importlib.util,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def chunk(kind,data):return struct.pack('<IH',len(data)+6,kind)+data

def package(clip_path,full_path,out,spa,aseprite,verify=True):
    spec=importlib.util.spec_from_file_location('whole_body',ROOT/'tools/whole-body-toolchain.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    clip_path=Path(clip_path).resolve();full_path=Path(full_path).resolve();_,clip=m.clip_input(clip_path);full=json.loads(full_path.read_text());out=Path(out).resolve()
    assert clip['canvas']==full['canvas'] and len(clip['frames'])==len(full['frames'])
    w,h=clip['canvas'];count=len(clip['frames']);assert 0<count<=65535 and 0<w<=65535 and 0<h<=65535
    orders={tuple(f['order'])for f in clip['frames']};assert len(orders)==1,'Changing equipment depth needs authored physical passes'
    order=list(orders.pop());images={};data=[]
    def read(slot):
        p=clip_path.parent/slot['asset']
        if str(p)not in images:
            im=Image.open(p);assert not im.info.get('icc_profile'),'Explicit ICC adapter required'
            images[str(p)]=im.convert('RGBA')
        return images[str(p)]
    for i,(f,expected)in enumerate(zip(clip['frames'],full['frames'])):
        assert f['duration_ms']==expected['duration_ms'];p=full_path.parent/expected['path'];assert sha(p)==expected['sha256']
        image=Image.open(p).convert('RGBA');comp=Image.new('RGBA',(w,h));parts=[]
        for name in order:
            slot=f['slots'][name]
            if slot:
                im=read(slot);comp.alpha_composite(im);raw=im.tobytes();parts.append((order.index(name),hashlib.sha256(raw).hexdigest(),raw))
        a=np.array(image);b=np.array(comp);visible=a[:,:,3]>0
        assert np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[visible],b[visible]),('Source composition mismatch',i)
        data.append((f['duration_ms'],parts))
    # No output exists until every source hash, canvas, clock and composition
    # has passed preflight. The original assets are always read-only.
    out.mkdir(parents=True,exist_ok=False);native=out/'sprite.aseprite';frames=[];first={};linked=0;compressed=0
    for i,(duration,parts)in enumerate(data):
        chunks=[]
        if i==0:
            chunks.append(chunk(0x2007,struct.pack('<HHI8x',1,0,0))) # standard sRGB metadata, no conversion
            for name in order:
                encoded=name.encode('utf8');chunks.append(chunk(0x2004,struct.pack('<6HB3xH',3,0,0,0,0,0,255,len(encoded))+encoded))
        for layer,digest,raw in parts:
            key=(layer,digest)
            if key in first:
                payload=struct.pack('<HhhBHh5xH',layer,0,0,255,1,0,first[key]);linked+=1
            else:
                payload=struct.pack('<HhhBHh5xHH',layer,0,0,255,2,0,w,h)+zlib.compress(raw,9);first[key]=i;compressed+=1
            chunks.append(chunk(0x2005,payload))
        body=b''.join(chunks);frames.append(struct.pack('<IHHH2xI',len(body)+16,0xF1FA,len(chunks),duration,len(chunks))+body)
    body=b''.join(frames);header=bytearray(128);struct.pack_into('<I5HIH',header,0,len(body)+128,0xA5E0,count,w,h,32,1,data[0][0]);header[34]=1;header[35]=1
    native.write_bytes(header+body)
    report={'tool_sha256':sha(Path(__file__)), 'native_file':native.name,'native_sha256':sha(native),'source_clip_sha256':sha(clip_path),'source_full_clip_sha256':sha(full_path),'public_format_spec':'aseprite/aseprite@b3e34acbae812b8a1d814c2e6285343b351c8945/docs/ase-file-specs.md','spec_sha256':'31a6a80526c24209361fc35f9431bd8909603bb106bb6c3ed866f9af28976ae3','frames':count,'layers_bottom_to_top':order,'durations_ms':[r[0]for r in data],'compressed_cels':compressed,'linked_hold_cels':linked,'pixels_transformed':False,'color_profile':'assign standard sRGB metadata; no pixel conversion','art_approval_granted':False,'native_roundtrip_pass':False,'production_pass':False}
    save(out/'package-review.json',report)
    if not verify:return report
    events=[]
    def call(command,payload):
        request={'aseprite':str(Path(aseprite).resolve()),'timeout_seconds':30,**payload}
        proc=subprocess.run([str(Path(spa).resolve()),*command.split(),'--input-json','-'],input=json.dumps(request),capture_output=True,text=True)
        try:result=json.loads(proc.stdout)
        except json.JSONDecodeError:raise RuntimeError(proc.stdout+proc.stderr)
        events.append({'operation':command,'request':request,'result':result,'returncode':proc.returncode});save(out/'spa-operations.json',events)
        assert proc.returncode==0 and result.get('status')=='success',result
        return result
    inspected=call('sprite get',{'sprite_file':str(native),'inspection_scope':['frames','layers','cels']});save(out/'native-inspection.json',inspected)
    assert [r['duration_ms']for r in inspected['frames']]==report['durations_ms']
    assert [r['name']for r in sorted(inspected['layers'],key=lambda r:r['path'])]==order
    valid=call('sprite validate',{'sprite_file':str(native),'expected':{'width':w,'height':h,'color_mode':'rgb','frame_count':count}});assert valid['valid']and not valid['findings']
    # Bound each real export below SPA's declared16Mpixel resource ceiling.
    batch=max(1,min(40,16777216//(w*h)));checks=[]
    for start in range(0,count,batch):
        numbers=list(range(start+1,min(count,start+batch)+1));dest=out/f'export-{start:04}';dest.mkdir()
        call('export sequence',{'source_sprite_file':str(native),'playback':{'kind':'frames','frame_numbers':numbers},'layer_composition':{'mode':'visible'},'destination':{'directory':str(dest),'filename_format':'{frame00}.png','if_exists':'fail'}})
        for local,number in enumerate(numbers):
            exported=dest/f'{local:02}.png';assert exported.is_file();a=np.array(Image.open(full_path.parent/full['frames'][number-1]['path']).convert('RGBA'));b=np.array(Image.open(exported).convert('RGBA'));visible=a[:,:,3]>0
            same=a.shape==b.shape and np.array_equal(a[:,:,3],b[:,:,3])and np.array_equal(a[visible],b[visible]);checks.append({'frame':number-1,'exact_visible_RGBA':same,'export_sha256':sha(exported)})
    report['native_roundtrip_pass']=all(r['exact_visible_RGBA']for r in checks);report['export_frames']=checks;save(out/'package-review.json',report);assert report['native_roundtrip_pass'],'Actual native export pixels changed'
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--clip',type=Path,required=True);p.add_argument('--full',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--spa',type=Path,default=ROOT/'work/tool-runtime/spa-env/bin/spa');p.add_argument('--aseprite',type=Path,default=ROOT/'work/tool-runtime/aseprite-build/bin/aseprite');p.add_argument('--pack-only',action='store_true');a=p.parse_args();r=package(a.clip,a.full,a.out,a.spa,a.aseprite,not a.pack_only);print(json.dumps({k:r[k]for k in ['native_file','frames','compressed_cels','linked_hold_cels','native_roundtrip_pass']}))
