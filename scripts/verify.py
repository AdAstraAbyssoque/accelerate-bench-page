from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin
import json,re
root=Path(__file__).resolve().parents[1]/'dist'
data=json.loads((root/'assets/results.json').read_text())
assert len(data['tasks'])==32 and len(data['models'])==16
assert all(len(t['rewards_percent'])==16 for t in data['tasks'])
assert [a['name'] for a in data['authors']]==['Bowen Liu','Yuhan Li','Nuo Chen','Weile Luo','Miao Peng','Qintong Zhang','Qifan Zhang','Jia Li','Ziqi Gao','Lydell Huang']
assert all((1 in a['affiliations']) == (a['name'] not in ['Jia Li','Ziqi Gao']) for a in data['authors'])
base = 'https://acceleratebench.com/'
pages = sorted(root.rglob('*.html'))

def page_url(page):
    path = page.relative_to(root).as_posix()
    return urljoin(base, path.removesuffix('index.html') if page.name == 'index.html' else path)

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ['href', 'src', 'data-figure'] and value:
                self.refs.append(value)
            if key == 'id':
                self.ids.add(value)

refs = []
anchors = {}
for page in pages:
    links = Links()
    links.feed(page.read_text())
    anchors[page] = links.ids
    refs.extend((page_url(page), ref) for ref in links.refs)
refs.extend((base, task['diagram']) for task in data['tasks'])
refs.extend((base, item['diagram']) for item in json.loads((root/'assets/methods.json').read_text()))
refs.extend((base, path) for path in re.findall(r"""url\(['"]?([^)'" ]+)""", (root/'style.css').read_text()))
for origin, ref in refs:
    resolved = urlsplit(urljoin(origin, ref))
    if resolved.hostname != urlsplit(base).hostname:
        continue
    target = root / unquote(resolved.path).lstrip('/')
    if target.is_dir():
        target = target/'index.html'
    assert target.is_file(), (origin, ref)
    if target in anchors and resolved.fragment:
        assert unquote(resolved.fragment) in anchors[target], (origin, ref)
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
  super().__init__();self.meta={};self.canonical=[];self.ld_blocks=[];self.in_ld=False;self.titles=[];self.in_title=False
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='title':self.in_title=True;self.titles.append('')
  if tag=='script' and attrs.get('type')=='application/ld+json':
   self.in_ld=True;self.ld_blocks.append('')
  if tag=='meta':self.meta.setdefault(attrs.get('name',attrs.get('property')),[]).append(attrs.get('content'))
  if tag=='link' and attrs.get('rel')=='canonical':self.canonical.append(attrs['href'])
 def handle_data(self,text):
  if self.in_ld:self.ld_blocks[-1]+=text
  if self.in_title:self.titles[-1]+=text
 def handle_endtag(self,tag):
  if tag=='script':self.in_ld=False
  if tag=='title':self.in_title=False
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
assert len(urls) == len(set(urls))
assert set(urls) == {page_url(p) for p in pages} | {base+'assets/accelerate-bench.pdf'}
assert 'Sitemap: '+base+'sitemap.xml' in (root/'robots.txt').read_text()
print('PASS: canonical URLs, social images, scholarly metadata, static authors, paper abstract, robots and sitemap.')

# Read just the generated subtrees as HTML, including inline names, footnotes and units.
class StaticContainers(HTMLParser):
    ids = {'rank-rows', 'task-grid', 'faq-entries', 'task-details'}
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
for index, (wrapper, task) in enumerate(zip(cards, data['tasks']), 1):
    card = wrapper.find('button')
    assert wrapper.find('a').get('href') == f"/tasks/{task['directory']}/"
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

faq_source = json.loads((root.parent/'scripts/faq.json').read_text())
copy = json.loads((root.parent/'scripts/task-pages-copy.json').read_text())
by_directory = {t['directory']: t for t in data['tasks']}
assert {page.parent.name for page in pages if page.parent != root} == set(by_directory)
assert len(pages) == len(by_directory) + 2
longest_title = longest_description = 0
for page in pages:
    html = page.read_text()
    meta = Metadata()
    meta.feed(html)
    url = page_url(page)
    assert meta.canonical == [url], page
    title, = meta.titles
    description, = meta.meta['description']
    assert 0 < len(description) <= 160, page
    blocks = [json.loads(block) for block in meta.ld_blocks]
    assert blocks, page
    if page.parent == root:
        assert meta.meta['og:title'] == meta.meta['twitter:title'] == [title]
        assert meta.meta['og:description'] == meta.meta['twitter:description'] == [description]
    if page.name == 'paper.html':
        # Scholar and arXiv use the exact paper title, which is longer than 70 characters.
        assert title == data['title'] and meta.meta['citation_title'] == [title], page
        continue
    assert 0 < len(title) <= 70, page
    if page.parent == root:
        graph = next(block['@graph'] for block in blocks if '@graph' in block)
        webpage, = [node for node in graph if node['@type'] == 'WebPage']
        assert webpage['name'] == title and webpage['description'] == description
        entries = static.elements['faq-entries'].findall('li')
        visible_faq = [dict(question=visible(item.find('.//h3')), answer=visible(item.find('.//p')))
                       for item in entries]
        schema, = [block for block in blocks if block.get('@type') == 'FAQPage']
        pairs = []
        for qa in schema['mainEntity']:
            assert qa['@type'] == 'Question' and qa['acceptedAnswer']['@type'] == 'Answer'
            pairs.append(dict(question=qa['name'], answer=qa['acceptedAnswer']['text']))
        assert len(pairs) == 8 and pairs == visible_faq == faq_source
        continue
    task = by_directory[page.parent.name]
    assert page.name == 'index.html' and len(title) <= 60, page
    entry = copy['tasks'][task['directory']]
    assert title == copy['templates']['title'].format(**task)
    assert description == copy['templates']['description'].format(**entry)
    longest_title = max(longest_title, len(title))
    longest_description = max(longest_description, len(description))
    graph, = blocks
    webpage, crumb = graph['@graph']
    assert webpage['@type'] == 'WebPage' and webpage['@id'] == webpage['url'] == url
    assert webpage['name'] == title and webpage['description'] == description
    assert webpage['isPartOf']['@id'] == base+'#website' and webpage['about']['@id'] == base+'#dataset'
    assert crumb['@type'] == 'BreadcrumbList' and webpage['breadcrumb']['@id'] == crumb['@id']
    assert [item['item'] for item in crumb['itemListElement']] == [base, url]
    content = StaticContainers()
    content.feed(html)
    main = content.elements['task-details']
    assert visible(main.find('.//h1')) == task['name']
    assert visible(main.find(".//p[@class='eyebrow']")) == copy['templates']['subtitle'].format(**task)
    assert visible(main.find(".//div[@class='task-intro']/div/p[last()]")) == entry['summary']
    parts = [visible(p) for p in main.findall(".//div[@class='task-contract']/div/p")]
    assert parts == [entry[k] for k in ['workload', 'correctness', 'timing'] if entry[k]], page
    limits = metadata[task['directory']]
    assert (task['version'], task['cpus'], task['memory_gib'], task['agent_hours']) == (
        limits['version'], limits['cpus'], limits['memory_mb']/1024, limits['agent_timeout_sec']/3600)
    params = main.findall(".//div[@class='task-meta']/span")
    assert [p.text for p in params] == ['Task version','CPU budget','Memory','Agent budget','Harbor Hub']
    harbor = params[-1].find('strong/a')
    if task['harbor']:
        assert harbor is not None and harbor.get('href') == task['harbor']
    else:
        assert harbor is None and task['name'] == 'ICON'
    assert [visible(p.find('strong')) for p in params] == [
        task['version'], f"{task['cpus']} CPUs", f"{task['memory_gib']} GiB", f"{task['agent_hours']} hours",
        'Open task ↗' if task['harbor'] else 'Full release only']
    assert [visible(th) for th in main.findall('.//thead/tr/th')] == ['Agent model', 'Reward']
    actual = [[visible(td) for td in row.findall('td')] for row in main.findall('.//tbody/tr')]
    expected = []
    for model, reward in zip(data['models'], task['rewards_percent']):
        value = 'Failed correctness' if reward is None else f'{reward:.1f}%'
        if model['name'] in task['stopped_agents']:
            value = 'Stopped by the provider’s safety system (scored as a failure)'
        expected.append([model['name'], value])
    assert actual == expected, page
print(f'PASS: {len(pages)} HTML pages and their JSON-LD, eight matching FAQ pairs, '
      f'32 task parameter sets and 512 ordered rewards. Task title/description maxima '
      f'{longest_title}/{longest_description}. Exact scholarly title preserved ({len(data["title"])} characters).')
