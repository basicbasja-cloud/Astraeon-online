#!/usr/bin/env python3
"""Creator's explicit free download through TLS-verified public guest flow.
No account, payment, paid upload, or credential changes. Guest CSRF/link values
are used only in memory and are never logged or published.
"""
import hashlib,http.cookiejar,json,re,zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,build_opener,HTTPCookieProcessor
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.csrf=None;self.uploads=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta' and a.get('name')=='csrf_token':self.csrf=a.get('value') or a.get('content')
  if 'data-upload_id' in a:self.uploads.append(a['data-upload_id'])
def main():
 base='https://kaylousberg.itch.io/kaykit-character-animations';receipt={'source_url':base,'requested_tier':'Free 1.1','account_used':False,'payment_submitted':False,'tls_verification':True}
 opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def get(url,data=None):
  with opener.open(Request(url,data=data,headers={'User-Agent':'AstraeonPublicFreeAssetResearch/1.0','Referer':base+'/purchase'}),timeout=25) as r:return r.read(35000001)
 try:
  purchase=get(base+'/purchase').decode();parser=Page();parser.feed(purchase)
  if not parser.csrf:raise ValueError('Guest download form has no session CSRF; stop')
  link=json.loads(get(base+'/download_url',urlencode({'csrf_token':parser.csrf}).encode()))
  if not link.get('url'):raise ValueError('No public free download page')
  download=get(link['url']).decode();(ROOT/'local-cache/kay-free-download-page.html').write_text(download)
  available=Page();available.feed(download);ids=available.uploads
  if 'Free 1.1' not in download or len(set(ids))!=1:raise ValueError('Public page does not have exactly one downloadable Free1.1 upload')
  response=json.loads(get(base+'/file/'+ids[0]+'?source=game_download&as_props=1',urlencode({'csrf_token':parser.csrf}).encode()))
  data=get(response['url'])
  if len(data)>35000000 or not data.startswith(b'PK'):raise ValueError('Unexpected archive')
  dest=ROOT/'local-cache/kaykit-current-free-1.1.zip';dest.write_bytes(data)
  with zipfile.ZipFile(dest) as archive:
   members=archive.namelist()
   for m in archive.infolist():
    p=Path(m.filename)
    if p.is_absolute() or '..' in p.parts or m.file_size>60000000:raise ValueError('Unsafe archive member')
    if m.is_dir():continue
    target=ROOT/'local-cache/kaykit-current-free'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(m))
  receipt.update(status='acquired',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),file=str(dest.relative_to(ROOT)),members=members)
 except Exception as e:receipt.update(status='not_acquired',error=str(e)[:220])
 (ROOT/'kaykit-acquisition.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='members'}))
if __name__=='__main__':main()
