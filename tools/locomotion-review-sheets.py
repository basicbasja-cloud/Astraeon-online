"""Tile unchanged captured frames, including the closing 7→0 transition.

This is a review artifact, not an asset repair or anatomical measurement.
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
directions=[('S','s'),('SE','sd'),('E','d'),('NE','wd'),('N','w'),('NW','wa'),('W','a'),('SW','sa')]
for mode in ['walk','run','sprint']:
    sheet=Image.new('RGB',(1296,1520),(34,45,56));draw=ImageDraw.Draw(sheet)
    for row,(direction,keys) in enumerate(directions):
        folder=args.input/'motion-series'/f'{mode}-{keys}';frames=json.loads((folder/'frames.json').read_text());selected={}
        for i,f in enumerate(frames):selected.setdefault(f['selectedPose']['column'],i)
        assert len(selected)==8,(folder,selected)
        for col in range(9):
            pose=col%8;i=selected[pose];picture=Image.open(folder/f'{i:03d}.png').convert('RGB');sheet.paste(picture,(col*144,row*190+30));draw.text((col*144+5,row*190+8),f'{direction} / {pose}',fill='white')
    sheet.save(args.output/f'{args.input.name}-{mode}-all-directions.png')
print('Saved actual captured 0..7..0 poses for all eight directions and three modes')
