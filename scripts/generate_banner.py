from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1500
HEIGHT = 500
FRAME_COUNT = 20
FRAME_DURATION_MS = 90
OUTPUT = Path("assets/header_irontech.gif")

DARK = (2, 7, 15)
NAVY = (4, 15, 27)
RED = (255, 63, 46)
RED_SOFT = (170, 25, 22)
CYAN = (32, 214, 244)
BLUE = (76, 156, 255)
GOLD = (245, 179, 76)
WHITE = (240, 244, 248)
MUTED = (130, 159, 179)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

TITLE_FONT = ImageFont.truetype(FONT_BOLD, 86)
SUBTITLE_FONT = ImageFont.truetype(FONT_BOLD, 22)
FOOTER_FONT = ImageFont.truetype(FONT_MONO, 17)
PANEL_TITLE_FONT = ImageFont.truetype(FONT_BOLD, 15)
SMALL_FONT = ImageFont.truetype(FONT_MONO, 12)
METRIC_FONT = ImageFont.truetype(FONT_MONO, 13)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def center_text(draw: ImageDraw.ImageDraw, y: int, text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, ...]) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = (WIDTH - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)


def gradient_background() -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), DARK + (255,))
    draw = ImageDraw.Draw(image, "RGBA")
    for y in range(HEIGHT):
        ty = y / max(1, HEIGHT - 1)
        for x in range(0, WIDTH, 3):
            tx = x / max(1, WIDTH - 1)
            left = (2, 10, 19)
            middle = (4, 16, 30)
            right = (15, 8, 25)
            if tx < 0.62:
                k = tx / 0.62
                color = tuple(lerp(left[i], middle[i], k) for i in range(3))
            else:
                k = (tx - 0.62) / 0.38
                color = tuple(lerp(middle[i], right[i], k) for i in range(3))
            color = tuple(min(255, color[i] + int(8 * ty)) for i in range(3))
            draw.rectangle((x, y, x + 2, y), fill=color + (255,))

    # Subtle grid
    for x in range(0, WIDTH, 30):
        draw.line((x, 0, x, HEIGHT), fill=(65, 146, 190, 18), width=1)
    for y in range(0, HEIGHT, 30):
        draw.line((0, y, WIDTH, y), fill=(65, 146, 190, 18), width=1)
    for x in range(0, WIDTH, 120):
        draw.line((x, 0, x, HEIGHT), fill=(160, 90, 230, 13), width=1)
    for y in range(0, HEIGHT, 120):
        draw.line((0, y, WIDTH, y), fill=(160, 90, 230, 13), width=1)

    # Ambient glows
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse((-170, 70, 470, 520), fill=(0, 174, 230, 40))
    gd.ellipse((1030, -180, 1640, 380), fill=(130, 55, 235, 40))
    gd.ellipse((440, 35, 1060, 500), outline=(255, 46, 38, 23), width=16)
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    return Image.alpha_composite(image, glow)


def angular_frame(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int, int], width: int = 2, cut: int = 24) -> None:
    x1, y1, x2, y2 = box
    points = [
        (x1 + cut, y1),
        (x2 - cut, y1),
        (x2, y1 + cut),
        (x2, y2 - cut),
        (x2 - cut, y2),
        (x1 + cut, y2),
        (x1, y2 - cut),
        (x1, y1 + cut),
        (x1 + cut, y1),
    ]
    draw.line(points, fill=color, width=width, joint="curve")


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, accent: tuple[int, int, int] = CYAN) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=(2, 10, 19, 215), outline=accent + (75,), width=1)
    draw.line((x1 + 14, y1 + 30, x2 - 14, y1 + 30), fill=accent + (75,), width=1)
    draw.text((x1 + 15, y1 + 9), title, font=PANEL_TITLE_FONT, fill=accent + (235,))
    draw.line((x1 + 10, y1 + 4, x1 + 47, y1 + 4), fill=RED + (155,), width=2)
    draw.line((x2 - 60, y1 + 4, x2 - 10, y1 + 4), fill=GOLD + (110,), width=1)


def progress_bar(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, value: float, color: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((x, y, x + width, y + 7), radius=3, fill=(21, 44, 57, 220))
    draw.rounded_rectangle((x, y, x + int(width * value), y + 7), radius=3, fill=color + (235,))
    draw.line((x, y + 9, x + width, y + 9), fill=color + (40,), width=1)


def arc_segments(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, count: int, rotation: float, color: tuple[int, int, int], width: int, span: float = 18.0) -> None:
    cx, cy = center
    box = (cx - radius, cy - radius, cx + radius, cy + radius)
    for index in range(count):
        start = rotation + index * (360 / count)
        draw.arc(box, start=start, end=start + span, fill=color + (185,), width=width)


def ring_hud(draw: ImageDraw.ImageDraw, center: tuple[int, int], phase: float) -> None:
    cx, cy = center
    draw.ellipse((cx - 165, cy - 165, cx + 165, cy + 165), outline=(54, 178, 230, 45), width=2)
    draw.ellipse((cx - 137, cy - 137, cx + 137, cy + 137), outline=(255, 72, 55, 50), width=2)
    draw.ellipse((cx - 108, cy - 108, cx + 108, cy + 108), outline=(245, 179, 76, 45), width=1)
    arc_segments(draw, center, 154, 12, phase * 360, RED, 4, 13)
    arc_segments(draw, center, 126, 16, -phase * 260, CYAN, 3, 10)
    arc_segments(draw, center, 96, 10, phase * 190, GOLD, 2, 16)
    for index in range(36):
        angle = math.radians(index * 10 + phase * 110)
        r1 = 171
        r2 = 176 if index % 3 else 182
        x1 = cx + math.cos(angle) * r1
        y1 = cy + math.sin(angle) * r1
        x2 = cx + math.cos(angle) * r2
        y2 = cy + math.sin(angle) * r2
        draw.line((x1, y1, x2, y2), fill=(110, 200, 240, 70), width=1)


def reactor(draw: ImageDraw.ImageDraw, center: tuple[int, int], phase: float) -> None:
    cx, cy = center
    pulse = 0.5 + 0.5 * math.sin(phase * math.tau)
    glow_radius = 50 + int(8 * pulse)
    draw.ellipse((cx - glow_radius, cy - glow_radius, cx + glow_radius, cy + glow_radius), fill=(255, 58, 42, 25))
    draw.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=RED + (180,), width=3)
    draw.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=GOLD + (180,), width=2)
    arc_segments(draw, center, 40, 12, phase * 390, WHITE, 5, 12)
    arc_segments(draw, center, 28, 8, -phase * 500, RED, 4, 18)
    draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 235, 215, 255), outline=RED + (255,), width=3)


def waveform(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], phase: float) -> None:
    x1, y1, x2, y2 = box
    mid = (y1 + y2) / 2
    points: list[tuple[float, float]] = []
    for x in range(x1, x2 + 1, 4):
        local = (x - x1) / max(1, x2 - x1)
        signal = math.sin(local * 18 * math.pi + phase * math.tau * 2.0) * 8
        signal += math.sin(local * 47 * math.pi + phase * math.tau * 3.2) * 3
        points.append((x, mid + signal))
    draw.line(points, fill=RED + (225,), width=2)
    draw.line((x1, mid, x2, mid), fill=(68, 119, 145, 65), width=1)


def title_layer(phase: float, scan_x: int) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    # Clean center plate guarantees crisp text.
    angular_frame(draw, (315, 158, 1185, 347), RED + (100,), 2, 32)
    draw.rounded_rectangle((330, 169, 1170, 335), radius=12, fill=(2, 8, 16, 238), outline=(46, 210, 245, 45), width=1)

    title = "NAKNAKGEO"
    title_box = draw.textbbox((0, 0), title, font=TITLE_FONT, stroke_width=2)
    title_x = (WIDTH - (title_box[2] - title_box[0])) // 2
    title_y = 167

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    glow_alpha = 90 + int(40 * (0.5 + 0.5 * math.sin(phase * math.tau)))
    gd.text((title_x, title_y), title, font=TITLE_FONT, fill=RED + (glow_alpha,), stroke_width=3, stroke_fill=RED + (glow_alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    layer = Image.alpha_composite(layer, glow)
    draw = ImageDraw.Draw(layer, "RGBA")

    # Shadow + bright metallic main title.
    draw.text((title_x + 3, title_y + 4), title, font=TITLE_FONT, fill=(85, 7, 8, 210), stroke_width=2, stroke_fill=(95, 10, 8, 210))
    draw.text((title_x, title_y), title, font=TITLE_FONT, fill=(255, 243, 239, 255), stroke_width=2, stroke_fill=RED + (255,))

    # Light sweep clipped visually across title area.
    sweep = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep, "RGBA")
    for dx in range(-90, 91):
        alpha = int(48 * max(0.0, 1.0 - abs(dx) / 90))
        sd.rectangle((scan_x + dx, 172, scan_x + dx + 1, 255), fill=(255, 255, 255, alpha))
    sweep = sweep.filter(ImageFilter.GaussianBlur(7))
    layer = Image.alpha_composite(layer, sweep)
    draw = ImageDraw.Draw(layer, "RGBA")

    subtitle = "SOFTWARE ENGINEERING · AI SYSTEMS · INFRASTRUCTURE · AUTOMATION"
    center_text(draw, 273, subtitle, SUBTITLE_FONT, WHITE + (255,))
    draw.line((420, 311, 1080, 311), fill=RED + (205,), width=2)
    draw.line((535, 316, 965, 316), fill=CYAN + (115,), width=1)
    footer = "BUILDING RELIABLE SYSTEMS, AI TOOLS, AND INFRASTRUCTURE"
    center_text(draw, 323, footer, FOOTER_FONT, GOLD + (245,))
    return layer


def draw_side_panels(draw: ImageDraw.ImageDraw, phase: float) -> None:
    # Left status panel
    panel(draw, (34, 60, 282, 205), "SYSTEM STATUS")
    labels = [("CORE SYSTEMS", 1.00), ("AI MODULES", 0.98), ("NETWORK", 0.97), ("SECURITY", 1.00)]
    for index, (label, value) in enumerate(labels):
        y = 99 + index * 25
        draw.text((53, y), label, font=SMALL_FONT, fill=MUTED + (245,))
        progress_bar(draw, 151, y + 3, 82, value, CYAN if index != 1 else BLUE)
        draw.text((239, y - 1), f"{int(value * 100)}%", font=SMALL_FONT, fill=WHITE + (235,))

    # Left diagnostic panel
    panel(draw, (34, 220, 282, 367), "SYSTEM DIAGNOSTICS", RED)
    waveform(draw, (55, 268, 260, 323), phase)
    draw.text((53, 336), "SIGNAL STRENGTH", font=SMALL_FONT, fill=MUTED + (230,))
    progress_bar(draw, 53, 353, 180, 0.88, CYAN)
    draw.text((239, 347), "88%", font=SMALL_FONT, fill=WHITE + (230,))

    # Right metrics panel
    panel(draw, (1218, 60, 1466, 205), "CORE METRICS", CYAN)
    cx, cy = 1272, 130
    draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), outline=RED + (180,), width=5)
    draw.ellipse((cx - 29, cy - 29, cx + 29, cy + 29), outline=CYAN + (120,), width=2)
    draw.text((cx - 22, cy - 20), "94", font=ImageFont.truetype(FONT_BOLD, 31), fill=WHITE + (255,))
    draw.text((cx - 11, cy + 14), "/100", font=SMALL_FONT, fill=MUTED + (220,))
    metrics = [("PERFORMANCE", 0.94), ("EFFICIENCY", 0.91), ("RELIABILITY", 0.96), ("SCALABILITY", 0.93)]
    for index, (label, value) in enumerate(metrics):
        y = 91 + index * 27
        draw.text((1324, y), label, font=SMALL_FONT, fill=MUTED + (235,))
        progress_bar(draw, 1404, y + 4, 42, value, CYAN)

    # Right activity panel
    panel(draw, (1218, 220, 1466, 367), "ACTIVITY FEED", CYAN)
    events = [
        ("10:21:45", "SYSTEM CHECK"),
        ("10:22:11", "DEPLOYMENT"),
        ("10:23:07", "AI MODEL UPDATE"),
        ("10:24:32", "INFRASTRUCTURE SYNC"),
        ("10:25:18", "BACKUP COMPLETE"),
    ]
    for index, (timestamp, event) in enumerate(events):
        y = 260 + index * 20
        active = ((int(phase * FRAME_COUNT) + index) % 5) == 0
        dot = RED if active else CYAN
        draw.ellipse((1238, y + 4, 1242, y + 8), fill=dot + (240,))
        draw.text((1250, y), timestamp, font=SMALL_FONT, fill=MUTED + (220,))
        draw.text((1311, y), event, font=SMALL_FONT, fill=(87, 173, 204, 230))
        draw.text((1434, y), "OK", font=SMALL_FONT, fill=CYAN + (230,))


def draw_data_traces(draw: ImageDraw.ImageDraw, phase: float) -> None:
    # Bottom circuit rails
    for row, color in [(430, RED), (448, CYAN), (468, GOLD)]:
        offset = int((phase * 150) % 70)
        for x in range(-70 + offset, WIDTH, 70):
            draw.line((x, row, x + 30, row), fill=color + (110,), width=2)
            draw.rectangle((x + 36, row - 2, x + 41, row + 3), fill=color + (145,))

    # Moving data points
    for index in range(14):
        x = int((index * 117 + phase * 360) % WIDTH)
        y = 401 + (index % 3) * 11
        color = CYAN if index % 2 == 0 else RED
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color + (220,))


def make_frame(index: int, base: Image.Image) -> Image.Image:
    phase = index / FRAME_COUNT
    frame = base.copy()
    draw = ImageDraw.Draw(frame, "RGBA")

    # Outer premium frame and angular rails
    angular_frame(draw, (8, 8, WIDTH - 8, HEIGHT - 8), GOLD + (125,), 2, 32)
    angular_frame(draw, (18, 20, WIDTH - 18, HEIGHT - 20), RED + (95,), 1, 26)
    draw.line((70, 39, 360, 39), fill=RED + (145,), width=2)
    draw.line((WIDTH - 360, 39, WIDTH - 70, 39), fill=RED + (145,), width=2)

    # Center ring system
    ring_hud(draw, (750, 225), phase)
    reactor(draw, (750, 440), phase)
    draw_side_panels(draw, phase)
    draw_data_traces(draw, phase)

    # Tiny stars and blinking nodes
    random.seed(2026)
    for star_index in range(34):
        x = random.randint(20, WIDTH - 20)
        y = random.choice([random.randint(22, 56), random.randint(378, 480)])
        alpha = 65 + int(120 * (0.5 + 0.5 * math.sin(phase * math.tau + star_index * 0.8)))
        color = CYAN if star_index % 3 else RED
        draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=color + (alpha,))

    # Scan bar across the composition
    scan_x = int(285 + phase * 930)
    scan = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan, "RGBA")
    for dx in range(-95, 96):
        alpha = int(28 * max(0.0, 1.0 - abs(dx) / 95))
        sd.rectangle((scan_x + dx, 50, scan_x + dx + 1, 380), fill=RED + (alpha,))
    scan = scan.filter(ImageFilter.GaussianBlur(10))
    frame = Image.alpha_composite(frame, scan)
    frame = Image.alpha_composite(frame, title_layer(phase, scan_x))

    # Rounded transparent corners for a polished banner edge
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WIDTH - 1, HEIGHT - 1), radius=22, fill=255)
    frame.putalpha(mask)
    return frame


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = gradient_background()
    frames: list[Image.Image] = []
    for index in range(FRAME_COUNT):
        frame = make_frame(index, base)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
