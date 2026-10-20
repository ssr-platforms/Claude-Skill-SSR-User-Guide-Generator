"""Contact sheets for reviewing screenshots or rendered slides.

  python3 sheet.py <images dir> <out prefix> [per sheet=9] [pattern=*.png]

Writes <out prefix>-001.jpg, -002.jpg ... with the images in name order, labelled,
three to a row, so a whole deck can be looked over in a few images.
"""
import glob, os, sys
from PIL import Image, ImageDraw

src, prefix = sys.argv[1], sys.argv[2]
per = int(sys.argv[3]) if len(sys.argv) > 3 else 9
pattern = sys.argv[4] if len(sys.argv) > 4 else '*.png'
files = sorted(glob.glob(os.path.join(src, pattern)))
W, H, cols = 640, 360, 3
out = []
for start in range(0, len(files), per):
    chunk = files[start:start + per]
    rows = -(-len(chunk) // cols)
    sheet = Image.new('RGB', (cols * W, rows * (H + 18)), 'white')
    dr = ImageDraw.Draw(sheet)
    for i, f in enumerate(chunk):
        im = Image.open(f).convert('RGB').resize((W, H))
        x, y = (i % cols) * W, (i // cols) * (H + 18)
        sheet.paste(im, (x, y + 18))
        dr.text((x + 4, y + 3), os.path.splitext(os.path.basename(f))[0], fill='black')
    name = f'{prefix}-{start // per + 1:03d}.jpg'
    sheet.save(name, quality=88)
    out.append(name)
print('\n'.join(out))
