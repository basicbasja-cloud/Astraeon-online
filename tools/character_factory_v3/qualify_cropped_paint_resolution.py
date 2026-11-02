"""Qualify native crop detail against its fixed canonical viewport, not padding.

A small tightly cropped slot may downsample into a larger transparent canvas.
This is a resolution calculation only, never an anatomy or art approval.
"""
import argparse
import json
from pathlib import Path


def positive_pair(value,name):
    if not isinstance(value,(list,tuple))or len(value)!=2 or any(type(v)is not int or v<1 for v in value):
        raise ValueError(name+' requires two positive integer dimensions')
    return value


def qualify(sheet_size,grid,source_canvas,source_crop,authoring_canvas):
    sw,sh=positive_pair(sheet_size,'sheet');columns,rows=positive_pair(grid,'grid')
    gw,gh=positive_pair(source_canvas,'source');aw,ah=positive_pair(authoring_canvas,'authoring')
    if not isinstance(source_crop,(list,tuple))or len(source_crop)!=4 or any(type(v)is not int for v in source_crop):raise ValueError('Integer source crop required')
    left,top,right,bottom=source_crop
    if not 0<=left<right<=gw or not 0<=top<bottom<=gh:raise ValueError('Source crop outside canvas')
    if aw*gh!=ah*gw:raise ValueError('Canvas scaling must be uniform')
    slot=[sw/columns,sh/rows];viewport=[left*aw/gw,top*ah/gh,right*aw/gw,bottom*ah/gh]
    required=[viewport[2]-viewport[0],viewport[3]-viewport[1]]
    if abs((slot[0]/slot[1])/((right-left)/(bottom-top))-1)>0.005:raise ValueError('Raw slot and fixed source crop aspect differ')
    ratios=[slot[i]/required[i]for i in range(2)]
    return {'status':'NATIVE_CROP_RESOLUTION_ONLY_NOT_ART_APPROVAL','sheet_size':[sw,sh],'grid':[columns,rows],
        'source_canvas':[gw,gh],'source_crop':list(source_crop),'authoring_canvas':[aw,ah],
        'raw_slot_size':slot,'canonical_viewport':viewport,'canonical_viewport_size':required,
        'native_pixels_per_authoring_pixel_xy':ratios,'requires_upsampling':min(ratios)<1,
        'native_resolution_sufficient':min(ratios)>=1,'canvas_padding_counted_as_drawn_detail':False,
        'anatomy_or_contact_approved':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists()or args.output.is_symlink():raise ValueError('Choose fresh output')
    result=qualify([1448,1086],[4,3],[1536,1536],[448,520,1088,1160],[768,768])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
