"""Reports built from the level descriptions in chunk 0 of every .DTF.

    python tools/hurlinf.py <install> text    <LEV1>      # the raw script
    python tools/hurlinf.py <install> header              # all level headers
    python tools/hurlinf.py <install> objects <LEV1>      # object table
    python tools/hurlinf.py <install> types               # type-ID census
    python tools/hurlinf.py <install> assets              # source file names

The parser keyword table lives in tools/hurlexe.py, which reads it out of the
executable rather than guessing it from the scripts.
"""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402



def levels(base):
    def key(p):
        m = re.search(r'(\d+)', os.path.basename(p))
        return (0, int(m.group(1))) if m else (1, 0)
    return sorted(glob.glob(os.path.join(base, '*.DTF')), key=key)


def load(path):
    return H.parse_inf(H.dtf_chunk(H.read(path), 0).decode('latin1'))


def cmd_text(base, which):
    sys.stdout.write(
        H.dtf_chunk(H.read(os.path.join(base, which + '.DTF')), 0)
        .decode('latin1'))


def cmd_header(base):
    keys = ['xPlayer', 'yPlayer', 'PlayerAngle', 'TopColor', 'BottomColor',
            'Shading', 'Floors', 'Resolution', 'ScreenBack', 'ScrollBack',
            'RedDoor', 'GreenDoor', 'BlueDoor', 'Vend', 'Exit', 'Shower',
            'Phone', 'Hitgrid']
    print('%-8s %s' % ('level', ' '.join('%8s' % k[:8] for k in keys)))
    for p in levels(base):
        h = load(p)['header']
        print('%-8s %s' % (os.path.basename(p)[:-4],
                           ' '.join('%8s' % h.get(k, '-') for k in keys)))


def cmd_objects(base, which):
    inf = load(os.path.join(base, which + '.DTF'))
    print('%-3s %-22s %5s %5s %5s  %s' % ('#', 'label', 'speed', 'type',
                                          'dir', 'states'))
    for o in inf['objects']:
        st = ','.join(k[0] for k in H.STATE_KEYS if k in o['states'])
        print('%-3d %-22s %5d %5d %5d  %s' % (o['number'], o['label'][:22],
                                              o['speed'], o['type'],
                                              o['dir'], st))


def cmd_types(base):
    """Which type ID goes with which designer label, across every level."""
    byid = collections.defaultdict(collections.Counter)
    for p in levels(base):
        for o in load(p)['objects']:
            byid[o['type']][re.sub(r'-\d+$', '', o['label'])] += 1
    print('%-5s %6s  %s' % ('type', 'count', 'labels'))
    for t in sorted(byid):
        c = byid[t]
        print('%-5d %6d  %s' % (t, sum(c.values()),
                                ', '.join('%s(%d)' % kv
                                          for kv in c.most_common(6))))


def cmd_assets(base):
    """The .gif source names the designers left in the trailing comments."""
    names = collections.defaultdict(set)
    for p in levels(base):
        lvl = os.path.basename(p)[:-4]
        inf = load(p)
        for kind in ('walls', 'objbitmaps'):
            for _slot, res, comment in inf[kind]:
                m = re.match(r'([A-Za-z0-9_\-]+\.(?:gif|GIF))', comment)
                if m:
                    names[m.group(1).lower()].add((lvl, res))
    print('%d distinct source file names recovered from comments' % len(names))
    for nm in sorted(names):
        w = sorted(names[nm])
        print('  %-14s %s' % (nm, ' '.join('%s:%d' % x for x in w[:8])))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'text':
        cmd_text(base, argv[3])
    elif cmd == 'header':
        cmd_header(base)
    elif cmd == 'objects':
        cmd_objects(base, argv[3])
    elif cmd == 'types':
        cmd_types(base)
    elif cmd == 'assets':
        cmd_assets(base)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
