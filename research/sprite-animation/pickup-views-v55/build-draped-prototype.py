"""Static continuous waist binding, no part cut or per-frame art edits."""
from pathlib import Path
import json,shutil,sys
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W'
d=json.loads((P/f'{view}-articulated-contract.json').read_text());old=json.dumps(d,separators=(',',':'))
d['definitions']['body']['hanging_cloth']={'x':([187,203,302,317] if view=='W' else [203,221,292,309]),'y':[294,329]}
d['scope']+=' Continuous pelvis-hanging garment field blended at belt; separate from shoulder-attached cape. Experimental, no visual pass inferred.'
new=json.dumps(d,separators=(',',':'));(P/f'{view}-draped-articulated-contract.json').write_text(new+'\n')
html=(P/f'{view}-articulated-review.html').read_text();assert old in html
(P/f'{view}-draped-articulated-review.html').write_text(html.replace(old,new))
shutil.copyfile(P.parents[2]/'tools/sprite-segmented-player.js',P/'inputs/sprite-segmented-player.js')
