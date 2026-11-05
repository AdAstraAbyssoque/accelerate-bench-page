from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
root=Path(__file__).resolve().parents[1]/'dist'
data=json.loads((root/'assets/results.json').read_text())
assert len(data['tasks'])==32 and len(data['models'])==12
assert all(len(t['rewards_percent'])==12 for t in data['tasks'])
assert [a['name'] for a in data['authors']]==['Bowen Liu','Yuhan Li','Nuo Chen','Weile Luo','Miao Peng','Qintong Zhang','Qifan Zhang','Jia Li','Ziqi Gao','Lydell Huang']
assert all((1 in a['affiliations']) == (a['name'] not in ['Jia Li','Ziqi Gao']) for a in data['authors'])
refs=[]
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src','data-figure'] and v:refs.append(v)
Links().feed((root/'index.html').read_text())
refs += [t['diagram'] for t in data['tasks']]
refs += [m['diagram'] for m in json.loads((root/'assets/methods.json').read_text())]
refs += re.findall(r'url\([\'\"]?([^\)\'\"]+)',(root/'style.css').read_text())
for ref in refs:
 u=urlsplit(ref)
 if u.scheme or u.netloc or not u.path:continue
 assert (root/unquote(u.path)).is_file(),ref
for p in root.rglob('*'):
 assert not p.is_symlink(),p
 if p.suffix in ['.html','.css','.js','.json','.svg','.md','.txt']:
  s=p.read_text()
  assert not re.search(r'/Users/|/dockerdata|/taijifs|\.woa\.com|sk-[A-Za-z0-9]{24}',s),p
print(f'PASS: 32 tasks, 12 models, author affiliations, {len(refs)} asset references and public-source scan.')
