"""List and extract the .RES / .TAB archive pairs.

    python tools/hurlres.py <install> list  [GRAPH]
    python tools/hurlres.py <install> dump  <GRAPH> <outdir>
    python tools/hurlres.py <install> all   <outdir>
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402


def archives(base):
    return sorted(os.path.basename(p)[:-4]
                  for p in glob.glob(os.path.join(base, '*.TAB')))


def cmd_list(base, name):
    tab = H.read(os.path.join(base, name + '.TAB'))
    ressize = os.path.getsize(os.path.join(base, name + '.RES'))
    ent = H.tab_entries(tab)
    print('%s.TAB  %d entries, %s.RES %d bytes' % (name, len(ent), name,
                                                   ressize))
    end = 0
    for nm, off, size in ent:
        print('  %-13s %#09x %8d' % (nm, off, size))
        end = max(end, off + size)
    if end != ressize:
        print('  !! directory covers %d of %d bytes' % (end, ressize))


def cmd_dump(base, name, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for nm, blob in H.res_entries(base, name):
        with open(os.path.join(outdir, nm), 'wb') as f:
            f.write(blob)
        n += 1
    print('wrote %d members of %s.RES to %s' % (n, name, outdir))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'list':
        cmd_list(base, argv[3] if len(argv) > 3 else 'GRAPH')
    elif cmd == 'dump':
        cmd_dump(base, argv[3], argv[4])
    elif cmd == 'all':
        for a in archives(base):
            cmd_dump(base, a, os.path.join(argv[3], a.lower()))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
