"""Fetch Debian development headers into work/ for the optional local Aseprite build."""
from pathlib import Path
import urllib.request,lzma,hashlib,subprocess,os,concurrent.futures,json
root=Path(__file__).resolve().parents[1]/'work/tool-runtime/x11';root.mkdir(parents=True,exist_ok=True);names={'libx11-dev','libxcursor-dev','libxi-dev','libxrandr-dev','libxext-dev','libxrender-dev','libxfixes-dev','libxcb1-dev','libxau-dev','libxdmcp-dev','x11proto-dev','xtrans-dev'}
url='https://deb.debian.org/debian/dists/trixie/main/binary-amd64/Packages.xz'
with urllib.request.urlopen(url,timeout=60)as r:data=lzma.decompress(r.read()).decode()
rows=[]
for entry in data.split('\n\n'):
 lines={line.split(': ',1)[0]:line.split(': ',1)[1]for line in entry.splitlines()if ': 'in line and not line.startswith(' ')}
 if lines.get('Package')in names:rows.append(lines)
assert {r['Package']for r in rows}==names

def fetch(r):
 url='https://deb.debian.org/debian/'+r['Filename']
 with urllib.request.urlopen(url,timeout=60)as f:blob=f.read()
 assert hashlib.sha256(blob).hexdigest()==r['SHA256']
 dest=root/(r['Package']+'.deb');dest.write_bytes(blob);subprocess.run(['dpkg-deb','-x',str(dest),str(root/'sysroot')],check=True);return {'package':r['Package'],'version':r['Version'],'url':url,'sha256':r['SHA256']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:receipt=list(pool.map(fetch,rows))
# Link build-time unversioned linker names to the existing OS runtime libraries.
for f in (root/'sysroot/usr/lib/x86_64-linux-gnu').glob('*.so'):
 if f.is_symlink()and not f.exists():
  dest=Path('/usr/lib/x86_64-linux-gnu')/os.readlink(f)
  if dest.exists():f.unlink();f.symlink_to(dest)
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Downloaded/extracted',len(receipt),'official Debian build header packages to local work directory')
