from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1100, 700
CENTER = (W // 2, H // 2)
BG_COLOR = (255, 255, 255)
TEXT_COLOR = (20, 24, 28)

CENTER_FILL = (240, 245, 255)
CENTER_OUTLINE = (100, 130, 200)

NODE_CIRCLE = (230, 238, 255)
NODE_BORDER = (120, 150, 210)
ARROW_COLOR = (150, 160, 175)
RING_COLOR = (220, 226, 240)

ICONS_DIR = "icons"
OUT_DIR = "docs"
OUT_GIF = os.path.join(OUT_DIR, "ci_cd_pipeline.gif")

TITLE = "DevOps CI/CD Pipeline"
SUBTITLE = "Automated build, test, and deployment workflow"
CENTER_LABEL = "Continuous Integration & Deployment"

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
        "desc": "Artifact repository",
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
        "desc": "Container registry",
        "icon": f"{ICONS_DIR}/gh-packages.png",
    },
    {
        "label": "Helm",
        "desc": "Chart packaging",
        "icon": f"{ICONS_DIR}/helm.png",
    },
    {
        "label": "FluxCD",
        "desc": "GitOps deploy",
        "icon": f"{ICONS_DIR}/fluxcd.png",
    },
]


def load_icon(path, size=(64, 64)):
    if not os.path.exists(path):
        print(f"[WARN] Icon not found: {path}")
        return None
    img = Image.open(path).convert("RGBA")
    return img.resize(size, Image.LANCZOS)


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered_multiline(draw, xy, text, font, fill):
    cx, cy = xy
    lines = text.split("\n")
    sizes = [text_size(draw, line, font) for line in lines]
    total_h = sum(h for _, h in sizes) + (len(lines) - 1) * 4
    y = cy - total_h / 2
    for (line, (w, h)) in zip(lines, sizes):
        draw.text((cx - w / 2, y), line, fill=fill, font=font)
        y += h + 4


def make_base_scene(fonts, icons):
    """
    Draw the static diagram (no animation ring) and return:
      - base image (PIL.Image)
      - list of node center positions
    """
    font_title, font_subtitle, font_center, font_node_label, font_node_desc = fonts

    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header
    tw, th = text_size(draw, TITLE, font_title)
    draw.text(((W - tw) / 2, 30), TITLE, fill=TEXT_COLOR, font=font_title)

    sw, sh = text_size(draw, SUBTITLE, font_subtitle)
    draw.text(((W - sw) / 2, 30 + th + 6), SUBTITLE,
              fill=(80, 90, 100), font=font_subtitle)

    # Center circle
    cx, cy = CENTER
    center_r = 90
    draw.ellipse(
        (cx - center_r, cy - center_r, cx + center_r, cy + center_r),
        fill=CENTER_FILL,
        outline=CENTER_OUTLINE,
        width=2,
    )
    draw_centered_multiline(draw, (cx, cy), CENTER_LABEL, font_center, TEXT_COLOR)

    # Nodes
    radius_nodes = 220
    node_icon_radius = 45
    node_centers = []
    n = len(STEPS)

    for i, step in enumerate(STEPS):
        label = step["label"]
        desc = step["desc"]
        icon_key = step["icon"]

        angle = 2 * math.pi * i / n - math.pi / 2
        nx = cx + radius_nodes * math.cos(angle)
        ny = cy + radius_nodes * math.sin(angle)
        node_centers.append((nx, ny))

        # circular badge
        draw.ellipse(
            (nx - node_icon_radius, ny - node_icon_radius,
             nx + node_icon_radius, ny + node_icon_radius),
            fill=NODE_CIRCLE,
            outline=NODE_BORDER,
            width=2,
        )

        icon = icons.get(icon_key)
        if icon is not None:
            ix = int(nx - icon.width / 2)
            iy = int(ny - icon.height / 2)
            img.paste(icon, (ix, iy), icon)

        # label + desc
        label_y = ny + node_icon_radius + 10
        lw, lh = text_size(draw, label, font_node_label)
        draw.text((nx - lw / 2, label_y), label, fill=TEXT_COLOR, font=font_node_label)

        desc_lines = desc.split("\n")
        sizes = [text_size(draw, line, font_node_desc) for line in desc_lines]
        cur_y = label_y + lh + 2
        for line, (dw, dh) in zip(desc_lines, sizes):
            draw.text((nx - dw / 2, cur_y), line, fill=(90, 100, 110), font=font_node_desc)
            cur_y += dh + 2

    # arrows between nodes
    shrink = 50
    for i in range(n):
        x1, y1 = node_centers[i]
        x2, y2 = node_centers[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        sx = x1 + ux * shrink
        sy = y1 + uy * shrink
        ex = x2 - ux * shrink
        ey = y2 - uy * shrink
        draw.line((sx, sy, ex, ey), fill=ARROW_COLOR, width=2)

    return img, node_centers


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Fonts
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_subtitle = ImageFont.truetype("DejaVuSans.ttf", 16)
        font_center = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
        font_node_label = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
        font_node_desc = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font_title = font_subtitle = font_center = font_node_label = font_node_desc = ImageFont.load_default()

    fonts = (font_title, font_subtitle, font_center, font_node_label, font_node_desc)

    # Load icons once
    icons = {}
    for step in STEPS:
        path = step["icon"]
        if path not in icons:
            icons[path] = load_icon(path)

    base_img, _ = make_base_scene(fonts, icons)

    # Generate frames with a small dot rotating around the center (looks "live")
    frames = []
    cx, cy = CENTER
    ring_r = 260
    num_frames = 32

    for f in range(num_frames):
        frame = base_img.copy()
        draw = ImageDraw.Draw(frame)

        angle = 2 * math.pi * f / num_frames - math.pi / 2
        dx = ring_r * math.cos(angle)
        dy = ring_r * math.sin(angle)
        px = cx + dx
        py = cy + dy

        dot_r = 6
        draw.ellipse(
            (px - dot_r, py - dot_r, px + dot_r, py + dot_r),
            fill=(100, 140, 230),
            outline=(70, 100, 190),
            width=2,
        )

        # faint ring behind the dot
        draw.ellipse(
            (cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
            outline=RING_COLOR,
            width=1,
        )

        frames.append(frame)

    # Save animated GIF
    frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=120,  # ms per frame
        loop=0,
        optimize=True,
    )
    print(f"Saved GIF: {OUT_GIF}")


if __name__ == "__main__":
    main()
