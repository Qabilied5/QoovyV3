#!/usr/bin/env python3
"""
Qoovy PWA Icon Generator
Generates all required PWA icons as PNG files using Pillow.
"""

import os
import math

def generate_icon(size, output_path, is_maskable=False):
    """Generate a Qoovy icon PNG using raw bytes (no Pillow needed)."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        pad = int(size * 0.08) if is_maskable else 0
        
        # Background circle / rounded rect
        r = size // 2 if not is_maskable else size // 2
        bg_color = (8, 8, 16, 255)
        draw.ellipse([pad, pad, size - pad, size - pad], fill=bg_color)
        
        # Gradient effect — draw concentric rings
        cx, cy = size // 2, size // 2
        radius = (size // 2) - pad
        
        # Purple-to-pink gradient rings
        for i in range(int(radius * 0.8), 0, -1):
            t = 1 - (i / (radius * 0.8))
            r_c = int(99 + (236 - 99) * t)
            g_c = int(68 + (64 - 68) * t)
            b_c = int(255 + (162 - 255) * t)
            alpha = int(40 * (1 - t))
            draw.ellipse(
                [cx - i, cy - i, cx + i, cy + i],
                outline=(r_c, g_c, b_c, alpha), width=1
            )
        
        # Outer glow ring
        glow_r = int(radius * 0.88)
        draw.ellipse(
            [cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
            outline=(167, 139, 250, 120), width=max(1, size // 48)
        )
        
        # Inner circle
        inner_r = int(radius * 0.78)
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
            fill=(12, 12, 22, 255), outline=(167, 139, 250, 60), width=max(1, size // 64)
        )
        
        # Music note icon (simplified disc)
        disc_r = int(radius * 0.38)
        draw.ellipse(
            [cx - disc_r, cy - disc_r, cx + disc_r, cy + disc_r],
            fill=(167, 139, 250, 220)
        )
        
        # Center hole
        hole_r = int(disc_r * 0.28)
        draw.ellipse(
            [cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r],
            fill=(8, 8, 16, 255)
        )
        
        # Q letter hint — draw a subtle "Q" using arc
        q_r = int(radius * 0.52)
        draw.arc(
            [cx - q_r, cy - q_r, cx + q_r, cy + q_r],
            start=30, end=320,
            fill=(236, 100, 162, 180), width=max(2, size // 24)
        )
        # Q tail
        tail_len = int(q_r * 0.35)
        draw.line(
            [cx + int(q_r * 0.55), cy + int(q_r * 0.55),
             cx + int(q_r * 0.55) + tail_len, cy + int(q_r * 0.55) + tail_len],
            fill=(236, 100, 162, 200), width=max(2, size // 24)
        )
        
        img.save(output_path, 'PNG', optimize=True)
        print(f"  ✓ {output_path} ({size}x{size})")
        return True
        
    except ImportError:
        return False

def generate_icon_svg_fallback(size, output_path):
    """Fallback: create a minimal valid PNG using struct."""
    import struct, zlib
    
    def png_chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    # Create a simple solid-color PNG
    width = height = size
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    
    # Image data — purple-ish background
    raw_rows = []
    for y in range(height):
        row = [0]  # filter byte
        for x in range(width):
            # Simple radial gradient
            cx, cy = width / 2, height / 2
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            r_max = min(cx, cy)
            
            if dist <= r_max:
                t = dist / r_max
                # Dark bg: #080810 -> purple edge
                r = int(8 + (99 - 8) * t * 0.5)
                g = int(8 + (68 - 8) * t * 0.3)
                b = int(16 + (255 - 16) * t * 0.4)
                row.extend([r, g, b])
            else:
                row.extend([8, 8, 16])
        raw_rows.append(bytes(row))
    
    raw_data = b''.join(raw_rows)
    compressed = zlib.compress(raw_data, 9)
    
    png_data = (
        b'\x89PNG\r\n\x1a\n' +
        png_chunk(b'IHDR', ihdr_data) +
        png_chunk(b'IDAT', compressed) +
        png_chunk(b'IEND', b'')
    )
    
    with open(output_path, 'wb') as f:
        f.write(png_data)
    print(f"  ✓ {output_path} ({size}x{size}) [fallback]")

if __name__ == '__main__':
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    maskable = {192, 512}
    out_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating Qoovy PWA icons...")
    for s in sizes:
        path = os.path.join(out_dir, f'icon-{s}.png')
        ok = generate_icon(s, path, is_maskable=(s in maskable))
        if not ok:
            generate_icon_svg_fallback(s, path)
    
    print(f"\nAll {len(sizes)} icons generated in: {out_dir}")