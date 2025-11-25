from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import math
import os

# ────────────────────── Canvas & Colors ──────────────────────
W, H = 1600, 900
CENTER = (W // 2, H // 2)

BG_COLOR = (255, 255, 255)      # WHITE background
TEXT_COLOR = (20, 24, 28)

CENTER_FILL = (240, 245, 255)
CENTER_OUTLINE = (100, 130, 200)

NODE_CIRCLE = (230, 238, 255)   # light circle behind icons
NODE_BORDER = (120, 150, 210)

ARROW_COLOR = (120, 130, 150)

TITLE = "CI/CD Pipeline Overview"
SUBTITLE = "Fluxcd GitOps Pipeline with GitHub Actions"
CENTER_LABEL = "Application\nDeployment Pipeline"

ICONS_DIR = "icons"

# Steps around the circle (order matters)
STEPS = [
    {
        "label": "GitHub",
        "desc": "Repo & trigger",
        "icon": f"{ICONS_DIR}/github.png",
    },
    {
        "label": "Maven",
        "desc": "Build (Java 21, WAR)",
        "icon": f"{ICONS_DIR}/maven.png",
    },
    {
        "label": "Tests / CodeQL",
        "desc": "Unit tests &\nstatic analysis",
        "icon": f"{ICONS_DIR}/codeql.png",
    },
    {
        "label": "Nexus",
        "desc": "Artifact\nrepository",
        "icon": f"{ICONS_DIR}/nexus.png",
    },
    {
        "label": "SonarQube",
        "desc": "Code quality &\nQuality Gate",
        "icon": f"{ICONS_DIR}/sonarqube.png",
    },
    {
        "label": "Docker",
        "desc": "Image build &\nsecurity scan",
        "icon": f"{ICONS_DIR}/docker.png",
    },
    {
        "label": "GH Packages",
        "desc": "Container\nregistry",
        "icon": f"{ICONS_DIR}/gh-packages.png",
    },
    {
        "label": "Helm",
        "desc": "Chart\npackaging",
        "icon": f"{ICONS_DIR}/helm.png",
    },
    {
        "label": "FluxCD",
        "desc": "GitOps\ndeploy",
        "icon": f"{ICONS_DIR}/fluxcd.png",
    },
]


# ──────────────────────── Helpers ────────────────────────────
def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont):
    """Return width, height for text using textbbox (Pillow ≥ 10)."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered_multiline(draw, xy, text, font, fill):
    """Draw multiline text centered on (cx, cy)."""
    cx, cy = xy
    lines = text.split("\n")
    sizes = [text_size(draw, line, font) for line in lines]
    total_h = sum(h for _, h in sizes) + (len(lines) - 1) * 4
    y = cy - total_h / 2
    for (line, (w, h)) in zip(lines, sizes):
        draw.text((cx - w / 2, y), line, fill=fill, font=font)
        y += h + 4


def draw_arrow(draw, start, end, color, width=3, head_len=16, head_width=10):
    """Draw a line with a triangular arrow head pointing to 'end'."""
    x1, y1 = start
    x2, y2 = end
    draw.line([start, end], fill=color, width=width)

    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux, uy = dx / dist, dy / dist

    bx = x2 - ux * head_len
    by = y2 - uy * head_len

    px, py = -uy, ux
    left = (bx + px * head_width, by + py * head_width)
    right = (bx - px * head_width, by - py * head_width)

    draw.polygon([end, left, right], fill=color)


def load_icon(path: str, size=(72, 72)):
    """Load an icon (RGBA) and resize. If missing/bad, return None."""
    if not os.path.exists(path):
        print(f"[WARN] Icon not found: {path}")
        return None
    try:
        img = Image.open(path).convert("RGBA")
    except UnidentifiedImageError:
        print(f"[WARN] Cannot identify image file: {path}")
        return None
    img = img.resize(size, Image.LANCZOS)
    return img


# ───────────────────────── Main ─────────────────────────────
def main():
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_subtitle = ImageFont.truetype("DejaVuSans.ttf", 22)
        font_center = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_node_label = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
        font_node_desc = ImageFont.truetype("DejaVuSans.ttf", 16)
    except OSError:
        font_title = font_subtitle = font_center = \
            font_node_label = font_node_desc = ImageFont.load_default()

    # ── Header ──
    tw, th = text_size(draw, TITLE, font_title)
    draw.text(((W - tw) / 2, 30), TITLE, fill=TEXT_COLOR, font=font_title)

    sw, sh = text_size(draw, SUBTITLE, font_subtitle)
    draw.text(((W - sw) / 2, 30 + th + 6), SUBTITLE,
              fill=(80, 90, 100), font=font_subtitle)

    # ── Center circle ──
    cx, cy = CENTER
    center_r = 110

    draw.ellipse(
        (cx - center_r, cy - center_r, cx + center_r, cy + center_r),
        fill=CENTER_FILL,
        outline=CENTER_OUTLINE,
        width=2,
    )
    draw_centered_multiline(draw, (cx, cy), CENTER_LABEL, font_center, TEXT_COLOR)

    # ── Circular icon nodes ──
    radius_nodes = 320  # distance from center to node center
    node_icon_radius = 50   # radius of colored circle around icon
    node_centers = []

    n = len(STEPS)

    for i, step in enumerate(STEPS):
        label = step["label"]
        desc = step["desc"]
        icon_path = step["icon"]

        angle = 2 * math.pi * i / n - math.pi / 2  # start at top, clockwise
        nx = cx + radius_nodes * math.cos(angle)
        ny = cy + radius_nodes * math.sin(angle)
        node_centers.append((nx, ny))

        # 1) Circular background behind icon
        draw.ellipse(
            (nx - node_icon_radius, ny - node_icon_radius,
             nx + node_icon_radius, ny + node_icon_radius),
            fill=NODE_CIRCLE,
            outline=NODE_BORDER,
            width=2,
        )

        # 2) Icon in the center of that circle
        icon = load_icon(icon_path, size=(72, 72))
        if icon is not None:
            icon_x = int(nx - icon.width / 2)
            icon_y = int(ny - icon.height / 2)
            img.paste(icon, (icon_x, icon_y), icon)

        # 3) Label and description below the icon
        #    (slightly moved outward from the center)
        text_offset = 80
        label_y = ny + text_offset

        lw, lh = text_size(draw, label, font_node_label)
        draw.text(
            (nx - lw / 2, label_y),
            label,
            fill=(30, 30, 40),
            font=font_node_label,
        )

        desc_lines = desc.split("\n")
        sizes = [text_size(draw, line, font_node_desc) for line in desc_lines]
        total_h = sum(h for _, h in sizes) + (len(desc_lines) - 1) * 2

        current_y = label_y + lh + 2
        for (line, (dw, dh)) in zip(desc_lines, sizes):
            draw.text(
                (nx - dw / 2, current_y),
                line,
                fill=(80, 90, 100),
                font=font_node_desc,
            )
            current_y += dh + 2

    # ── Arrows between nodes following pipeline order ──
    shrink = 60  # pull arrows back from node centers
    for i in range(n):
        x1, y1 = node_centers[i]
        x2, y2 = node_centers[(i + 1) % n]  # next; wraps last → first

        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist

        start = (x1 + ux * shrink, y1 + uy * shrink)
        end = (x2 - ux * shrink, y2 - uy * shrink)

        draw_arrow(draw, start, end, ARROW_COLOR, width=3)

    out_path = "ci_cd_circular_icons_white.png"
    img.save(out_path)
    print(f"Saved {out_path} in {os.getcwd()}")


if __name__ == "__main__":
    main()
