from pathlib import Path
import json, re
from shutil import copy2
from lxml import html
from PIL import Image, ImageOps

root = Path(__file__).parent
archive = root.parent / 'esmengineers.com'
kit = root.parent / 'esm-brand/kit'
trends = root.parent / 'esm-trends/kit/04-Typography'
assets = root / 'source/assets'

def convert(path, name, width=1500):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    im.thumbnail((width, width), Image.Resampling.LANCZOS)
    im.save(assets / name, 'WEBP', quality=84, method=6)

for label, filename in {
    'switchgear': 'Picss5-4d92aa4a1dbb.png',
    'field-engineer':'IMG_1242-358cc5212665.jpg',
    'design':'Picss3-198314aecfaf.png',
    'equipment':'IMG_0734-194f5fd243c6.jpg',
    'testing':'IMG_1239-58e45302f474.jpg',
    'ups':'IMG_0739-4815dbc6a2bf.jpg',
}.items():
    convert(archive/'assets'/filename, label+'.webp')
copy2(kit/'01-Logos/ESM-Primary-Logo-On-Dark.png', assets/'esm-logo.png')
copy2(kit/'01-Logos/ESM-Logo-Mark.png', assets/'esm-mark.png')
for f in trends.iterdir():
    # Pages load the typefaces from template-assets; the licences stay with the site assets.
    if f.suffix == '.ttf':
        copy2(f, root/'source/template-assets'/f.name)
    elif f.suffix == '.txt':
        copy2(f, assets/f.name)
posts = []
for p in (archive/'blog').glob('*.html'):
    tree=html.fromstring(p.read_text())
    content=tree.xpath('//*[contains(concat(" ",normalize-space(@class)," "), " e-content ")]')[0]
    title=' '.join(tree.xpath('//main//h1')[0].text_content().split())
    title=re.sub(r'[\s🍽️❄⚽🌎]+$', '', title)
    date=tree.xpath('//main//time')[0].get('datetime')
    name=p.stem
    blocks=[]
    for element in content.xpath('.//p|.//h2|.//h3|.//h4|.//img|.//li[not(descendant::p)]'):
        if element.tag == 'img':
            src=element.get('src')
            if not src or not (p.parent/src).is_file():
                continue
            file=f'post-{date}-{len(blocks)}.webp'
            convert(p.parent/src,file,1350)
            blocks.append(['image',file])
            continue
        value=' '.join(element.text_content().split())
        if value:
            blocks.append(['heading' if element.tag.startswith('h') else 'text',value])
    excerpt=next((b[1] for b in blocks if b[0]=='text'), '')
    words=excerpt.split()
    excerpt=' '.join(words[:25])+('…' if len(words)>25 else '')
    image=next((b[1] for b in blocks if b[0]=='image'),'switchgear.webp')
    posts.append(dict(slug=name,title=title,date=date,excerpt=excerpt,cover=image,blocks=blocks))
(root/'source/posts.json').write_text(json.dumps(sorted(posts,key=lambda p:p['date'],reverse=True),indent=2,ensure_ascii=False)+'\n')
