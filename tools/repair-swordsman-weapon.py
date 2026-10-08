#!/usr/bin/env python3
"""Targeted offline sword repair; preserve the other five painted source strips."""
import argparse, datetime, hashlib, importlib.util, json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--body', default='male')
parser.add_argument('--animation', required=True, choices=['Hit'])
parser.add_argument('--base-candidate', required=True)
args = parser.parse_args()
source = ROOT/'authoring/characters/swordsman-production'
body = source/args.body
definition = json.loads((body/'definition.json').read_text())
clip = definition['clips'][args.animation]
count = len(clip['durations'])
parts = definition['defaultParts']
guides = json.loads((body/'pose-guides.json').read_text())['guides']
paths = {slot:body/'normalized/parts'/part/args.animation/'strip.png' for slot,part in parts.items()}
strips = {slot:Image.open(path).convert('RGBA') for slot,path in paths.items()}
history = body/'motion-candidates'/args.animation
base = history/args.base_candidate
spec = importlib.util.spec_from_file_location('painter',ROOT/'tools/build-swordsman-production.py')
painter = importlib.util.module_from_spec(spec);spec.loader.exec_module(painter)

def composite(layers):
    film = Image.new('RGBA',(320*count,320*8))
    for row,direction in enumerate(definition['directions']):
        for index,frame in enumerate(clip['directions'][direction]['frames']):
            rect = (index*320,row*320,(index+1)*320,(row+1)*320)
            cell = Image.new('RGBA',(320,320))
            for slot in frame.get('drawOrder',definition['drawOrder']):
                cell.alpha_composite(layers[slot].crop(rect))
            film.paste(cell,(index*320,row*320))
    return film

assert np.array_equal(np.asarray(composite(strips)),np.asarray(Image.open(base/'composite-strip.png').convert('RGBA'))), 'Current source does not match repair base'
unchanged = {slot:hashlib.sha256(path.read_bytes()).hexdigest() for slot,path in paths.items() if slot!='Weapon'}
weapon = Image.new('RGBA',(320*count,320*8))
for row,direction in enumerate(definition['directions']):
    master = Image.open(body/'modular-masters'/direction/'Weapon.png').convert('RGBA')
    for index,frame in enumerate(clip['directions'][direction]['frames']):
        cell = painter.rigid_weapon(master,guides[direction]['hand_R'],frame['sockets']['hand_R'],0.)
        weapon.paste(cell,(index*320,row*320))
strips['Weapon'] = weapon
film = composite(strips)
output = history/f'candidate-{len(list(history.glob("candidate-*")))+1:02d}'
output.mkdir()
weapon.save(paths['Weapon']);film.save(output/'composite-strip.png')
preview = []
for index in range(count):
    image = Image.new('RGBA',(1280,640),(31,48,60,255));draw = ImageDraw.Draw(image)
    for row,direction in enumerate(definition['directions']):
        x,y=row%4*320,row//4*320
        image.alpha_composite(film.crop((index*320,row*320,(index+1)*320,(row+1)*320)),(x,y))
        draw.text((x+10,y+15),direction,fill='white')
        draw.line((x,y+264,x+320,y+264),fill=(54,74,82))
    preview.append(image.convert('RGB').quantize(colors=256,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE))
for speed,name in [(1,'normal'),(.25,'quarter')]:
    preview[0].save(output/(name+'.gif'),save_all=True,append_images=preview[1:],duration=[round(t/speed) for t in clip['durations']],loop=0)
assert all(hashlib.sha256(paths[slot].read_bytes()).hexdigest()==digest for slot,digest in unchanged.items())
record = {'candidateId':f'{args.body}-{args.animation.lower()}-{output.name}','dateTimeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'method':'Targeted offline rigid weapon translation at existing anatomical grip; other five lossless source strips unchanged',
          'purpose':'Remove unintended sword swing from short hit recoil','sourceReferences':[str(base.relative_to(ROOT)),str((body/'modular-masters').relative_to(ROOT))],
          'prompt':None,'negativePrompt':None,'status':'awaiting-visual-gate','ownerApproval':'NOT_APPROVED','unchangedStripSHA256':unchanged,
          'repairSourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(output/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
old = json.loads((base/'provenance.json').read_text());old.update({'status':'rejected','rejectionReason':'Rest blade proxy differed from the actual painted source angle; flinch must carry its sword without swinging.'})
(base/'provenance.json').write_text(json.dumps(old,indent=2)+'\n')
print(output.relative_to(ROOT))
