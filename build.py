from datetime import date
from html import escape
import json
from pathlib import Path
from posixpath import relpath
from source.services import SERVICES

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
SRC = ROOT / 'source'
POSTS = json.loads((SRC/'posts.json').read_text())
PHONE, DISPLAY, EMAIL = '+18443763647', '+1 (844) 376-3647', 'contact@esmengineers.com'
LABELS = {
    'en': dict(home='Home', services='Services', about='About', blog='Insights', contact='Contact',
               ups='UPS support', call='Call UPS', project='Discuss a project', explore='Explore services',
               menu='Menu', skip='Skip to content', all='All services', read='Read article', more='View all insights'),
    'es': dict(home='Inicio', services='Servicios', about='Nosotros', blog='Noticias', contact='Contacto',
               ups='Asistencia para UPS', call='Llamar UPS', project='Consulte su proyecto', explore='Ver servicios',
               menu='Menú', skip='Ir al contenido', all='Todos los servicios', read='Leer artículo', more='Ver todas las noticias'),
}
ALTS = {
    'switchgear.webp': ('Row of industrial electrical switchgear cabinets','Fila de gabinetes eléctricos industriales'),
    'field-engineer.webp': ('Field worker beside electrical equipment','Técnico junto a equipos eléctricos'),
    'design.webp': ('Engineering drawings and hard hats on a worktable','Planos de ingeniería y cascos sobre una mesa de trabajo'),
    'equipment.webp': ('Electrical components inside equipment','Componentes eléctricos dentro de un equipo'),
    'testing.webp': ('Field worker inspecting electrical panels','Técnico inspeccionando tableros eléctricos'),
    'ups.webp': ('Technician beside an electrical equipment cabinet','Técnico junto a un gabinete de equipos eléctricos'),
}
OUT = '<svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 18 18 6M7 6h11v11"/></svg>'
def esc(x):
    return escape(x, quote=True)

def loc(lang, path=''):
    return ('es/' if lang=='es' else '') + path

def page_file(path):
    return path.rstrip('/') + '/index.html' if path else 'index.html'

class Page:
    def __init__(self, lang, route='', current='', translated=True):
        self.lang, self.route, self.current = lang, route, current
        self.es = lang=='es'
        self.words = LABELS[lang]
        self.file = page_file(loc(lang,route))
        self.folder = str(Path(self.file).parent)
        self.translated = translated
        # A server can show a page such as 404.html at any URL depth, so it needs root-absolute links.
        self.absolute = False

    def t(self, english, spanish):
        return spanish if self.es else english

    def url(self, route='', lang=None):
        target = loc(lang or self.lang,route)
        if self.absolute:
            return '/' + (target.rstrip('/') + '/' if target else '')
        return relpath(page_file(target),self.folder)

    def asset(self, filename):
        if self.absolute:
            return '/assets/' + filename
        return relpath('assets/'+filename,self.folder)

    def photo(self, name, cls='', lazy=True, decorative=False):
        alt = '' if decorative else ALTS.get(name,('Photo from the ESM Engineers article','Foto del artículo de ESM Engineers'))[self.es]
        loading = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
        return f'<img class="{cls}" src="{self.asset(name)}" alt="{esc(alt)}"{loading}>'

    def display_date(self, iso):
        d=date.fromisoformat(iso)
        if self.es:
            months='enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split()
            return f'{d.day} de {months[d.month-1]} de {d.year}'
        return f'{d:%B} {d.day}, {d.year}'

def inquiry(p, support=False):
    labels = p.t(
        ['Name','Company','Work email','Phone','Service of interest','Project details','Prepare project email','This opens a draft in your email app. You can review it before sending.'],
        ['Nombre','Empresa','Correo de trabajo','Teléfono','Servicio de interés','Detalles del proyecto','Preparar correo del proyecto','Se abrirá un borrador en su aplicación de correo. Puede revisarlo antes de enviarlo.'])
    if support:
        labels = p.t(
            ['Name','Company','Email','Callback number','UPS make and model','Issue and site location','Prepare support email','For urgent support, call. This form prepares a follow-up email.'],
            ['Nombre','Empresa','Correo electrónico','Número de contacto','Marca y modelo de UPS','Problema y ubicación','Preparar correo de asistencia','Para asistencia urgente, llame. Este formulario prepara un correo de seguimiento.'])
    options=''.join(f'<option>{esc(s[p.lang][0])}</option>' for s in SERVICES)
    field=f'<input id="topic" name="{labels[4]}" maxlength="120" required>' if support else f'<select id="topic" name="{labels[4]}" required><option value="">{p.t("Select a service","Seleccione un servicio")}</option>{options}</select>'
    status=p.t('Your draft is ready. Send it from your email app, or copy your details into a message to the address above.',
               'Su borrador está listo. Envíelo desde su aplicación de correo o copie los datos en un mensaje a la dirección indicada.')
    subject=p.t('UPS support request','Solicitud de asistencia para UPS') if support else p.t('Project inquiry','Consulta de proyecto')
    return f'''<form class="inquiry" data-email="{EMAIL}" data-subject="{subject}" data-status="{status}">
<div class="field"><label for="person">{labels[0]}</label><input id="person" name="{labels[0]}" autocomplete="name" maxlength="100" required></div>
<div class="field"><label for="company">{labels[1]}</label><input id="company" name="{labels[1]}" autocomplete="organization" maxlength="100" required></div>
<div class="field"><label for="email">{labels[2]}</label><input id="email" type="email" name="{labels[2]}" autocomplete="email" maxlength="150" required></div>
<div class="field"><label for="phone">{labels[3]}{' *' if support else ''}</label><input id="phone" type="tel" name="{labels[3]}" autocomplete="tel" maxlength="40" {'required' if support else ''}></div>
<div class="field wide"><label for="topic">{labels[4]}</label>{field}</div>
<div class="field wide"><label for="details">{labels[5]}</label><textarea id="details" rows="5" name="{labels[5]}" maxlength="1200" required></textarea></div>
<div class="wide"><p class="form-note">{labels[7]}</p><button class="button primary" type="submit" disabled>{labels[6]} {OUT}</button><p class="form-status" role="status"></p>
<noscript><p>{p.t('Email us directly at','Escríbanos directamente a')} <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></noscript></div></form>'''

if __name__ == '__main__':
    import sys
    # template_build imports this module as "build"; reuse it instead of loading a second copy.
    sys.modules.setdefault('build', sys.modules[__name__])
    from template_build import build
    build()
