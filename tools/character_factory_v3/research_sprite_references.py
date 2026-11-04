import argparse,pathlib,json,urllib.request,concurrent.futures,hashlib,subprocess
parser=argparse.ArgumentParser(description='Fetch pinned RO/Flare/ManaPlus research sources and inventory with Craft Anything')
parser.add_argument('--output',type=pathlib.Path,required=True)
parser.add_argument('--craft-cli',type=pathlib.Path,required=True)
args=parser.parse_args()
root=args.output.resolve()
if root.exists() or root.is_symlink():raise ValueError('Choose a fresh output outside the repository')
repo=pathlib.Path(__file__).resolve().parents[2]
if root==repo or repo in root.parents:raise ValueError('Keep third-party research sources outside the game repository')
root.mkdir(parents=True)
pins={'kivutar/goro':'33389d39e7a0e6ede2fd277b5b93afad02708b0e','flareteam/flare-engine':'f9a17a266293a897a1d7eae2d54408b0de39af27','flareteam/flare-game':'af6eee6d339ac98011864bfe89da837fe7769c28','ManaPlus/ManaPlus':'40ebe02e81b34f5b02ea682d2d470a20e7e63cfc'}
sets={'kivutar/goro':['game/sprites/render.go','game/sprites/attack.go','game/sprites/assets.go','LICENSE'],'flareteam/flare-engine':['src/Animation.cpp','src/Animation.h','src/AnimationSet.cpp','src/Entity.cpp','COPYING'],'flareteam/flare-game':['mods/fantasycore/animations/avatar/male/longsword.txt','mods/fantasycore/animations/avatar/male/head_short.txt','mods/fantasycore/animations/avatar/female/longsword.txt','mods/fantasycore/animations/avatar/female/head_long.txt','LICENSE.txt'],'ManaPlus/ManaPlus':['src/being/compoundsprite.cpp','src/resources/sprite/animatedsprite.cpp','src/resources/sprite/spritedef.cpp','COPYING']}
records=[]
def fetch(row):
 repo,sha,path=row;url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}';p=root/'sources'/repo/path
 try:
  data=urllib.request.urlopen(url,timeout=30).read();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return {'repo':repo,'revision':sha,'path':path,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'status':'downloaded'}
 except Exception as e:return {'repo':repo,'revision':sha,'path':path,'url':url,'status':'unavailable','error':str(e)}
rows=[]
for repo,files in sets.items():
 rows += [(repo,pins[repo],p) for p in files]
with concurrent.futures.ThreadPoolExecutor(6) as pool:records=list(pool.map(fetch,rows))
(root/'source-manifest.json').write_text(json.dumps(records,indent=2)+'\n');print([(r['repo'],r['path'],r['status']) for r in records])

if any(r['status']!='downloaded' for r in records):raise RuntimeError('Some research sources are unavailable; see manifest')
for name,repo in [('ro','kivutar/goro'),('flare-engine','flareteam/flare-engine'),('flare-game','flareteam/flare-game'),('mana','ManaPlus/ManaPlus')]:
 data=subprocess.check_output([str(args.craft_cli.resolve()),'--deep','--project',str(root/(name+'.cany')),'core-archive-show','--path',str(root/'sources'/repo),'--limit','20'])
 (root/(name+'-inventory.json')).write_bytes(data)
# Inspect the downloaded Flare animation records without loading game assets.
parsed=[]
for path in sorted((root/'sources/flareteam/flare-game/mods/fantasycore/animations/avatar').glob('*/*.txt')):
 actions={};current=None
 for line in path.read_text().splitlines():
  line=line.strip()
  if line.startswith('['):current=actions.setdefault(line.strip('[]'),{'entries':[]})
  elif current is not None and '=' in line and not line.startswith('#'):
   key,value=line.split('=',1)
   if key=='frame':current['entries'].append([int(x) for x in value.split(',')])
   elif key in ('frames','duration','type'):current[key]=value
 for action in actions.values():
  entries=action.pop('entries')
  action.update({'directions':sorted(set(e[1] for e in entries)),'frame_records':len(entries),'rect_width_range':[min(e[4] for e in entries),max(e[4] for e in entries)],'rect_height_range':[min(e[5] for e in entries),max(e[5] for e in entries)],'distinct_offsets':len(set((e[6],e[7]) for e in entries))})
 parsed.append({'file':str(path.relative_to(root/'sources')),'animations':actions})
(root/'flare-animation-summary.json').write_text(json.dumps(parsed,indent=2)+'\n')
