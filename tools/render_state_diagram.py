"""Render this project's small UML state diagram from its PlantUML source.

Requires Pillow; no PlantUML server, Java, or network is used.
The positions below define this diagram's layout; labels come from the source.
"""
from pathlib import Path
import math
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BOXES = {
    'IDLE': (660, 155, 940, 275),
    'RUN': (1160, 425, 1460, 545),
    'SLEEP': (140, 425, 440, 545),
    'AUTO_RUN': (590, 775, 1010, 965),
}
ROUTES = {
    ('[*]', 'IDLE'): ([(800, 95), (800, 155)], (815, 110)),
    ('IDLE', 'RUN'): ([(940, 195), (1310, 195), (1310, 425)], (1040, 160)),
    ('RUN', 'IDLE'): ([(1160, 465), (1050, 465), (1050, 245), (940, 245)], (1060, 300)),
    ('IDLE', 'SLEEP'): ([(660, 195), (290, 195), (290, 425)], (325, 160)),
    ('SLEEP', 'RUN'): ([(440, 495), (1160, 495)], (630, 455)),
    ('IDLE', 'AUTO_RUN'): ([(800, 275), (800, 775)], (815, 650)),
    ('RUN', 'AUTO_RUN'): ([(1310, 545), (1310, 870), (1010, 870)], (1170, 745)),
    ('SLEEP', 'AUTO_RUN'): ([(290, 545), (290, 870), (590, 870)], (305, 745)),
    ('AUTO_RUN', 'IDLE'): ([(590, 820), (510, 820), (510, 320), (730, 320), (730, 275)], (515, 585)),
    ('AUTO_RUN', 'RUN'): ([(1010, 920), (1510, 920), (1510, 505), (1460, 505)], (1220, 945)),
}


def font(size, bold=False):
    path = Path('C:/Windows/Fonts/malgunbd.ttf' if bold else 'C:/Windows/Fonts/malgun.ttf')
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)


def render():
    source = (ROOT / 'state_diagram.puml').read_text(encoding='utf-8')
    edges = re.findall(r'^(\[\*\]|\w+) --> (\w+)(?: : (.*))?$', source, re.M)
    if {(a, b) for a, b, _ in edges} != set(ROUTES):
        raise ValueError('Update the layout when the UML connections change.')
    image = Image.new('RGB', (1600, 1180), '#f5f7fb')
    draw = ImageDraw.Draw(image)
    title = re.search(r'^title (.+)$', source, re.M).group(1)
    draw.text((55, 25), title, font=font(34, True), fill='#14243b')
    draw.ellipse((788, 72, 812, 96), fill='#14243b')
    for a, b, label in edges:
        points, position = ROUTES[a, b]
        draw.line(points, fill='#526783', width=3, joint='curve')
        x, y = points[-1]
        px, py = points[-2]
        theta = math.atan2(y - py, x - px)
        triangle = [(x, y)] + [(x - 14 * math.cos(theta + d), y - 14 * math.sin(theta + d)) for d in (-0.45, 0.45)]
        draw.polygon(triangle, fill='#526783')
        if label:
            if a == 'AUTO_RUN':
                label = label.replace(' 그리고 ', '\n그리고 ')
            if a == 'RUN' and b == 'IDLE':
                label = '이동 방향키\n입력 없음'
            bounds = draw.multiline_textbbox(position, label, font=font(20))
            draw.rectangle((bounds[0] - 5, bounds[1] - 4, bounds[2] + 5, bounds[3] + 4), fill='#f5f7fb')
            draw.multiline_text(position, label, font=font(20), fill='#203853', spacing=6)
    colors = {'IDLE': '#dfeafa', 'RUN': '#ddf3e9', 'SLEEP': '#ece3fa', 'AUTO_RUN': '#fff0d0'}
    for name, rect in BOXES.items():
        draw.rounded_rectangle(rect, radius=18, fill=colors[name], outline='#426180', width=3)
        alias = re.search(rf'^state "(.+)" as {name}$', source, re.M)
        draw.text(((rect[0] + rect[2]) / 2, rect[1] + 15), alias.group(1) if alias else name,
                  anchor='mt', font=font(24, True), fill='#14243b')
        match = re.search(rf'note bottom of {name}\n(.*?)\nend note', source, re.S)
        lines = [s.strip() for s in match.group(1).splitlines()] if match else []
        # Long AUTO_RUN notes are displayed below the graph, keeping the state readable.
        content = '\n'.join(lines[:1] if name == 'AUTO_RUN' else lines)
        draw.multiline_text((rect[0] + 18, rect[1] + 58), content, font=font(21), fill='#203853', spacing=7)
        if name == 'AUTO_RUN':
            draw.multiline_text((rect[0] + 18, rect[1] + 95), '가속 → 감속 → 정지\n경계에서는 방향만 반전', font=font(20), fill='#203853', spacing=8)
    note = re.search(r'note bottom of AUTO_RUN\n(.*?)\nend note', source, re.S).group(1)
    lines = [s.strip() for s in note.splitlines()][2:]
    legend = re.search(r'legend bottom\n(.*?)\nendlegend', source, re.S).group(1)
    footer = '\n'.join(lines + [s.strip() for s in legend.splitlines()])
    draw.multiline_text((55, 1005), footer, font=font(20), fill='#31465e', spacing=8)
    output = ROOT / 'state_diagram.png'
    image.save(output)
    print(output)


if __name__ == '__main__':
    render()
