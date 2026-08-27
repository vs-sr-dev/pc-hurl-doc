"""Shared helpers for the H.U.R.L. / Slob Zone data files.

Nothing here needs the game installed system-wide: every entry point takes the
directory that holds H.EXE and the *.DTF files.
"""
import io
import os
import struct

# ---------------------------------------------------------------- containers

DTF_SLOTS = 500          # the offset table is always 500 uint32 = 2000 bytes
TAB_RECORD = 21          # char name[13]; uint32 offset; uint32 size


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def dtf_offsets(data):
    """Return the used chunk offsets of a .DTF/.OVL container.

    The header is a fixed 500-entry uint32 table. Unused slots are zero and the
    last used entry points one past the final chunk, i.e. at EOF.
    """
    offs = struct.unpack_from('<%dI' % DTF_SLOTS, data, 0)
    used = []
    for o in offs:
        if o == 0:
            break
        used.append(o)
    return used


def dtf_chunks(data):
    """Yield (index, offset, bytes) for every chunk in a .DTF container."""
    o = dtf_offsets(data)
    for i in range(len(o) - 1):
        yield i, o[i], data[o[i]:o[i + 1]]


def dtf_chunk(data, index):
    o = dtf_offsets(data)
    return data[o[index]:o[index + 1]]


def tab_entries(tab):
    """Parse a .TAB directory into [(name, offset, size), ...]."""
    out = []
    for i in range(len(tab) // TAB_RECORD):
        rec = tab[i * TAB_RECORD:(i + 1) * TAB_RECORD]
        name = rec[:13].split(b'\0')[0].decode('latin1')
        off, size = struct.unpack_from('<II', rec, 13)
        out.append((name, off, size))
    return out


def res_entries(base, name):
    """Open <name>.TAB / <name>.RES and yield (member, bytes)."""
    tab = read(os.path.join(base, name + '.TAB'))
    res = read(os.path.join(base, name + '.RES'))
    for nm, off, size in tab_entries(tab):
        yield nm, res[off:off + size]


def chunk_kind(c):
    if c[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF'
    if c[:4] == b'FORM' and c[8:12] == b'PBM ':
        return 'PBM'
    if c[:4] == b'FORM':
        return 'IFF'
    if c[:2] == b'; ' or c[:8] == b'MapFile:':
        return 'INF'
    return 'RAW'


# ------------------------------------------------------------------- imaging

def gif_size(c):
    return struct.unpack_from('<HH', c, 6)


def gif_palette(c):
    """Global colour table of a GIF, or None when the file carries no GCT."""
    flags = c[10]
    if not flags & 0x80:
        return None
    n = 2 << (flags & 7)
    return c[13:13 + n * 3]


def decode_gif(c):
    """(width, height, index bytes, palette list) using Pillow."""
    from PIL import Image
    im = Image.open(io.BytesIO(c))
    im.load()
    return im.width, im.height, im.tobytes(), im.getpalette()


def iff_chunks(data):
    """Walk a FORM container, yielding (id, payload)."""
    if data[:4] != b'FORM':
        raise ValueError('not an IFF FORM')
    end = 8 + struct.unpack_from('>I', data, 4)[0]
    pos = 12
    while pos + 8 <= min(end, len(data)):
        cid = data[pos:pos + 4]
        size = struct.unpack_from('>I', data, pos + 4)[0]
        yield cid, data[pos + 8:pos + 8 + size]
        pos += 8 + size + (size & 1)


def decode_pbm(data):
    """Decode an IFF PBM (DPaint II, 256 colours). Returns (w, h, pixels, pal)."""
    w = h = None
    comp = 0
    pal = None
    body = None
    for cid, payload in iff_chunks(data):
        if cid == b'BMHD':
            w, h, _x, _y, _planes, _mask, comp = struct.unpack_from(
                '>HHhhBBB', payload, 0)
        elif cid == b'CMAP':
            pal = payload
        elif cid == b'BODY':
            body = payload
    if body is None:
        raise ValueError('PBM has no BODY')
    if comp == 0:
        pix = body[:w * h]
    elif comp == 1:
        pix = unpack_byterun1(body, w * h)
    else:
        raise ValueError('unknown PBM compression %d' % comp)
    return w, h, pix, pal


def unpack_byterun1(src, want):
    """Amiga ByteRun1 (PackBits) decompression."""
    out = bytearray()
    i = 0
    n = len(src)
    while i < n and len(out) < want:
        b = src[i]
        i += 1
        if b < 128:
            out += src[i:i + b + 1]
            i += b + 1
        elif b > 128:
            out += bytes([src[i]]) * (257 - b)
            i += 1
    return bytes(out[:want])


def save_png(path, w, h, pixels, palette):
    from PIL import Image
    im = Image.frombytes('P', (w, h), bytes(pixels))
    if palette:
        im.putpalette(list(palette) + [0] * (768 - len(palette)))
    im.save(path)


# ------------------------------------------------------------------ the maps

MAP_W = MAP_H = 64
MAP_CELLS = MAP_W * MAP_H          # 4096
MAP_PLANES = 6

# AckReadMapFile in H.EXE issues six fread() calls of exactly these sizes,
# in this order, and the game's own code names the destinations.  Note that
# xGrid and yGrid are read 8712 bytes each, not 8192: the array is 4356
# uint16 (66 x 66), of which only the first 4096 are the 64 x 64 grid.
PLANE_SIZES = [8192, 8192, 8712, 8712, 8192, 8192]
PLANE_NAMES = ['map', 'objects', 'xGrid', 'yGrid', 'floor', 'ceiling']
MAP_GRID_BYTES = sum(PLANE_SIZES)  # 50192


def parse_map(chunk):
    """Split a .DTF map chunk into its six grids plus the trailing list.

    Every plane is returned truncated to the 4096 cells that are addressed;
    the 260 spare uint16 at the end of xGrid and yGrid are dropped (they are
    empty in every shipped level).
    """
    planes = []
    off = 0
    for size in PLANE_SIZES:
        planes.append(list(struct.unpack_from('<%dH' % MAP_CELLS, chunk, off)))
        off += size
    return planes, chunk[MAP_GRID_BYTES:]


def map_slack(chunk):
    """The 260 unaddressed uint16 at the end of xGrid and of yGrid."""
    out = []
    off = 0
    for i, size in enumerate(PLANE_SIZES):
        if size > MAP_CELLS * 2:
            n = (size - MAP_CELLS * 2) // 2
            out.append(list(struct.unpack_from(
                '<%dH' % n, chunk, off + MAP_CELLS * 2)))
        off += size
    return out


def cell(plane, x, y):
    return plane[y * MAP_W + x]


# ---------------------------------------------------------------- .INF files

SECTION_KEYS = {'Walls', 'EndWalls', 'Objects', 'EndObjects', 'Bitmaps',
                'EndBitmaps', 'EndBitMaps', 'ObjDesc', 'EndDesc', 'End'}

STATE_KEYS = ('Create', 'Destroy', 'Walk', 'Attack', 'Interact')


def parse_inf(text):
    """Parse a level description into a light structure.

    Returns dict(header={...}, walls=[(slot, res, comment)],
                 objbitmaps=[(slot, res, comment)], objects=[{...}]).
    """
    header, walls, objbmp, objects = {}, [], [], []
    cur = None
    where = None          # 'walls' | 'objbitmaps' | 'objdesc'
    in_bitmaps = False
    pending = ''
    for raw in text.splitlines():
        line = raw.split(';')[0].strip()
        comment = raw.split(';', 1)[1].strip() if ';' in raw else ''
        if not line:
            # a lone comment right before Number: is the designer's label
            if comment and not comment.startswith(('Number', 'Flags')):
                pending = comment
            continue
        if line.endswith(':') and line[:-1] in SECTION_KEYS:
            key = line[:-1]
            if key == 'Walls':
                where = 'walls'
            elif key == 'Objects':
                where = 'objbitmaps'
            elif key == 'ObjDesc':
                where = 'objdesc'
            elif key in ('EndWalls', 'EndObjects', 'EndDesc'):
                where = None
            elif key == 'Bitmaps':
                in_bitmaps = True
            elif key in ('EndBitmaps', 'EndBitMaps'):
                in_bitmaps = False
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key, val = key.strip(), val.strip()
            if where == 'objdesc':
                if key == 'Number':
                    n = [int(v) for v in val.split(',')]
                    cur = {'label': pending, 'number': n[0], 'speed': n[1],
                           'type': n[2], 'dir': n[3] if len(n) > 3 else 0,
                           'states': {}}
                    objects.append(cur)
                    pending = ''
                elif cur is not None and key in STATE_KEYS:
                    parts = [p.strip() for p in val.split(',')]
                    cur['states'][key] = {
                        'flags': parts[0],
                        'views': int(parts[1]),
                        'per_view': int(parts[2]),
                        'bitmaps': [int(p) for p in parts[3:] if p],
                    }
                continue
            header[key] = val
            continue
        if in_bitmaps and ',' in line:
            a, b = line.split(',')[:2]
            rec = (int(a), int(b), comment)
            (walls if where == 'walls' else objbmp).append(rec)
    return {'header': header, 'walls': walls, 'objbitmaps': objbmp,
            'objects': objects}


# --------------------------------------------------------------------- audio

def snd_to_wav(raw, rate=11000):
    """Wrap a raw unsigned 8-bit mono .SND in a RIFF/WAVE header."""
    hdr = b'RIFF' + struct.pack('<I', 36 + len(raw)) + b'WAVEfmt '
    hdr += struct.pack('<IHHIIHH', 16, 1, 1, rate, rate, 1, 8)
    hdr += b'data' + struct.pack('<I', len(raw))
    return hdr + raw
