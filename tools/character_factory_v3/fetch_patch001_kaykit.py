import hashlib,html,http.cookiejar,json,re,urllib.parse,urllib.request,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];dest=root/'authoring/characters/factory-v3/motions/inbox/kaykit-animation-intake';dest.mkdir(parents=True,exist_ok=True)
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));url='https://kaylousberg.itch.io/kaykit-character-animations';page=opener.open(url,timeout=30).read().decode();assert 'CC0' in page and 'FREE' in page
csrf=html.unescape(re.search(r'<meta name="csrf_token" value="(.*?)"',page).group(1));request=urllib.request.Request(url+'/download_url',data=urllib.parse.urlencode({'csrf_token':csrf}).encode());free_url=json.loads(opener.open(request,timeout=30).read())['url'];downloads=opener.open(free_url,timeout=30).read().decode();candidates=re.findall(r'data-upload_id="(\d+)"',downloads);print('Unlocked free upload IDs',candidates,flush=True)
if len(candidates)!=1:
 (dest/'free-download-page.html').write_text(downloads);raise ValueError('Inspect unlocked free uploads; do not choose a source/paid tier')
u=candidates[0];request=urllib.request.Request(url+'/file/'+u+'?source=game_download&as_props=1',data=b'');asset_url=json.loads(opener.open(request,timeout=30).read())['url'];archive=dest/'kaykit-character-animations-free.zip'
if not archive.exists():archive.write_bytes(opener.open(asset_url,timeout=60).read())
files=[]
with zipfile.ZipFile(archive)as z:
 for e in z.infolist():
  if e.is_dir():continue
  # Retain only reusable medium-rig GLTF ranged/general/movement sets and evidence.
  if not (e.filename.lower().endswith(('.txt','.md','.gltf','.bin','.glb','.png'))):continue
  if not (any(s in e.filename for s in ['Rig_Medium','License','LICENSE','README','Animations.md'])):continue
  p=(dest/'extracted'/e.filename).resolve();assert p.is_relative_to((dest/'extracted').resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(e));files.append({'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
receipt={'creator':'Kay Lousberg','url':url,'tier':'FREE','price_paid':0,'license':'CC0-1.0','upload_id':u,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':files,'status':'INTAKE_NOT_VISUAL_APPROVAL'};(root/'authoring/characters/factory-v3/patch-0.0.1/research/kaykit-download.json').write_text(json.dumps(receipt,indent=2)+'\n');print({'archive_bytes':archive.stat().st_size,'retained_files':len(files)},flush=True)
