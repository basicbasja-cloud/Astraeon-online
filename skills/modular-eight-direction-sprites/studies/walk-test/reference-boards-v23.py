"""Rebuild native-clock boards from captured files. No camera tracking or pose fitting."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/combat-gait-study-v23/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    records=[]
    for p in sorted(OUT.glob('RO-*action*.png')):
        if '-review' in p.name:continue
        im=Image.open(p);cw=max(256,im.width*3+32);ch=im.height*3+58
        board=Image.new('RGB',(cw*im.n_frames,ch),'#272727');draw=ImageDraw.Draw(board);clock=0;fs=[]
        for i in range(im.n_frames):
            im.seek(i);duration=im.info.get('duration',0);f=im.convert('RGBA').resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
            board.paste(f,(cw*i+(cw-f.width)//2,48),f);draw.text((cw*i+8,8),f'{p.stem}\n{i} / {clock}ms / {duration}ms',fill='white')
            fs.append({'index':i,'time_ms':clock,'duration_ms':duration});clock+=duration
        name=p.stem.replace('-action87','')+'-review.png' if p.stem.startswith('RO-weapon') else p.stem+'-review.png'
        board.save(OUT/name);records.append({'file':p.name,'sha256':sha(p),'scale_uniform':3,'board':name,'frames':fs,'total_ms':clock})
    dump(OUT/'RO-board-provenance.json',records)
    # Exact source frames, plus a separately labeled cropped diagnostic.
    p=OUT/'witchcrafter-2018-attack-combo.gif';im=Image.open(p);times=[];clock=0
    for i in range(im.n_frames):im.seek(i);duration=im.info.get('duration',0);times.append({'index':i,'time_ms':clock,'duration_ms':duration});clock+=duration
    directory=OUT/'witchcrafter-two-strikes';directory.mkdir(exist_ok=True);full=OUT/'witchcrafter-two-strikes-full';full.mkdir(exist_ok=True)
    crop=[160,260,330,495];records=[]
    for i in range(9,45):
        im.seek(i);f=im.convert('RGBA');whole=full/f'{i:04}.png';whole_image=f.copy();whole_image.save(whole);part=f.crop(crop);path=directory/f'{i:04}.png';part.save(path)
        records.append({**times[i],'path':str(path.relative_to(ROOT)),'sha256':sha(path),'full_path':str(whole.relative_to(ROOT)),'full_sha256':sha(whole),'crop':crop,'camera_tracking_applied':False,'crop_excludes_parts_of_trail':True,'visible_foot_contact':'occluded_by_grass_unknown','native_sprite_key_id':None})
    source={'url':'https://forum.defold.com/uploads/default/original/2X/9/91442b9a25d09fab508a22eae81a680f86293d89.gif','post':'https://forum.defold.com/t/witchcrafter-empire-legends/32285/12','date':'2018-11-07','sha256':sha(p)}
    dump(OUT/'witchcrafter-clock.json',{'source':source,'canvas':list(im.size),'frames':times,'total_ms':clock,'scope':'Older developer capture; not asserted identical to user isolated2021clip.'})
    dump(directory/'capture.json',{'source':source,'selection':list(range(9,45)),'crop_fixed':True,'frames':records,'scope':'Decoded screenshot exposures, not native sprite keys/bones/physical contact proof.'})
    print('NATIVE_REFERENCE_BOARDS',len(records),'Witchcrafter selected exposures;',len(times),'full timestamps')
if __name__=='__main__':main()
