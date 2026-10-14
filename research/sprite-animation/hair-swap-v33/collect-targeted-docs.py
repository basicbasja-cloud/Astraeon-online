"""Acquire bounded official attachment/skin/render documents. Save raw pages only
in ignored local-cache; publish URL/hash/status and a short selected excerpt.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,sys,urllib.request
P=Path(__file__).resolve().parent
SOURCES={'skins':('https://esotericsoftware.com/spine-skins','skin'),'attachments':('https://esotericsoftware.com/spine-attachments','attachment'),'canvasitem':('https://docs.godotengine.org/en/stable/classes/class_canvasitem.html','modulate')}
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.words=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.words.extend(d.split())
name=sys.argv[1];url,term=SOURCES[name];cache=P/'local-cache';cache.mkdir(exist_ok=True)
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Astraeon-sprite-research/0.33'}),timeout=30) as response:
 raw=response.read(3*1024*1024);status=response.status;final=response.url
(cache/(name+'.html')).write_bytes(raw);parser=Text();parser.feed(raw.decode('utf8',errors='replace'));words=parser.words
# Pick explanatory material after the document title/navigation; short excerpt,
# not redistribution of the complete external article.
occurrences=[i for i,w in enumerate(words) if w.lower().strip('.,:')==term]
start=next((i for i in occurrences if i>250),occurrences[0] if occurrences else 0);excerpt=' '.join(words[max(0,start-8):start+42])
receipt={'url':url,'final_url':final,'http_status':status,'retrieved_date':'2026-10-14','raw_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'selected_excerpt_under60words':excerpt,'review_level':'Downloaded; selected sections searched/read for current paper-doll draw/order/opacity questions. No engine/provider project executed.'}
(P/('source-'+name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'source':name,'status':status,'excerpt':excerpt}))
