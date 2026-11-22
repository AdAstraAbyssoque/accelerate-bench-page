from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
root=Path(__file__).resolve().parents[1]/'dist'
data=json.loads((root/'assets/results.json').read_text())
assert len(data['tasks'])==32 and len(data['models'])==16
assert all(len(t['rewards_percent'])==16 for t in data['tasks'])
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
 if p.suffix in ['.html','.css','.js','.mjs','.json','.svg','.md','.txt']:
  s=p.read_text()
  assert not re.search(r'/Users/|/dockerdata|/taijifs|\.woa\.com|sk-[A-Za-z0-9]{24}',s),p
print(f'PASS: 32 tasks, 16 models, author affiliations, {len(refs)} asset references and public-source scan.')

# Metadata must agree with the deployed canonical host and the reported authors.
from xml.etree import ElementTree
from datetime import date
class Metadata(HTMLParser):
 def __init__(self):
  super().__init__();self.meta={};self.canonical=[];self.ld_blocks=[];self.in_ld=False
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='script' and attrs.get('type')=='application/ld+json':
   self.in_ld=True;self.ld_blocks.append('')
  if tag=='meta':self.meta.setdefault(attrs.get('name',attrs.get('property')),[]).append(attrs.get('content'))
  if tag=='link' and attrs.get('rel')=='canonical':self.canonical.append(attrs['href'])
 def handle_data(self,text):
  if self.in_ld:self.ld_blocks[-1]+=text
 def handle_endtag(self,tag):
  if tag=='script':self.in_ld=False
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
 blocks=[json.loads(block) for block in parsed.ld_blocks]
 graph=next(b for b in blocks if '@graph' in b or b.get('@type')=='ScholarlyArticle')
 article=next(x for x in graph['@graph'] if x['@type']=='ScholarlyArticle') if '@graph' in graph else graph
 assert [a['name'] for a in article['author']]==[a['name'] for a in data['authors']]
 assert article['creativeWorkStatus']=='Preprint'
 assert article['sameAs']=='https://arxiv.org/abs/2611.20882'
 assert article['identifier']=='arXiv:2611.20882'
 assert article['datePublished']=='2026-11-16' and 'doi' not in article
 if filename=='paper.html':
  assert parsed.meta['citation_author']==[a['name'] for a in data['authors']]
  assert parsed.meta['citation_pdf_url']==[base+'assets/accelerate-bench.pdf']
  assert parsed.meta['citation_publication_date']==['2026/11/16']
  assert parsed.meta['citation_arxiv_id']==['2611.20882']
  assert article['abstract'] in text
  assert 'src="app.js"' not in text
 else:
  website, = (n for n in graph['@graph'] if n['@type']=='WebSite')
  dataset, = (n for n in graph['@graph'] if n['@type']=='Dataset')
  assert dataset['alternateName']==website['alternateName']=='AccelerateBench'
  assert dataset['name']==website['name'] and dataset['url']==base
  assert dataset['creator']==article['author'] and dataset['description']
  assert len(set(dataset['sameAs']))==4 and article['sameAs'] in dataset['sameAs']
  assert dataset['keywords'] and all(d['@type']=='DataDownload' and d['url'] for d in dataset['distribution'])
  assert 'citation_title' not in parsed.meta
  author_markup=re.search(r'<div id="author-list"[^>]*>(.*?)</div>',text,re.S)[1]
  assert all(a['name'] in author_markup for a in data['authors'])
  assert 'href="paper.html"' in text
urls=[e.text for e in ElementTree.parse(root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
for entry in ElementTree.parse(root/'sitemap.xml').getroot():
 lastmod, = entry.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
 assert date.fromisoformat(lastmod.text).isoformat()==lastmod.text
assert urls==[base,base+'paper.html',base+'assets/accelerate-bench.pdf']
assert 'Sitemap: '+base+'sitemap.xml' in (root/'robots.txt').read_text()
print('PASS: canonical URLs, social images, scholarly metadata, static authors, paper abstract, robots and sitemap.')

# Read just the generated subtrees as HTML, including inline names, footnotes and units.
class StaticContainers(HTMLParser):
    ids = {'rank-rows', 'task-grid'}
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.elements = {}
        self.stack = []

    def handle_starttag(self, tag, attrs):
        element_id = dict(attrs).get('id')
        if not self.stack and element_id not in self.ids:
            return
        element = ElementTree.Element(tag, dict(attrs))
        if self.stack:
            self.stack[-1].append(element)
        if element_id in self.ids:
            assert element_id not in self.elements, element_id
            self.elements[element_id] = element
        if tag not in self.void:
            self.stack.append(element)

    def handle_endtag(self, tag):
        if self.stack and tag not in self.void:
            assert self.stack.pop().tag == tag, tag

    def handle_data(self, value):
        if self.stack:
            element = self.stack[-1]
            if len(element):
                child = element[-1]
                child.tail = (child.tail or '') + value
            else:
                element.text = (element.text or '') + value

def visible(element):
    return ''.join(element.itertext()).strip()

static = StaticContainers()
static.feed((root/'index.html').read_text())
static.close()
assert not static.stack
rows = static.elements['rank-rows']
models = sorted(data['models'], key=lambda model: -model['score'])
assert len(rows) == len(models)
for index, (row, model) in enumerate(zip(rows, models), 1):
    expected = [
        f'{index:02}', model['name'] + ('†' if model['stopped_tasks'] else ''),
        model['harness'], f"{model['score']:.1f}%", f"{model['gm']:.2f}×",
        f"{model['a125']:.1f}%", f"{model['a2']:.1f}%"
    ]
    assert row.tag == 'tr' and [visible(td) for td in row.findall('td')] == expected, model['name']

cards = static.elements['task-grid']
metadata = json.loads((root.parent/'scripts/task-metadata-v11.json').read_text())
assert len(cards) == len(data['tasks']) == len(metadata)
for index, (card, task) in enumerate(zip(cards, data['tasks']), 1):
    assert card.tag == 'button' and card.get('class') == 'task-card'
    assert card.get('data-task') == task['id'] and visible(card.find('.//h3')) == task['name']
    assert visible(card.find('.//p')) == task['area']
    assert visible(card.find(".//span[@class='task-index']")) == f'{index:02}'
    assert card.find('.//img').get('src') == task['diagram']
    meta = metadata[task['directory']]
    assert meta['cpus'] == task['cpus'] and meta['memory_mb'] / 1024 == task['memory_gib']
    resources = card.find(".//div[@class='task-card-foot']/span")
    assert visible(resources) == f"{task['cpus']} CPUs · {task['memory_gib']} GiB", task['id']
print('PASS: 16 static seven-column leaderboard rows, 32 task cards, Dataset JSON-LD and sitemap dates.')
