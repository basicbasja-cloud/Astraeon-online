"""Recompress only unreferenced inactive guide-cache IDAT, preserving visible pixels.

All non-IDAT PNG chunks remain byte-identical, including color/date metadata.
Only fully transparent RGB is normalized; every alpha and visible RGB is exact.
Never touch current jobs, sealed/frozen captures, source art or referenced caches.
"""
import numpy as np
import argparse,concurrent.futures,hashlib,io,json,re,struct,subprocess,zlib
from pathlib import Path
from PIL import Image
from patch001_factory import BASE,ROOT


def repack(raw):
    if raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Not PNG')
    chunks=[];position=8
    while position<len(raw):
        size=struct.unpack('>I',raw[position:position+4])[0];end=position+size+12
        if end>len(raw):raise ValueError('Truncated PNG')
        block=raw[position:end];kind=block[4:8];data=block[8:-4]
        if zlib.crc32(kind+data)&0xffffffff!=struct.unpack('>I',block[-4:])[0]:raise ValueError('PNG CRC differs')
        chunks.append((kind,data,block));position=end
    source=Image.open(io.BytesIO(raw));source.load()
    if source.mode not in ['RGB','RGBA']:raise ValueError('Unsupported cache mode')
    pixels=np.array(source);normalized=pixels.copy();cleared=0
    if source.mode=='RGBA':
        selected=pixels[:,:,3]==0;cleared=int(np.any(pixels[selected,:3]!=0,axis=1).sum());normalized[selected,:3]=0
    stream=io.BytesIO();Image.fromarray(normalized).save(stream,format='PNG',compress_level=6)
    encoded=stream.getvalue();position=8;packed=b'';new_header=None
    while position<len(encoded):
        length=struct.unpack('>I',encoded[position:position+4])[0];kind=encoded[position+4:position+8];data=encoded[position+8:position+8+length]
        if kind==b'IHDR':new_header=data
        if kind==b'IDAT':packed+=data
        position+=length+12
    if new_header!=next(data for kind,data,_ in chunks if kind==b'IHDR'):raise ValueError('PNG encoding geometry/mode changed')
    identity=hashlib.sha256(normalized.tobytes()).hexdigest()
    compressed=b''.join(data for kind,data,_ in chunks if kind==b'IDAT')
    if len(packed)>=len(compressed):return raw,{'canonical_pixel_sha256':identity,'alpha_zero_rgb_normalized_pixels':0}
    result=[raw[:8]];written=False
    for kind,data,block in chunks:
        if kind==b'IDAT':
            if not written:result.append(struct.pack('>I',len(packed))+b'IDAT'+packed+struct.pack('>I',zlib.crc32(b'IDAT'+packed)&0xffffffff));written=True
        else:result.append(block)
    result=b''.join(result)
    with Image.open(io.BytesIO(result))as after:
        if source.mode!=after.mode or source.size!=after.size or normalized.tobytes()!=after.tobytes()or source.info!=after.info:raise ValueError('Visible pixels/alpha/metadata changed')
    return result,{'canonical_pixel_sha256':identity,'alpha_zero_rgb_normalized_pixels':cleared}



def compact(path):
    raw=path.read_bytes();packed,payload=repack(raw)
    if raw!=packed:
        temporary=path.with_suffix('.idat.tmp');temporary.write_bytes(packed);temporary.replace(path)
    return {'file':str(path.relative_to(ROOT)),'bytes_before':len(raw),'bytes_after':len(packed),'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(packed).hexdigest(),**payload,'visible_rgb_alpha_and_non_idat_chunks_changed':False}


def run(plan,output):
    if output.exists():raise ValueError('Choose a fresh receipt')
    selected=json.loads(plan.read_text());active=set(json.loads((BASE/'ledger.json').read_text())['guide_jobs']);folders=[]
    for row in selected:
        key=row['guide'];folder=BASE/'guides'/key
        if key in active or not re.fullmatch('[a-f0-9]{20}',key):raise ValueError('Not an inactive native cache')
        manifest=json.loads((folder/'manifest.json').read_text())
        if manifest.get('render_pose_freeze')or manifest.get('sampling_override'):raise ValueError('Sealed/frozen cache excluded')
        search=subprocess.run(['rg','--no-ignore','-q','-F',key,'.','-g','*.json','-g','*.md','-g','*.py','-g','*.js','-g','*.txt','-g','!**/guides/**','-g','!**/.git/**','-g','!authoring/characters/factory-v3/patch-0.0.1/guide-jobs/**','-g','!authoring/characters/factory-v3/patch-0.0.1/paint-jobs/**','-g','!**/research/canonical-rig-runtime-20261024/cache-compaction*.json'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if search.returncode!=1:raise ValueError('Cache is referenced outside planning descriptors: '+key)
        folders.append(folder)
    output.parent.mkdir(parents=True,exist_ok=True);rows=[]
    for folder in folders:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:rows.extend(pool.map(compact,sorted(folder.glob('*/*.png'))))
        result={'status':'INACTIVE_UNREFERENCED_CACHE_REPACKED_EXACT_VISIBLE_PIXELS_ALPHA_AND_METADATA','current_jobs_touched':False,'source_art_touched':False,'files':rows,'bytes_before':sum(r['bytes_before']for r in rows),'bytes_after':sum(r['bytes_after']for r in rows)};output.write_text(json.dumps(result,indent=2)+'\n');print(folder.name,result['bytes_before']-result['bytes_after'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.plan,a.output)
