#!/usr/bin/env python3
"""Normalize a whole eight-direction strip using ONE shared source registration.
All parts/clips of a character use definition.source.normalization; never fit alpha
bounds independently. Off-canvas painted pixels fail instead of disappearing.
"""
import argparse
import json
import math
from pathlib import Path
from PIL import Image

DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']

def normalize(definition, animation, source_path, output_path, input_order):
    if sorted(input_order) != sorted(DIRECTIONS) or len(input_order) != 8:
        raise ValueError('Supply all eight direction names exactly once; no mirroring')
    config = definition['source']['normalization']
    sw,sh = config['sourceFrameWidth'],config['sourceFrameHeight']
    factor = config['scale']
    if not isinstance(sw,int) or not isinstance(sh,int) or min(sw,sh) <= 0 or not isinstance(factor,(int,float)) or isinstance(factor,bool) or not math.isfinite(factor) or factor<=0:
        raise ValueError('Invalid shared normalization')
    root = config['sourceRootAnchor']
    if not isinstance(root,list) or len(root)!=2 or not all(isinstance(n,(int,float)) and math.isfinite(n) for n in root) or not (0<=root[0]<=sw and 0<=root[1]<=sh):
        raise ValueError('Invalid shared source root')
    count = len(definition['clips'][animation]['durations'])
    canvas = definition['canvas']
    w,h = canvas['frameWidth'],canvas['frameHeight']
    output = Image.new('RGBA',(w*count,h*8),(0,0,0,0))
    scaled_w,scaled_h = round(sw*factor),round(sh*factor)
    dx,dy = round(canvas['rootAnchorX']-root[0]*factor),round(canvas['rootAnchorY']-root[1]*factor)
    with Image.open(source_path) as source:
        source.load()
        if source.mode!='RGBA' or source.size!=(sw*count,sh*8):
            raise ValueError('Input must be an RGBA whole strip with the declared source cells')
        if source.getchannel('A').getextrema()[0] != 0:
            raise ValueError('Input strip must have a transparent background')
        for row,direction in enumerate(DIRECTIONS):
            source_row=input_order.index(direction)
            for index in range(count):
                frame=source.crop((index*sw,source_row*sh,(index+1)*sw,(source_row+1)*sh))
                frame=frame.resize((scaled_w,scaled_h),Image.Resampling.LANCZOS)
                bounds=frame.getchannel('A').getbbox()
                if bounds and (bounds[0]+dx<0 or bounds[1]+dy<0 or bounds[2]+dx>w or bounds[3]+dy>h):
                    raise ValueError(f'Painted pixels exceed canvas: {direction}/{index}; repair shared registration')
                cell=Image.new('RGBA',(w,h),(0,0,0,0));cell.paste(frame,(dx,dy))
                output.paste(cell,(index*w,row*h))
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output.save(output_path,format='PNG',compress_level=9)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--definition',type=Path,required=True)
    parser.add_argument('--animation',required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--input-order',default=','.join(DIRECTIONS))
    args=parser.parse_args()
    normalize(json.loads(args.definition.read_text()),args.animation,args.input,args.output,args.input_order.split(','))
