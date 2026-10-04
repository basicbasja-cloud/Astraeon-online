"""Read only map metadata from public rAthena; never ship its terrain cells.

Produces a small, revision-pinned research report. Dimensions are navigation
cells, not meters or automatically interchangeable Astraeon world units.
"""
import argparse,json,struct,urllib.request
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
def read(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Astraeon-reference-research'})
 return urllib.request.urlopen(req,timeout=30).read()
sha=json.loads(read('https://api.github.com/repos/rathena/rathena/commits/master'))['sha']
url=f'https://raw.githubusercontent.com/rathena/rathena/{sha}/db/pre-re/map_cache.dat'
data=read(url);size,count=struct.unpack_from('<IH',data);assert size==len(data)
cursor=8;found=None
for _ in range(count):
 name,x,y,length=struct.unpack_from('<12sHHI',data,cursor);cursor+=20
 if name.rstrip(b'\0')==b'prontera':found={'width':x,'height':y,'units':'navigation cells'}
 cursor+=length
assert cursor==len(data) and found
report={'repository':'rathena/rathena','revision':sha,'source':url,'map':'prontera','dimensions':found,
 'limits':['Only the header metadata is retained; no cell grid, models or textures are saved.',
 'World-unit conversion needs player-relative scale and travel calibration; equal numerical dimensions alone do not reproduce the walking experience.']}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
