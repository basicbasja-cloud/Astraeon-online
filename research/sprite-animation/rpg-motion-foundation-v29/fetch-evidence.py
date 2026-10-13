#!/usr/bin/env python3
"""Read public source pages; retain receipts, bounded excerpts and ignored cache.

No login, purchase, provider activation or automatic execution of fetched files.
GitHub documents resolve through the observed commit, never a floating raw URL.
"""
import concurrent.futures, hashlib, json, re, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'local-cache'

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag=='a':
            href=dict(attrs).get('href')
            if href: self.links.append(href)
        if tag in ('p','h1','h2','h3','li','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def get(url, cap=12_000_000):
    request=Request(url, headers={'User-Agent':'AstraeonMotionResearch/1.0'})
    try: response=urlopen(request, timeout=22)
    except HTTPError as error: response=error
    with response:
        data=response.read(cap+1)
        if len(data)>cap: raise ValueError('Response exceeds bounded page limit')
        r=SimpleNamespace(status_code=response.status,url=response.url,headers=response.headers)
    return r, data

def collect(source):
    receipt={'id':source['id'],'requested_url':source['url'],'checked_at_utc':datetime.now(timezone.utc).isoformat(),'asset_downloaded':False,'frame_analyzed':False}
    try:
        url=source['url']; u=urlparse(url)
        if u.hostname=='github.com':
            bits=u.path.strip('/').split('/'); repo='/'.join(bits[:2])
            mr, md=get('https://api.github.com/repos/'+repo)
            if mr.status_code!=200: raise ValueError('Repository metadata HTTP '+str(mr.status_code))
            meta=json.loads(md); branch=meta['default_branch']
            cr, cd=get('https://api.github.com/repos/'+repo+'/commits/'+branch)
            if cr.status_code!=200: raise ValueError('Commit metadata HTTP '+str(cr.status_code))
            commit=json.loads(cd)['sha']; receipt.update(repo=repo,commit=commit,code_license=meta.get('license'))
            if len(bits)>3 and bits[2]=='blob':
                path='/'.join(bits[4:]); url='https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+path
            else:
                rr, rd=get('https://api.github.com/repos/'+repo+'/readme')
                if rr.status_code!=200: raise ValueError('README metadata HTTP '+str(rr.status_code))
                path=json.loads(rd)['path']; url='https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+path
            receipt['pinned_path']=path
        r,data=get(url); receipt.update(http_status=r.status_code,final_url=r.url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),content_type=r.headers.get('content-type',''))
        if r.status_code!=200:
            receipt['status']='http_error'; return receipt
        suffix='.pdf' if data.startswith(b'%PDF') else '.txt'
        cache=CACHE/(source['id']+suffix); cache.write_bytes(data); receipt['cache_path']=str(cache.relative_to(ROOT))
        if suffix=='.pdf':
            receipt['status']='pdf_retrieved_not_full_read'; return receipt
        raw=data.decode('utf-8',errors='replace')
        if '<html' in raw[:5000].lower() or '<!doctype' in raw[:5000].lower():
            parser=Text(); parser.feed(raw); content=''.join(parser.parts)
            receipt['asset_links']=[x for x in parser.links if re.search(r'\.(zip|glb|fbx|bvh|gif|mp4|png)(?:[?#]|$)',x,re.I)][:25]
        else: content=raw
        (CACHE/(source['id']+'-readable.txt')).write_text(content)
        words=content.split(); receipt['text_words']=len(words)
        blocked=any(x in content[:2000].lower() for x in ('just a moment','verify you are human','access denied','checking your browser'))
        receipt['status']='challenge_or_access_page' if blocked else ('page_retrieved' if len(words)>25 else 'sparse_page')
        receipt['excerpt']=' '.join(words[:100])
        # Bounded snippets only, full third-party article is not published.
        hits=[]
        for line in content.splitlines():
            if re.search(r'licens|CC0|creative commons|commercial|redistribut|frames|animation|root.motion|skeleton|contact',line,re.I):
                hits.append(' '.join(line.split())[:240])
        receipt['inspection_hints']=hits[:6]
    except Exception as exc: receipt.update(status='fetch_failed',error=str(exc)[:300])
    return receipt

def main():
    CACHE.mkdir(exist_ok=True)
    sources=json.loads((ROOT/'sources.json').read_text())['sources']
    started=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        receipts=list(pool.map(collect,sources))
    (ROOT/'retrieval.json').write_text(json.dumps({'schema':'public-reference-retrieval-v1','date':'2026-10-13','receipts':receipts},indent=2)+'\n')
    counts={status:sum(r['status']==status for r in receipts) for status in sorted(set(r['status'] for r in receipts))}
    print(json.dumps({'sources':len(sources),'statuses':counts,'seconds':round(time.time()-started,1)}))
if __name__=='__main__': main()
