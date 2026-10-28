"""Visualize source foot-bone projections on preserved and proposed artwork.

Projected rig bones and alpha silhouettes are distinct observations. No foot
identity, planted contact, or visible image quality is certified by this tool.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
GUIDE=BASE/'guides/c297971fcef09188ff60/manifest.json'
BODY=BASE/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack/NW/BodyCostume'
CANDIDATE=BASE/'review/swordsman-nw-registration-proposal-20261028/frame15/BodyCostume.png'
BINDING=BASE/'cutouts/f163f5e0b852f2767596/bindings.json'
STORE=BASE/'cutout-store/index.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def build(output):
    if output.exists():raise ValueError('Choose a fresh output')
    g=json.loads(GUIDE.read_text())['views']['NW']['frames']; bindings=json.loads(BINDING.read_text()); store=json.loads(STORE.read_text())
    records={r['index']:r for r in bindings['frames'] if r['direction']=='NW'}
    if not {0,14,15} <= records.keys():raise ValueError('Missing imported frame')
    rows=[('00 original',0,BODY/'000.png'),('14 original',14,BODY/'014.png'),('15 original',15,BODY/'015.png'),('15 candidate',15,CANDIDATE)]
    box=(300,480,445,590);page=Image.new('RGB',(1740,405),'#ddd');draw=ImageDraw.Draw(page);pins={}
    for col,(title,index,path) in enumerate(rows):
        art=Image.open(path).convert('RGBA');record=records[index];asset=store['assets'][record['assets']['BodyCostume']];oid=asset['object']
        original=(ROOT/store['objects'][oid]['file']).resolve()
        if not original.is_relative_to(ROOT):raise ValueError('Source object outside repository')
        pix=Image.open(original).convert('RGBA')
        if hashlib.sha256(pix.tobytes()).hexdigest()!=oid:raise ValueError('Imported source pixels changed')
        if col<3 and pix.tobytes()!=art.tobytes():raise ValueError('Reference and imported body differ')
        if col==3:
            shifted=Image.new('RGBA',pix.size);shifted.alpha_composite(pix,(-8,0))
            if shifted.tobytes()!=art.tobytes():raise ValueError('Candidate does not match reviewed whole-frame translation')
        pins[str(path.relative_to(ROOT))]=sha(path);pins[str(original.relative_to(ROOT))]=sha(original)
        tile=Image.new('RGBA',art.size,'#ddd');tile.alpha_composite(art);markers=ImageDraw.Draw(tile)
        for key,color in [('foot_l','#00d5f5'),('foot_r','#ff3b30')]:
            x,y=(v/2 for v in g[index]['landmarks'][key]);markers.ellipse((x-3,y-3,x+3,y+3),fill=color)
        crop=tile.crop(box).resize((435,330),Image.Resampling.NEAREST);page.paste(crop.convert('RGB'),(col*435,60));draw.text((col*435+5,10),title,fill='black');draw.text((col*435+5,28),'cyan=guide foot L   red=guide foot R',fill='black')
    output.mkdir(parents=True);page.save(output/'foot-landmarks.png')
    pins.update({str(p.relative_to(ROOT)):sha(p) for p in (GUIDE,BINDING,STORE,Path(__file__).resolve())})
    proof={'status':'PROVISIONAL_FOOT_ASSOCIATION_NOT_CONTACT_APPROVAL','views':['NW'],'frames':[0,14,15],'candidate_translation_author_px':[-8,0],'shared_inspection_crop_author_px':list(box),'enlargement':3,'source_sha256':pins,'observation':'Projected foot R lies on the visible forward boot; foot L marker lies over the painted lower-leg region rather than an unambiguously distinct rear shoe. Bone origins are not ground-contact pixels.','contact_verified':False,'art_approved':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps({k:v for k,v in build(a.output).items() if k!='source_sha256'}))
