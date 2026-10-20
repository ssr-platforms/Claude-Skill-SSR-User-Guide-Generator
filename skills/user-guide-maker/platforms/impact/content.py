"""Everything the IMPACT User Guide SAYS, and where each callout points.

The guide walks through building a test FROM SCRATCH — the demo test
SO2GKM679H ("Snack Shelf Test"), built by capture-build.js to follow the user's
own project ABUVANIDYQ — with "Understanding the ..." overviews placed just
before the steps that use them, and restoring a previous version last.

build.py owns the mechanics (template surgery, shapes, images); this file owns
the words and the geometry. To add a section: capture its screenshot, then add
slides here and an entry to TOC. See ../PROGRESS.md.

Coordinates are CSS px of the 1600x900 capture viewport. Boxes come from the
control dumps (screenshots/controls.json and build-controls.json) by on-screen
label wherever possible; the few typed boxes are things with no single element.

Callout = (number, highlight box or None, badge centre, arrow end).
Description markup: **bold**, and [[Learn more|slide-key]] for a link.
"""
import datetime, json, os

ACCENT = '8C0F28'                                   # IMPACT's accent (the template's violet is 901A8A)

_d = datetime.date.today()
_sfx = 'th' if 11 <= _d.day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(_d.day % 10, 'th')
META = {
    'title': os.environ.get('GUIDE_TITLE', 'IMPACT User Guide'),
    'version': (f"Version No. {os.environ.get('GUIDE_VERSION', '1')} ", f'– {_d.day}', _sfx, f" of {_d.strftime('%B %Y')}"),
}
TOC_INTRO = (META['title'], ' is designed to be used as a step-by-step guide in creating and configuring your own attention tests. Check out the ')

INTRO = {
    'lead': ('IMPACT is a visual-attention research tool that measures the attention-grabbing power, or “pull”, '
             'of packaging, advertising and other visual assets.'),
    'body': ('As a scalable alternative to traditional eye tracking, IMPACT asks respondents to find a target that replaces part '
             'of an image. Their reaction times show which regions of the design attract attention most strongly, and an explicit '
             'round records the areas they most like looking at. The results are shown as heatmaps, similar to those from '
             'eye-tracking tools, and can be exported for further analysis. This guide builds a complete test from scratch, step by step.'),
    'list_head': 'The IMPACT IDE typically consists of the following components:',
    'list': [
        ('Instructions', 'Used to write and edit every message respondents read, including the welcome screen, round instructions, warnings and completion messages.'),
        ('Settings', 'Used to set the pace of the test – the pauses, the countdown and the timeout warning – and when hints are shown.'),
        ('Test Flow', 'Shows the respondent’s path through the test and lets you switch the welcome, practice, main and explicit rounds on or off.'),
        ('Advanced', 'Used to add custom CSS and JavaScript for extended design and functional customisation.'),
        ('Preview', 'Opens the saved test in a new tab, exactly as a respondent will see it.'),
        ('Stimuli', 'Used to add the images being tested and lay a grid of cells over each one.'),
        ('Cell Groups', 'Used to name regions of a stimulus, such as each product on a shelf, so results can be reported for each one.'),
        ('Styles', 'Used to set the colours, fonts and borders of the test, including the click feedback.'),
        ('AI Assistant', 'Answers questions about IMPACT and your test, and can propose changes for you to approve.'),
    ],
}

# Table of contents: (label, slide key), in the order the guide is read.
TOC = [
    ('Cover page', 'cover'),
    ('Table of Contents', 'toc'),
    ('Introduction', 'intro'),
    ('Understanding the IMPACT IDE', 'ide-1'),
    ('How do I Take the Quick Tour?', 'tour-1'),
    ('How do I See What\u2019s New?', 'news-1'),
    ('Understanding the Stimuli Panel', 'stimuli-1'),
    ('How do I Add a Stimulus?', 'add-1'),
    ('How do I Set Up the Stimulus Grid?', 'grid-1'),
    ('Understanding the Stage Toolbar', 'toolbar-1'),
    ('How do I Paint Active Cells?', 'active-1'),
    ('How do I Paint Priority Cells?', 'prio-1'),
    ('How do I Set the Trials and the Explicit Round?', 'trials-1'),
    ('How do I Create Cell Groups?', 'groups-1'),
    ('Understanding the Target View', 'target'),
    ('How do I Choose the Target?', 'choose-1'),
    ('Understanding the Configure Icons Pop-up Modal', 'icons'),
    ('Understanding the Instructions Side Panel', 'instructions-1'),
    ('Understanding the Instruction Editor', 'editor-1'),
    ('How do I Edit the Welcome Message?', 'welcome-1'),
    ('Understanding the Settings Side Panel', 'settings-1'),
    ('Understanding the Test Flow Side Panel', 'testflow'),
    ('How do I Switch a Round Off?', 'roundoff-1'),
    ('Understanding the Styles Panel', 'styles'),
    ('Understanding the Theme Palette', 'styles-palette'),
    ('Understanding the Page Background', 'styles-background'),
    ('Understanding Radius & Border', 'styles-radius'),
    ('Understanding Typography', 'styles-typography'),
    ('Understanding the Advanced Side Panel', 'advanced'),
    ('How do I Save the Test?', 'save-1'),
    ('How do I Preview the Test?', 'preview-1'),
    ('How do I Preview on Another Device?', 'device-1'),
    ('Understanding the AI Assistant', 'assistant'),
    ('How do I Restore a Previous Version?', 'restore-1'),
]


# --------------------------------------------------------------------------- geometry helpers
class Controls:
    """Both control dumps, looked up by state + on-screen label."""

    def __init__(self, shots):
        self.c, self.extra = {}, {}
        for name in ('controls.json', 'build-controls.json'):
            data = json.load(open(os.path.join(shots, name)))
            self.c.update(data['controls'])
            self.extra.update(data['extra'])

    def __call__(self, state, s=None, prefix=None, cls=None, id=None, t=None, nth=0):
        """Box of the nth visible control in `state` matching every given filter."""
        hits = [e for e in self.c[state]
                if (s is None or e['s'] == s) and (prefix is None or e['s'].startswith(prefix))
                and (cls is None or cls in e['c'].split()) and (id is None or e['id'] == id) and (t is None or e['t'] == t)]
        if len(hits) <= nth:
            raise KeyError(f'no control in {state!r} matching s={s!r} prefix={prefix!r} cls={cls!r} id={id!r} t={t!r}')
        return hits[nth]['b']


def union(*boxes):
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes); y1 = max(b[1] + b[3] for b in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


def pad(b, p=3):
    return [b[0] - p, b[1] - p, b[2] + 2 * p, b[3] + 2 * p]


def rect(r):
    """[x0, y0, x1, y1] -> [x, y, w, h]"""
    return [r[0], r[1], r[2] - r[0], r[3] - r[1]]


def co(n, box, side, at, t=0.5, hl=True, along=None):
    """Callout from a badge on `side` of `box`, sitting at coordinate `at` on the
    other axis (x for left/right, y for top/bottom). `along` overrides where on
    the edge the arrow lands (absolute px), otherwise fraction `t` of the edge."""
    x, y, w, h = box
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


def describe(items):
    return [(n, f'**{label}** – {text}') for n, label, text in items]


def overview(key, title, shot, items, split, **kw):
    """An "Understanding the ..." section: every badge on each slide, the
    descriptions divided at the indexes in `split`."""
    calls = [c for c, _, _ in items]
    bounds = [0] + list(split) + [len(items)]
    out = []
    for i in range(len(bounds) - 1):
        part = items[bounds[i]:bounds[i + 1]]
        k = key if len(bounds) == 2 else f'{key}-{i + 1}'
        out.append(dict(key=k, title=title, shot=shot, callouts=calls,
                        descs=describe([(c[0], l, t) for c, l, t in part]), **kw))
    return out


def step_slides(key, title, steps):
    """A "How do I ...?" section: one step per slide, the list growing; the
    step's box is spotlit (everything else dimmed) and outlined.
    steps = [(text, shot, box, side, at), ...]"""
    out = []
    for i, (text, shot, box, side, at) in enumerate(steps, 1):
        out.append(dict(key=f'{key}-{i}', title=title, shot=shot, spotlight=box,
                        callouts=[co(i, box, side, at)],
                        descs=[(n, steps[n - 1][0]) for n in range(1, i + 1)]))
    return out


# --------------------------------------------------------------------------- slides
def slides(shots):
    C = Controls(shots)
    X = C.extra
    out = []
    PANEL_CROP = [96, 64, 314, 800]          # the left column / a side panel
    PANEL_PLACE = dict(x=3.05, y=1.70, h=5.0)

    # ---- Understanding the IMPACT IDE (the finished test; 10 callouts over 2 slides)
    rail = union(C('ide', s='Instructions', t='button'), C('ide', s='Preview', t='button'))
    out += overview('ide', 'Understanding the IMPACT IDE', 'ide.png', [
        (co(1, pad(rail, -2), 'left', -80), 'Side Menu',
         'Opens the Instructions, Settings, Test Flow, Advanced and Preview panels used to set up the rest of the test. [[Learn more|instructions-1]]'),
        (co(2, C('ide', id='tour-stimuli'), 'left', -80, along=640), 'Stimuli Panel',
         'Used to add and manage the images for the Main and Practice rounds, and to set each image’s grid, trials and explicit phase. [[Learn more|stimuli-1]]'),
        (co(3, C('ide', id='tour-summary'), 'left', -80, along=775), 'Summary',
         'Shows how many cells, active cells and priority cells the selected stimulus has, and how many trials it adds.'),
        (co(4, X['strip'], 'bottom', 312, along=900), 'Stage Toolbar',
         'Switches between editing the Stimuli and the Target, and holds the tools for painting cells. [[Learn more|toolbar-1]]'),
        (co(5, C('ide', t='iframe'), 'bottom', 980, along=1150), 'Stage',
         'A live preview of the test as respondents will see it. Cells are painted directly on the stimulus here.'),
        (co(6, C('ide', id='tour-screens'), 'top', -84, along=760), 'Go to / Previous / Next',
         'Jumps to any screen of the test, or steps through them in order, to preview it on the stage.'),
        (co(7, C('ide', id='tour-save'), 'top', -84, along=1160), 'Undo / Redo, Save and More',
         'Undo or redo your edits, save the test, and open the menu for Recent changes and Discard changes. [[Learn more|save-1]]'),
        (co(8, C('ide', s='Open AI Assistant', t='button'), 'top', -84), 'AI Assistant',
         'Opens the AI Assistant, which answers questions about IMPACT and your test and can propose changes for you to approve.'),
        (co(9, C('ide', id='tour-devices'), 'right', 1680), 'Device View',
         'Previews the test on a desktop, tablet or mobile screen at a chosen resolution.'),
        (co(10, union(C('ide', s='Config', t='button'), C('ide', id='tour-cell-groups')), 'right', 1680, along=550), 'Config / Styles',
         'Config holds the selected stimulus’s cell groups; Styles sets the colours, fonts and borders of the test. [[Learn more|groups-1]]'),
    ], split=[5])

    # ---- How do I Take the Quick Tour?
    out += step_slides('tour', 'How do I Take the Quick Tour?', [
        ('Click **How it works** at the top of the Stimuli column. The tour also opens by itself the first time you open the IDE.',
         'ide.png', pad(C('ide', id='how-it-works-btn'), 3), 'right', 470),
        ('Each step explains one part of the IDE. The numbered dots show how far through the 13 steps you are.',
         'tour-1.png', [584, 242, 436, 416], 'right', 1110),
        ('The part being explained is outlined on screen. Click **Next** or **Back** to move between steps, or **Skip tour** to close it.',
         'tour-2.png', [122, 264, 434, 394], 'right', 640),
    ])

    # ---- How do I See What's New?
    out += step_slides('news', 'How do I See What\u2019s New?', [
        ('Click **What\u2019s New** at the top of the screen. A red dot means there are updates you have not read yet.',
         'ide.png', pad(C('ide', prefix="What's New", t='button'), 3), 'bottom', 330),
        ('Each release lists what was **Added**, **Changed** and **Fixed**, newest first. Click **Close** when you are done.',
         'whats-new.png', [428, 62, 744, 772], 'right', 1260),
    ])

    # ---- Understanding the Stimuli Panel (crop of the left column)
    L, R = 30, 450
    out += overview('stimuli', 'Understanding the Stimuli Panel', 'ide.png', [
        (co(1, union(C('ide', s='Stimuli', t='button'), C('ide', s='Stimuli actions')), 'left', L), 'Stimuli header',
         'Collapses or expands the panel. The count shows which stimulus is selected, and the menu (⋮) offers Configure all grids and Select all.'),
        (co(2, union(C('ide', s='Main'), C('ide', s='Practice')), 'right', R), 'Main / Practice',
         'Switches between the stimuli of the Main Round and the Practice Round.'),
        (co(3, C('ide', t='img', nth=0), 'left', L), 'Stimulus Preview',
         'Shows the selected stimulus with its painted cells.'),
        (co(4, union(C('ide', s='Replace image from the gallery'), C('ide', s='Delete stimulus')), 'right', R), 'Image Tools',
         'Replace the image from the gallery, edit it, or delete the stimulus.'),
        (co(5, union(C('ide', s='Snack Shelf', t='button'), C('ide', s='Add stimulus')), 'left', L), 'Filmstrip',
         'Every stimulus in the round. Click one to select it, or click + Add to add another from the gallery.'),
        (co(6, C('ide', s='Stimulus name'), 'right', R), 'Stimulus Name',
         'The name of the selected stimulus.'),
        (co(7, union(C('ide', s='Columns', t='label'), C('ide', s='Increase Rows')), 'left', L), 'Columns × Rows',
         'Sets the size of the grid of cells laid over the stimulus.'),
        (co(8, [108, 538, 265, 70], 'right', R), 'Trials',
         'The most trials this stimulus runs. Priority cells run first; the rest are picked at random from the active cells. Leave blank for no limit.'),
        (co(9, [108, 612, 265, 56], 'left', L), 'Explicit phase',
         'Includes this stimulus in the explicit round, where respondents rate it after the main round.'),
        (co(10, C('ide', id='tour-summary'), 'right', R), 'Summary',
         'Read-only counts for the selected stimulus: cells, active and priority cells, and the trials it adds to the round.'),
    ], split=[5], crop=[96, 120, 290, 748], place=dict(x=3.05, y=1.70, h=5.0))

    # ---- How do I Add a Stimulus?
    image_on_stage = [409, 354, 878, 412]
    out += step_slides('add', 'How do I Add a Stimulus?', [
        ('A new test starts with one empty stimulus. In the **Stimuli** panel, click the empty slot (**Drop, or pick from the gallery**).',
         'new-test.png', C('new-test', prefix='DROP, OR PICK FROM THE GALLERY', t='button'), 'right', 470),
        ('The **Gallery** opens on the images in **This survey**. Click the image you want to test. You can also **Upload** a new one.',
         'add-gallery.png', C('add-gallery', prefix='Screenshot (7) edited', t='button'), 'left', 318),
        ('Click **Add**.',
         'add-selected.png', pad(C('add-selected', s='Add', t='button'), 3), 'bottom', 760),
        ('The image becomes the stimulus and appears on the stage, ready for its grid.',
         'add-done.png', image_on_stage, 'top', 312),
    ])

    # ---- How do I Set Up the Stimulus Grid?
    out += step_slides('grid', 'How do I Set Up the Stimulus Grid?', [
        ('Give the stimulus a name in the **Stimulus name** field, e.g. **Snack Shelf**.',
         'grid-name.png', pad(C('grid-name', s='Stimulus name'), 3), 'right', 470),
        ('Set the **Columns** and **Rows**, e.g. **30 × 20**. The grid on the stage updates as you type; smaller cells measure the design more finely.',
         'grid-size.png', pad(union(C('grid-size', s='Columns', t='label'), C('grid-size', s='Increase Rows')), 3), 'right', 470),
    ])

    # ---- Understanding the Stage Toolbar (crop of the strip)
    TOP, BOT = 64, 330
    readout = [905, 137, 142, 28]       # a plain span: not in the control dump
    out += overview('toolbar', 'Understanding the Stage Toolbar', 'ide.png', [
        (co(1, union(C('ide', cls='stage-tab', nth=0), C('ide', cls='stage-tab', nth=1)), 'top', TOP), 'Editing',
         'Switches the stage between the Stimuli (the grid and its cells) and the Target (the target and its distractors).'),
        (co(2, readout, 'top', TOP), 'Cell count',
         'How many cells on the selected stimulus are marked – or grouped, when the scope is Cell Groups.'),
        (co(3, C('ide', prefix='Clear cells'), 'top', TOP), 'Clear cells',
         'Removes the painting from every cell on the selected stimulus, after asking you to confirm.'),
        (co(4, C('ide', s='Reset tools'), 'top', TOP), 'Reset',
         'Restores the tools, cell colours and overlays to their defaults. Painted cells are kept.'),
        (co(5, C('ide', s='Lock editing'), 'top', TOP), 'Editable / Locked',
         'Locks every editing control on the strip so the test cannot be changed by accident.'),
        (co(6, C('ide', cls='tool-group', nth=0), 'bottom', BOT), 'Tool',
         'Pointer (V) clicks single cells, Brush (B) paints as you drag, Box (M) fills a rectangle and Eraser (E) clears cells.'),
        (co(7, C('ide', cls='tool-group', nth=1), 'bottom', BOT), 'Scope',
         'Target Cells paints which cells are active and priority; Cell Groups assigns cells to the group picked in the right panel.'),
        (co(8, C('ide', cls='tool-group', nth=2), 'bottom', BOT, along=925), 'Mark as',
         'Paint cells as Active (they become trials) or Priority (they always run, even under a trial limit). Click a colour dot to change it.'),
        (co(9, C('ide', cls='tool-group--end'), 'bottom', BOT, along=1150), 'Overlays',
         'Show or hide the painted cells, the grid lines and the cell coordinates on the stage.'),
    ], split=[5], crop=[400, 120, 896, 148], place=dict(x=0.95, y=3.05, w=8.0))

    # ---- How do I Paint Active Cells?
    top_shelf = union(*[rect(r) for r in X['topShelf']])
    bottom_shelf = union(*[rect(r) for r in X['bottomShelf']])
    out += step_slides('active', 'How do I Paint Active Cells?', [
        ('Under **TOOL**, click the **Box** (or press **M**).',
         'active-box.png', pad(C('active-box', s='Box'), 3), 'bottom', 318),
        ('Under **MARK AS**, select **Active**. Every active cell becomes a trial.',
         'active-mark.png', pad(union(C('active-mark', prefix='Change the Active colour', t='label'),
                                      C('active-mark', prefix='Paint cells Active')), 3), 'bottom', 318),
        ('Drag a box over each product on the top shelf. The cells it covers turn the **Active** colour.',
         'active-top.png', pad(top_shelf, 2), 'left', 466),
        ('Do the same for the bottom shelf. The cell count and the **Summary** update as you paint.',
         'active-bottom.png', pad(bottom_shelf, 2), 'left', 466),
    ])

    # ---- How do I Paint Priority Cells?
    logo = X['logo']
    cells = [523, 371, 123, 68]          # the 4x3 block of cells the logo strokes cover
    out += step_slides('prio', 'How do I Paint Priority Cells?', [
        ('Under **TOOL**, click the **Brush** (or press **B**).',
         'prio-brush.png', pad(C('prio-brush', s='Brush'), 3), 'bottom', 318),
        ('Under **MARK AS**, select **Priority**.',
         'prio-mark.png', pad(union(C('prio-mark', prefix='Change the Priority colour', t='label'),
                                    C('prio-mark', prefix='Paint cells Priority')), 3), 'bottom', 318),
        ('Drag across the cells you want to mark, such as a logo. They turn the **Priority** colour. '
         'Priority cells always run, even when a trial limit is set.',
         'prio-paint.png', cells, 'left', 440),
    ])

    # ---- How do I Set the Trials and the Explicit Round?
    out += step_slides('trials', 'How do I Set the Trials and the Explicit Round?', [
        ('Enter the most trials the stimulus should run in **Trials**, e.g. **50**. The line below says how they are chosen: priority cells first, the rest at random.',
         'trials.png', [108, 536, 265, 72], 'right', 470),
        ('Switch on **Explicit phase** to have respondents rate this stimulus after the main round.',
         'explicit.png', [108, 610, 265, 58], 'right', 470),
    ])

    # ---- How do I Create Cell Groups?
    dialog = [634, 306, 332, 290]
    out += step_slides('groups', 'How do I Create Cell Groups?', [
        ('Under **SCOPE**, select **Cell Groups**. Keep the **Box** tool for drawing over each product.',
         'groups-scope.png', pad(C('groups-scope', prefix='Assign cells to a group', t='button'), 3), 'bottom', 318),
        ('In the **Cell Groups** panel, click **+ New group**.',
         'groups-scope.png', pad(C('groups-scope', s='Create a new cell group'), 3), 'left', 1250),
        ('Enter a **Name** for the group, e.g. **Chippy**. A colour is picked for you; click it to choose another.',
         'groups-named.png', pad(union(C('groups-named', s='Name', t='label'), C('groups-named', s='Choose Colour')), 4), 'left', 560),
        ('Click **Create group**.',
         'groups-named.png', pad(C('groups-named', s='Create the group'), 3), 'bottom', 660),
        ('Drag a box over the product to put its cells in the group, then click **Done** in the panel.',
         'groups-first.png', pad(rect(X['topShelf'][0]), 2), 'left', 466),
        ('Repeat for each product. The panel lists every group with its colour and cell count.',
         'groups-all.png', C('groups-all', id='tour-cell-groups'), 'left', 1250),
    ])

    # ---- Understanding the Target View (strip + a band of the stage)
    TOP, BOT, LEFT = 72, 420, 348
    out += overview('target', 'Understanding the Target View', 'target.png', [
        (co(1, C('target', cls='bar-group', nth=0), 'left', LEFT), 'Target icon',
         'Chooses the icon set: the target respondents search for, and the distractor icon repeated around it.'),
        (co(2, C('target', cls='bar-group', nth=1), 'top', TOP), 'Size',
         'The size of the target and distractor icons.'),
        (co(3, C('target', cls='bar-group', nth=2), 'top', TOP), 'Spacing',
         'The gap between the target and the distractors around it.'),
        (co(4, C('target', cls='bar-group', nth=3), 'top', TOP), 'Target',
         'How strongly the target shows. The swatch previews it.'),
        (co(5, C('target', cls='bar-group', nth=4), 'left', LEFT), 'Distractors',
         'How strongly the distractors show.'),
        (co(6, C('target', cls='bar-group--end'), 'bottom', BOT), 'Configure',
         'Opens the Configure Icons library, where icon sets are added, edited and switched on or off.'),
        (co(7, C('target', s='Reset target settings'), 'top', TOP), 'Reset',
         'Restores the target settings to their defaults.'),
    ], split=[], crop=[400, 120, 896, 250], place=dict(x=0.95, y=2.45, w=8.0))

    # ---- How do I Choose the Target?
    out += step_slides('choose', 'How do I Choose the Target?', [
        ('Under **EDITING**, click **Target**. The stage shows the target among its distractors.',
         'target-tab.png', pad(C('target-tab', prefix='The target and its distractors'), 2), 'right', 760),
        ('Open the target list and pick an icon, e.g. **Crosscut**.',
         'target-picker.png', pad(C('target-picker', prefix='Crosscut Smile', t='div'), 3), 'right', 650),
        ('Adjust the **Size**, **Spacing**, and how strongly the **Target** and **Distractors** show, e.g. 50% each.',
         'target-set.png', C('target-set', id='tour-target-bar'), 'bottom', 330),
    ])

    # ---- Understanding the Configure Icons Pop-up Modal (opened from the Target view's Configure)
    IL, IR = 400, 1200
    out += overview('icons', 'Understanding the Configure Icons Pop-up Modal', 'configure-icons.png', [
        (co(1, C('configure-icons', s='Close', cls='ide-modal-close'), 'right', IR), 'Close (X) icon',
         'Closes the dialog.'),
        (co(2, [496, 194, 606, 22], 'left', IL), 'Built-in Sets',
         'The icon sets that come with IMPACT. The number is how many there are.'),
        (co(3, [516, 242, 132, 62], 'left', IL), 'Target \u203a Distractor',
         'Each set\u2019s target icon (T), and the distractor icon (D) repeated around it.'),
        (co(4, [982, 256, 104, 34], 'right', IR), 'Active',
         'Switches a set on or off. Only active sets can be chosen in the Target view.'),
        (co(5, C('configure-icons', s='Add Custom Icon Set'), 'left', IL), 'Add Custom Icon Set',
         'Builds a set of your own from icons, shapes, a colour palette or your own images.'),
        (co(6, [498, 770, 98, 24], 'left', IL), 'Count',
         'How many sets there are, and how many are active.'),
        (co(7, C('configure-icons', s='Done', t='button'), 'right', IR), 'Done',
         'Closes the dialog. Changes are kept as you make them.'),
    ], split=[], crop=[454, 70, 692, 764], place=dict(x=1.4, y=1.70, h=5.0))

    # ---- Understanding the Instructions Side Panel (two crops of the scrolling list)
    L, R = 26, 470
    rows = lambda state, *names: union(*[next(e['b'] for e in C.c[state] if e['t'] == 'div' and e['s'].startswith(n)) for n in names])
    flow = pad(rows('instructions', 'Welcome Message', 'Explicit Round'), 3)
    warnings = pad(rows('instructions', 'Too Slow', 'Selection Error'), 3)
    system = pad(rows('instructions-2', 'Screenout Message', 'Saving Failed'), 3)
    others = pad(rows('instructions-2', 'Others'), 3)
    welcome = rows('instructions', 'Welcome Message')
    ins_a = [
        (co(1, C('instructions', s='Close Instructions panel'), 'right', R), 'Close (X) icon',
         'Closes the Instructions side panel.'),
        (co(2, flow, 'left', L), 'Flow',
         'The screens respondents read as they move through the test: Welcome Message, Practice Round, Main Round and Explicit Round.'),
        (co(3, welcome, 'right', R, hl=False, along=welcome[1] + 32), 'Screen',
         'Each row shows the screen’s name and its opening words. Click it to edit the screen. [[Learn more|welcome-1]]'),
        (co(4, warnings, 'left', L), 'Warnings',
         'Shown when a respondent is too slow (Too Slow) or appears to be selecting at random (Selection Error).'),
    ]
    ins_b = [
        (co(5, system, 'left', L), 'System',
         'The messages around the test: screened out, complete, saving and a failed save.'),
        (co(6, others, 'left', L), 'Global – Others',
         'Shared text used throughout the test, such as loading messages, labels and the round banners.'),
    ]
    out.append(dict(key='instructions-1', title='Understanding the Instructions Side Panel', shot='instructions.png',
                    crop=PANEL_CROP, place=PANEL_PLACE, callouts=[c for c, _, _ in ins_a],
                    descs=describe([(c[0], l, t) for c, l, t in ins_a])))
    out.append(dict(key='instructions-2', title='Understanding the Instructions Side Panel', shot='instructions-2.png',
                    crop=PANEL_CROP, place=PANEL_PLACE, callouts=[c for c, _, _ in ins_b],
                    descs=describe([(c[0], l, t) for c, l, t in ins_b])))

    # ---- Understanding the Instruction Editor (a screen opened from the list)
    E_ = 'ins-open'
    out += overview('editor', 'Understanding the Instruction Editor', 'ins-open.png', [
        (co(1, C(E_, s='Back to instructions'), 'left', L), 'Back',
         'Returns to the list of instruction screens.'),
        (co(2, C(E_, s='Close Instructions panel'), 'right', R), 'Close (X) icon',
         'Closes the Instructions side panel.'),
        (co(3, union(C(E_, s='Bold', nth=0), C(E_, s='Justify'), C(E_, prefix='Insert this test')), 'left', L), 'Toolbar',
         'Bold, italic, underline, text colour, alignment, subscript and superscript; insert a picture from the gallery, or this test\u2019s target or distractor.'),
        (co(4, pad(next(e['b'] for e in C.c[E_] if 'ProseMirror' in e['c'].split()), 4), 'right', R), 'Content',
         'The message itself. The stage shows it as respondents will see it while you type.'),
        (co(5, union(C(E_, s='Insert Target here'), C(E_, s='Insert Distractor here')), 'left', L), 'Target / Distractor',
         'Puts a picture of this test\u2019s target or distractor into the text, so the message can show it rather than describe it. You can also type @.'),
        (co(6, union(C(E_, s='Bold', nth=1), pad(next(e['b'] for e in C.c[E_] if 'ProseMirror' in e['c'].split() and e['s'] == 'START'), 4)), 'right', R), 'Button Text',
         'The label on the screen\u2019s button, e.g. START.'),
        (co(7, C(E_, s='0', t='input'), 'left', L), 'Button Delay',
         'How long, in milliseconds, the button stays disabled, so respondents read the message before moving on.'),
        (co(8, [112, 622, 267, 46], 'right', R), 'Box Width',
         'The width of the message card, as a percentage of the screen.'),
        (co(9, union(C(E_, s='Previous', t='button'), [251, 812, 129, 36]), 'left', L), 'Previous / Next',
         'Moves to the previous or next instruction screen.'),
    ], split=[5], crop=PANEL_CROP, place=PANEL_PLACE)

    # ---- How do I Edit the Welcome Message?
    editor = next(e['b'] for e in C.c['ins-edited'] if 'ProseMirror' in e['c'].split())
    out += step_slides('welcome', 'How do I Edit the Welcome Message?', [
        ('Click **Instructions** in the side menu.',
         'ins-rail.png', pad(C('ins-rail', s='Instructions', t='button'), -2), 'right', 150),
        ('Under **FLOW**, click **Welcome Message**.',
         'ins-list.png', pad(rows('instructions', 'Welcome Message'), 2), 'right', 450),
        ('Type your message in **Content**. The stage shows the screen as respondents will see it; use **Next** to move on to the next screen.',
         'ins-edited.png', pad(editor, 6), 'right', 450),
    ])

    # ---- Understanding the Settings Side Panel (Timing, then Hints)
    set_a = [
        (co(1, C('settings', s='Close Settings panel'), 'right', R), 'Close (X) icon',
         'Closes the Settings side panel.'),
        (co(2, union(C('settings', s='Timing', t='button'), C('settings', prefix='Reset Timing')), 'right', R, along=155), 'Timing',
         'Collapses or expands the section. The circular arrow resets every timing to the standard pace.'),
        (co(3, [117, 185, 255, 86], 'left', L), 'Preset',
         'Fast, Standard or Slow: a starting point for the four values below, which you can then fine-tune.'),
        (co(4, [125, 276, 242, 127], 'right', R), 'Inter-stimulus',
         'The blank pause between one stimulus and the next, in milliseconds.'),
        (co(5, [125, 412, 242, 127], 'left', L), 'Inter-trial',
         'The pause between one trial ending and the next starting, in milliseconds.'),
        (co(6, [125, 549, 242, 127], 'right', R), 'Countdown',
         'The 3–2–1 countdown shown before a round begins, in seconds.'),
        (co(7, [125, 685, 242, 127], 'left', L), 'Timeout warning',
         'How long a respondent can be idle before the Too Slow warning appears, in seconds.'),
    ]
    hints = union(C('settings-hints', s='Hint on the practice round'), C('settings-hints', s='Hint on the main round'))
    set_b = [
        (co(8, union(C('settings-hints', s='Hints', t='button'), C('settings-hints', prefix='Reset Hints')), 'right', R, along=214), 'Hints',
         'A hint points respondents at the target for a few seconds. The circular arrow resets hints to the practice round only.'),
        (co(9, [125, 268, 247, 110], 'left', L), 'Practice round',
         'Switch the hint on or off for the practice round, and set how many seconds it waits before showing.'),
        (co(10, [125, 400, 247, 60], 'left', L), 'Main round',
         'Switch the hint on or off for the main round.'),
    ]
    out.append(dict(key='settings-1', title='Understanding the Settings Side Panel', shot='settings.png',
                    crop=PANEL_CROP, place=PANEL_PLACE, callouts=[c for c, _, _ in set_a],
                    descs=describe([(c[0], l, t) for c, l, t in set_a])))
    out.append(dict(key='settings-2', title='Understanding the Settings Side Panel', shot='settings-hints.png',
                    crop=PANEL_CROP, place=PANEL_PLACE, callouts=[c for c, _, _ in set_b],
                    descs=describe([(c[0], l, t) for c, l, t in set_b])))

    # ---- Understanding the Test Flow Side Panel
    node = lambda name: next(e['b'] for e in C.c['testflow']
                             if 'vue-flow__node' in e['c'].split() and e['s'].startswith(name))
    out += overview('testflow', 'Understanding the Test Flow Side Panel', 'testflow.png', [
        (co(1, C('testflow', s='Close Test Flow panel'), 'right', R), 'Close (X) icon',
         'Closes the Test Flow side panel.'),
        (co(2, node('Participant arrives'), 'left', L), 'Participant arrives',
         'Where every respondent starts: by opening the test link.'),
        (co(3, C('testflow', s='Welcome', t='input'), 'right', R), 'Round switches',
         'Switch the Welcome, Practice or Main step off and respondents skip past it. A skipped step is dimmed and the path runs around it.'),
        (co(4, union(node('Practice round'), node('Main round')), 'left', L), 'Practice / Main round',
         'How many stimuli and trials each round runs.'),
        (co(5, node('Explicit round'), 'right', R), 'Explicit round',
         'Respondents rate the stimuli marked for it. Switching it off clears those marks; switching it on restores them.'),
        (co(6, union(node('Saving results'), node('Complete')), 'right', R), 'Saving results / Complete',
         'The answers are saved, retrying if the save fails, and the respondent is then redirected back.'),
        (co(7, union(*[e['b'] for e in C.c['testflow'] if 'vue-flow__controls-button' in e['c'].split()]), 'left', L), 'Zoom controls',
         'Zoom the diagram in or out, or fit it to the panel.'),
    ], split=[], crop=PANEL_CROP, place=PANEL_PLACE)

    # ---- How do I Switch a Round Off?
    practice_node = next(e['b'] for e in C.c['round-off'] if 'vue-flow__node' in e['c'].split() and e['s'].startswith('Practice round'))
    out += step_slides('roundoff', 'How do I Switch a Round Off?', [
        ('Click **Test Flow** in the side menu.',
         'ide.png', pad(C('ide', s='Test Flow', t='button'), -2), 'right', 150),
        ('Click the switch on the round respondents should skip, e.g. **Practice round**.',
         'testflow.png', pad(C('testflow', s='Practice round', t='input'), 4), 'right', 470),
        ('The round is dimmed and marked **Off \u2013 skipped**, and the path runs around it. Save to keep the change; click the switch again to turn the round back on.',
         'round-off.png', pad(practice_node, 3), 'right', 470),
    ])

    # ---- Understanding the Styles Panel (right panel: the tab, then each section open on its own)
    ST_CROP, ST_PLACE = [1308, 244, 284, 652], dict(x=3.6, y=1.70, h=5.0)
    SL, SR = 1250, 1650
    head = lambda state, name: C(state, s=name, t='button')
    out += overview('styles', 'Understanding the Styles Panel', 'styles.png', [
        (co(1, C('styles', s='Panel sections'), 'right', SR), 'Config / Styles',
         'The right panel\u2019s two tabs. Styles sets how the test looks; every change shows on the stage straight away.'),
        (co(2, head('styles', 'Theme Palette'), 'left', SL), 'Theme Palette',
         'The small set of colours the whole test follows. [[Learn more|styles-palette]]'),
        (co(3, head('styles', 'Page Background'), 'right', SR), 'Page Background',
         'The colour, and an optional image, behind the stimulus and every instruction screen. [[Learn more|styles-background]]'),
        (co(4, head('styles', 'Radius & Border'), 'left', SL), 'Radius & Border',
         'The corners, outline and shadow of the instruction card and its buttons. [[Learn more|styles-radius]]'),
        (co(5, head('styles', 'Typography'), 'right', SR), 'Typography',
         'The font, size and line spacing of every message. [[Learn more|styles-typography]]'),
    ], split=[], crop=ST_CROP, place=ST_PLACE)

    P_ = 'styles-palette'
    out += overview('styles-palette', 'Understanding the Theme Palette', 'styles-palette.png', [
        (co(1, union(C(P_, s='Instruction card fill'), C(P_, s='Text colour')), 'left', SL), 'Base surfaces',
         '100 is the instruction card\u2019s fill, 200 the page background behind the grid, 300 the border colour; A is the text colour.'),
        (co(2, union(C(P_, s='Primary fill'), C(P_, s='Primary text')), 'left', SL), 'Primary',
         'The instruction button, the round banner, the countdown and the hint. The first swatch is the fill, A the text on it.'),
        (co(3, union(C(P_, s='Hover fill'), C(P_, s='Hover text')), 'right', SR), 'Hover',
         'The instruction button while it is hovered or pressed. Follows Primary until you set it.'),
        (co(4, union(C(P_, s='Neutral fill'), C(P_, s='Neutral text')), 'left', SL), 'Neutral',
         'The instruction button while it is disabled, before its Button Delay has passed.'),
        (co(5, union(C(P_, prefix='Choose Success'), C(P_, prefix='Choose Error')), 'right', SR), 'Status colours',
         'The flash after a respondent clicks: Success on the target, Error on a miss. Feedback is always on; only its colours change.'),
        (co(6, [1336, 738, 226, 156], 'left', SL), 'Where primary appears',
         'A preview of everything Primary colours: the round banner, the countdown, the hint and the buttons.'),
    ], split=[], crop=ST_CROP, place=ST_PLACE)

    B_ = 'styles-background'
    out += overview('styles-background', 'Understanding the Page Background', 'styles-background.png', [
        (co(1, [1336, 424, 225, 80], 'left', SL), 'Preview',
         'Shows the background as it will look.'),
        (co(2, C(B_, prefix='Choose Background colour'), 'right', SR), 'Colour',
         'The solid colour behind the stimulus grid and every instruction screen. Click it to pick another.'),
        (co(3, C(B_, s='Upload image\u2026', t='label'), 'left', SL), 'Image',
         'An optional picture layered over the colour.'),
        (co(4, C(B_, prefix='Image position', t='label'), 'right', SR), 'Image position',
         'Where the image sits: centre, an edge or a corner.'),
        (co(5, C(B_, prefix='Image fit', t='label'), 'left', SL), 'Image fit',
         'Fill (cover), Fit (contain), Stretch, or Original (tile) for a repeating pattern. Image repeat, Image opacity and Brightness follow below.'),
    ], split=[], crop=ST_CROP, place=ST_PLACE)

    R_ = 'styles-radius'
    out += overview('styles-radius', 'Understanding Radius & Border', 'styles-radius.png', [
        (co(1, union(C(R_, prefix='Square corner', nth=0), C(R_, prefix='Fully rounded corner', nth=0)), 'left', SL), 'Instruction card',
         'The corner shape of the welcome, instruction, warning and completion screens.'),
        (co(2, union(C(R_, prefix='Square corner', nth=1), C(R_, prefix='Fully rounded corner', nth=1)), 'left', SL), 'Buttons',
         'The corner shape of START, CONTINUE and every other instruction button.'),
        (co(3, [1336, 680, 226, 62], 'right', SR), 'Card border',
         'An outline around the instruction card, in the base-300 colour. 0 leaves it borderless.'),
        (co(4, [1336, 785, 226, 60], 'left', SL), 'Card shadow',
         'How far the instruction card lifts off the background. 0 sits it flat.'),
    ], split=[], crop=ST_CROP, place=ST_PLACE)

    T_ = 'styles-typography'
    out += overview('styles-typography', 'Understanding Typography', 'styles-typography.png', [
        (co(1, C(T_, prefix='Font family', t='label'), 'left', SL), 'Font family',
         'The font of every instruction and message.'),
        (co(2, C(T_, s='Font size', t='label'), 'left', SL), 'Font size',
         'In vmin, so the text scales with the respondent\u2019s screen rather than being fixed in pixels.'),
        (co(3, C(T_, s='Line height', t='label'), 'right', SR), 'Line height',
         'The spacing between lines of text.'),
        (co(4, [1336, 698, 226, 84], 'right', SR), 'Preview',
         'Sample text in the chosen font, size and line height.'),
    ], split=[], crop=ST_CROP, place=ST_PLACE)

    # ---- Understanding the Advanced Side Panel
    out += overview('advanced', 'Understanding the Advanced Side Panel', 'advanced.png', [
        (co(1, union(C('advanced', prefix='Custom stylesheet'), C('advanced', prefix='Custom script')), 'left', L), 'styles.css / script.js',
         'Switch between the custom stylesheet and the custom script.'),
        (co(2, C('advanced', s='Nothing to clear'), 'right', R), 'Clear',
         'Empties the open file, after asking you to confirm.'),
        (co(3, [113, 174, 266, 544], 'left', L), 'Code editor',
         'Write CSS or JavaScript here. The stylesheet is applied after the theme, so it can change anything the Styles panel cannot reach.'),
        (co(4, [113, 722, 266, 22], 'right', R), 'Status bar',
         'The file type, its length, and whether it is in use.'),
        (co(5, [113, 758, 266, 86], 'left', L), 'Note',
         'A reminder of where the code runs: in the respondent’s browser, on the survey page.'),
    ], split=[], crop=PANEL_CROP, place=PANEL_PLACE)

    # ---- How do I Save the Test?
    out += step_slides('save', 'How do I Save the Test?', [
        ('**Unsaved changes** appears beside **SAVE** whenever the test has edits that are not saved yet. Click **SAVE**.',
         'save-before.png', pad(C('save-before', prefix='Unsaved changes'), 3), 'bottom', 300),
        ('Once saved, the note clears. Every save is kept as a version you can go back to. [[Learn more|restore-1]]',
         'save-after.png', pad(C('save-after', id='tour-save'), 3), 'bottom', 300),
    ])

    # ---- How do I Preview the Test?
    out += step_slides('preview', 'How do I Preview the Test?', [
        ('Click **Preview** in the side menu. Save first: the preview runs the saved test.',
         'preview-rail.png', pad(C('preview-rail', s='Preview', t='button'), -2), 'right', 150),
        ('The test opens in a new tab, starting with the welcome screen, exactly as a respondent will see it.',
         'preview-engine.png', pad(union(C('preview-engine', prefix='Welcome to IMPACT', t='div'), C('preview-engine', s='START', t='button')), 16), 'top', 230),
    ])

    # ---- How do I Preview on Another Device?
    D_ = 'device-mobile'
    options = [e['b'] for e in C.c['device-list'] if e['t'] == 'button' and e['b'][0] == 1345 and e['b'][1] + e['b'][3] <= 510]   # visible part of the scrolling list
    out += step_slides('device', 'How do I Preview on Another Device?', [
        ('Under **Device View**, click **Tablet**. The stage shows the test at a tablet\u2019s screen size.',
         'device-tablet.png', pad(C('device-tablet', s='Tablet preview'), 3), 'left', 1250),
        ('Click **Mobile** for a phone.',
         D_ + '.png', pad(C(D_, s='Mobile preview'), 3), 'left', 1250),
        ('Open the list below to choose a model. Each one is listed with its screen size.',
         'device-list.png', pad(union(C('device-list', prefix='iPhone 16/17', cls='ide-field'), *options), 3), 'left', 1250),
        ('Click the rotate button to turn the device on its side.',
         D_ + '.png', pad(C(D_, s='Switch to landscape'), 3), 'bottom', 300),
    ])

    # ---- Understanding the AI Assistant (the dock's welcome screen)
    A_ = 'assistant'
    AL, AR = 470, 1230
    out += overview('assistant', 'Understanding the AI Assistant', 'assistant.png', [
        (co(1, C(A_, s='Toggle chat history'), 'left', AL), 'Chat history',
         'Your earlier conversations with the assistant. Click one to carry on where you left off.'),
        (co(2, [792, 248, 114, 32], 'top', 200), 'AI Assistant',
         '\u201cOnline\u201d means it is ready to answer.'),
        (co(3, union(C(A_, s='Assistant actions'), C(A_, s='Minimise')), 'right', AR), 'Menu / Minimise',
         'More options, or shrink the assistant back to its launcher.'),
        (co(4, C(A_, s='Start a conversation'), 'left', AL), 'Start a conversation',
         'Opens the chat, with suggested questions and actions to start from.'),
        (co(5, [656, 596, 382, 78], 'right', AR), 'Ask',
         'Questions about this test \u2013 its rounds, stimuli, trials and settings \u2013 and about IMPACT itself.'),
        (co(6, [656, 686, 382, 78], 'left', AL), 'Act',
         'Ask it to build or change your test. Every change is shown as a proposal first and only applied when you approve it.'),
        (co(7, [558, 824, 580, 22], 'right', AR), 'Note',
         'The assistant can make mistakes, so review a proposal before applying it. Using it means agreeing to the terms and conditions.'),
    ], split=[], crop=[528, 236, 640, 624], place=dict(x=1.5, y=1.85, h=4.85))

    # ---- How do I Restore a Previous Version?  (last: it undoes saved work)
    row = next(e['b'] for e in C.c['recent'] if 'rc-row-wrap' in e['c'].split())
    out += step_slides('restore', 'How do I Restore a Previous Version?', [
        ('Click the **More actions** (⋮) menu beside **SAVE**.',
         'ide.png', pad(C('ide', s='More actions', t='label'), 3), 'bottom', 320),
        ('Click **Recent changes**.',
         'kebab.png', C('kebab', prefix='Restore the setup', t='button'), 'left', 900),
        ('The **Recent Changes** panel lists every saved version, newest first. Click a version to see what changed in it.',
         'recent.png', row, 'left', 1095),
        ('Each change shows its old and new value. Click **RESTORE THIS VERSION**, then confirm, to put the test back to how it was before that save.',
         'recent-detail.png', C('recent-detail', s='RESTORE THIS VERSION', t='button'), 'left', 1095),
    ])
    return out
