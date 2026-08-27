"""Decode the game's pictures: GIF87a tiles, IFF-PBM backdrops, the FLI logo.

    python tools/hurlgfx.py <install> palettes            # palette census
    python tools/hurlgfx.py <install> png <LEV1> <outdir> # every image, as PNG
    python tools/hurlgfx.py <install> sheet <LEV1> <out.png>
    python tools/hurlgfx.py <install> res  <GRAPH> <outdir>
    python tools/hurlgfx.py <install> fli  info|frames <outdir>
    python tools/hurlgfx.py <install> font <out.png>      # the KIT.OVL font
"""
import collections
import glob
import hashlib
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402


def _png(path, w, h, pix, pal):
    H.save_png(path, w, h, pix, pal)


def cmd_palettes(base):
    """How many distinct 256-colour tables the shipped art actually uses."""
    pals = collections.Counter()
    where = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(base, '*.DTF'))):
        data = H.read(p)
        for i, _o, c in H.dtf_chunks(data):
            pal = None
            if H.chunk_kind(c) == 'GIF':
                pal = H.gif_palette(c)
            elif H.chunk_kind(c) == 'PBM':
                pal = H.decode_pbm(c)[3]
            if pal:
                k = hashlib.sha1(bytes(pal)).hexdigest()[:8]
                pals[k] += 1
                where[k].add(os.path.basename(p))
    for name in ('GRAPH', 'CUT', 'INTRO'):
        if not os.path.exists(os.path.join(base, name + '.TAB')):
            continue
        for nm, blob in H.res_entries(base, name):
            if blob[:3] == b'GIF':
                pal = H.gif_palette(blob)
                k = hashlib.sha1(bytes(pal)).hexdigest()[:8]
                pals[k] += 1
                where[k].add(name + '.RES')
    print('%-10s %6s  %s' % ('palette', 'images', 'appears in'))
    for k, n in pals.most_common():
        print('%-10s %6d  %s' % (k, n, ', '.join(sorted(where[k])[:6])))


def cmd_png(base, which, outdir):
    os.makedirs(outdir, exist_ok=True)
    data = H.read(os.path.join(base, which + '.DTF'))
    n = 0
    for i, _o, c in H.dtf_chunks(data):
        k = H.chunk_kind(c)
        if k == 'GIF':
            w, h, pix, pal = H.decode_gif(c)
        elif k == 'PBM':
            w, h, pix, pal = H.decode_pbm(c)
        else:
            continue
        _png(os.path.join(outdir, '%s_%03d.png' % (which.lower(), i)),
             w, h, pix, pal)
        n += 1
    print('wrote %d images to %s' % (n, outdir))


def cmd_sheet(base, which, out, cols=16):
    from PIL import Image
    data = H.read(os.path.join(base, which + '.DTF'))
    tiles = []
    for i, _o, c in H.dtf_chunks(data):
        if H.chunk_kind(c) == 'GIF':
            w, h, pix, pal = H.decode_gif(c)
            im = Image.frombytes('P', (w, h), pix)
            im.putpalette(pal)
            tiles.append((i, im.convert('RGB')))
    if not tiles:
        return
    tw, th = tiles[0][1].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
    for n, (_i, im) in enumerate(tiles):
        sheet.paste(im, ((n % cols) * tw, (n // cols) * th))
    sheet.save(out)
    print('%d tiles -> %s (%dx%d)' % (len(tiles), out, *sheet.size))


def cmd_res(base, name, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for nm, blob in H.res_entries(base, name):
        if blob[:3] != b'GIF':
            continue
        w, h, pix, pal = H.decode_gif(blob)
        _png(os.path.join(outdir, nm.replace('.gif', '.png')), w, h, pix, pal)
        n += 1
    print('wrote %d images to %s' % (n, outdir))


# ------------------------------------------------------------------ the FLIC

def fli_info(path):
    d = H.read(path)
    size, magic, frames, w, h, depth, flags, speed = struct.unpack_from(
        '<IHHHHHHH', d, 0)
    print('%s: %d bytes (header says %d), magic %#06x' %
          (os.path.basename(path), len(d), size, magic))
    print('  %dx%d %d-bit, %d frames, speed %d (1/70 s ticks)' %
          (w, h, depth, frames, speed))
    return d, frames, w, h


def fli_frames(path, outdir):
    """Minimal FLI decoder: enough for the one .FLI the game ships."""
    from PIL import Image
    d, frames, w, h = fli_info(path)
    os.makedirs(outdir, exist_ok=True)
    pos = 128
    buf = bytearray(w * h)
    pal = [0] * 768
    written = 0
    while pos + 16 <= len(d) and written < frames:
        fsize, ftype, chunks = struct.unpack_from('<IHH', d, pos)
        if ftype != 0xF1FA:
            pos += max(fsize, 1)
            continue
        cpos = pos + 16
        for _ in range(chunks):
            csize, ctype = struct.unpack_from('<IH', d, cpos)
            body = d[cpos + 6:cpos + csize]
            if ctype == 11:          # FLI_COLOR256/64 (6-bit)
                pal = _fli_palette(body, pal, 4)
            elif ctype == 4:
                pal = _fli_palette(body, pal, 1)
            elif ctype == 13:        # FLI_BLACK
                buf = bytearray(w * h)
            elif ctype == 15:        # FLI_BRUN
                _fli_brun(body, buf, w, h)
            elif ctype == 12:        # FLI_LC
                _fli_lc(body, buf, w)
            elif ctype == 16:        # FLI_COPY
                buf[:] = body[:w * h]
            cpos += csize
        im = Image.frombytes('P', (w, h), bytes(buf))
        im.putpalette(pal)
        im.save(os.path.join(outdir, 'f%04d.png' % written))
        written += 1
        pos += fsize
    print('wrote %d frames to %s' % (written, outdir))


def _fli_palette(body, pal, scale):
    pal = list(pal)
    n = struct.unpack_from('<H', body, 0)[0]
    p = 2
    idx = 0
    for _ in range(n):
        skip, count = body[p], body[p + 1]
        p += 2
        idx += skip
        if count == 0:
            count = 256
        for _c in range(count):
            for ch in range(3):
                pal[idx * 3 + ch] = min(255, body[p + ch] * scale)
            p += 3
            idx += 1
    return pal


def _fli_brun(body, buf, w, h):
    p = 0
    for y in range(h):
        p += 1                       # packet count byte, ignored
        x = 0
        while x < w:
            n = struct.unpack_from('<b', body, p)[0]
            p += 1
            if n >= 0:
                buf[y * w + x:y * w + x + n] = bytes([body[p]]) * n
                p += 1
                x += n
            else:
                n = -n
                buf[y * w + x:y * w + x + n] = body[p:p + n]
                p += n
                x += n


def _fli_lc(body, buf, w):
    first, nlines = struct.unpack_from('<HH', body, 0)
    p = 4
    y = first
    for _ in range(nlines):
        packets = body[p]
        p += 1
        x = 0
        for _q in range(packets):
            skip = body[p]
            n = struct.unpack_from('<b', body, p + 1)[0]
            p += 2
            x += skip
            if n >= 0:
                buf[y * w + x:y * w + x + n] = body[p:p + n]
                p += n
                x += n
            else:
                n = -n
                buf[y * w + x:y * w + x + n] = bytes([body[p]]) * n
                p += 1
                x += n
        y += 1


def cmd_font(base, out):
    kit = H.read(os.path.join(base, 'KIT.OVL'))
    chunk = H.dtf_chunk(kit, 2)
    w, h, pix, pal = H.decode_pbm(chunk)
    _png(out, w, h, pix, pal)
    print('font BBM %dx%d -> %s' % (w, h, out))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'palettes':
        cmd_palettes(base)
    elif cmd == 'png':
        cmd_png(base, argv[3], argv[4])
    elif cmd == 'sheet':
        cmd_sheet(base, argv[3], argv[4])
    elif cmd == 'res':
        cmd_res(base, argv[3], argv[4])
    elif cmd == 'font':
        cmd_font(base, argv[3])
    elif cmd == 'fli':
        path = os.path.join(base, 'MLOGO.FLI')
        if argv[3] == 'info':
            fli_info(path)
        else:
            fli_frames(path, argv[4])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
