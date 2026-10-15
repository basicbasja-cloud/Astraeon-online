#!/usr/bin/env python3
"""Meaningful observer abstention controls and exact-byte/export checks."""
from pathlib import Path
import importlib.util,json,hashlib,subprocess,sys
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',P/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
checks={}
empty=Image.new('RGBA',(384,512))
checks['empty_abstains']=a.boot(empty,a.WINDOWS['screen_left_boot'])['status']=='UNKNOWN_EMPTY'
blank=np.zeros((512,384,4),dtype=np.uint8);blank[470:485,164:180,3]=255
checks['window_edge_abstains']=a.boot(Image.fromarray(blank),a.WINDOWS['screen_left_boot'])['status']=='UNKNOWN_WINDOW_CUT'
seq=a.cells(P/'raw/N-attempt3.png')
checks['actual_surfaces_covered']=all(a.boot(im,b)['status']=='VISIBLE_SURFACE_ONLY' for im in seq for b in a.WINDOWS.values())
values=[a.boot(im,a.WINDOWS['screen_left_boot'])['bottom_y'] for im in seq]
# Shift one test fixture by8px to show the existing6px budget catches actual-surface drift.
fixture=Image.new('RGBA',(384,512));fixture.paste(seq[3],(0,8))
shift=a.boot(fixture,a.WINDOWS['screen_left_boot'])
checks['8px_real_surface_negative']=shift['status']!='VISIBLE_SURFACE_ONLY' or max(values+[shift['bottom_y']])-min(values+[shift['bottom_y']])>6
checks['lossless_exports']=all(np.array_equal(np.asarray(im),np.asarray(Image.open(P/'frames'/f'{k:02}.png'))) for k,im in enumerate(seq))
old=a.cells(P/'inputs/N-before-reconstructed.png');root=P.parent/'paintover-handoff-v46'
checks['parent_frame_pixels_exact']=all(np.array_equal(np.asarray(im),np.asarray(Image.open(root/'frames/N'/f'{k:02}.png'))) for k,im in enumerate(old))
manual=json.loads((P/'manual-review.json').read_text())
checks['retained_wrong_hand_rejection']=manual['findings'][0]['status']=='AGENT_REJECTED_WRONG_HAND_AND_SIZE'
checks['hidden_points_remain_unknown']=all(x['hidden_joint_coordinates'] is None for x in manual['per_key'])
strict=subprocess.run([sys.executable,str(P/'audit.py'),'--require-production'],capture_output=True,text=True)
checks['strict_release_blocks']=strict.returncode==1
checks['407px_is_not_399px']=json.loads((P/'review.json').read_text())['candidates']['attempt3']['components'][0]['height']==407
result={'pass':all(checks.values()),'checks':checks,'production_pass':False,'scope':'Observer controls and decoded artifacts, not visual acceptance'}
(P/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['pass'] else 1)
