from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT = ROOT_DIR / "assets" / "logo" / "articleops-logo.ico"
SIZES = (16, 32, 48, 64, 128, 256)


def clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def over(dst: tuple[int, int, int, int], src: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    alpha = sa / 255
    out_alpha = alpha + da / 255 * (1 - alpha)
    if out_alpha <= 0:
        return 0, 0, 0, 0
    return (
        clamp((sr * alpha + dr * da / 255 * (1 - alpha)) / out_alpha),
        clamp((sg * alpha + dg * da / 255 * (1 - alpha)) / out_alpha),
        clamp((sb * alpha + db * da / 255 * (1 - alpha)) / out_alpha),
        clamp(out_alpha * 255),
    )


def set_pixel(
    pixels: list[tuple[int, int, int, int]],
    size: int,
    x: int,
    y: int,
    color: tuple[int, int, int, int],
) -> None:
    if 0 <= x < size and 0 <= y < size:
        pixels[y * size + x] = over(pixels[y * size + x], color)


def scale(value: float, size: int) -> float:
    return value * size / 320


def draw_round_rect(
    pixels: list[tuple[int, int, int, int]],
    size: int,
    x: float,
    y: float,
    width: float,
    height: float,
    radius: float,
    color: tuple[int, int, int, int],
) -> None:
    x0, y0 = scale(x, size), scale(y, size)
    x1, y1 = scale(x + width, size), scale(y + height, size)
    r = scale(radius, size)
    for py in range(max(0, int(y0)), min(size, math.ceil(y1))):
        for px in range(max(0, int(x0)), min(size, math.ceil(x1))):
            cx = min(max(px + 0.5, x0 + r), x1 - r)
            cy = min(max(py + 0.5, y0 + r), y1 - r)
            if math.hypot(px + 0.5 - cx, py + 0.5 - cy) <= r:
                set_pixel(pixels, size, px, py, color)


def draw_circle(
    pixels: list[tuple[int, int, int, int]],
    size: int,
    cx: float,
    cy: float,
    radius: float,
    color: tuple[int, int, int, int],
) -> None:
    center_x, center_y, r = scale(cx, size), scale(cy, size), scale(radius, size)
    for py in range(max(0, int(center_y - r)), min(size, math.ceil(center_y + r))):
        for px in range(max(0, int(center_x - r)), min(size, math.ceil(center_x + r))):
            if math.hypot(px + 0.5 - center_x, py + 0.5 - center_y) <= r:
                set_pixel(pixels, size, px, py, color)


def draw_line(
    pixels: list[tuple[int, int, int, int]],
    size: int,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    color: tuple[int, int, int, int],
) -> None:
    x1, y1 = scale(start[0], size), scale(start[1], size)
    x2, y2 = scale(end[0], size), scale(end[1], size)
    line_width = scale(width, size)
    min_x = max(0, int(min(x1, x2) - line_width))
    max_x = min(size, math.ceil(max(x1, x2) + line_width))
    min_y = max(0, int(min(y1, y2) - line_width))
    max_y = min(size, math.ceil(max(y1, y2) + line_width))
    dx, dy = x2 - x1, y2 - y1
    length_squared = dx * dx + dy * dy
    for py in range(min_y, max_y):
        for px in range(min_x, max_x):
            if length_squared == 0:
                distance = math.hypot(px + 0.5 - x1, py + 0.5 - y1)
            else:
                t = max(0, min(1, ((px + 0.5 - x1) * dx + (py + 0.5 - y1) * dy) / length_squared))
                distance = math.hypot(px + 0.5 - (x1 + t * dx), py + 0.5 - (y1 + t * dy))
            if distance <= line_width / 2:
                set_pixel(pixels, size, px, py, color)


def draw_icon(size: int) -> bytes:
    pixels: list[tuple[int, int, int, int]] = [(0, 0, 0, 0)] * (size * size)
    draw_round_rect(pixels, size, 0, 0, 320, 320, 72, (15, 23, 42, 255))

    draw_line(pixels, size, (72, 232), (130, 126), 22, (29, 78, 216, 255))
    draw_line(pixels, size, (130, 126), (248, 58), 22, (15, 118, 110, 255))
    draw_line(pixels, size, (76, 232), (188, 232), 3, (226, 232, 240, 90))
    draw_line(pixels, size, (188, 232), (256, 164), 3, (226, 232, 240, 90))
    draw_line(pixels, size, (256, 164), (256, 60), 3, (226, 232, 240, 90))

    draw_round_rect(pixels, size, 90, 82, 142, 166, 22, (226, 232, 240, 255))
    draw_round_rect(pixels, size, 112, 114, 78, 10, 5, (30, 41, 59, 255))
    draw_round_rect(pixels, size, 112, 142, 96, 8, 4, (100, 116, 139, 255))
    draw_round_rect(pixels, size, 112, 164, 74, 8, 4, (100, 116, 139, 255))
    draw_round_rect(pixels, size, 112, 186, 92, 8, 4, (100, 116, 139, 255))
    draw_round_rect(pixels, size, 112, 214, 54, 16, 8, (15, 118, 110, 255))

    draw_circle(pixels, size, 72, 232, 17, (245, 158, 11, 255))
    draw_circle(pixels, size, 160, 112, 13, (56, 189, 248, 255))
    draw_circle(pixels, size, 248, 58, 17, (34, 197, 94, 255))
    draw_line(pixels, size, (235, 214), (270, 179), 12, (248, 250, 252, 255))
    draw_line(pixels, size, (240, 179), (270, 179), 12, (248, 250, 252, 255))
    draw_line(pixels, size, (270, 179), (270, 209), 12, (248, 250, 252, 255))

    raw_rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            row.extend(pixels[y * size + x])
        raw_rows.append(b"\x00" + bytes(row))

    raw = b"".join(raw_rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    return png


def write_ico() -> None:
    images = [(size, draw_icon(size)) for size in SIZES]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + len(images) * 16
    entries = []
    payload = []
    for size, image in images:
        width_byte = 0 if size >= 256 else size
        entries.append(struct.pack("<BBBBHHII", width_byte, width_byte, 0, 0, 1, 32, len(image), offset))
        payload.append(image)
        offset += len(image)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(header + b"".join(entries) + b"".join(payload))


if __name__ == "__main__":
    write_ico()
    print(f"Wrote {OUTPUT}")
