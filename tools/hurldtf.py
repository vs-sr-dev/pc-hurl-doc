"""List and extract the chunks of a .DTF / .OVL container.

    python tools/hurldtf.py <install> list  [LEV1]
    python tools/hurldtf.py <install> dump  <LEV1|PICS|KIT> <outdir>
    python tools/hurldtf.py <install> census
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402


def containers(base):
    out = sorted(glob.glob(os.path.join(base, '*.DTF')))
    ovl = os.path.join(base, 'KIT.OVL')
    if os.path.exists(ovl):
        out.append(ovl)
    return out


def cmd_list(base, which):
    path = os.path.join(base, which + ('.OVL' if which == 'KIT' else '.DTF'))
    data = H.read(path)
    print('%s  %d bytes' % (os.path.basename(path), len(data)))
    for i, off, c in H.dtf_chunks(data):
        k = H.chunk_kind(c)
        extra = ''
        if k == 'GIF':
            extra = '%dx%d' % H.gif_size(c)
        elif k == 'PBM':
            w, h, _p, _pal = H.decode_pbm(c)
            extra = '%dx%d' % (w, h)
        print('  [%3d] %#09x %8d  %-4s %s' % (i, off, len(c), k, extra))


def cmd_dump(base, which, outdir):
    path = os.path.join(base, which + ('.OVL' if which == 'KIT' else '.DTF'))
    data = H.read(path)
    os.makedirs(outdir, exist_ok=True)
    ext = {'GIF': 'gif', 'PBM': 'lbm', 'INF': 'inf', 'RAW': 'bin', 'IFF': 'iff'}
    for i, _off, c in H.dtf_chunks(data):
        k = H.chunk_kind(c)
        name = '%s_%03d.%s' % (which.lower(), i, ext[k])
        with open(os.path.join(outdir, name), 'wb') as f:
            f.write(c)
    print('wrote %d chunks to %s' % (len(H.dtf_offsets(data)) - 1, outdir))


def cmd_census(base):
    import collections
    import hashlib
    seen = collections.defaultdict(list)
    print('%-11s %6s %5s %5s %5s %5s' % ('file', 'chunks', 'inf', 'map',
                                         'pbm', 'gif'))
    for p in containers(base):
        data = H.read(p)
        c = collections.Counter()
        for i, _off, ch in H.dtf_chunks(data):
            k = H.chunk_kind(ch)
            c[k] += 1
            if k == 'GIF':
                seen[hashlib.sha1(ch).hexdigest()].append(os.path.basename(p))
        print('%-11s %6d %5d %5d %5d %5d' % (
            os.path.basename(p), sum(c.values()), c['INF'], c['RAW'],
            c['PBM'], c['GIF']))
    total = sum(len(v) for v in seen.values())
    print('\n%d GIF chunks across all containers, %d distinct images '
          '(%.1f%% redundancy)' % (total, len(seen),
                                   100.0 * (1 - len(seen) / float(total))))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'list':
        cmd_list(base, argv[3] if len(argv) > 3 else 'LEV1')
    elif cmd == 'dump':
        cmd_dump(base, argv[3], argv[4])
    elif cmd == 'census':
        cmd_census(base)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
