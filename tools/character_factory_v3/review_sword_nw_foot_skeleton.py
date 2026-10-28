"""Project same-frame native foot chains into the Swordsman NW review canvas.

Bone head/tail coordinates are not shoe surfaces or verified ground contacts.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
GUIDE=BASE/'guides/c297971fcef09188ff60/manifest.json'
NATIVE=BASE/'research/native-rig-library-20261026/source/c297971fcef09188ff60.json'
BODY=BASE/'review/preserved-swordsman-canonical-cutouts-20261023/BasicAttack/NW/BodyCostume'
CANDIDATE=BASE/'review/swordsman-nw-registration-proposal-20261028/frame15/BodyCostume.png'
BINDING=BASE/'cutouts/f163f5e0b852f2767596/bindings.json'
STORE=BASE/'cutout-store/index.json'
NAMES=('foot_l','ball_l','ball_leaf_l','foot_r','ball_r','ball_leaf_r')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def project(camera,world):
    x,y,z=camera['rotation'];rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]]);ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]]);rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
    R=rz@ry@rx;delta=np.array(world)-np.array(camera['location']);ppm=768/camera['ortho_scale']
    return [384+float(np.dot(delta,R[:,0]))*ppm,384-float(np.dot(delta,R[:,1]))*ppm]
def build(output):
    if output.exists():raise ValueError('Choose a fresh output')
    guide=json.loads(GUIDE.read_text());native=json.loads(NATIVE.read_text());bindings=json.loads(BINDING.read_text());store=json.loads(STORE.read_text())
    if native['source_manifest_sha256']!=sha(GUIDE):raise ValueError('Native pose library refers to another guide')
    records={r['index']:r for r in bindings['frames'] if r['direction']=='NW'};camera=guide['views']['NW']['camera'];frames=guide['views']['NW']['frames']
    rows=[('00 original',0,BODY/'000.png'),('14 original',14,BODY/'014.png'),('15 original',15,BODY/'015.png'),('15 candidate',15,CANDIDATE)]
    box=(300,480,445,590);page=Image.new('RGB',(1740,405),'#ddd');draw=ImageDraw.Draw(page);pins={};observations=[];max_error=0.
    for col,(title,index,path) in enumerate(rows):
        native_frame=native['frames'][index]; source=frames[index];bones=native_frame['bones']
        if native_frame['action']!=source['action'] or abs(native_frame['source_frame']-source['source_frame'])>1e-7:raise ValueError('Native frame differs from guide')
        points={n:{k:project(camera,bones[n][k]) for k in ('head','tail')} for n in NAMES}
        for n in ('foot_l','foot_r'):
            expected=np.array(source['landmarks'][n])*.5;error=float(np.linalg.norm(np.array(points[n]['head'])-expected));max_error=max(max_error,error)
            if error>0.001:raise ValueError('Camera projection differs from recorded guide')
        record=records[index];asset=store['assets'][record['assets']['BodyCostume']];oid=asset['object'];source_path=(ROOT/store['objects'][oid]['file']).resolve()
        if not source_path.is_relative_to(ROOT):raise ValueError('Object outside repository')
        src=Image.open(source_path).convert('RGBA');art=Image.open(path).convert('RGBA')
        if hashlib.sha256(src.tobytes()).hexdigest()!=oid:raise ValueError('Imported object changed')
        if col<3 and src.tobytes()!=art.tobytes():raise ValueError('Original artwork differs from import')
        if col==3:
            shifted=Image.new('RGBA',src.size);shifted.alpha_composite(src,(-8,0))
            if shifted.tobytes()!=art.tobytes():raise ValueError('Candidate differs from proposed translation')
        tile=Image.new('RGBA',art.size,'#ddd');tile.alpha_composite(art);marker=ImageDraw.Draw(tile)
        for n in NAMES:
            color='#00bbdf' if n.endswith('_l') else '#f64238';h=points[n]['head'];t=points[n]['tail']
            marker.line((tuple(h),tuple(t)),fill=color,width=2);marker.ellipse((h[0]-2,h[1]-2,h[0]+2,h[1]+2),fill=color)
        page.paste(tile.crop(box).resize((435,330),Image.Resampling.NEAREST).convert('RGB'),(col*435,60));draw.text((col*435+5,10),title,fill='black');draw.text((col*435+5,28),'cyan=left chain   red=right chain',fill='black')
        pins[str(path.relative_to(ROOT))]=sha(path);pins[str(source_path.relative_to(ROOT))]=sha(source_path);observations.append({'frame':index,'candidate':col==3,'projected_bones':points})
    output.mkdir(parents=True);page.save(output/'foot-chains.png')
    for p in (GUIDE,NATIVE,BINDING,STORE,Path(__file__).resolve()):pins[str(p.relative_to(ROOT))]=sha(p)
    receipt={'status':'NATIVE_FOOT_CHAIN_OVERLAY_NOT_CONTACT_APPROVAL','projection_max_error_author_px':max_error,'source_sha256':pins,'views':['NW'],'frames':[0,14,15],'bone_names':list(NAMES),'observations':observations,'interpretation':'Bone origins and tails are not shoe surfaces, sole-contact points, or proof of painted foot identity. Candidate is unapproved.','contact_verified':False,'art_approved':False,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=build(a.output);print(json.dumps({'status':r['status'],'projection_max_error_author_px':r['projection_max_error_author_px']}))
