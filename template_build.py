from copy import deepcopy
from pathlib import Path
from posixpath import normpath
from shutil import copy2, copytree, rmtree
import re
from urllib.parse import urlsplit
from lxml import html, etree

from build import Page, SERVICES, POSTS, ROOT, SRC, DIST, EMAIL, PHONE, DISPLAY, esc, inquiry

TEMPLATES = SRC/'template'
VENDOR = SRC/'template-assets'
VENDOR.mkdir(exist_ok=True)
SNAPSHOT = ROOT.parent/'trends-eng.webflow.io/assets'

def select(node, token):
    return node.xpath('descendant-or-self::*[contains(concat(" ",normalize-space(@class)," "),$k)]',k=f' {token} ')

def one(node, token):
    return next(iter(select(node,token)),None)

def trim(node,*classes):
    for cl in classes:
        for el in select(node,cl):
            if el.getparent() is not None:
                el.getparent().remove(el)

def put(node, value):
    if node is None:
        return
    for child in list(node):
        node.remove(child)
    node.text = value

def txt(node, cls, text):
    put(one(node,cls),text)

def setall(node, cls, text):
    for n in select(node,cls):
        put(n,text)

def fragment(node, source):
    for item in html.fragments_fromstring(source):
        if isinstance(item,str):
            node.text=(node.text or '')+item
        else:
            node.append(item)

def body_parts(tree,*keep):
    body=tree.find('body')
    for n in list(body):
        if not isinstance(n.tag,str):
            body.remove(n)
        elif n.tag not in ('script','style') and not set(n.get('class','').split()).intersection(keep):
            body.remove(n)
    return body

def setimg(el, page, filename, alt=''):
    if el is not None:
        el.set('src',page.asset(filename))
        el.set('alt',alt)
        for a in ('srcset','sizes'):
            el.attrib.pop(a,None)

def replace_images(node,p,files):
    for img,file in zip(node.xpath('.//img'),files):
        setimg(img,p,file)

def btn(node, label, href):
    if node is None:
        return
    node.set('href',href)
    for cl in ('button-text-front','button-text-back'):
        setall(node,cl,label)

def logo(p):
    return f'<img class="nav-logo-image" src="{p.asset("esm-logo.png")}" alt="ESM Engineers">'

def load_template(name,page):
    tree=html.fromstring((TEMPLATES/name).read_text())
    tree.set('lang',page.lang)
    for key in ('data-wf-domain','data-wf-status'):
        tree.attrib.pop(key,None)
    for e in tree.iter():
        if not isinstance(e.tag,str):
            continue
        for attr in ('src','href','poster'):
            value=e.get(attr,'')
            m=re.match(r'^(?:\.\./)*assets/(.+)$',value)
            if m:
                e.set(attr,'vendor:'+m[1])
    title=tree.find('.//title')
    for e in tree.xpath('//meta[not(@charset) and not(@name="viewport")]|//head/link[not(@rel="stylesheet")]'):
        e.getparent().remove(e)
    for e in tree.xpath('//script[@src="vendor:offline.js"]'):
        e.getparent().remove(e)
    head=tree.find('head')
    fragment(head,f'<meta name="robots" content="noindex, nofollow"><link rel="icon" href="{page.asset("esm-mark.png")}"><link rel="stylesheet" href="{page.asset("esm-template.css")}"><script defer src="{page.asset("esm-template.js")}"></script>')
    return tree,title

def header(tree,p,home=False):
    root=one(tree,'header')
    root.tag='header'
    root.set('class',root.get('class','')+(' esm-home-header' if home else ' esm-inner-header'))
    a=one(root,'nav-logo')
    a.set('href',p.url()); a.attrib.pop('aria-current',None)
    put(a,'')
    fragment(a,logo(p))
    menu=one(root,'menu-wrapper')
    sample=deepcopy(one(menu,'menu-item'))
    put(menu,'')
    for key in ('services','about','blog','contact'):
        item=deepcopy(sample)
        link=item.find('.//a')
        link.set('href',p.url(key))
        txt(link,'nav-front-text',p.words[key])
        if p.current==key:
            link.set('aria-current','page')
        menu.append(item)
    for href,label,cl in [
        (p.url('services/ups-support'),p.words['ups'],'esm-nav-support'),
        (p.url(p.route if p.translated else 'blog','en' if p.es else 'es'),'EN' if p.es else 'ES','esm-nav-language'),
    ]:
        item=deepcopy(sample)
        item.set('class',item.get('class')+' '+cl)
        link=item.find('.//a');link.set('href',href);txt(link,'nav-front-text',label)
        if cl.endswith('language'):
            link.set('hreflang','en' if p.es else 'es')
        menu.append(item)
    btn(one(one(root,'nav-button-block'),'icon-button'),p.words['project'],p.url('contact'))
    group=one(root,'humburger-and-button')
    anchor=html.fragment_fromstring(f'<a class="esm-mobile-call" href="tel:{PHONE}">{p.words["call"]}</a>')
    group.insert(list(group).index(one(group,'humberger-menu-wrap')),anchor)

def footer(tree,p):
    f=one(tree,'footer')
    setimg(one(f,'footer-thumbnail'),p,'switchgear.webp')
    trim(f,'footer-newsletter','address-block','privacy-menu-box','social-box-list','footer-contact','follow-box','white-menu-box')
    a=one(f,'footer-logo'); a.set('href',p.url())
    setimg(a.find('img'),p,'esm-logo.png','ESM Engineers')
    txt(f,'footer-title','ESM Engineers')
    txt(f,'copyright-text','© ESM Engineers')
    top=next((x for x in select(f,'footer-top-block') if 'bottom' in x.get('class','').split()),None)
    if top is not None and len(top)==0:
        top.getparent().remove(top)
    menu=one(f,'menu-group-list');put(menu,'')
    groups=[
        [(p.url(key),p.words[key]) for key in ('services','about','blog','contact')],
        [(p.url('services/'+s['slug']),s[p.lang][0]) for s in SERVICES],
        [(f'mailto:{EMAIL}',EMAIL),(f'tel:{PHONE}',DISPLAY),('https://www.linkedin.com/company/electrical-systems-management-llc','LinkedIn')],
    ]
    for group in groups:
        items=''.join(f'<a class="footer-contact-link _03 w-inline-block" href="{esc(href)}"><div>{esc(label)}</div></a>' for href,label in group)
        fragment(menu,f'<div class="single-menu-box">{items}</div>')

def cta(tree,p):
    x=one(tree,'cta')
    if x is None:
        return
    trim(x,'subtitle-box')
    txt(x,'cta-home-title',p.t('Start your project','Inicie su proyecto'))
    txt(x,'cta-text',p.t('Talk with our team about engineering design, testing, or critical power support.',
                          'Hable con nuestro equipo sobre diseño de ingeniería, pruebas o asistencia para energía crítica.'))
    a,b=select(x,'icon-button')[:2]
    btn(a,p.words['project'],p.url('contact'))
    btn(b,p.words['ups'],p.url('services/ups-support'))

def about_slice(x,p):
    txt(x,'subtitle-text',p.t('Our story','Nuestra historia'))
    txt(x,'about-vision-title',p.t('How we work','Cómo trabajamos'))
    txt(x,'vision-text',p.t('We work alongside owners, architects, and facility teams.',
                            'Trabajamos con propietarios, arquitectos y equipos de instalaciones.'))
    txt(x,'about-section-title',p.t('Engineering for the systems your facility depends on.',
                                   'Ingeniería para los sistemas de los que depende su instalación.'))
    trim(x,'about-ticker-box','about-user-box','project-author-box','award-logo-box')
    for n in select(x,'about-meta-text-box'):
        put(n,'')
        fragment(n,f'<p class="vision-text">{p.t("From building design to commissioning and maintenance, ESM helps facilities plan and verify how critical systems perform.","Desde el diseño hasta la puesta en servicio y el mantenimiento, ESM ayuda a planificar y verificar el desempeño de los sistemas críticos.")}</p>')
    if (n:=one(x,'image-block')) is not None:
        if p.route=='about':
            setimg(n.find('.//img'),p,'houston-skyline.webp',p.t('Downtown Houston skyline','Horizonte del centro de Houston'))
        else:
            setimg(n.find('.//img'),p,'design.webp')
    for n,file in zip(select(x,'single-image-slider'),('testing.webp','switchgear.webp','field-engineer.webp')):
        setimg(n,p,file)
    b=one(x,'icon-button')
    btn(b,p.t('About ESM','Acerca de ESM'),p.url('about'))

def blog_cards(parent,p,posts):
    cards=select(parent,'blog-collection-item')
    if not cards:
        return
    listnode=cards[0].getparent()
    prototype=deepcopy(cards[0])
    for n in cards:
        listnode.remove(n)
    for entry in posts:
        card=deepcopy(prototype)
        one(card,'blog-card-item').set('href',p.url('blog/'+entry['slug'],'en'))
        setimg(card.find('.//img'),p,entry['cover'])
        txt(card,'blog-date-text',p.display_date(entry['date']))
        txt(card,'blog-category-text',p.t('Company news','Noticias'))
        txt(card,'blog-card-title',entry['title'])
        txt(card,'blog-text',entry['excerpt'])
        if p.es:
            # Articles are published in English only.
            for cl in ('blog-card-title','blog-text'):
                if (n:=one(card,cl)) is not None:
                    n.set('lang','en')
        listnode.append(card)
    trim(parent,'blog-pagination')

def home(tree,p):
    body=body_parts(tree,'hero-content-wrapper','service','blog','cta','footer')
    h=one(tree,'hero')
    title=p.t('Engineering design, testing, and critical power support','Diseño, pruebas y soporte de energía crítica')
    intro=p.t('We design commercial building systems, verify how they perform, and maintain critical power equipment.',
              'Diseñamos sistemas para edificios comerciales, verificamos su desempeño y mantenemos equipos de energía crítica.')
    txt(h,'hero-main-title',title)
    txt(h,'hero-text',intro)
    btn(one(one(h,'hero-text-button'),'icon-button'),p.words['explore'],p.url('services'))
    photos=[
        ('office','office-facade.webp',p.t('Glass office building under a blue sky','Edificio de oficinas de vidrio bajo un cielo azul')),
        ('rooftop','rooftop-cooling.webp',p.t('Cooling towers on a commercial rooftop','Torres de enfriamiento en la azotea de un edificio comercial')),
        ('testing','testing.webp',p.t('Field technician inspecting electrical cabinets','Técnico en campo inspeccionando gabinetes eléctricos')),
    ]
    scene,file,alt=photos[0]
    banner=one(h,'banner-image')
    setimg(banner,p,file,alt)
    banner.set('data-hero-scene',scene)
    banner.attrib.pop('loading',None)
    banner.set('fetchpriority','high')
    badge=one(h,'hero-base');badge.set('href',p.url('contact'));badge.set('aria-label',p.words['project'])
    setimg(one(h,'bage-image'),p,'esm-hero-badge-es.svg' if p.es else 'esm-hero-badge.svg')
    for i,(item,(scene,file,alt)) in enumerate(zip(select(h,'hero-image-box'),photos)):
        item.tag='button'
        item.attrib.pop('href',None)
        item.set('type','button')
        item.set('data-hero-image',p.asset(file))
        item.set('data-hero-scene',scene)
        item.set('aria-label',alt)
        item.set('aria-pressed','true' if i==0 else 'false')
        trim(item,'hidden-text')
        setimg(one(item,'slider-image-hero'),p,Path(file).stem+'-thumb.webp')
    about_slice(one(tree,'about'),p)
    services=one(tree,'service-content-wrapper')
    txt(services,'service-title',p.t('Engineering services','Servicios de ingeniería'))
    txt(services,'subtitle-text',p.words['services'])
    for i,(s,link,box) in enumerate(zip(SERVICES,select(services,'service-title-link'),select(services,'single-image-service'))):
        title=s[p.lang][0]
        href=p.url('services/'+s['slug'])
        link.set('href',href);link.set('data-service-index',str(i))
        txt(link,'service-card-title',title)
        photo=one(box,'single-servic-image');photo.set('href',href)
        setimg(photo.find('.//img'),p,s['image'])
        put(one(box,'service-category-box'),title)
    more=one(services,'more-service-text');more.text=''
    link=one(more,'all-service-link');link.set('href',p.url('services'));put(link,p.words['all'])
    blog=one(tree,'blog')
    txt(blog,'subtitle-text',p.words['blog'])
    txt(blog,'blog-title',p.t('News from ESM Engineers','Noticias de ESM Engineers'))
    btn(one(blog,'icon-button'),p.words['more'],p.url('blog'))
    blog_cards(blog,p,POSTS[:3])
    return 'ESM Engineers',intro

def service_list(tree,p):
    body_parts(tree,'header','service-hero','service-milti','cta','footer')
    x=one(tree,'service-hero')
    title=p.t('Engineering services','Servicios de ingeniería')
    intro=p.t('Design, verification, and field support for commercial buildings and critical facilities.',
              'Diseño, verificación y asistencia en campo para edificios comerciales e instalaciones críticas.')
    txt(x,'hero-service-title',title)
    txt(x,'subtitle-text',p.words['services'])
    txt(x,'service-hero-text',intro)
    trim(x,'our-partner')
    for image,asset in zip(select(one(x,'service-hero-right'),'image-cut'),('switchgear.webp','field-engineer.webp')):
        setimg(image,p,asset)
    btn(one(x,'icon-button'),p.words['project'],p.url('contact'))
    x=one(tree,'service-milti')
    txt(x,'service-section-title',p.t('Explore our services','Explore nuestros servicios'))
    for s,card in zip(SERVICES,select(x,'service-collection-item')):
        title2,summary,*_=s[p.lang]
        one(card,'service-item-link').set('href',p.url('services/'+s['slug']))
        txt(card,'service-card-title',title2)
        txt(card,'servcie-excerpt',summary)
        setall(card,'button-text-front',p.t('Service details','Ver servicio'))
        setall(card,'button-text-back',p.t('Service details','Ver servicio'))
        setimg(card.find('.//img'),p,s['image'])
    return title,intro

def detail_banner(tree,p,title,intro,image,eyebrow):
    x=one(tree,'service-details-banner')
    txt(x,'service-details-title',title)
    txt(x,'service-excerpt',intro)
    txt(x,'subtitle-text',eyebrow)
    txt(x,'banner-button-text',p.t('Read more','Leer más'))
    alt=p.t('Industrial electrical switchgear cabinets','Gabinetes de distribución eléctrica industrial') if image=='switchgear.webp' else ''
    if image=='rooftop-cooling.webp':
        alt=p.t('Cooling towers on a commercial rooftop','Torres de enfriamiento en la azotea de un edificio comercial')
    setimg(one(x,'service-details-image'),p,image,alt)
    trim(x,'details-banner-gallery','blog-details-block')
    return x

def service_detail(tree,p,service):
    body_parts(tree,'header','service-details-banner','service-details','footer')
    title,intro,heading,detail,scopes=service[p.lang]
    detail_banner(tree,p,title,intro,service['image'],p.words['services'])
    x=one(tree,'service-details')
    x.set('id','content-details')
    txt(one(x,'service-sidebar'),'subtitle-text',p.words['services'])
    sidebar=one(x,'sidebar-cllection-list');put(sidebar,'')
    for item in SERVICES:
        cls=' esm-current-service' if item==service else ''
        fragment(sidebar,f'<div class="sidebar-cllection-item w-dyn-item"><a class="esm-sidebar-link{cls}" href="{p.url("services/"+item["slug"])}">{esc(item[p.lang][0])}</a></div>')
    main=one(x,'project-details-box')
    keep=deepcopy(one(main,'icon-button'))
    put(main,'')
    fragment(main,f'<div class="single-details-block"><div class="w-richtext"><h2>{esc(heading)}</h2><p>{esc(detail)}</p></div></div>')
    scope=''.join(f'<div class="single-process-card"><h3>{esc(h)}</h3><p>{esc(b)}</p></div>' for h,b in scopes)
    fragment(main,f'<div class="details-process-block"><h2 class="details-process-title">{p.t("Service scope","Alcance del servicio")}</h2><div class="process-card-box esm-process-grid">{scope}</div></div>')
    if service['slug']=='ups-support':
        fragment(main,f'<p><a class="esm-direct-call" href="tel:{PHONE}">{p.words["call"]} · {DISPLAY}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>')
        fragment(main,inquiry(p,True))
    else:
        btn(keep,p.words['project'],p.url('contact'));main.append(keep)
    return title,intro

def about_page(tree,p):
    body_parts(tree,'header','about-hero','landing-about','our-value','cta','footer')
    title=p.t('About ESM Engineers','Acerca de ESM Engineers')
    intro=p.t('Engineering consulting for commercial, industrial, and public-sector facilities.',
              'Consultoría de ingeniería para instalaciones comerciales, industriales y del sector público.')
    txt(tree,'about-hero-title',title)
    x=one(tree,'about-showcase')
    replace_images(x,p,['design.webp','switchgear.webp'])
    txt(x,'about-overlay-title',p.t('Critical power support','Asistencia para energía crítica'))
    txt(one(tree,'about-header-top'),'subtitle-text',p.t('Our story','Nuestra historia'))
    for n,v in zip(select(x,'about-gallery-title'),[p.t('Commercial design','Diseño comercial'),p.t('Testing and verification','Pruebas y verificación'),p.t('Critical power support','Asistencia para energía crítica')]):
        put(n,v)
    about_slice(one(tree,'landing-about'),p)
    value=one(tree,'value-content-wrapper')
    if value is not None:
        put(value,'')
        labels=p.t([('Collaboration','Work with owners, architects, and operators.'),('Diversity','Bring different technical perspectives to each project.'),('Creativity','Develop practical solutions for complex problems.'),('Development','Build skills through training and mentorship.')],
                   [('Colaboración','Trabajamos con propietarios, arquitectos y operadores.'),('Diversidad','Aportamos distintas perspectivas técnicas a cada proyecto.'),('Creatividad','Desarrollamos soluciones prácticas para problemas complejos.'),('Desarrollo','Fortalecemos capacidades mediante capacitación y mentoría.')])
        blocks=''.join(f'<div class="single-process-card"><h3>{esc(h)}</h3><p>{esc(v)}</p></div>' for h,v in labels)
        fragment(value,f'<h2 class="value-title">{p.t("How we work","Cómo trabajamos")}</h2><div class="process-card-box esm-values-grid">{blocks}</div>')
    return title,intro

def contact_page(tree,p):
    body_parts(tree,'header','contact-header','contact-section','footer')
    title=p.t('Contact ESM Engineers','Contacte con ESM Engineers')
    intro=p.t('Tell us what you are planning and which engineering services you need.',
              'Cuéntenos qué está planeando y qué servicios de ingeniería necesita.')
    txt(tree,'contact-hero-title',title);txt(tree,'contact-block-title',p.words['project'])
    txt(one(tree,'contact-hero'),'subtitle-text',p.words['contact'])
    txt(tree,'contact-block-text',intro)
    trim(one(tree,'contact-left-title-subtitle'),'subtitle-box')
    for card,(name,value,href) in zip(select(tree,'contact-icon-box'),[
        (p.t('Email','Correo'),EMAIL,'mailto:'+EMAIL),
        (p.t('Phone','Teléfono'),DISPLAY,'tel:'+PHONE),
        (p.words['ups'],p.words['call'],'tel:'+PHONE),
    ]):
        txt(card,'block-icon-title',name)
        if (icon:=one(card,'icon-image')) is not None:
            icon.set('alt','')
        link=one(card,'contact-icon-link')
        if link is not None:
            # Some template cards already wrap the text in a link; retarget it rather than nesting a second one.
            link.set('href',href)
            txt(link,'block-icon-text',value)
        else:
            node=one(card,'block-icon-text')
            put(node,'');fragment(node,f'<a href="{href}">{esc(value)}</a>')
    x=one(tree,'contact-right-content');put(x,'');fragment(x,inquiry(p))
    return title,intro

def blog_page(tree,p):
    body_parts(tree,'header','blog-header','blog-collection-area','cta','footer')
    title=p.words['blog']
    intro=p.t('News and updates from ESM Engineers.','Noticias de ESM Engineers. Los artículos se publicaron en inglés.')
    txt(tree,'blog-hero-title',title)
    txt(one(tree,'blog-header'),'subtitle-text',intro)
    for item,post in zip(select(tree,'featured-slider-content'),POSTS):
        item.set('href',p.url('blog/'+post['slug'],'en'))
        txt(item,'featured-post-title',post['title'])
        if p.es and (n:=one(item,'featured-post-title')) is not None:
            n.set('lang','en')
        txt(item,'featured-label',p.t('Featured post','Artículo destacado'))
        setimg(item.find('.//img'),p,post['cover'])
    blog_cards(one(tree,'blog-collection-area'),p,POSTS)
    return title,intro

def blog_detail(tree,p,post):
    body_parts(tree,'header','service-details-banner','blog-single','cta','footer')
    title,intro=post['title'],post['excerpt']
    x=detail_banner(tree,p,title,intro,post['cover'],p.words['blog'])
    parts=[f'<p class="esm-date"><time datetime="{post["date"]}">{p.display_date(post["date"])}</time></p>']
    skipped_cover=False
    for tag,value in post['blocks']:
        if tag=='image':
            if value==post['cover'] and not skipped_cover:
                skipped_cover=True
                continue
            parts.append(f'<figure>{p.photo(value)}</figure>')
        elif tag=='heading':
            parts.append(f'<h2>{esc(value)}</h2>')
        else:
            parts.append(f'<p>{esc(value)}</p>')
    article=html.fragment_fromstring('<article class="section-padding" id="content-details"><div class="w-layout-blockcontainer container w-container esm-article w-richtext">'+''.join(parts)+'</div></article>')
    x.addnext(article)
    related=one(tree,'blog-single')
    txt(related,'blog-title',p.t('More from ESM','Más de ESM'))
    btn(one(related,'icon-button'),p.words['more'],p.url('blog'))
    blog_cards(related,p,[a for a in POSTS if a!=post][:3])
    return title,intro

def write(tree,title_node,p,title,description):
    title_node.text=title if title=='ESM Engineers' else title+' | ESM Engineers'
    fragment(tree.find('head'),f'<meta name="description" content="{esc(description)}">')
    header(tree,p,home=not p.route)
    footer(tree,p)
    cta(tree,p)
    body=tree.find('body')
    skip=html.fragment_fromstring(f'<a class="esm-skip" href="#main">{p.words["skip"]}</a>')
    body.insert(0,skip)
    main=etree.Element('main',id='main')
    navigation=next(iter(tree.xpath('//body//header')),None)
    if navigation is not None and navigation.getparent() is not body:
        # The homepage template nests its absolutely positioned header inside the hero.
        # Lift it to the top of <body> so it stays a banner landmark outside <main>.
        navigation.getparent().remove(navigation)
        navigation.tail=None
        body.insert(1,navigation)
    if navigation is not None:
        navigation.addnext(main)
    else:
        body.insert(1,main)
    for child in list(body):
        if isinstance(child.tag,str) and child.tag not in ('main','script','style','header','footer') and child!=skip:
            main.append(child)
    for e in tree.iter():
        if not isinstance(e.tag,str):
            continue
        for key in ('src','href','poster'):
            val=e.get(key,'')
            if val.startswith('vendor:'):
                file=val[7:]
                vendor(file)
                e.set(key,p.asset('trends/'+file))
    path=DIST/p.file;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!doctype html>'))

def vendor(filename):
    # Resolve CSS-relative references such as "fonts/../x.woff" before the safety check.
    filename=normpath(filename)
    assert not filename.startswith('/') and '..' not in Path(filename).parts
    target=VENDOR/filename
    if target.exists():
        return
    source=SNAPSHOT/filename
    if not source.is_file():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True,exist_ok=True)
    copy2(source,target)
    if target.suffix=='.css':
        for raw in re.findall(r'url\(["\']?([^\)"\']+)',target.read_text()):
            if not urlsplit(raw).scheme and not raw.startswith(('#','/')):
                vendor(str(Path(filename).parent / raw))

def build():
    # Start from an empty output folder so removed pages and assets do not linger.
    rmtree(DIST,ignore_errors=True)
    for lang in ('en','es'):
        for path,key,name,fn in [
            ('','','index.html',home),('services','services','service-02.html',service_list),
            ('about','about','about-us.html',about_page),('contact','contact','contact.html',contact_page),
            ('blog','blog','blog.html',blog_page),
        ]:
            p=Page(lang,path,key)
            tree,title=load_template(name,p)
            write(tree,title,p,*fn(tree,p))
        for service in SERVICES:
            p=Page(lang,'services/'+service['slug'],'services')
            tree,title=load_template('service/commercial-construction.html',p)
            write(tree,title,p,*service_detail(tree,p,service))
    for post in POSTS:
        p=Page('en','blog/'+post['slug'],'blog',translated=False)
        tree,title=load_template('blog/innovative-materials.html',p)
        write(tree,title,p,*blog_detail(tree,p,post))
    p=Page('en','not-found')
    p.file='404.html'
    p.folder='.'
    p.absolute=True
    tree,title=load_template('contact.html',p)
    body_parts(tree,'header','contact-header','footer')
    lead=one(tree,'contact-hero')
    trim(lead,'subtitle-box')
    txt(lead,'contact-hero-title','Page not found')
    fragment(lead,f'<p><a class="esm-404-link" href="{p.url()}">Go to homepage</a></p>')
    p.translated=False
    write(tree,title,p,'Page not found','The requested page may have moved.')
    copytree(SRC/'assets',DIST/'assets',dirs_exist_ok=True)
    copytree(VENDOR,DIST/'assets'/'trends',dirs_exist_ok=True)
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    print('Built Trends-Eng layouts for both languages and the five archived articles.')
