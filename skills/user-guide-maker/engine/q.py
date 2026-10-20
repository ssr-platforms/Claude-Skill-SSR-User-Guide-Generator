"""Look up controls in the capture dumps, to place callouts.

  python3 q.py <screenshots dir> <state> [text] [x0 y0 x1 y1]

Prints every visible control captured in <state> (a screenshot's name) whose label,
placeholder, tour hook or row tag contains [text], optionally only those inside the
box x0,y0 - x1,y1 (CSS px of the 1600x900 viewport). Each line: tag, role, hook, row,
label, box [x, y, w, h], classes, id.
"""
import glob, json, os, sys

shots, state = sys.argv[1], sys.argv[2]
sub = sys.argv[3] if len(sys.argv) > 3 else ''
area = list(map(int, sys.argv[4:8])) if len(sys.argv) > 7 else None
d = {}
for f in glob.glob(os.path.join(shots, '*controls.json')):
    d.update(json.load(open(f))['controls'])
if state not in d:
    sys.exit(f'no state {state!r}; captured: ' + ', '.join(sorted(d)))
for e in d[state]:
    b = e['b']
    hay = ' '.join(str(e.get(k, '')) for k in ('s', 'ph', 'tour', 'row')).lower()
    if sub and sub.lower() not in hay:
        continue
    if area and not (b[0] >= area[0] and b[1] >= area[1] and b[0] + b[2] <= area[2] and b[1] + b[3] <= area[3]):
        continue
    if e['t'] in ('g', 'path', 'svg') and not e.get('tour'):
        continue
    print(e['t'], e.get('role') or '-', e.get('tour') or '-', e.get('row') or '-', repr(e['s'][:60]), b,
          e.get('cls', e.get('c', '')), e.get('id', ''))
