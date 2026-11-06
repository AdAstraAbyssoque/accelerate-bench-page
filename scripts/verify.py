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
for page in root.glob('*.html'):
 Links().feed(page.read_text())
refs += [t['diagram'] for t in data['tasks']]
refs += [m['diagram'] for m in json.loads((root/'assets/methods.json').read_text())]
refs += re.findall(r'url\([\'\"]?([^\)\'\"]+)',(root/'style.css').read_text())
for ref in refs:
 u=urlsplit(ref)
 if u.scheme or u.netloc or not u.path:continue
 target=root/unquote(u.path)
 if target.is_dir():target=target/'index.html'
 assert target.is_file(),ref
for p in root.rglob('*'):
 assert not p.is_symlink(),p
 if p.suffix in ['.html','.css','.js','.json','.svg','.md','.txt']:
  s=p.read_text()
  assert not re.search(r'/Users/|/dockerdata|/taijifs|\.woa\.com|sk-[A-Za-z0-9]{24}',s),p
print(f'PASS: 32 tasks, 12 models, author affiliations, {len(refs)} asset references and public-source scan.')

# Metadata must agree with the deployed canonical host and the reported authors.
from xml.etree import ElementTree
class Metadata(HTMLParser):
 def __init__(self):
  super().__init__();self.meta={};self.canonical=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='meta':self.meta.setdefault(attrs.get('name',attrs.get('property')),[]).append(attrs.get('content'))
  if tag=='link' and attrs.get('rel')=='canonical':self.canonical.append(attrs['href'])
base='https://acceleratebench.com/'
for filename in ['index.html','paper.html']:
 text=(root/filename).read_text();parsed=Metadata();parsed.feed(text)
 url=base if filename=='index.html' else base+filename
 assert parsed.canonical==[url]
 assert parsed.meta['og:url']==[url]
 assert parsed.meta['twitter:card']==['summary_large_image']
 for key in ['og:image','twitter:image']:
  image=parsed.meta[key][0];assert image.startswith(base)
  assert (root/image.removeprefix(base)).is_file()
 graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
 article=next(x for x in graph['@graph'] if x['@type']=='ScholarlyArticle') if '@graph' in graph else graph
 assert [a['name'] for a in article['author']]==[a['name'] for a in data['authors']]
 assert article['creativeWorkStatus']=='Draft'
 assert 'datePublished' not in article and 'doi' not in article
 if filename=='paper.html':
  assert parsed.meta['citation_author']==[a['name'] for a in data['authors']]
  assert parsed.meta['citation_pdf_url']==[base+'assets/accelerate-bench.pdf']
  assert parsed.meta['citation_publication_date']==['2026']
  assert article['abstract'] in text
  assert 'src="app.js"' not in text
 else:
  assert 'citation_title' not in parsed.meta
  author_markup=re.search(r'<div id="author-list"[^>]*>(.*?)</div>',text,re.S)[1]
  assert all(a['name'] in author_markup for a in data['authors'])
  assert 'href="paper.html"' in text
urls=[e.text for e in ElementTree.parse(root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert urls==[base,base+'paper.html',base+'assets/accelerate-bench.pdf']
assert 'Sitemap: '+base+'sitemap.xml' in (root/'robots.txt').read_text()
print('PASS: canonical URLs, social images, scholarly metadata, static authors, paper abstract, robots and sitemap.')
