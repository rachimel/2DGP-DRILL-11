"""Extract per-frame opaque bounds; Pillow is only needed to rebuild metadata."""
from pathlib import Path
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
image = Image.open(ROOT / 'animation_sheet.png')
bounds = {}
for bottom in (1, 101, 201, 301):
    top = image.height - bottom - 100
    bounds[str(bottom)] = [image.crop((1 + i * 100, top, 101 + i * 100, top + 100)).getbbox()
                           for i in range(8)]
(ROOT / 'sprite_bounds.json').write_text(json.dumps(bounds, indent=2) + '\n', encoding='utf-8')
