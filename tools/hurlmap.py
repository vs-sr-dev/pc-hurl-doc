"""The 64x64 map grids in chunk 1 of every .DTF.

    python tools/hurlmap.py <install> info                 # sizes and planes
    python tools/hurlmap.py <install> ascii  <LEV1> [plane]
    python tools/hurlmap.py <install> png    <LEV1> <out.png>
    python tools/hurlmap.py <install> tail   <LEV1>        # the trailing list
    python tools/hurlmap.py <install> shared               # boilerplate records
    python tools/hurlmap.py <install> runs                 # X/Y grid evidence
    python tools/hurlmap.py <install> walls                # wall flag bits
    python tools/hurlmap.py <install> objects <LEV1>       # placed objects
"""
import collections
import glob
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402


def levels(base):
    def key(p):
        m = re.search(r'(\d+)', os.path.basename(p))
        return (0, int(m.group(1))) if m else (1, 0)
    return sorted(glob.glob(os.path.join(base, '*.DTF')), key=key)


def load(path):
    d = H.read(path)
    return H.parse_inf(H.dtf_chunk(d, 0).decode('latin1')), \
        H.parse_map(H.dtf_chunk(d, 1))


def cmd_info(base):
    print('%-8s %8s %8s %6s' % ('level', 'map bytes', 'tail', 'records'))
    for p in levels(base):
        chunk = H.dtf_chunk(H.read(p), 1)
        _planes, tail = H.parse_map(chunk)
        print('%-8s %8d %8d %6.1f' % (os.path.basename(p)[:-4], len(chunk),
                                      len(tail), (len(tail) - 2) / 5.0))


def cmd_ascii(base, which, plane=0):
    _inf, (planes, _tail) = load(os.path.join(base, which + '.DTF'))
    g = planes[int(plane)]
    print('%s plane %s (%s)' % (which, plane, H.PLANE_NAMES[int(plane)]))
    print('   ' + ''.join(str(x % 10) for x in range(H.MAP_W)))
    for y in range(H.MAP_H):
        row = ''.join('.' if g[y * H.MAP_W + x] == 0
                      else ('#' if g[y * H.MAP_W + x] < 256 else '@')
                      for x in range(H.MAP_W))
        print('%2d %s' % (y, row))


def cmd_png(base, which, out, scale=8):
    from PIL import Image
    inf, (planes, _tail) = load(os.path.join(base, which + '.DTF'))
    im = Image.new('RGB', (H.MAP_W * scale, H.MAP_H * scale), (16, 16, 20))
    px = im.load()

    def box(x, y, rgb):
        for j in range(scale):
            for i in range(scale):
                px[x * scale + i, y * scale + j] = rgb

    for y in range(H.MAP_H):
        for x in range(H.MAP_W):
            i = y * H.MAP_W + x
            if planes[0][i]:
                v = planes[0][i]
                box(x, y, (200, 200, 210) if v < 256 else (220, 120, 60))
            elif planes[4][i]:
                box(x, y, (40, 60, 40))
            if planes[1][i]:
                box(x, y, (90, 190, 255))
    hx = int(inf['header'].get('xPlayer', 0)) // 64
    hy = int(inf['header'].get('yPlayer', 0)) // 64
    box(hx, hy, (255, 60, 60))
    im.save(out)
    print('%s -> %s (player start %d,%d)' % (which, out, hx, hy))


def cmd_tail(base, which):
    """The trailing per-cell list.

    AckReadMapFile reads a uint16 count and then, for each entry, a uint16
    cell index followed by exactly three bytes which it treats as a
    NUL-terminated string: the length is strlen(), capped at 3, and the
    result is stored as a length-prefixed byte list hung off four per-cell
    pointer arrays (cell and cell+1 in one, cell and cell+64 in the other).
    """
    inf, (planes, tail) = load(os.path.join(base, which + '.DTF'))
    wall = {slot: c for slot, _res, c in inf['walls']}
    count = struct.unpack_from('<H', tail, 0)[0]
    print('%s: %d records in %d trailing bytes' % (which, count, len(tail)))
    pos = 2
    for _i in range(count):
        cell = struct.unpack_from('<H', tail, pos)[0]
        payload = tail[pos + 2:pos + 5].split(b'\0')[0]
        pos += 5
        base_wall = planes[0][cell]
        print('  (%2d,%2d) %d value%s %-12s  cell wall %#06x %s'
              % (cell % H.MAP_W, cell // H.MAP_W, len(payload),
                 '' if len(payload) == 1 else 's',
                 ','.join(str(b) for b in payload) or '-',
                 base_wall, wall.get(base_wall & 0xff, '')[:18]))


def cmd_shared(base):
    """Records that are identical across level files - copied boilerplate."""
    import collections
    seen = collections.Counter()
    total = 0
    for p in levels(base):
        _inf, (_planes, tail) = load(p)
        count = struct.unpack_from('<H', tail, 0)[0]
        total += 1
        for i in range(count):
            seen[tail[2 + i * 5:7 + i * 5]] += 1
    print('records present in all %d map files:' % total)
    for rec, n in seen.most_common():
        cell = struct.unpack_from('<H', rec, 0)[0]
        payload = rec[2:].split(b'\0')[0]
        print('  x%-2d  cell %5d (%2d,%2d)  %s'
              % (n, cell, cell % H.MAP_W, cell // H.MAP_W,
                 ','.join(str(b) for b in payload) or '(empty)'))


def cmd_runs(base):
    """Mean run length per plane: the evidence for which plane is which."""
    import numpy as np
    print('%-8s %-10s %6s %9s %9s' % ('level', 'plane', 'cells',
                                      'h-run', 'v-run'))
    for p in levels(base):
        _inf, (planes, _t) = load(p)
        for idx in range(H.MAP_PLANES):
            m = np.array(planes[idx], dtype=np.uint16).reshape(64, 64) != 0
            hs, vs = _runs(m), _runs(m.T)
            print('%-8s %-10s %6d %9.2f %9.2f'
                  % (os.path.basename(p)[:-4], H.PLANE_NAMES[idx],
                     int(m.sum()), hs, vs))
        print()


def cmd_walls(base):
    """Decode the wall cells above 255 as `flags << 8 | slot`."""
    byflag = collections.defaultdict(collections.Counter)
    special = collections.defaultdict(collections.Counter)
    keys = ('RedDoor', 'GreenDoor', 'BlueDoor', 'Vend', 'Exit', 'Shower',
            'Phone')
    for p in levels(base):
        inf, (planes, _t) = load(p)
        h = inf['header']
        spec = {int(h[k]): k for k in keys if k in h}
        wall = {slot: c for slot, _res, c in inf['walls']}
        for g in planes[:4]:
            for v in g:
                if v > 255:
                    byflag[v >> 8][wall.get(v & 255, '?')[:22]] += 1
                    special[v >> 8][spec.get(v & 255, '(plain wall)')] += 1
    for fl in sorted(byflag):
        print('flag %#04x  %d cells' % (fl, sum(byflag[fl].values())))
        print('   special slots: %s' % dict(special[fl]))
        print('   textures: %s' % ', '.join(
            '%s(%d)' % kv for kv in byflag[fl].most_common(6)))


def _runs(mask):
    total = n = 0
    for row in mask:
        c = 0
        for v in row:
            if v:
                c += 1
            elif c:
                total += c
                n += 1
                c = 0
        if c:
            total += c
            n += 1
    return total / float(n) if n else 0.0


def cmd_objects(base, which):
    """Cross-reference the object grid with the .INF object table."""
    inf, (planes, _t) = load(os.path.join(base, which + '.DTF'))
    bynum = {o['number']: o for o in inf['objects']}
    placed = []
    for i, v in enumerate(planes[1]):
        if v:
            placed.append((i % H.MAP_W, i // H.MAP_W, v))
    print('%s: %d of %d defined objects appear in the grid'
          % (which, len(placed), len(inf['objects'])))
    for x, y, num in placed:
        o = bynum.get(num)
        print('  (%2d,%2d) #%-3d %-22s type %s'
              % (x, y, num, o['label'][:22] if o else '??',
                 o['type'] if o else '?'))
    missing = sorted(set(bynum) - set(n for _x, _y, n in placed))
    if missing:
        print('  never placed: %s' % ', '.join(str(m) for m in missing))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'info':
        cmd_info(base)
    elif cmd == 'ascii':
        cmd_ascii(base, argv[3], argv[4] if len(argv) > 4 else 0)
    elif cmd == 'png':
        cmd_png(base, argv[3], argv[4])
    elif cmd == 'tail':
        cmd_tail(base, argv[3])
    elif cmd == 'shared':
        cmd_shared(base)
    elif cmd == 'walls':
        cmd_walls(base)
    elif cmd == 'runs':
        cmd_runs(base)
    elif cmd == 'objects':
        cmd_objects(base, argv[3])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
