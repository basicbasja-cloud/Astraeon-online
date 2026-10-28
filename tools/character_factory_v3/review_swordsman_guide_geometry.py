"""Review preserved Swordsman art against same-frame projected rig landmarks.

Diagnostic only: no alpha-bounds statistic certifies planted contact, anatomy,
visual quality, or game readiness. Full-canvas scale remains fixed throughout.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'
SOURCE = ROOT / 'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'
VIEWS = ('SW', 'NW', 'NE', 'SE')
JOINTS = ('head', 'pelvis', 'hand_l', 'hand_r', 'foot_l', 'foot_r')
BONES = (('head','pelvis'), ('hand_l','pelvis'), ('hand_r','pelvis'), ('foot_l','pelvis'), ('foot_r','pelvis'))


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output):
    if output.exists():
        raise ValueError('Choose a fresh output directory')
    ledger = read(BASE/'ledger.json')
    jobs = [j for j in ledger['paint_jobs'].values() if j['character']=='swordsman-male-patch001' and 'BasicAttack' in j['actions']]
    if len(jobs)!=1: raise ValueError('Ambiguous preserved action')
    job=jobs[0]; folder=BASE/'cutouts'/job['id']; bindings=read(folder/'bindings.json'); receipt=read(folder/'import-receipt.json')
    if receipt.get('paint_job') != job['id'] or not receipt.get('all_frames_present'): raise ValueError('Missing technical import')
    guide_path=BASE/'guides'/job['guide_job']/'manifest.json'; guide=read(guide_path)
    if guide['job']['id'] != job['guide_job']: raise ValueError('Wrong motion guide')
    store=read(BASE/'cutout-store/index.json'); records={(x['direction'],x['index']):x for x in bindings['frames']}
    expected={(v,i) for v in VIEWS for i in range(16)}
    if set(records)!=expected: raise ValueError('Unexpected binding sequence')
    durations=read(SOURCE/'assembly-audit.json')['durations_ms']
    if len(durations)!=16: raise ValueError('Unexpected timeline')
    cache={}; rows=[]; pictures=[]
    def image_for(asset_id):
        asset=store['assets'][asset_id];oid=asset['object'];obj=store['objects'][oid]
        if oid not in cache:
            path=(ROOT/obj['file']).resolve()
            if not path.is_relative_to(ROOT): raise ValueError('Cutout outside repository')
            image=Image.open(path).convert('RGBA')
            if list(image.size)!=[768,768] or hashlib.sha256(image.tobytes()).hexdigest()!=oid: raise ValueError('Cutout changed')
            cache[oid]=image
        return cache[oid]
    output.mkdir(parents=True)
    for i in range(16):
        board=Image.new('RGB',(960,264),'#e6e6e6');draw=ImageDraw.Draw(board)
        for column,view in enumerate(VIEWS):
            record=records[view,i]; source=guide['views'][view]['frames'][i]; joints=source['landmarks']
            if not all(k in joints for k in JOINTS): raise ValueError('Guide joint missing')
            master=Image.new('RGBA',(768,768)); parts={}
            for role in record['layer_draw_order']:
                if role not in record['assets']: continue
                asset=store['assets'][record['assets'][role]]
                if asset.get('role')!=role or asset.get('pose_id')!=record['pose_id'] or asset.get('camera_id')!=record['camera_id']:
                    raise ValueError('Asset role, pose or camera differs from binding')
                part=image_for(record['assets'][role]);parts[role]=part;master.alpha_composite(part)
            if not {'HeadHair','BodyCostume','Weapon'}<=parts.keys(): raise ValueError('Core part missing')
            image=master.resize((240,240),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(240,240),'#e6e6e6');tile.alpha_composite(image)
            mark=ImageDraw.Draw(tile); xy={k:(joints[k][0]*240/1536,joints[k][1]*240/1536) for k in JOINTS}
            for a,b in BONES:mark.line((xy[a],xy[b]),fill=(34,185,225,255),width=1)
            for name,(x,y) in xy.items():
                color=(255,87,60,255) if name.startswith('foot') else (255,230,35,255)
                mark.ellipse((x-2,y-2,x+2,y+2),fill=color)
            board.paste(tile.convert('RGB'),(column*240,24));draw.text((column*240+4,4),f'{view} / frame {i:02d}',fill='black')
            hair=parts['HeadHair'].getchannel('A').getbbox();body=parts['BodyCostume'].getchannel('A').getbbox()
            if not hair or not body: raise ValueError('Empty head or body')
            rows.append({'direction':view,'index':i,'source_frame':source['source_frame'],
                'guide_head_y_runtime':round(xy['head'][1],4), 'guide_foot_l_y_runtime':round(xy['foot_l'][1],4),
                'guide_foot_r_y_runtime':round(xy['foot_r'][1],4),
                'hair_alpha_top_runtime':round(hair[1]*240/768,4),'body_alpha_bottom_runtime':round(body[3]*240/768,4),
                'visible_span_runtime':round((body[3]-hair[1])*240/768,4),
                'note':'Unverified alpha bounds: hair and body bottom are not tracked anatomical contact landmarks'})
        pictures.append(board)
    pictures[0].save(output/'four-view-guide-overlay.gif',save_all=True,append_images=pictures[1:],duration=durations,loop=0,disposal=2)
    enlarged=[frame.resize((1920,528),Image.Resampling.NEAREST) for frame in pictures]
    enlarged[0].save(output/'four-view-guide-overlay-2x.gif',save_all=True,append_images=enlarged[1:],duration=durations,loop=0,disposal=2)
    pictures[0].save(output/'frame00.png');pictures[7].save(output/'frame07.png')
    with (output/'frame-metrics.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');writer.writeheader();writer.writerows(rows)
    proof={'status':'SAME_FRAME_GUIDE_OVERLAY_DIAGNOSTIC_NOT_VISUAL_APPROVAL','frames':len(rows),'directions':list(VIEWS),'durations_ms':durations,'guide_sha256':sha(guide_path),'binding_sha256':sha(folder/'bindings.json'),'ledger_sha256':sha(BASE/'ledger.json'),'store_index_sha256':sha(BASE/'cutout-store/index.json'),'timing_source_sha256':sha(SOURCE/'assembly-audit.json'),'implementation_sha256':sha(Path(__file__)),'object_hashes_checked':len(cache),'shared_canvas':[768,768],'runtime_canvas':[240,240],'frame_specific_fit':False,'contact_verified':False,'art_approved':False,'runtime_admitted':False,'interpretation':'Body alpha bottom and hair alpha top are provisional visible bounds, not anatomically tracked crown/foot landmarks; pose and occlusion change them. GIF repeats a one-shot for inspection only.'}
    (output/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();print(json.dumps(build(args.output)))
