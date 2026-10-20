"""Everything the IMPRINT User Guide SAYS, and where each callout points.

The guide walks through building the Test to populate FROM SCRATCH, following the Test to
clone: plan.json (written by plan.js, beside this file) holds the reference's own names and
values, so the examples quote them ("e.g. Beers", "e.g. Hobgoblin 500ml"). Test creation comes
first; the extra functions (Advanced, Restore a Previous Version, the assistant) come last.

build.py owns the mechanics; this file owns the words and the geometry. Coordinates are CSS px
of the 1600x900 capture viewport; boxes come from the control dumps by on-screen label.

Robust by design: a section whose screenshots or controls are missing is skipped with a
warning (and build.py drops its contents entry), and inside an overview a callout whose
control is not found is left out and the rest renumbered.

Callout = (number, highlight box(es) or None, badge centre, arrow end).
Description markup: **bold**, and [[Learn more|slide-key]] for a link.
"""
import datetime, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = json.load(open(os.path.join(HERE, 'plan.json'))) if os.path.exists(os.path.join(HERE, 'plan.json')) else {}
X = PLAN.get('examples', {})

ACCENT = '901A8A'                                         # IMPRINT violet, the template's own

def _date():
    d = datetime.date.today()
    suffix = 'th' if 11 <= d.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d.day % 10, 'th')
    return d, suffix

_d, _sfx = _date()
META = {
    'title': os.environ.get('GUIDE_TITLE', 'IMPRINT User Guide'),
    'version': (f"Version No. {os.environ.get('GUIDE_VERSION', '1')} ", f'– {_d.day}', _sfx, f" of {_d.strftime('%B %Y')}"),
}
TOC_INTRO = (META['title'], ' is designed to be used as a step-by-step guide in building your own shelf test, '
             'from adding the first product to sharing it with respondents. Check out the ')

INTRO = {
    'lead': ('IMPRINT is a powerful market research tool that helps brands make sure their products and brand assets '
             'are easy to find in today’s crowded and competitive market.'),
    'body': ('Respondents are shown a virtual shelf and asked to find a product as quickly as they can. How fast and how '
             'accurately they find it measures the “push” type of attention a pack receives – how well it '
             'stands out when shoppers have only seconds to choose, in a physical store or online. An optional '
             'questionnaire afterwards records what respondents think of the products. This guide builds a complete '
             'shelf test from scratch, step by step, and then covers the editor’s additional functions.'),
    'list_head': 'The IMPRINT editor typically consists of the following components:',
    'list': [
        ('Products', 'Used to add the product images for the Main and Practice rounds and set each product’s name, price, category, variant, layers and role (target or filler).'),
        ('Instructions', 'Used to write every message respondents read, including the welcome, round instructions, warnings and the screenout and complete messages.'),
        ('Questionnaire', 'Used to add explicit questions that respondents answer after the main round.'),
        ('Themes', 'Used to apply or save the look of a shelf – its backdrop, frame, posts and price-tag colours.'),
        ('Settings', 'Used to set the shelves, the products on each shelf, the search task, warnings, exclusion and timing.'),
        ('Test Flow', 'Shows the respondent’s path through the test and switches each step on or off.'),
        ('Style Panel', 'Used to style the shelf scene and the pop-up windows, for each device.'),
        ('Simulate and Preview', 'Used to try the test as a respondent would before and after publishing it.'),
        ('Advanced', 'Used to add custom CSS and JavaScript for extended design and functional customisation.'),
    ],
}

# Table of contents: (label, first slide key). Entries whose slides are missing are dropped by build.py.
TOC = [
    ('Cover page', 'cover'), ('Table of Contents', 'toc'), ('Introduction', 'intro'),
    ('How do I Add an IMPRINT Component to a Survey?', 'component-1'),
    ('Understanding the IMPRINT Editor', 'ide-1'),
    ('How do I Take the Quick Tour?', 'tour-1'),
    ('Understanding the Products Side Panel', 'products'),
    ('Understanding the Gallery Pop-up Modal', 'gallery'),
    ('How do I Add Products?', 'add-1'),
    ('Understanding the New Products Pop-up Modal', 'newprod-1'),
    ('How do I Add a Category?', 'cat-1'),
    ('How do I Set Each Product’s Details?', 'set-1'),
    ('Understanding the Product Card', 'card'),
    ('How do I Add a Variant?', 'var-1'),
    ('How do I Resize a Product on the Shelf?', 'resize-1'),
    ('Understanding the Image Editor', 'imged-1'),
    ('How do I Edit a Product Image?', 'img-1'),
    ('How do I Delete Products?', 'del-1'),
    ('How do I Copy Products to the Practice Round?', 'copy-1'),
    ('Understanding the Settings Side Panel', 'settings-1'),
    ('How do I Set the Shelves for Each Device?', 'shelves-1'),
    ('How do I Set the Search Task?', 'search-1'),
    ('How do I Set Exclusion and Warnings?', 'errors-1'),
    ('Understanding the Quick Access Toolbar', 'quick'),
    ('Understanding the Test Flow Side Panel', 'flow-1'),
    ('How do I Switch a Step On or Off?', 'step-1'),
    ('Understanding the Instructions Side Panel', 'ins-1'),
    ('Understanding the Instruction Editor', 'ined-1'),
    ('How do I Edit an Instruction Screen?', 'inedit-1'),
    ('Understanding the Questionnaire Side Panel', 'qpanel'),
    ('Understanding the Question Editor', 'qed'),
    ('How do I Add a Question?', 'q-1'),
    ('Understanding the Style Panel', 'style'),
    ('How do I Change the Shelf Background?', 'bg-1'),
    ('How do I Style the Shelf Frame and Posts?', 'frame-1'),
    ('Understanding the Modal Layout', 'modal'),
    ('Understanding the Theme Palette', 'palette'),
    ('Understanding Radius & Border', 'radius'),
    ('Understanding Typography', 'typo'),
    ('Understanding the Themes Side Panel', 'themes'),
    ('How do I Apply a Theme?', 'apply-1'),
    ('How do I Save a Shelf as a Theme?', 'stheme-1'),
    ('How do I Preview on Another Device?', 'device-1'),
    ('How do I Simulate the Test?', 'sim-1'),
    ('How do I Save the Test?', 'save-1'),
    ('How do I Open the Live or Draft Test?', 'open-1'),
    ('Understanding the Advanced Side Panel', 'advanced'),
    ('How do I Restore a Previous Version?', 'restore-1'),
    ('Understanding the AI Assistant', 'assistant'),
    ('How do I See What’s New?', 'news-1'),
]


# --------------------------------------------------------------------------- geometry helpers
class Controls:
    """Every *controls.json dump in the screenshots folder, looked up by state + label."""

    def __init__(self, shots):
        self.c, self.extra = {}, {}
        for f in sorted(glob.glob(os.path.join(shots, '*controls.json'))):
            if os.path.basename(f).startswith('read-'):
                continue
            data = json.load(open(f))
            self.c.update(data.get('controls', {}))
            self.extra.update(data.get('extra', {}))

    def all(self, state, s=None, prefix=None, t=None, tour=None, row=None, ph=None, id=None, within=None, role=None, cls=None):
        def inside(b):
            return within is None or (b[0] >= within[0] - 1 and b[1] >= within[1] - 1
                                      and b[0] + b[2] <= within[0] + within[2] + 1 and b[1] + b[3] <= within[1] + within[3] + 1)
        return [e for e in self.c.get(state, [])
                if (s is None or e['s'] == s) and (prefix is None or e['s'].startswith(prefix))
                and (t is None or e['t'] == t) and (tour is None or e.get('tour') == tour) and (row is None or e.get('row') == row)
                and (ph is None or e.get('ph') == ph) and (id is None or e.get('id') == id) and inside(e['b'])
                and (role is None or e.get('role') == role) and (cls is None or cls in e.get('cls', '').split())]

    def __call__(self, state, nth=0, **kw):
        hits = self.all(state, **kw)
        if len(hits) <= nth:
            raise KeyError(f'no control in {state!r} matching {kw}')
        return hits[nth]['b']


def union(*boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


def pad(b, p=3):
    return [b[0] - p, b[1] - p, b[2] + 2 * p, b[3] + 2 * p]


def co(n, box, side, at, t=0.5, hl=True, along=None):
    """Callout from a badge on `side` of `box` (one box or a list; the arrow lands on the first),
    the badge at coordinate `at` on the other axis. `along` fixes where on the edge it lands."""
    first = box[0] if isinstance(box[0], (list, tuple)) else box
    x, y, w, h = first
    if side == 'left':
        ty = along if along is not None else y + t * h
        to, badge = (x, ty), (at, ty)
    elif side == 'right':
        ty = along if along is not None else y + t * h
        to, badge = (x + w, ty), (at, ty)
    elif side == 'top':
        tx = along if along is not None else x + t * w
        to, badge = (tx, y), (tx, at)
    else:
        tx = along if along is not None else x + t * w
        to, badge = (tx, y + h), (tx, at)
    return (n, box if hl else None, badge, to)


def ov(key, title, shot, rows, split=(), **kw):
    """An "Understanding the ..." section. rows = [(box or callable, side, at, label, text, opts)];
    a row whose box cannot be found is left out and the rest renumbered. `split` divides the
    descriptions over several slides (indexes into the rows that survive)."""
    items = []
    for r in rows:
        boxf, side, at, label, text = r[:5]
        opts = r[5] if len(r) > 5 else {}
        try:
            box = boxf() if callable(boxf) else boxf
        except (KeyError, StopIteration, IndexError, TypeError) as e:
            print(f'note: {key}: callout "{label}" left out ({e})')
            continue
        items.append((box, side, at, label, text, opts))
    calls = [co(i + 1, b, side, at, **o) for i, (b, side, at, _, _, o) in enumerate(items)]
    descs = [(i + 1, f'**{label}** – {text}') for i, (_, _, _, label, text, _) in enumerate(items)]
    bounds = [0] + [s for s in split if 0 < s < len(items)] + [len(items)]
    out = []
    for i in range(len(bounds) - 1):
        k = key if len(bounds) == 2 else f'{key}-{i + 1}'
        out.append(dict(key=k, title=title, shot=shot, callouts=calls, descs=descs[bounds[i]:bounds[i + 1]], **kw))
    return out


def steps(key, title, rows):
    """A "How do I ...?" section: one step per slide, the list growing; the step's box (or boxes)
    is spotlit and outlined. rows = [(text, shot, box or callable, side, at)]; a step whose box
    cannot be found is left out."""
    ok = []
    for text, shot, boxf, side, at in rows:
        try:
            box = boxf() if callable(boxf) else boxf
        except (KeyError, StopIteration, IndexError, TypeError) as e:
            print(f'note: {key}: step "{text[:40]}…" left out ({e})')
            continue
        ok.append((text, shot, box, side, at))
    out = []
    for i, (text, shot, box, side, at) in enumerate(ok, 1):
        out.append(dict(key=f'{key}-{i}', title=title, shot=shot, spotlight=box, callouts=[co(i, box, side, at)],
                        descs=[(n, ok[n - 1][0]) for n in range(1, i + 1)]))
    return out


def eg(*names):
    """' e.g. **a**, **b** and **c**' or ''."""
    names = [n for n in names if n]
    if not names:
        return ''
    if len(names) == 1:
        return f'e.g. **{names[0]}**'
    return 'e.g. ' + ', '.join(f'**{n}**' for n in names[:-1]) + f' and **{names[-1]}**'


# --------------------------------------------------------------------------- slides
def slides(shots):
    C = Controls(shots)
    XT = C.extra
    out = []
    section = lambda name, fn: _section(out, name, fn)

    MODAL_CROP, MODAL_PLACE = [342, 58, 916, 784], dict(x=1.75, y=1.85, h=4.85)
    ML, MR = 290, 1300
    PANEL = [116, 55, 380, 810]
    PP = dict(x=3.25, y=1.80, h=5.0)
    L, R = 70, 545
    RAIL = lambda i: [0, round(55 + i * 100.6), 120, 100]         # 0 Products … 7 Preview
    F_ = 'ide-final' if 'ide-final' in C.c else 'ide'
    batch, cat = X.get('batch') or [], X.get('category')
    n_batch = len(batch)
    first_item = (X.get('item') or {}).get('name') or (batch[0] if batch else None)

    # ---- How do I Add an IMPRINT Component to a Survey?  (the template's own Fluent slides)
    section('component', lambda: [dict(key=f'component-{i}', template=f'slide{7 + i}.xml',
                                       title='How do I Add an IMPRINT Component to a Survey?') for i in range(1, 7)])

    # ---- Understanding the IMPRINT Editor
    def ide():
        I = 'ide'
        TOP, BOT = -84, 984
        return ov('ide', 'Understanding the IMPRINT Editor', 'ide.png', [
            (lambda: pad(C(I, tour='sidebar-core-rail'), -2), 'left', -80, 'Side Menu',
             'Opens the Products, Instructions, Questionnaire, Themes, Settings, Test Flow, Advanced and Preview panels used to build the test. [[Learn more|products]]'),
            (lambda: C(I, s='How it works', t='button'), 'top', TOP, 'How it works', 'Starts the Quick Tour, a short guided walk through the editor.', dict(along=180)),
            (lambda: C(I, t='label', within=[150, 6, 420, 44]), 'top', TOP, 'Test name', 'The test you are editing. Click it to switch to another test in the same project.', dict(along=262)),
            (lambda: C(I, tour='simulate'), 'top', TOP, 'Simulate', 'Plays the test as a respondent would meet it, unsaved changes included. Nothing is recorded.', dict(along=345)),
            (lambda: C(I, tour='flow-navigation'), 'top', TOP, 'Go to / Previous / Next', 'Jumps to any screen of the test, or steps through the screens in order, to see it in the preview.'),
            (lambda: C(I, s='Edit history'), 'top', TOP, 'Undo / Redo', 'Undoes or redoes your recent edits.', dict(along=1070)),
            (lambda: C(I, s='Save', t='button'), 'top', TOP, 'Save', 'Saves the test and makes it live for respondents. The red dot beside it means there are unsaved changes.'),
            (lambda: C(I, s='More save options'), 'top', -40, 'More save options', 'Opens Live and Draft preview, Save as draft, Save as theme and Recent changes.'),
            (lambda: C(I, tour='header-whats-new'), 'top', TOP, 'What’s New', 'Lists what was added, changed and fixed in each release. A red dot means there is something you have not read.', dict(along=1295)),
            (lambda: C(I, tour='ai-assistant-trigger'), 'top', TOP, 'AI Assistant', 'Opens or closes the AI Assistant chat box.', dict(along=1420)),
            (lambda: C(I, tour='device-view-card'), 'right', 1680, 'Device View', 'Previews the test on a desktop, tablet or mobile screen at a chosen resolution.'),
            (lambda: C(I, tour='style-sections'), 'right', 1680, 'Style Panel', 'Styles the shelf scene – backdrop, frame, posts and price tags – and the pop-up windows. The edge arrow hides or shows it.'),
            (lambda: C(I, tour='preview-frame'), 'left', -80, 'Preview', 'A live preview of the screen respondents will see. It updates as you change products, settings and styles.', dict(along=560)),
            (lambda: C(I, tour='ai-assistant'), 'bottom', BOT, 'AI Assistant chat box', 'Ask about your test or describe a change; every change is shown for you to approve before it is applied.'),
            (lambda: C(I, s='Open quick access'), 'bottom', BOT, 'Quick Access', 'Opens a strip of the most used settings: shelves, products per shelf and the search task.'),
            (lambda: C(I, s='Shuffle Products'), 'bottom', BOT + 44, 'Shuffle', 'Shuffles the products on the shelf, to check how the layout varies from one respondent to the next.'),
            (lambda: C(I, s='Screenshot'), 'bottom', BOT, 'Screenshot', 'Downloads a picture of the shelf as it is shown in the preview.'),
        ], split=[6, 12])
    section('ide', ide)

    # ---- How do I Take the Quick Tour?
    section('tour', lambda: steps('tour', 'How do I Take the Quick Tour?', [
        ('Click **How it works** at the top left of the editor. The tour also opens by itself the first time you edit a test.',
         F_ + '.png', lambda: pad(C(F_, s='How it works', t='button'), 3), 'bottom', 170),
        ('The **Quick tour** opens. The numbered dots show its steps; the first explains what the tour covers.',
         'tour-1.png', lambda: C('tour-1', role='dialog'), 'right', 1100),
        ('Each step outlines the part of the editor it explains, e.g. the side menu. Click **Next** or **Back** to move between steps.',
         'tour-2.png', lambda: C('tour-2', role='dialog'), 'right', 650),
        ('**Download Full Guide** opens this guide. Click **Skip tour**, or the **X**, to close the tour at any time.',
         'tour-3.png', lambda: C('tour-3', role='dialog'), 'left', 1080),
    ]))

    # ---- Understanding the Products Side Panel
    def products():
        P = 'products-full'
        clip = lambda b, y1: [b[0], b[1], b[2], min(b[3], y1 - b[1])]
        return ov('products', 'Understanding the Products Side Panel', P + '.png', [
            (lambda: C(P, s='Close Products panel'), 'right', R, 'Close (X) icon', 'Closes the Products side panel.'),
            (lambda: union(C(P, s='Main Round', t='button', within=PANEL), C(P, s='Practice Round', t='button', within=PANEL)), 'right', R,
             'Main Round / Practice Round', 'Switches between the products of the Main Round and the Practice Round.'),
            (lambda: C(P, s='New product'), 'left', L, 'New Product', 'Opens the Gallery to add products to the round. [[Learn more|add-1]]'),
            (lambda: clip(C(P, prefix='Edit Price Tag', t='div'), 806), 'right', R, 'Product card', 'One card per product, with its image, name, price, category, variant, layers and role. [[Learn more|card]]'),
            (lambda: C(P, id='SidebarFooter'), 'left', L, 'Products / Targets / Fillers', 'How many products the round has, and how many are targets or fillers. Click one to show only those products.'),
            (lambda: C(P, s='', t='button', within=[460, 400, 40, 120]), 'right', R, 'Chevron icon', 'Expands or collapses the Products side panel.'),
        ], crop=PANEL, place=PP)
    section('products', products)

    # ---- Understanding the Gallery Pop-up Modal
    TAB_TIP = {'This survey': 'Only this study can use it', 'Project-wide': 'Every survey in this project', 'Public': 'Any team on the platform'}
    tile = lambda st: next(e['b'] for e in C.c[st] if e['t'] == 'button' and 150 <= e['b'][2] <= 175 and 140 <= e['b'][3] <= 170)

    def gallery():
        G = 'add-project'
        return ov('gallery', 'Understanding the Gallery Pop-up Modal', G + '.png', [
            (lambda: C(G, s=TAB_TIP['This survey']), 'top', 20, 'This survey', 'Images only this test can use.'),
            (lambda: C(G, s=TAB_TIP['Project-wide']), 'top', 20, 'Project-wide', 'Images shared by every survey in the project.'),
            (lambda: C(G, s=TAB_TIP['Public']), 'top', 20, 'Public', 'The image library shared with every team on the platform.'),
            (lambda: C(G, ph='Search by name'), 'left', ML, 'Search by name', 'Finds an image by its name in the open tab.'),
            (lambda: C(G, s='Add from this computer', t='button'), 'right', MR, 'Add from this computer', 'Uploads new images from your computer into the gallery.'),
            (lambda: tile(G), 'left', ML, 'Image', 'Click an image to pick it; the number on it is the order the products will be added in. Click it again to remove it.'),
            (lambda: C(G, s='Cancel', t='button'), 'left', ML, 'Cancel', 'Closes the Gallery without adding anything.'),
            (lambda: C(G, prefix='Add ', t='button', within=[600, 740, 700, 90]), 'right', MR, 'Add images', 'Adds the picked images as new products. The number counts the images picked.'),
            (lambda: C(G, s='Close', t='button'), 'right', MR, 'Close (X) icon', 'Closes the Gallery.'),
        ], crop=MODAL_CROP, place=MODAL_PLACE)
    section('gallery', gallery)

    # ---- How do I Add Products?
    tab = X.get('tab', 'Project-wide')

    def add():
        picks = [b for b in (C.all('add-selected', s=g, t='button') for g in X.get('batchGallery', [])) for b in b[:1]]
        picks = [p['b'] for p in picks if p['b'][1] > 40 and p['b'][1] + p['b'][3] < 760]
        return steps('add', 'How do I Add Products?', [
            ('Click **Products** in the side menu.', 'new-test.png', lambda: C('new-test', s='Products', t='div'), 'right', 260),
            ('Make sure **Main Round** is selected, then click **New Product**.', 'products-empty.png', lambda: C('products-empty', s='New product'), 'right', 640),
            (f'The **Gallery** opens. Click **{tab}** to see the images there. [[Learn more|gallery]]',
             'add-gallery.png', lambda: pad(C('add-gallery', s=TAB_TIP[tab]), 2), 'top', 150),
            (f'Click each image you want to add{", " + eg("every product in " + cat) if cat else ""}. The numbers show the order they will be added in.'.replace('e.g. **every product in ', 'e.g. every product in **'),
             'add-selected.png', lambda: [pad(b, 2) for b in picks] if picks else None, 'left', 300),
            (f'Click **Add {n_batch} image{"s" if n_batch != 1 else ""}**.', 'add-selected.png',
             lambda: pad(C('add-selected', prefix=f'Add {n_batch} image', t='button'), 3), 'bottom', 870),
            ('The **New Products** pop-up opens with a row for each image, ready to set up. [[Learn more|newprod-1]]',
             'new-products.png', [352, 68, 896, 764], 'left', 300),
        ])
    section('add', add)

    # ---- Understanding the New Products Pop-up Modal
    def newprod():
        N = 'new-products'
        col = lambda x0, x1: [x0, 340, x1 - x0, 100]
        IN = 600
        return ov('newprod', 'Understanding the New Products Pop-up Modal', N + '.png', [
            (lambda: C(N, s='N/A', t='button', nth=0), 'left', ML, 'Category', 'Gives every product below the same category, or adds a new one. [[Learn more|cat-1]]'),
            (lambda: C(N, s='N/A', t='button', nth=1), 'right', MR, 'Variant', 'Gives every product below the same variant, such as a brand or a flavour.'),
            ([372, 266, 422, 38], 'left', ML, 'Price / Set all', 'Type a price and click Set all to give it to every product below.'),
            (lambda: union(C(N, s='All Target', t='button'), C(N, s='All Filler', t='button')), 'right', MR, 'Role on shelf',
             'All Target makes every product one respondents search for; All Filler makes them all display-only.'),
            (col(366, 422), 'bottom', IN, 'Image', 'The product’s image, from the gallery.'),
            (col(424, 764), 'bottom', IN, 'Name', 'The product’s name, taken from the image’s name. Change it here.'),
            (col(768, 860), 'bottom', IN, 'Price', 'The price on the product’s price tag.'),
            (col(864, 972), 'bottom', IN, 'Layers', 'How many layers high the product is stacked on the shelf.'),
            (col(976, 1084), 'bottom', IN, 'Items/layer', 'How many of the product stand side by side in each layer.'),
            (col(1088, 1200), 'bottom', IN, 'Role', 'Target (searched for) or Filler (on display only), for this product alone.'),
            (col(1204, 1234), 'right', MR, 'Remove (×)', 'Takes the product off the list before it is added.', dict(along=405)),
            (lambda: C(N, s='Go back', t='button'), 'left', ML, 'Go back', 'Returns to the Gallery with your picks kept.'),
            (lambda: C(N, prefix='Add ', t='button', within=[600, 740, 700, 90]), 'right', MR, 'Add products', 'Adds the products to the round.'),
            (lambda: C(N, s='Close', t='button'), 'right', MR, 'Close (X) icon', 'Closes the pop-up without adding anything.'),
        ], split=[7], crop=MODAL_CROP, place=MODAL_PLACE)
    section('newprod', newprod)

    # ---- How do I Add a Category?
    if cat:
        section('cat', lambda: steps('cat', 'How do I Add a Category?', [
            ('In the **New Products** pop-up, click the **Category** field.', 'new-products.png',
             lambda: pad(C('new-products', s='N/A', t='button', nth=0), 3), 'left', 300),
            ('Click **+ Add category** at the bottom of the list.', 'cat-open.png', lambda: pad(C('cat-open', s='Add category'), 3), 'left', 300),
            (f'The **Select Category** pop-up opens. Type the name in **New category**, {eg(cat)}.', 'cat-typed.png',
             lambda: pad(C('cat-typed', s=cat, t='input'), 3), 'left', 300),
            ('Click **Add**. The new category appears below **N/A**.', 'cat-typed.png', lambda: pad(C('cat-typed', s='Add', t='button'), 3), 'right', 1300),
            ('Click the new category to choose it for every product in the pop-up.', 'cat-added.png',
             lambda: pad(C('cat-added', s=cat, t='button'), 6), 'left', 300),
            ('The pop-up closes and **Category** shows the new category for all the products below.', 'cat-applied.png',
             lambda: pad(C('cat-applied', s=cat, t='button'), 3), 'left', 300),
        ]))

    # ---- How do I Set Each Product's Details?
    def details():
        F, F2 = 'np-filled', 'np-filled-2'
        LIST_TOP, LIST_BOT = 371, 756
        shown = lambda b: b[1] >= LIST_TOP - 2 and b[1] + b[3] <= LIST_BOT
        rows2 = [e for e in C.c[F2] if e.get('row') and shown(e['b'])]
        renamed = X.get('renamed')
        rn = renamed['name'] if renamed else first_item
        layered = [n for n in X.get('layered', []) if any(e['row'] == n for e in rows2)] or [rows2[-1]['row']]
        item = X.get('item') or {}
        others = X.get('otherCategories') or []
        return steps('set', 'How do I Set Each Product’s Details?', [
            (('Change a product’s **Name** if needed, ' + eg(rn) + '. Each name starts as the image’s name.') if renamed
             else 'Change a product’s **Name** if needed. Each name starts as the image’s name.',
             F + '.png', lambda: pad(C(F, t='input', within=C(F, row=rn)), 3), 'left', 300),
            (f'Type each product’s **Price**{", " + eg(item.get("price")) if item.get("price") else ""}. To give every product the same price, type it in the top **Price** field and click **Set all**.',
             F + '.png', lambda: pad(union(*[e['b'] for e in C.c[F] if e['t'] == 'input' and e.get('ph') == '0.00' and e['b'][0] > 760 and shown(e['b'])]), 3), 'right', 1300),
            (f'Use **+** and **–** under **Layers** to stack a product'
             + (f', e.g. **{X.get("layers")}** for {" and ".join(X["layered"])}.' if X.get('layered') else '.'),
             F2 + '.png', lambda: pad(union(*[[864, C(F2, row=n)[1] + 14, 108, C(F2, row=n)[3] - 28] for n in layered]), 2), 'right', 1300),
            (f'Use **+** and **–** under **Items/layer** to set how many of each product stand side by side, e.g. **{X.get("count", 1)}**. The shelf shows as many as fit.',
             F2 + '.png', lambda: pad(union(*[[976, e['b'][1] + 14, 108, e['b'][3] - 28] for e in rows2]), 2), 'right', 1300),
            ('Leave **Target** on products respondents will search for, or click **Filler** for products that are only on display.',
             F2 + '.png', lambda: pad(union(*[e['b'] for e in C.c[F2] if e['t'] == 'button' and e['s'] in ('Target', 'Filler') and shown(e['b'])]), 3), 'right', 1300),
            (f'Click **Add {n_batch} product{"s" if n_batch != 1 else ""}**.', F2 + '.png',
             lambda: pad(C(F2, prefix='Add ', t='button', within=[600, 740, 700, 90]), 3), 'bottom', 870),
            ('When the products are added, click **Done**. Remember to save your changes.', 'np-progress.png',
             lambda: pad(C('np-progress', s='Done', t='button'), 3), 'right', 1300),
            ((f'Repeat for each category, {eg(*others)}. ' if others else 'Repeat for any other products. ') + 'The counts show every product in the round.',
             'products-full.png', lambda: pad(C('products-full', id='SidebarFooter'), 2), 'top', 700),
        ])
    section('set', details)

    # ---- Understanding the Product Card
    def card():
        V = 'var-card' if 'var-card' in C.c else 'products-full'
        name = XT.get('variantCard')
        crd = C(V, row=name) if name and C.all(V, row=name) else C(V, prefix='Edit Price Tag', t='div')
        line = lambda dy: [150, crd[1] + dy - 5, 296, 32]
        return ov('card', 'Understanding the Product Card', V + '.png', [
            (lambda: C(V, t='input', within=[150, crd[1] + 15, 40, 40]), 'left', L, 'Select', 'Ticks the product, to delete it together with others. [[Learn more|del-1]]'),
            (lambda: C(V, s='Edit', t='button', within=crd), 'right', R, 'Edit', 'Opens the image editor, to crop the image, remove its background or replace it. [[Learn more|imged-1]]'),
            (lambda: C(V, t='input', within=[150, crd[1] + 205, 300, 70]), 'left', L, 'Name', 'The product’s name. Click it to change it.'),
            (line(273), 'right', R, 'Price Tag', 'The price shown on the shelf. Click it to change it.'),
            (line(311), 'left', L, 'Category', 'Click the category to choose another, or to add a new one.'),
            (line(350), 'right', R, 'Variant', 'Click the variant to choose another, or to add a new one. [[Learn more|var-1]]'),
            (line(389), 'left', L, 'Layers', 'How many layers high the product is stacked, for the device you are previewing.'),
            (line(428), 'right', R, 'Items per layer', 'How many of the product stand side by side, for the device you are previewing.'),
            (lambda: C(V, prefix='Target Filler', t='div', within=crd), 'left', L, 'Target / Filler', 'Whether respondents search for the product (Target) or it is only on display (Filler).'),
        ], crop=PANEL, place=PP)
    section('card', card)

    # ---- How do I Add a Variant?
    v = X.get('variant')
    if v and 'var-card' in C.c:
        vname, vprod = v['name'], XT.get('variantCard') or v['products'][0]

        def variant():
            crd = C('var-card', row=vprod)
            vline = [330, crd[1] + 340, 125, 35]
            return steps('var', 'How do I Add a Variant?', [
                (f'In the **Products** panel, find the product, {eg(vprod)}, and click its **Variant** (**N/A**).', 'var-card.png',
                 lambda: pad(C('var-card', s='N/A', t='div', within=vline), 4), 'right', 640),
                (f'The **Select Variant** pop-up opens. Type the name in **New variant**, {eg(vname)}.', 'var-typed.png',
                 lambda: pad(C('var-typed', s=vname, t='input', within=[590, 560, 330, 120]), 3), 'left', 520),
                ('Click **Add**. The new variant appears below **N/A**.', 'var-typed.png', lambda: pad(C('var-typed', s='Add', t='button'), 3), 'right', 1100),
                ('Click the new variant to give it to the product.', 'var-added.png', lambda: pad(C('var-added', s=vname, t='button'), 6), 'left', 520),
                ('The pop-up closes and the card shows the variant.' + (f' Give it to the other products of that variant by choosing it from the list, {eg(*[p for p in v["products"] if p != vprod][:2])}.' if len(v['products']) > 1 else ''),
                 'var-applied.png', lambda: pad(C('var-applied', s=vname, t='div', within=vline), 4), 'right', 640),
            ])
        section('var', variant)

    # ---- How do I Resize a Product on the Shelf?
    rz = XT.get('resize')
    if rz:
        section('resize', lambda: steps('resize', 'How do I Resize a Product on the Shelf?', [
            (f'In the preview, point at the product, {eg(rz["product"])}. A box with a handle at each corner appears around it.',
             'resize-hover.png', pad(rz['box'], 4), 'right', 560),
            ('Drag a top handle down to make the product shorter, or up to make it taller, so packs stand at their real sizes.',
             'resize-hover.png', pad(rz['grip'], 4), 'right', 560),
            ('The product keeps its new height. Each device keeps its own: tablet and mobile follow desktop until you resize them there.',
             'resize-done.png', pad(rz.get('after') or rz['box'], 4), 'right', 560),
        ]))

    # ---- Understanding the Image Editor / How do I Edit a Product Image? / How do I Delete Products?
    ED = 'editor'
    section('imged', lambda: ov('imged', 'Understanding the Image Editor', ED + '.png', [
        ([964, 135, 74, 34], 'top', 80, 'Undo / Redo', 'Undoes or redoes your changes to the image.'),
        (lambda: C(ED, s='Save Image', t='button'), 'top', 80, 'Save Image', 'Saves the edited image. It is saved to the gallery and used for the product.'),
        (lambda: C(ED, s='Close editor'), 'right', 1310, 'Close (X) icon', 'Closes the editor without saving.'),
        ([350, 180, 900, 540], 'left', 290, 'Image', 'The product image being edited.'),
        (lambda: C(ED, s='Replace image'), 'left', 290, 'Replace', 'Swaps the image for another one.'),
        (lambda: C(ED, s='Export image'), 'bottom', 830, 'Export', 'Downloads the image to your computer.'),
        (lambda: C(ED, s='Remove background'), 'bottom', 830, 'Remove BG', 'Removes the image’s background with AI, leaving the pack on its own.'),
        (lambda: C(ED, s='Crop', t='button'), 'bottom', 830, 'Crop', 'Cuts the image down to the part you choose. [[Learn more|img-1]]'),
        ([978, 731, 260, 34], 'right', 1310, 'Size', 'The image’s width and height in pixels, and its file size.'),
    ], split=[5], crop=[340, 110, 920, 680], place=dict(x=1.5, y=1.85, h=4.85)))
    section('img', lambda: steps('img', 'How do I Edit a Product Image?', [
        ('In the **Products** panel, click **Edit** on the product’s image.', 'del-selected.png', lambda: pad(C('del-selected', s='Edit', t='button'), 3), 'right', 640),
        ('The **Image Editor** opens. Click **Crop**.', ED + '.png', lambda: pad(C(ED, s='Crop', t='button'), 3), 'bottom', 860),
        ('Drag the handles to choose the part of the image to keep.', 'editor-crop.png', [600, 200, 400, 480], 'left', 440),
        ('Click **Apply**, or **Cancel** to leave the image as it was.', 'editor-crop.png', lambda: pad(C('editor-crop', s='Apply', t='button'), 3), 'bottom', 860),
        ('Click **Save Image** to keep the change. **Remove BG** and **Size** are used the same way.', ED + '.png', lambda: pad(C(ED, s='Save Image', t='button'), 3), 'bottom', 240),
    ]))
    section('del', lambda: steps('del', 'How do I Delete Products?', [
        ('In the **Products** panel, tick the box on each product to delete. **Select all** ticks every product in the round.', 'del-selected.png',
         lambda: pad(C('del-selected', t='input', within=[150, 370, 40, 40]), 4), 'right', 640),
        ('Click **Delete** in the bar at the foot of the panel.', 'del-selected.png',
         lambda: pad(C('del-selected', s='Delete', t='button', within=[120, 800, 360, 70]), 3), 'top', 740),
        ('Click **Delete** to confirm, or **Cancel** to keep the products. Save the test to keep the change.', 'del-confirm.png',
         lambda: pad(C('del-confirm', s='Delete', t='button', within=[700, 420, 500, 140]), 3), 'right', 1200),
    ]))

    # ---- How do I Copy Products to the Practice Round?
    pr = PLAN.get('practice', {})
    flip = XT.get('copyFlip')
    if pr.get('mode') == 'copy' and 'copy-modal' in C.c:
        def copy():
            rows = [
                ('In the **Products** panel, click **Practice Round**.', 'prac-empty.png', lambda: pad(C('prac-empty', s='Practice Round', t='button', within=PANEL), 3), 'right', 640),
                ('Click **New Product**.', 'prac-empty.png', lambda: C('prac-empty', s='New product'), 'right', 640),
                ('In the **Gallery**, click **Use the Main Round’s products instead**.', 'prac-gallery.png', lambda: C('prac-gallery', prefix='Use the Main Round'), 'left', 290),
                ('A pop-up lists every Main Round product, ready to copy. They replace anything already in the Practice Round.', 'copy-modal.png', [512, 68, 576, 764], 'left', 440),
            ]
            if pr.get('startFiller'):
                rows.append(('Click **All Filler**, so the products are on display only.', 'copy-filler.png', lambda: pad(C('copy-filler', s='All Filler', t='button'), 3), 'right', 1160))
            if flip and flip.get('box'):
                rows.append((f'Click **{flip["role"]}** on the product{" respondents search for in practice" if flip["role"] == "Target" else " that is only on display"}, {eg(flip["name"])}.',
                             'copy-target.png', pad(flip['box'], 4), 'right', 1160))
            rows += [
                ('Click **Replace the Practice Round with these products**.', 'copy-target.png', lambda: pad(C('copy-target', prefix='Replace the Practice Round'), 3), 'bottom', 870),
                ('The Practice Round now holds the products. Save the test to keep it.', 'prac-full.png', lambda: pad(C('prac-full', id='SidebarFooter'), 2), 'top', 740),
            ]
            return steps('copy', 'How do I Copy Products to the Practice Round?', rows)
        section('copy', copy)

    # ---- Understanding the Settings Side Panel
    S0 = 'set-desktop-before'
    sec = lambda name: C(S0, prefix=name, t='button', within=PANEL)
    section('settings', lambda: ov('settings', 'Understanding the Settings Side Panel', S0 + '.png', [
        (lambda: C(S0, s='Close Settings panel'), 'right', R, 'Close (X) icon', 'Closes the Settings side panel.'),
        (lambda: union(C(S0, s='Main Round', t='button', within=PANEL), C(S0, s='Practice Round', t='button', within=PANEL)), 'right', R,
         'Main Round / Practice Round', 'Switches between the settings of the two rounds.'),
        ([150, 236, 298, 80], 'left', L, 'Number of shelves', 'How many shelves the respondent sees, for the device you are previewing. [[Learn more|shelves-1]]'),
        ([150, 332, 298, 80], 'right', R, 'Products per shelf', 'How many products stand on each shelf, for the device you are previewing.'),
        (lambda: union(C(S0, t='button', within=[150, 440, 180, 70]), C(S0, s='+', t='button', within=PANEL)), 'left', L, 'Search type / Search count',
         'Whether respondents search for a product, a category or a variant, and how many times. [[Learn more|search-1]]'),
        (lambda: C(S0, prefix='Mixed categories', t='label'), 'right', R, 'Mixed categories per shelf',
         'On: products flow across shelves, so a shelf can hold more than one category. Off: each shelf holds one.'),
        (lambda: sec('Error handling'), 'left', L, 'Error handling & warnings', 'Exclusion, the error threshold and the idle timeout. [[Learn more|errors-1]]'),
        (lambda: sec('Timing controls'), 'right', R, 'Timing controls', 'The pause between one search and the next.'),
        (lambda: sec('End links'), 'left', L, 'End links', 'Where respondents are sent when they finish or are screened out.'),
    ], split=[5], crop=PANEL, place=PP))

    # ---- How do I Set the Shelves for Each Device?
    m = PLAN.get('settings', {}).get('main', {})
    sp = pad(union([150, 236, 298, 80], [150, 332, 298, 80]), 2)
    dev = lambda st, name: [pad(C(st, s=name, t='button'), 3), sp]
    section('shelves', lambda: steps('shelves', 'How do I Set the Shelves for Each Device?', [
        ('Click **Settings** in the side menu and keep **Main Round** selected.', S0 + '.png', lambda: C(S0, s='Settings', t='div', within=[0, 55, 125, 805]), 'right', 260),
        ('Under **Device View**, click **Desktop**.', S0 + '.png', lambda: pad(C(S0, s='Desktop', t='button'), 3), 'left', 1180),
        (f'Set **Number of shelves** and **Products per shelf** by dragging the slider or typing in the box, e.g. **{m.get("shelves")}** and **{m.get("productsPerShelves")}**.',
         'set-desktop.png', sp, 'right', 640),
        (f'Click **Tablet** and set its shelves, e.g. **{m.get("tabShelves")}** and **{m.get("tabProductsPerShelves")}**.', 'set-tablet.png', lambda: dev('set-tablet', 'Tablet'), 'left', 1180),
        (f'Click **Mobile** and set its shelves, e.g. **{m.get("mobileShelves")}** and **{m.get("mobileProductsPerShelves")}**. Repeat for the **Practice Round**.',
         'set-mobile.png', lambda: dev('set-mobile', 'Mobile'), 'left', 1180),
    ]))

    # ---- How do I Set the Search Task?
    TYPES = ['Product', 'Category', 'Variant']
    mt, pt = TYPES[int(m.get('categorySearch', 0) or 0)], TYPES[int(PLAN.get('settings', {}).get('practice', {}).get('categorySearch', 0) or 0)]
    section('search', lambda: steps('search', 'How do I Set the Search Task?', [
        ('In **Settings**, with **Main Round** selected, open the **Search type** list.', 'search-before.png',
         lambda: pad(C('search-before', t='button', within=[150, 440, 180, 70]), 3), 'right', 640),
        (f'Choose what respondents search for: a **Product**, a **Category** or a **Variant**, {eg(mt)}.', 'search-open.png', lambda: pad(C('search-open', role='listbox'), 3), 'right', 640),
        (f'Use **+** and **–** under **Search count** to set how many times each product is searched for, e.g. **{m.get("productSearch", 1)}**.',
         'search-set.png', pad([333, 462, 110, 40], 3), 'right', 640),
        (f'Click **Practice Round** and set its search the same way, e.g. **{pt}**.', 'search-set.png',
         lambda: pad(C('search-set', s='Practice Round', t='button', within=PANEL), 3), 'right', 640),
    ]))

    # ---- How do I Set Exclusion and Warnings?
    section('errors', lambda: steps('errors', 'How do I Set Exclusion and Warnings?', [
        ('In **Settings**, click **Error handling & warnings** to open it.', 'errors-open.png', lambda: pad(C('errors-open', s='Error handling & warnings', t='button'), 3), 'right', 640),
        ('**Exclusion** screens out respondents who use up their retries. A wrong pick and an idle timeout each cost one.', 'errors-set.png',
         lambda: pad(C('errors-set', prefix='Exclusion Drop', t='label'), 3), 'right', 640),
        (f'Set the **Exclusion threshold**: the retries allowed across the round, e.g. **{m.get("retrialExclusion")}**.', 'errors-set.png', pad([150, 690, 298, 70], 2), 'right', 640),
        ('**Random selection error threshold** is how many wrong products may be clicked on one trial; **Idle timeout**, below it, how long a trial waits.',
         'errors-set.png', pad([150, 812, 298, 52], 2), 'right', 640),
    ]))

    # ---- Understanding the Quick Access Toolbar
    QA = 'quick-access'
    lab = lambda name, w: [*C(QA, prefix=name, t='label')[:2], w, 72]
    section('quick', lambda: ov('quick', 'Understanding the Quick Access Toolbar', QA + '.png', [
        (lambda: lab('Shelves', 140), 'top', 650, 'Shelves', 'How many shelves are shown, for the device you are previewing.'),
        (lambda: lab('Products per Shelf', 163), 'top', 650, 'Products per Shelf', 'How many products stand on each shelf, for the device you are previewing.'),
        (lambda: lab('Search Type', 150), 'top', 650, 'Search Type', 'Whether respondents search for a product, a category or a variant.'),
        (lambda: lab('Search Count', 140), 'top', 650, 'Search Count', 'How many times each product is searched for.'),
        (lambda: lab('Categories per Shelf', 155), 'top', 650, 'Categories per Shelf', 'Mixed together, or one category only on each shelf.'),
        (lambda: C(QA, s='Close quick access'), 'top', 650, 'Close quick access', 'Closes the toolbar. The same button opens it.'),
        (lambda: C(QA, s='Shuffle Products'), 'top', 650, 'Shuffle', 'Shuffles the products on the shelf.'),
        (lambda: C(QA, s='Screenshot'), 'top', 650, 'Screenshot', 'Downloads a picture of the shelf.'),
    ], crop=[140, 690, 1120, 190], place=dict(x=0.95, y=2.9, w=8.0)))

    # ---- Understanding the Test Flow Side Panel / How do I Switch a Step On or Off?
    TF = 'testflow'
    node = lambda name: C(TF, tour=name, t='div')
    section('flow', lambda: ov('flow', 'Understanding the Test Flow Side Panel', TF + '.png', [
        (lambda: C(TF, s='Close Test Flow panel'), 'right', R, 'Close (X) icon', 'Closes the Test Flow side panel.'),
        (lambda: node('start'), 'left', L, 'Respondent arrives', 'Where every respondent starts: by opening the test link.'),
        (lambda: node('welcome'), 'right', R, 'Step', 'Each step of the respondent’s path. A step switched off is greyed out and marked Skipped, and the path runs around it. [[Learn more|step-1]]'),
        (lambda: union(*[C(TF, s=n, role='switch') for n in ('Welcome message', 'Practice round', 'Main round', 'Questionnaire')]), 'right', R,
         'Switches', 'Switch a step off and respondents skip past it.', dict(along=420)),
        (lambda: union(node('practice'), node('main')), 'left', L, 'Practice round / Main round', 'How many targets and trials each round runs.'),
        (lambda: node('questionnaire'), 'left', L, 'Questionnaire', 'How many questions respondents answer after the main round.'),
        (lambda: union(node('saving'), node('complete')), 'right', R, 'Saving results / Complete message',
         'The answers are saved, retrying if needed, and respondents see the Complete message and are sent on.'),
        (lambda: node('screenout'), 'right', R, 'Screenout message', 'With exclusion on, respondents who run out of retries are screened out here.'),
        (lambda: C(TF, cls='vue-flow__controls'), 'left', L, 'Zoom controls', 'Zoom the diagram in or out, or fit it to the panel.'),
    ], split=[5], crop=PANEL, place=PP))
    ff = XT.get('flowFlip') or {'key': 'welcome', 'label': 'Welcome message', 'on': False}
    section('step', lambda: steps('step', 'How do I Switch a Step On or Off?', [
        ('Click **Test Flow** in the side menu.', 'flow.png', RAIL(5), 'right', 260),
        (f'Click the switch on the step respondents should skip, {eg(ff["label"])}.', 'flow.png', lambda: pad(C('flow', s=ff['label'], role='switch'), 5), 'right', 640),
        ('The step is greyed out and marked **Skipped**, and the path runs around it. Click the switch again to turn it back on.' if not ff.get('on')
         else 'The step runs again and the path goes through it. Click the switch again to skip it.',
         'flow-off.png', lambda: pad(C('flow-off', tour=ff['key'], t='div'), 3), 'right', 640),
    ]))

    # ---- Instructions
    IN1, IN2, IO = 'instructions', 'instructions-2', 'ins-open'
    row_ = lambda st, n: C(st, tour=n, t='div')
    pm = lambda st, n: C(st, cls='ProseMirror', nth=n)

    def ins():
        a = ov('ins-1', 'Understanding the Instructions Side Panel', IN1 + '.png', [
            (lambda: C(IN1, s='Close Instructions panel'), 'right', R, 'Close (X) icon', 'Closes the Instructions side panel.'),
            (lambda: union(row_(IN1, 'welcome'), row_(IN1, 'main_no_prac')), 'left', L, 'Flow',
             'The screens respondents read as they go through the test: Welcome, Practice Round, Main Round and Main Round (No Practice).'),
            (lambda: row_(IN1, 'welcome'), 'right', R, 'Screen', 'Each row shows the screen’s name and its opening words. A step switched off in Test Flow is greyed out and tagged Skipped.', dict(hl=False)),
            (lambda: union(row_(IN1, 'warning'), row_(IN1, 'warning2')), 'left', L, 'Warnings', 'Shown when a respondent is too slow, or clicks products at random.'),
            (lambda: union(row_(IN1, 'screenout'), row_(IN1, 'end')), 'right', R, 'System', 'The Screenout and Complete messages at the end of the test.'),
        ], crop=PANEL, place=PP)
        for s_ in a:
            s_['key'] = 'ins-1'
        b = ov('ins-2', 'Understanding the Instructions Side Panel', IN2 + '.png', [
            (lambda: row_(IN2, 'others'), 'left', L, 'Global – Others', 'Shared text used throughout the test: loading messages, labels and the saving messages.'),
            (lambda: row_(IN2, 'practice'), 'right', R, 'Edit a screen', 'Click a row to edit that screen. [[Learn more|inedit-1]]', dict(hl=False)),
        ], crop=PANEL, place=PP)
        for s_ in b:
            s_['key'] = 'ins-2'
            s_['callouts'] = [(c[0] + 5,) + tuple(c[1:]) for c in s_['callouts']]
            s_['descs'] = [(n + 5, t) for n, t in s_['descs']]
        return a[:1] + b[:1]
    section('ins', ins)
    section('ined', lambda: ov('ined', 'Understanding the Instruction Editor', IO + '.png', [
        (lambda: C(IO, s='Back to instructions'), 'left', L, 'Back', 'Returns to the list of screens.'),
        (lambda: C(IO, s='Close Instructions panel'), 'right', R, 'Close (X) icon', 'Closes the Instructions side panel.'),
        (lambda: union(C(IO, s='Bold', nth=0), C(IO, s='Insert image')), 'left', L, 'Toolbar',
         'Bold, italic, alignment and pictures. With the panel widened, also underline, colour, subscript and superscript.'),
        (lambda: pm(IO, 0), 'right', R, 'Content', 'The message itself. The preview shows it as respondents will see it.'),
        (lambda: union(C(IO, s='Bold', nth=1), pm(IO, 1)), 'left', L, 'Button Text', 'The words on the screen’s button, e.g. START.'),
        (lambda: C(IO, t='input', within=[130, 600, 300, 100]), 'right', R, 'Button Delay', 'How long, in milliseconds, the button waits before it can be pressed, so the message is read first.'),
        ([137, 690, 310, 80], 'left', L, 'Modal Width', 'How wide the message card is, for the device you are previewing.'),
        (lambda: union(C(IO, s='Previous', t='button', within=PANEL), C(IO, s='Next', t='button', within=PANEL)), 'right', R, 'Previous / Next', 'Moves to the previous or next screen.'),
    ], split=[4], crop=PANEL, place=PP))
    which = XT.get('insOpen', 'practice')
    section('inedit', lambda: steps('inedit', 'How do I Edit an Instruction Screen?', [
        ('Click **Instructions** in the side menu.', IN1 + '.png', RAIL(1), 'right', 260),
        (f'Click the screen to edit, {eg("Practice Round" if which == "practice" else "Main Round")}.', IN1 + '.png', lambda: pad(row_(IN1, which), 2), 'right', 640),
        ('Type the message in **Content**. The preview shows it as respondents will see it.', IO + '.png', lambda: pad(pm(IO, 0), 4), 'right', 640),
        ('Change the **Button Text** if needed.', IO + '.png', lambda: pad(union(C(IO, s='Bold', nth=1), pm(IO, 1)), 4), 'right', 640),
        ('Click **Next** to go on to the next screen, or **Back** to return to the list.', IO + '.png', lambda: pad(C(IO, s='Next', t='button', within=PANEL), 3), 'top', 740),
    ]))

    # ---- Questionnaire
    QP, QO, QF = 'questionnaire', 'question-open', 'q-filled'
    q0 = X.get('question') or {}
    plain = lambda h: ' '.join(str(h or '').replace('<', ' <').split()) if h else ''
    strip = lambda h: __import__('re').sub(r'<[^>]+>', '', str(h or '')).strip()
    section('qpanel', lambda: ov('qpanel', 'Understanding the Questionnaire Side Panel', QP + '.png', [
        (lambda: C(QP, s='Close Questionnaire panel'), 'right', R, 'Close (X) icon', 'Closes the Questionnaire side panel.'),
        (lambda: C(QP, s='Show questionnaire', role='switch'), 'right', R, 'Show questionnaire', 'Switches the questionnaire on or off. It is asked after the main round finishes.'),
        (lambda: union(*[e['b'] for e in C.c[QP] if e.get('tour') and e['t'] == 'div' and e['b'][0] == 136]), 'left', L, 'Questions',
         'Each question’s title and opening words. Click one to edit it. [[Learn more|qed]]'),
        (lambda: C(QP, t='input', within=[140, 240, 40, 40]), 'right', R, 'Select', 'Tick questions to delete them together.'),
        (lambda: C(QP, s='Add question'), 'left', L, 'Add question', 'Adds a new question to the end of the list. [[Learn more|q-1]]'),
    ], crop=PANEL, place=PP))
    section('qed', lambda: ov('qed', 'Understanding the Question Editor', QO + '.png', [
        (lambda: C(QO, s='Back to questionnaire'), 'left', L, 'Back', 'Returns to the list of questions.'),
        (lambda: C(QO, s='Delete question'), 'right', R, 'Delete question', 'Deletes the question, after asking you to confirm.'),
        (lambda: C(QO, t='input', within=[130, 140, 340, 70]), 'left', L, 'Title', 'The question’s name, used in the list and in the results.'),
        (lambda: union(C(QO, s='Bold', nth=0), pm(QO, 0)), 'right', R, 'Content', 'The question respondents read before they choose.'),
        (lambda: union(C(QO, s='Bold', nth=1), pm(QO, 1)), 'left', L, 'Button Text', 'The words on the button that starts the choice.'),
        (lambda: union(C(QO, s='Bold', nth=2), pm(QO, 2)), 'right', R, 'Bottom Instructions', 'The line shown below the shelf while respondents choose.'),
    ], crop=PANEL, place=PP))
    if PLAN.get('questions'):
        qs = PLAN['questions']
        section('q', lambda: steps('q', 'How do I Add a Question?', [
            ('Click **Questionnaire** in the side menu and switch on **Show questionnaire**.', 'q-list.png', lambda: pad(C('q-list', s='Show questionnaire', role='switch'), 4), 'right', 640),
            ('A new questionnaire has one question. Click it to open it.', 'q-on.png', lambda: pad(next(e['b'] for e in C.c['q-on'] if e.get('tour') and e['t'] == 'div'), 2), 'right', 640),
            (f'Type the **Title**, {eg(q0.get("title"))}.', QF + '.png', lambda: pad(C(QF, t='input', within=[130, 140, 340, 70]), 3), 'right', 640),
            (f'Type the question in **Content**, {eg(strip(q0.get("text")))}.', QF + '.png', lambda: pad(pm(QF, 0), 4), 'right', 640),
            (f'Type the **Button Text**, {eg(strip(q0.get("button")))}.', QF + '.png', lambda: pad(pm(QF, 1), 6), 'right', 640),
            (f'Type the **Bottom Instructions**, {eg(strip(q0.get("short_text")))}.', QF + '.png', lambda: pad(pm(QF, 2), 4), 'right', 640),
            ('Click **Back** (‹) to return to the list, then click **Add question**.', 'q-list-1.png', lambda: pad(C('q-list-1', s='Add question'), 3), 'right', 640),
            (f'The new question is added to the list. Click it and fill it in the same way{", " + eg(*[q["title"] for q in qs[1:3]]) if len(qs) > 1 else ""}.',
             'q-added.png', lambda: [pad([e['b'] for e in C.c['q-added'] if e.get('tour') and e['t'] == 'div'][-1], 2)], 'right', 640),
        ]))

    # ---- Style panel
    ST = 'styles'
    head = lambda st, n: C(st, s=n, t='button')
    SL, SR = 1196, 1655
    section('style', lambda: ov('style', 'Understanding the Style Panel', ST + '.png', [
        (lambda: C(ST, tour='device-view-card'), 'left', SL, 'Device View', 'The device and screen the preview shows. [[Learn more|device-1]]'),
        (lambda: head(ST, 'Shelf Style'), 'left', SL, 'Shelf Style', 'The shelf scene: its backdrop, frame, posts and price tags. [[Learn more|bg-1]]'),
        (lambda: head(ST, 'Modal Layout'), 'left', SL, 'Modal Layout', 'The text size, line spacing, direction and shadow of the pop-up windows. [[Learn more|modal]]'),
        (lambda: head(ST, 'Theme Palette'), 'right', SR, 'Theme Palette', 'The colours of the pop-up windows and their buttons. [[Learn more|palette]]'),
        (lambda: head(ST, 'Radius & Border'), 'left', SL, 'Radius & Border', 'The corner shape of the pop-up windows and buttons. [[Learn more|radius]]'),
        (lambda: head(ST, 'Typography'), 'right', SR, 'Typography', 'The font of every word the respondent reads. [[Learn more|typo]]'),
        (lambda: C(ST, s='Reset to default', nth=0), 'right', SR, 'Reset to default', 'Puts a section back to its default values.', dict(along=280)),
    ], crop=[1246, 55, 354, 490], place=dict(x=3.7, y=1.85, h=4.6)))

    bd = XT.get('backdrop')
    if bd and 'bg-picked' in C.c:
        if bd.get('mode') in ('swatch', 'custom'):
            section('bg', lambda: steps('bg', 'How do I Change the Shelf Background?', [
                ('In the **Style Panel**, under **Shelf Style**, click **Plain colour**. (**Picture** chooses or uploads a background image.)', 'look-before.png',
                 lambda: pad(C('look-before', s='Plain colour', t='button'), 3), 'left', 1180),
                (f'Click a colour, {eg(bd["label"])}. It applies straight away. **Custom colour** picks any other shade.' if bd['mode'] == 'swatch'
                 else f'Click the **Custom colour** swatch and type the colour’s code, {eg(bd["label"])}. It applies straight away.',
                 'bg-plain.png', (lambda: pad(C('bg-plain', s=bd['label'], t='button'), 4)) if bd['mode'] == 'swatch' else (lambda: pad(C('bg-plain', s='Choose', t='button'), 4)), 'left', 1180),
                ('The shelves now stand in front of the colour you picked.', 'bg-picked.png', [120, 107, 1130, 640], 'bottom', 840),
            ]))
        else:
            section('bg', lambda: steps('bg', 'How do I Change the Shelf Background?', [
                ('In the **Style Panel**, under **Shelf Style**, keep **Picture** and click **Grid view** to see every background.', 'bg-grid.png',
                 lambda: pad(C('bg-grid', s='Grid view'), 3), 'left', 1180),
                ('Click the picture you want. It applies straight away; **Brightness** below darkens it.', 'bg-picked.png', [1263, 233, 315, 500], 'left', 1180),
            ]))

    fp = XT.get('framePicker')
    fr = PLAN.get('style', {}).get('frame', {})
    if 'frame-section' in C.c:
        c0 = (fr.get('colours') or [{}])[0]
        nums = {n['label']: n['value'] for n in fr.get('numbers', [])}
        post = PLAN.get('style', {}).get('post', {}).get('colours') or []
        rows = [(f'In the **Style Panel**, scroll down to **Shelf frame** and click the swatch of a colour, {eg(fp or "Front Color")}.', 'frame-section.png',
                 lambda: pad(C('frame-section', s=f'Choose {fp or "Front Color"}'), 4), 'top', 760)]
        if fp:
            rows.append((f'Pick a colour, or type its code in the box{", " + eg(str(c0.get("value", "")).lstrip("#")) if c0.get("value") else ""}. Do the same for the frame’s other colours.',
                         'frame-picker.png', lambda: pad(next(e['b'] for e in C.c['frame-picker'] if e['t'] == 'input' and 'vc-' not in e.get('cls', '') and e['b'][0] > 900 and e['b'][1] > 600), 3), 'left', 880))
        if 'frame-done' in C.c:
            rows.append((f'Set **Top depth** and **Eye level** to choose how much of each shelf’s top shows'
                         + (f', e.g. **{nums.get("Top depth")}** and **{nums.get("Eye level")}**.' if nums else '.'),
                         'frame-done.png', lambda: [pad(e['b'], 3) for e in C.c['frame-done'] if e['t'] == 'input' and e['b'][0] > 1500 and e['b'][2] < 60][:2], 'left', 1180))
        if post and 'post-done' in C.c:
            rows.append(('Under **Post area**, set the **Background Color** and **Shadow Color** of the uprights the same way.', 'post-done.png',
                         lambda: pad(union(C('post-done', s='Choose Background Color', nth=0), C('post-done', s='Choose Shadow Color', nth=1)), 4), 'left', 1180))
        section('frame', lambda: steps('frame', 'How do I Style the Shelf Frame and Posts?', rows))

    SM, PL, RD, TY = 'styles-modal', 'styles-palette', 'styles-radius', 'styles-typography'
    section('modal', lambda: ov('modal', 'Understanding the Modal Layout', SM + '.png', [
        ([1280, 357, 135, 66], 'left', SL, 'Font Size', 'The text size of the pop-up windows, set for each device.'),
        ([1427, 357, 135, 66], 'right', SR, 'Line Height', 'The spacing between lines of text.'),
        ([1280, 438, 281, 69], 'left', SL, 'Text Direction', 'Left to Right, or Right to Left for languages such as Arabic.'),
        ([1280, 515, 281, 64], 'right', SR, 'Shadow', 'How strongly the pop-up window’s shadow shows.'),
    ], crop=[1246, 280, 354, 320], place=dict(x=3.7, y=2.2, h=3.8)))
    section('palette', lambda: ov('palette', 'Understanding the Theme Palette', PL + '.png', [
        ([1276, 400, 290, 118], 'left', SL, 'Surfaces', 'Cards: the pop-up windows and the hint card. Text on cards: the text on them.'),
        ([1276, 545, 290, 232], 'right', SR, 'Buttons & muted', 'The buttons, their text, their colours when pointed at, and the muted (disabled) button.'),
        ([1276, 790, 290, 110], 'left', SL, 'Status', 'Error, Warning, Success and Info: used for warnings, screen-outs and completion.'),
    ], crop=[1246, 340, 354, 560], place=dict(x=3.7, y=1.85, h=4.9)))
    section('radius', lambda: ov('radius', 'Understanding Radius & Border', RD + '.png', [
        (lambda: union(C(RD, s='Cards & tiles — None'), C(RD, s='Cards & tiles — Pill')), 'left', SL, 'Cards & tiles', 'The corner shape of the pop-up windows and hint cards, from None to Pill.'),
        (lambda: union(C(RD, s='Buttons — None'), C(RD, s='Buttons — Pill')), 'right', SR, 'Buttons', 'The corner shape of the buttons respondents press, such as START and NEXT.'),
    ], crop=[1246, 400, 354, 380], place=dict(x=3.7, y=2.1, h=4.2)))
    section('typo', lambda: ov('typo', 'Understanding Typography', TY + '.png', [
        (lambda: union(C(TY, s='Font family', t='label'), C(TY, t='button', within=[1270, 555, 300, 60])), 'left', SL, 'Font family',
         'The font of every word the respondent reads: shelf labels, price tags and pop-up windows.'),
    ], crop=[1246, 460, 354, 200], place=dict(x=3.7, y=2.8, h=2.4)))

    # ---- Themes
    TH = 'themes'
    theme = XT.get('theme') or 'the theme'
    apply_btn = lambda: C(TH, prefix='Apply ', t='button', within=PANEL)
    section('themes', lambda: ov('themes', 'Understanding the Themes Side Panel', TH + '.png', [
        (lambda: C(TH, s='Close Themes panel'), 'right', R, 'Close (X) icon', 'Closes the Themes side panel.'),
        ([136, 121, 320, 42], 'left', L, 'Search themes', 'Finds a theme by its name.'),
        ([137, 235, 318, 150], 'left', L, 'Theme card', 'A picture of the theme’s shelf, its name, whether it is a Team or System theme, its colours and who made it.'),
        (lambda: C(TH, s='Add to favourites', nth=0), 'right', R, 'Favourite', 'Stars the theme so it is easy to find.'),
        (lambda: C(TH, prefix='Delete ', t='button', within=PANEL), 'right', R, 'Delete', 'Deletes a theme your team made, after asking you to confirm.'),
        (apply_btn, 'left', L, 'Apply', 'Gives the test this theme’s look. [[Learn more|apply-1]]'),
    ], crop=PANEL, place=PP))
    section('apply', lambda: steps('apply', 'How do I Apply a Theme?', [
        ('Click **Themes** in the side menu.', TH + '.png', RAIL(3), 'right', 260),
        (f'Find the theme you want, {eg(theme)}, and click **Apply**.', TH + '.png', lambda: pad(apply_btn(), 3), 'right', 640),
        ('A pop-up shows what changes – the backdrop, frame, posts and price-tag colours – and what stays the same.', 'theme-apply.png', [568, 527, 464, 123], 'left', 440),
        ('Click **Apply theme**. The theme is applied and the test saved; use **Recent changes** to go back. [[Learn more|restore-1]]', 'theme-apply.png', pad([902, 682, 130, 42], 3), 'right', 1160),
    ]))
    KB = 'kebab'
    section('stheme', lambda: steps('stheme', 'How do I Save a Shelf as a Theme?', [
        ('Click **More save options** (⋮) beside **Save**.', KB + '.png', pad([1202, 65, 32, 32], 3), 'left', 880),
        ('Click **Save as theme**.', KB + '.png', pad([952, 345, 126, 20], 5), 'left', 880),
        ('The **Save as Theme** pop-up shows the shelf and its colours. Type a **Theme name**.', 'save-theme-named.png',
         lambda: pad(C('save-theme-named', t='input', within=[480, 520, 640, 70]), 3), 'left', 420),
        ('Add **Tags** if you like, to make the theme easy to find, and choose **Who can use it**.', 'save-theme-named.png', pad([488, 618, 624, 124], 2), 'left', 420),
        ('Click **Save theme**. The theme is added to the **Themes** panel, ready to apply to other tests.', 'save-theme-named.png',
         lambda: pad(C('save-theme-named', s='Save theme', t='button'), 3), 'right', 1180),
    ]))

    # ---- Devices, Simulate, Save, Live/Draft
    section('device', lambda: steps('device', 'How do I Preview on Another Device?', [
        ('Under **Device View**, click **Tablet**.', F_ + '.png', lambda: pad(C(F_, s='Tablet', t='button'), 3), 'left', 1180),
        ('The preview shows the test on a tablet screen.', 'device-tablet.png', lambda: C('device-tablet', tour='preview-frame'), 'right', 1220),
        ('Click **Mobile** for a phone. Each device keeps its own number of shelves and products per shelf.', 'device-mobile.png',
         lambda: pad(C('device-mobile', s='Mobile', t='button'), 3), 'left', 1180),
        ('Open the screen list to choose a model. Each one is listed with its screen size.', 'device-list.png', pad([1280, 166, 281, 470], 2), 'left', 1180),
    ]))
    SR_ = 'sim-run'
    section('sim', lambda: steps('sim', 'How do I Simulate the Test?', [
        ('Click **Simulate**, or press **Ctrl+Enter**. If anything is missing, a list shows it with a button to fix it, or **Simulate anyway**.',
         F_ + '.png', lambda: pad(C(F_, tour='simulate'), 3), 'bottom', 170),
        ('The test plays in the preview as a respondent meets it, unsaved changes included. Nothing is recorded.', SR_ + '.png', [376, 222, 970, 570], 'bottom', 860),
        ('The step bar shows where the respondent is. Click a step to start the run there; **Restart** starts again.', SR_ + '.png',
         lambda: pad(C(SR_, tour='simulation-controls'), 3), 'bottom', 170),
        ('The device bar runs the test on another device or screen.', SR_ + '.png', pad([668, 115, 384, 44], 3), 'bottom', 230),
        ('When the run ends, a summary shows the time taken, the trials and the answers. Click **Back to editing** to return to your test.', SR_ + '.png',
         lambda: pad(C(SR_, s='Back to editing', t='button'), 3), 'bottom', 170),
    ]))
    section('save', lambda: steps('save', 'How do I Save the Test?', [
        ('A red dot and **Unsaved changes** appear beside **Save** while the test has edits that are not saved. Click **Save**.', 'save-before.png',
         lambda: pad(union(C('save-before', role='status'), C('save-before', s='Save', t='button')), 3), 'bottom', 200),
        ('The test is saved and live. Click **Preview Test** to open it, or **Close**.', 'save-done.png', pad([576, 310, 448, 280], 2), 'left', 440),
        ('The red dot clears. Every save is kept as a version you can go back to. [[Learn more|restore-1]]', 'save-after.png',
         lambda: pad(C('save-after', tour='save-actions'), 3), 'bottom', 200),
    ]))
    section('open', lambda: steps('open', 'How do I Open the Live or Draft Test?', [
        ('Click **More save options** (⋮) beside **Save**.', KB + '.png', pad([1202, 65, 32, 32], 3), 'left', 880),
        ('Click **Live preview** to open the saved test in a new tab. **Draft preview** opens a version saved with **Save as draft**.', KB + '.png', pad([947, 209, 274, 42], 3), 'left', 880),
        ('The test opens as respondents will see it. **Preview** in the side menu opens it too.', 'preview-live.png', [160, 76, 1280, 750], 'bottom', 870),
    ]))

    # ---- Additional functions
    AD = 'advanced'
    section('advanced', lambda: ov('advanced', 'Understanding the Advanced Side Panel', AD + '.png', [
        (lambda: C(AD, s='Close Advanced panel'), 'right', R, 'Close (X) icon', 'Closes the Advanced side panel.'),
        (lambda: C(AD, s='Custom code files', role='tablist'), 'left', L, 'CSS / JavaScript', 'Switches between the custom stylesheet and the custom script.'),
        (lambda: union(C(AD, s='Copy to clipboard'), C(AD, s='Clear this file')), 'right', R, 'Copy / Clear', 'Copies the open file, or empties it (Undo brings it back for a few seconds).'),
        ([150, 206, 298, 500], 'left', L, 'Code editor', 'CSS is added to the survey page; JavaScript runs after the survey loads. Use them for changes the panels cannot make.'),
        ([150, 724, 298, 24], 'right', R, 'Status', 'The number of lines, and whether the code is in use.'),
        ([150, 756, 298, 56], 'left', L, 'Note', 'A reminder of what the code is for and where it runs.'),
    ], crop=PANEL, place=PP))
    section('restore', lambda: steps('restore', 'How do I Restore a Previous Version?', [
        ('Click **More save options** (⋮) beside **Save**, then **Recent changes**.', KB + '.png', pad([952, 396, 136, 20], 5), 'left', 880),
        ('The **Recent Changes** panel lists every saved version, newest first, with what changed and who saved it. **From Date** and **To Date** narrow the list.',
         'recent.png', [1116, 194, 459, 109], 'left', 1050),
        ('Click a version to see each change in it, from its old value to its new one.', 'recent-detail.png', [1208, 84, 376, 800], 'left', 1195),
        ('Click **Restore** on the version to go back to.', 'recent-detail.png', pad([1108, 269, 59, 25], 3), 'left', 780),
        ('Click **Restore** to confirm. The test goes back to that version and the page reloads. **Cancel** keeps it as it is.', 'recent-confirm.png', pad([1042, 486, 70, 32], 3), 'right', 1200),
    ]))
    AS = 'assistant'
    section('assistant', lambda: ov('assistant', 'Understanding the AI Assistant', AS + '.png', [
        (lambda: C(AS, s='Toggle chat history'), 'left', 300, 'Chat history', 'Your earlier conversations with the assistant.'),
        ([640, 292, 120, 32], 'top', 250, 'AI Assistant', '“Online” means it is ready to answer.'),
        (lambda: union(C(AS, s='More actions'), C(AS, s='Minimise')), 'right', 1070, 'Menu / Minimise', 'More options, or shrink the assistant back to the bar at the foot of the preview.'),
        (lambda: C(AS, s='Start a conversation'), 'left', 300, 'Start a conversation', 'Opens the chat, with suggested questions and actions to start from.'),
        ([492, 632, 384, 80], 'right', 1070, 'Ask', 'Questions about your shelf test, its rounds, products and settings, and about IMPRINT.'),
        ([492, 722, 384, 78], 'left', 300, 'Act', 'Ask it to build or change your test. Every change is shown first and only applied when you approve it.'),
    ], crop=[350, 270, 680, 590], place=dict(x=1.6, y=1.85, h=4.9)))
    section('news', lambda: steps('news', 'How do I See What’s New?', [
        ('Click **What’s New** at the top of the editor. A red dot means there are notes you have not read.', F_ + '.png',
         lambda: pad(C(F_, tour='header-whats-new'), 3), 'bottom', 150),
        ('Each release lists what was **Added**, **Changed** and **Fixed**, newest first. Click **Close** when you are done.', 'whats-new.png', [416, 60, 768, 780], 'right', 1260),
    ]))
    return out


def _section(out, name, fn):
    """Adds a section's slides; a section that cannot be built is skipped with a warning."""
    try:
        got = fn() or []
    except (KeyError, StopIteration, IndexError, TypeError, ValueError) as e:
        print(f'WARNING section {name!r} skipped: {e}')
        return
    for s_ in got:
        if s_.get('spotlight') is None and not s_.get('template'):
            s_.pop('spotlight', None)
    out.extend(got)
