"""Build a platform's User Guide deck from the house User Guide template.

  python3 -E build.py <template.pptx> <screenshots dir> <out.pptx> <heights.json> <content dir>
  python3 -E build.py --heights-from <measure.json> <manifest.json> <heights.json>

<content dir> holds the platform's content.py (every word and callout) and receives
manifest.json (the slide order). content.py may set ACCENT (hex, no #; the template's
own violet is 901A8A) and TOC_INTRO = (bold lead, rest of the sentence).

The deck keeps the template's own masters, layouts, embedded fonts and artwork:
its cover, contents and introduction slides are edited in place, and every
screenshot slide is a clone of its "Understanding the ..." slide (title bar +
Table of Contents button), with the badges, arrows, highlight boxes and the
description list generated here, in the platform's accent colour.

Slides whose screenshot is missing are dropped with a warning, and so are contents
entries whose slides are gone, so one failed capture never stops the deck.

Text heights can only be known after PowerPoint lays the text out, so run.sh
builds once, measures each description in PowerPoint (render-measure.ps1),
converts that with --heights-from, and builds again. See ../SKILL.md.
"""
import copy, json, os, re, shutil, sys, tempfile, zipfile
from lxml import etree
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
DECL = ' '.join(f'xmlns:{k}="{NS[k]}"' for k in ('p', 'a', 'r'))
R_SLIDE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'
R_IMAGE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
CT_SLIDE = 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
TEMPLATE_VIOLET = ('901A8A', 'AB44FF')  # the template's own accent
EMU = 914400
VIEW_W, VIEW_H = 1600, 900            # CSS px of the capture viewport

# Template slides that are kept or used as a base
COVER, INTRO_SLIDE, SHOT_BASE = 'slide1.xml', 'slide7.xml', 'slide14.xml'
TOC_SLIDES = ['slide2.xml', 'slide3.xml', 'slide4.xml', 'slide5.xml']   # the template's two-column contents slides
PER_COLUMN = 13                                                          # entries per column; 26 per contents slide

# Default screenshot placement (inches) and the template's badge size
FULL_PLACE = dict(x=0.95, y=1.95, w=8.0)
BADGE_W, BADGE_H = 224583 / EMU, 246180 / EMU
DESC_X, DESC_W, DESC_Y, DESC_GAP, TEXT_DX = 9.82, 3.12, 1.70, 0.13, 0.34
SLIDE_BOTTOM_LIMIT = 7.15             # descriptions must end above this
MAX_IMAGE_W = 2000                    # px; screenshots are captured at 3200 (~250 dpi at the 8" a full one is shown at)


def E(inches):
    return int(round(inches * EMU))


def parse(path):
    return etree.parse(path)


def write(tree, path):
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)


def frag(xml):
    return etree.fromstring(f'<root {DECL}>{xml}</root>')[0]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# Links keep the text colour (the template's own trick) instead of the theme's green/blue hyperlink colour
HLINK_AS_TEXT = ('<a:extLst><a:ext uri="{A12FA001-AC4F-418D-AE19-62706E023703}">'
                 '<ahyp:hlinkClr xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor" val="tx"/></a:ext></a:extLst>')
NBSP = '\u00a0'   # keeps a link label on one line
FONT = '<a:latin typeface="Poppins"/><a:ea typeface="Poppins"/><a:cs typeface="Poppins"/><a:sym typeface="Poppins"/>'


class Rels:
    """A slide's relationships file, with helpers to add links and images."""

    def __init__(self, path):
        self.path, self.tree = path, parse(path)

    def add(self, typ, target):
        ids = {r.get('Id') for r in self.tree.getroot()}
        n = 1
        while f'rId{n}' in ids:
            n += 1
        el = etree.SubElement(self.tree.getroot(), f'{{{NS["rel"]}}}Relationship')
        el.set('Id', f'rId{n}'); el.set('Type', typ); el.set('Target', target)
        return f'rId{n}'

    def keep_only(self, types=('/slideLayout',), targets=()):
        for r in list(self.tree.getroot()):
            if not (r.get('Type').endswith(types) or r.get('Target') in targets):
                self.tree.getroot().remove(r)

    def save(self):
        write(self.tree, self.path)


def runs(md, rels=None, links=None, sz=1000, color='<a:schemeClr val="tx1"/>'):
    """**bold** and [[label|slide-key]] markup -> a:r runs."""
    out = []
    for part in re.split(r'(\[\[[^\]]+\]\])', md):
        m = re.fullmatch(r'\[\[([^|\]]+)\|([^\]]+)\]\]', part)
        if m:
            label, key = m.groups()
            rid = rels.add(R_SLIDE, links[key])
            out.append(f'<a:r><a:rPr lang="en-US" sz="{sz}" b="1" u="sng" dirty="0"><a:solidFill>{color}</a:solidFill>{FONT}'
                       f'<a:hlinkClick r:id="{rid}" action="ppaction://hlinksldjump">{HLINK_AS_TEXT}</a:hlinkClick></a:rPr><a:t>{esc(label).replace(" ", NBSP)}</a:t></a:r>')
            continue
        for i, bit in enumerate(re.split(r'\*\*', part)):
            if bit:
                b = ' b="1"' if i % 2 else ''
                out.append(f'<a:r><a:rPr lang="en-US" sz="{sz}"{b} dirty="0"><a:solidFill>{color}</a:solidFill>{FONT}</a:rPr>'
                           f'<a:t xml:space="preserve">{esc(bit)}</a:t></a:r>')
    return ''.join(out)


class Shapes:
    """Generates the shape XML for one slide, keeping cNvPr ids unique."""

    def __init__(self):
        self.next_id = 3000

    def id(self):
        self.next_id += 1
        return self.next_id

    def badge(self, n, cx, cy):
        x, y = cx - BADGE_W / 2, cy - BADGE_H / 2
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{self.id()}" name="Badge {n}" descr="Small square with numeral {n} inside"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(BADGE_W)}" cy="{E(BADGE_H)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:solidFill><a:srgbClr val="{ACCENT}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr" anchorCtr="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
                f'<a:p><a:pPr algn="ctr"><a:buNone/></a:pPr><a:r><a:rPr lang="en-US" sz="1000" b="1" dirty="0"><a:solidFill><a:schemeClr val="lt1"/></a:solidFill>{FONT}</a:rPr><a:t>{n}</a:t></a:r></a:p></p:txBody></p:sp>')

    def arrow(self, x0, y0, x1, y1, n):
        fh = ' flipH="1"' if x1 < x0 else ''
        fv = ' flipV="1"' if y1 < y0 else ''
        return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{self.id()}" name="Arrow {n}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
                f'<p:spPr><a:xfrm{fh}{fv}><a:off x="{E(min(x0, x1))}" y="{E(min(y0, y1))}"/><a:ext cx="{E(abs(x1 - x0))}" cy="{E(abs(y1 - y0))}"/></a:xfrm>'
                f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom><a:noFill/>'
                f'<a:ln w="12700" cap="flat" cmpd="sng"><a:solidFill><a:srgbClr val="{ACCENT}"/></a:solidFill><a:prstDash val="solid"/><a:round/>'
                f'<a:headEnd type="none" w="sm" len="sm"/><a:tailEnd type="triangle" w="med" len="med"/></a:ln></p:spPr></p:cxnSp>')

    def box(self, x, y, w, h, n):
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{self.id()}" name="Highlight {n}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:noFill/><a:ln w="19050"><a:solidFill><a:srgbClr val="{ACCENT}"/></a:solidFill></a:ln></p:spPr></p:sp>')

    def pic(self, rid, x, y, w, h):
        return (f'<p:pic><p:nvPicPr><p:cNvPr id="{self.id()}" name="Screenshot"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
                f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
                f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
                f'<a:effectLst><a:outerShdw blurRad="63500" sx="102000" sy="102000" algn="ctr" rotWithShape="0"><a:prstClr val="black"><a:alpha val="40000"/></a:prstClr></a:outerShdw></a:effectLst></p:spPr></p:pic>')

    def text(self, x, y, w, h, body, name):
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="{self.id()}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
                f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:spAutoFit/></a:bodyPr><a:lstStyle/>'
                f'<a:p><a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:buNone/></a:pPr>{body}</a:p></p:txBody></p:sp>')


def estimate_h(md, width):
    """First-pass guess at a description's height; PowerPoint's measurement replaces it."""
    plain = re.sub(r'\[\[([^|\]]+)\|[^\]]+\]\]', r'\1', md).replace('**', '')
    per_line = max(10, int(width / 0.074))
    lines, cur = 1, 0
    for w in plain.split():
        if cur and cur + 1 + len(w) > per_line:
            lines, cur = lines + 1, len(w)
        else:
            cur += (1 if cur else 0) + len(w)
    return lines * 0.17


# --------------------------------------------------------------------------- --heights-from
if len(sys.argv) > 1 and sys.argv[1] == '--heights-from':
    measure, manifest, out = sys.argv[2:5]
    order = json.load(open(manifest))
    m = json.loads(open(measure, encoding='utf-8-sig').read())
    json.dump({order[int(k) - 1]: v for k, v in m.items() if v}, open(out, 'w'), indent=1, sort_keys=True)
    print('heights written for', len([v for v in m.values() if v]), 'slides')
    sys.exit(0)

TEMPLATE, SHOTS, OUT, HEIGHTS_FILE, CONTENT_DIR = sys.argv[1:6]
sys.path.insert(0, os.path.abspath(CONTENT_DIR))
import content  # noqa: E402
ACCENT = getattr(content, 'ACCENT', '901A8A').lstrip('#').upper()
HEIGHTS = json.load(open(HEIGHTS_FILE)) if os.path.exists(HEIGHTS_FILE) else {}
BUILD = tempfile.mkdtemp(prefix='user-guide-')
P = lambda *a: os.path.join(BUILD, *a)
zipfile.ZipFile(TEMPLATE).extractall(BUILD)

SLIDES = []
for _s in content.slides(SHOTS):
    if _s.get('template') or os.path.exists(os.path.join(SHOTS, _s['shot'])):
        SLIDES.append(_s)
    else:
        print('WARNING dropped slide', _s['key'], '- no screenshot', _s['shot'])
_keys = {_s['key'] for _s in SLIDES} | {'cover', 'toc', 'intro'}
TOC_ENTRIES = []
for _label, _key in content.TOC:
    if _key is None or _key in _keys:
        TOC_ENTRIES.append((_label, _key))
    else:
        print('WARNING dropped contents entry', repr(_label), '- its slides are missing')
content.TOC = TOC_ENTRIES
N_TOC = -(-len(content.TOC) // (2 * PER_COLUMN))
assert N_TOC <= len(TOC_SLIDES), f'{len(content.TOC)} contents entries need more than {len(TOC_SLIDES)} contents slides'
TOC_USED = TOC_SLIDES[:N_TOC]
TOC_KEYS = ['toc'] + [f'toc-{i}' for i in range(2, N_TOC + 1)]
TOC_SLIDE = TOC_USED[0]                 # what 'Table of Contents' buttons jump to
KEPT = [s['template'] for s in SLIDES if s.get('template')]          # template slides reused as they are
FIXED = (COVER, *TOC_USED, INTRO_SLIDE, *KEPT)  # template slides edited in place
ORDER = ['cover'] + TOC_KEYS + ['intro'] + [s['key'] for s in SLIDES]
assert len(set(ORDER)) == len(ORDER), 'slide keys must be unique'
FILE = {'cover': COVER, 'intro': INTRO_SLIDE, **dict(zip(TOC_KEYS, TOC_USED))}
for i, s in enumerate(SLIDES):
    FILE[s['key']] = s.get('template') or f'slide{200 + i}.xml'

# --------------------------------------------------------------------------- package surgery
base_xml = open(P('ppt/slides', SHOT_BASE), encoding='utf-8').read()
base_rels = open(P('ppt/slides/_rels', SHOT_BASE + '.rels'), encoding='utf-8').read()

pres = parse(P('ppt/presentation.xml'))
prels = parse(P('ppt/_rels/presentation.xml.rels'))
ct = parse(P('[Content_Types].xml'))
rid_target = {r.get('Id'): r.get('Target') for r in prels.getroot()}
sld_lst = pres.find('.//p:sldIdLst', NS)
keep_ids = {}
for s in list(sld_lst):
    f = os.path.basename(rid_target[s.get(f'{{{NS["r"]}}}id')])
    keep_ids[f] = s
    sld_lst.remove(s)
next_sld_id = max(int(s.get('id')) for s in keep_ids.values()) + 1

# delete every template slide except the three edited in place, with its notes and comments
removed = []
for f in [f for f in os.listdir(P('ppt/slides')) if f.endswith('.xml')]:
    if f in FIXED:
        continue
    rels_path = P('ppt/slides/_rels', f + '.rels')
    if os.path.exists(rels_path):
        for r in parse(rels_path).getroot():
            if r.get('Type').endswith('/notesSlide'):
                nf = os.path.normpath(os.path.join(P('ppt/slides'), r.get('Target')))
                removed.append('/ppt/notesSlides/' + os.path.basename(nf))
                for path in (nf, os.path.join(os.path.dirname(nf), '_rels', os.path.basename(nf) + '.rels')):
                    if os.path.exists(path):
                        os.remove(path)
        os.remove(rels_path)
    os.remove(P('ppt/slides', f))
    removed.append('/ppt/slides/' + f)
for r in list(prels.getroot()):
    if r.get('Type') == R_SLIDE and os.path.basename(r.get('Target')) not in FIXED:
        prels.getroot().remove(r)
if os.path.isdir(P('ppt/comments')):
    shutil.rmtree(P('ppt/comments'))
for o in list(ct.getroot()):
    pn = o.get('PartName') or ''
    if pn in removed or pn.startswith('/ppt/comments/'):
        ct.getroot().remove(o)

# register the new screenshot slides as copies of the base
prel_ids = {r.get('Id') for r in prels.getroot()}
def new_prel_id():
    n = 1
    while f'rId{n}' in prel_ids:
        n += 1
    prel_ids.add(f'rId{n}')
    return f'rId{n}'

target_rid = {os.path.basename(r.get('Target')): r.get('Id') for r in prels.getroot() if r.get('Type') == R_SLIDE}
for key in ORDER:
    f = FILE[key]
    if f not in FIXED:
        open(P('ppt/slides', f), 'w', encoding='utf-8').write(base_xml)
        open(P('ppt/slides/_rels', f + '.rels'), 'w', encoding='utf-8').write(base_rels)
        rid = new_prel_id()
        el = etree.SubElement(prels.getroot(), f'{{{NS["rel"]}}}Relationship')
        el.set('Id', rid); el.set('Type', R_SLIDE); el.set('Target', 'slides/' + f)
        o = etree.SubElement(ct.getroot(), '{http://schemas.openxmlformats.org/package/2006/content-types}Override')
        o.set('PartName', '/ppt/slides/' + f); o.set('ContentType', CT_SLIDE)
        s = etree.SubElement(sld_lst, f'{{{NS["p"]}}}sldId')
        s.set('id', str(next_sld_id)); next_sld_id += 1
        s.set(f'{{{NS["r"]}}}id', rid)
    else:
        sld_lst.append(keep_ids[f])
write(pres, P('ppt/presentation.xml'))
write(prels, P('ppt/_rels/presentation.xml.rels'))
write(ct, P('[Content_Types].xml'))

# recolour: the template's violet -> the platform's accent, wherever it is written
if ACCENT not in TEMPLATE_VIOLET:
    for d in ('ppt/slides', 'ppt/slideLayouts', 'ppt/slideMasters'):
        for f in os.listdir(P(d)):
            if f.endswith('.xml'):
                t = open(P(d, f), encoding='utf-8').read()
                t2 = t
                for v in TEMPLATE_VIOLET:
                    t2 = t2.replace(v, ACCENT)
                if t2 != t:
                    open(P(d, f), 'w', encoding='utf-8').write(t2)


# --------------------------------------------------------------------------- slide editing helpers
def strip_comment_refs(x):
    for ext in list(x.iter(f'{{{NS["p"]}}}ext')):
        if any(etree.QName(c).localname == 'commentRel' for c in ext):
            ext.getparent().remove(ext)


def shape_named(x, name):
    for sp in x.iter(f'{{{NS["p"]}}}sp'):
        c = sp.find('.//p:cNvPr', NS)
        if c is not None and c.get('name') == name:
            return sp
    raise KeyError(name)


def set_title(x, text):
    for sp in x.iter(f'{{{NS["p"]}}}sp'):
        if sp.find('.//p:ph[@type="title"]', NS) is not None:
            para = sp.find('.//a:p', NS)
            rs = para.findall('a:r', NS)
            for r in rs[1:]:
                para.remove(r)
            rs[0].find('a:t', NS).text = text
            return
    raise KeyError('title')


def para_with(template_p, runs_xml):
    para = copy.deepcopy(template_p)
    for child in list(para):
        if child.tag != f'{{{NS["a"]}}}pPr':
            para.remove(child)
    for r in frag(f'<x>{runs_xml}</x>'):
        para.append(r)
    return para


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(f'{{{NS["a"]}}}t'))


LINKS = {k: FILE[k] for k in FILE}

# --------------------------------------------------------------------------- cover
x = parse(P('ppt/slides', COVER)); strip_comment_refs(x)
set_title(x, content.META['title'])
ver = shape_named(x, 'Google Shape;167;p1').find('.//a:p', NS)
for t, v in zip([r.find('a:t', NS) for r in ver.findall('a:r', NS)], content.META['version']):
    t.text = v
write(x, P('ppt/slides', COVER))
rels = Rels(P('ppt/slides/_rels', COVER + '.rels')); rels.keep_only(('/slideLayout', '/notesSlide', '/image')); rels.save()

# --------------------------------------------------------------------------- table of contents
def toc_runs(rpr):
    def run(text, bold):
        rp = re.sub(r'\sb="[01]"', '', rpr).replace('<a:rPr ', f'<a:rPr b="{1 if bold else 0}" ', 1)
        return f'<a:r>{rp}<a:t xml:space="preserve">{esc(text)}</a:t></a:r>'
    lead, rest = getattr(content, 'TOC_INTRO', (content.META['title'],
                         ' is designed to be used as a step-by-step guide in building your own test. Check out the '))
    return (run(lead, True) + run(rest, False)
            + run('Learn more', True) + run(' text guide on each page for more information. Contents of this guide are listed below:', False))


for si, toc_file in enumerate(TOC_USED):
    x = parse(P('ppt/slides', toc_file)); strip_comment_refs(x)
    rels = Rels(P('ppt/slides/_rels', toc_file + '.rels')); rels.keep_only(('/slideLayout', '/notesSlide'))
    intro_shape = shape_named(x, 'Google Shape;192;p2')
    ip = intro_shape.findall('.//a:p', NS)[0]
    rpr = re.sub(r'\sxmlns:\w+="[^"]*"', '', etree.tostring(ip.find('.//a:rPr', NS)).decode())
    ip.getparent().replace(ip, para_with(ip, toc_runs(rpr)))
    columns = [shape_named(x, 'Google Shape;193;p2'), shape_named(x, 'Google Shape;194;p2')]
    proto = columns[0].find('.//p:txBody/a:p', NS)
    # every contents slide holds 2 x PER_COLUMN entries; the last one splits what is left evenly
    start = si * 2 * PER_COLUMN
    left = len(content.TOC) - start
    per = PER_COLUMN if left >= 2 * PER_COLUMN else -(-left // 2)
    for ci, col in enumerate(columns):
        first = start + ci * per
        entries = content.TOC[first:min(first + per, start + 2 * PER_COLUMN)]
        if not entries:
            col.getparent().remove(col)
            continue
        tb = col.find('.//p:txBody', NS)
        for para in tb.findall('a:p', NS):
            tb.remove(para)
        for label, key in entries:
            para = copy.deepcopy(proto)
            para.find('a:pPr/a:buAutoNum', NS).set('startAt', str(first + 1))   # numbering runs on across columns and slides
            ppr = para.find('a:pPr', NS); ppr.set('marL', '310896'); ppr.set('indent', '-310896')   # room for '28.'
            r = para.find('a:r', NS)
            r.find('a:t', NS).text = label
            link = r.find('.//a:hlinkClick', NS)
            if key is None:          # a planned section with no slides yet: grey, not linked
                rpr = link.getparent(); rpr.remove(link)
                for f in rpr.findall('a:solidFill', NS):
                    rpr.remove(f)
                rpr.set('u', 'none')
                rpr.insert(0, frag('<a:solidFill><a:srgbClr val="A6A6A6"/></a:solidFill>'))
            else:
                link.set(f'{{{NS["r"]}}}id', rels.add(R_SLIDE, LINKS[key]))
            tb.append(para)
    write(x, P('ppt/slides', toc_file)); rels.save()

# --------------------------------------------------------------------------- introduction
x = parse(P('ppt/slides', INTRO_SLIDE)); strip_comment_refs(x)
rels = Rels(P('ppt/slides/_rels', INTRO_SLIDE + '.rels')); rels.keep_only(('/slideLayout', '/notesSlide')); rels.save()
tb = shape_named(x, 'TextBox 4').find('.//p:txBody', NS)
ps = tb.findall('a:p', NS)
texts = [text_of(p) for p in ps]
pick = lambda pred: ps[next(i for i, t in enumerate(texts) if pred(t))]
p_blank, p_lead = ps[0], pick(lambda t: t.startswith('IMPRINT is'))
p_body, p_head = pick(lambda t: t.startswith('In a world')), pick(lambda t: 'typically consists' in t)
p_bullet = pick(lambda t: t.startswith('Products'))
r11 = lambda md: runs(md, sz=1100, color='<a:srgbClr val="000000"/>')
I = content.INTRO
new = [copy.deepcopy(p_blank), para_with(p_lead, r11('**' + I['lead'] + '**')), copy.deepcopy(p_blank),
       para_with(p_body, r11(I['body'])), copy.deepcopy(p_blank), para_with(p_head, r11(I['list_head']))]
new += [para_with(p_bullet, r11(f'**{label}** – {desc}')) for label, desc in I['list']]
for para in ps:
    tb.remove(para)
for para in new:
    tb.append(para)
write(x, P('ppt/slides', INTRO_SLIDE))


# --------------------------------------------------------------------------- screenshot slides
def prepare_image(spec, out_name):
    im = Image.open(os.path.join(SHOTS, spec['shot'])).convert('RGB')
    sc = im.width / VIEW_W
    if spec.get('spotlight'):
        boxes = spec['spotlight'] if isinstance(spec['spotlight'][0], (list, tuple)) else [spec['spotlight']]
        p = 4
        veil = Image.blend(im, Image.new('RGB', im.size, (30, 30, 30)), 0.42)
        for x0, y0, w, h in boxes:         # one or more lit areas
            crop = tuple(int(v * sc) for v in (x0 - p, y0 - p, x0 + w + p, y0 + h + p))
            veil.paste(im.crop(crop), crop[:2])
        im = veil
    cx, cy, cw, ch = spec.get('crop') or [0, 0, VIEW_W, VIEW_H]
    im = im.crop(tuple(int(v * sc) for v in (cx, cy, cx + cw, cy + ch)))
    if im.width > MAX_IMAGE_W:   # ~300 dpi at the 8" a full screenshot is shown at
        im = im.resize((MAX_IMAGE_W, round(im.height * MAX_IMAGE_W / im.width)), Image.LANCZOS)
    # JPEG at 4:4:4 keeps UI text crisp at a fraction of the PNG's size
    im.save(P('ppt/media', out_name), 'JPEG', quality=85, subsampling=0, optimize=True)


warnings = []
for spec in SLIDES:
    f, key = FILE[spec['key']], spec['key']
    if spec.get('template'):                 # a reused template slide: only its title changes
        x = parse(P('ppt/slides', f)); strip_comment_refs(x)
        set_title(x, spec['title'])
        write(x, P('ppt/slides', f))
        rels = Rels(P('ppt/slides/_rels', f + '.rels'))
        rels.keep_only(('/slideLayout', '/notesSlide', '/image'), targets=(TOC_SLIDE,))
        rels.save()
        continue
    cx, cy, cw, ch = spec.get('crop') or [0, 0, VIEW_W, VIEW_H]
    pl = dict(FULL_PLACE, **(spec.get('place') or {}))
    if 'h' in (spec.get('place') or {}) and 'w' not in (spec.get('place') or {}):
        k = pl['h'] / ch
        pl['w'] = cw * k
    else:
        k = pl['w'] / cw
    img_w, img_h = cw * k, ch * k
    to_in = lambda px, py: (pl['x'] + (px - cx) * k, pl['y'] + (py - cy) * k)

    media = f'guide_{key}.jpeg'
    prepare_image(spec, media)
    x = parse(P('ppt/slides', f)); strip_comment_refs(x)
    rels = Rels(P('ppt/slides/_rels', f + '.rels'))
    rels.keep_only(('/slideLayout',), targets=(TOC_SLIDE,))
    rid = rels.add(R_IMAGE, '../media/' + media)
    set_title(x, spec['title'])
    tree = x.find('.//p:spTree', NS)
    for el in list(tree):
        if etree.QName(el).localname in ('nvGrpSpPr', 'grpSpPr'):
            continue
        if el.find('.//p:ph[@type="title"]', NS) is not None or text_of(el).strip() == 'Table of Contents':
            continue
        tree.remove(el)

    sh = Shapes()
    xml = [sh.pic(rid, pl['x'], pl['y'], img_w, img_h)]
    for n, box, badge, to in spec['callouts']:
        for b in ((box if isinstance(box[0], (list, tuple)) else [box]) if box else []):
            bx, by = to_in(b[0], b[1])
            xml.append(sh.box(bx, by, b[2] * k, b[3] * k, n))
        bx, by = to_in(*badge)
        tx, ty = to_in(*to)
        dx, dy = tx - bx, ty - by
        if abs(dx) >= abs(dy):
            sx, sy = bx + (BADGE_W / 2 if dx > 0 else -BADGE_W / 2), by
        else:
            sx, sy = bx, by + (BADGE_H / 2 if dy > 0 else -BADGE_H / 2)
        xml.append(sh.arrow(sx, sy, tx, ty, n))
        xml.append(sh.badge(n, bx, by))

    y = DESC_Y
    tw = DESC_W - TEXT_DX
    for n, md in spec['descs']:
        name = f'Desc {n}'
        h = HEIGHTS.get(key, {}).get(name)
        h = h / 72 if h else estimate_h(md, tw)
        xml.append(sh.badge(n, DESC_X + BADGE_W / 2, y + BADGE_H / 2))
        xml.append(sh.text(DESC_X + TEXT_DX, y + 0.025, tw, h, runs(md, rels, LINKS), name))
        y += max(h, BADGE_H) + DESC_GAP
    if y - DESC_GAP > SLIDE_BOTTOM_LIMIT:
        warnings.append(f'{key}: descriptions run to {y - DESC_GAP:.2f}" (limit {SLIDE_BOTTOM_LIMIT}") - split the slide')

    for el in frag(f'<x>{"".join(xml)}</x>'):
        tree.append(el)
    write(x, P('ppt/slides', f))
    rels.save()

# --------------------------------------------------------------------------- tidy and pack
used = set()
for root, _, files in os.walk(P('ppt')):
    for fn in files:
        if fn.endswith('.rels'):
            for r in parse(os.path.join(root, fn)).getroot():
                if r.get('TargetMode') != 'External':
                    used.add(os.path.basename(r.get('Target')))
for fn in os.listdir(P('ppt/media')):
    if fn not in used:
        os.remove(P('ppt/media', fn))

app = P('docProps/app.xml')
if os.path.exists(app):
    s = open(app, encoding='utf-8').read()
    s = re.sub(r'<Slides>\d+</Slides>', f'<Slides>{len(ORDER)}</Slides>', s)
    s = re.sub(r'<Notes>\d+</Notes>', '<Notes>3</Notes>', s)
    open(app, 'w', encoding='utf-8').write(s)

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(P('[Content_Types].xml'), '[Content_Types].xml')
    for root, _, files in os.walk(BUILD):
        for fn in files:
            full = os.path.join(root, fn)
            arc = os.path.relpath(full, BUILD).replace(os.sep, '/')
            if arc != '[Content_Types].xml':
                z.write(full, arc)
shutil.rmtree(BUILD)
json.dump(ORDER, open(os.path.join(CONTENT_DIR, 'manifest.json'), 'w'), indent=1)
print(f'wrote {OUT} ({len(ORDER)} slides, {os.path.getsize(OUT) // 1024} KB)')
for w in warnings:
    print('WARNING', w)
