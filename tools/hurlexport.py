"""One shot: everything the other tools can produce, into one directory.

    python tools/hurlexport.py <install> <outdir> [rate]

Nothing here is committed to the repository - the output is derived from your
own copy of the game.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H      # noqa: E402
import hurlaudio         # noqa: E402
import hurlgfx           # noqa: E402
import hurlres           # noqa: E402


def containers(base):
    def key(p):
        m = re.search(r'(\d+)', os.path.basename(p))
        return (0, int(m.group(1))) if m else (1, 0)
    return [os.path.basename(p)[:-4]
            for p in sorted(glob.glob(os.path.join(base, '*.DTF')), key=key)]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, out = argv[1], argv[2]
    rate = int(argv[3]) if len(argv) > 3 else hurlaudio.DEFAULT_RATE
    os.makedirs(out, exist_ok=True)

    # level descriptions, verbatim
    d = os.path.join(out, 'inf')
    os.makedirs(d, exist_ok=True)
    for name in containers(base):
        chunk = H.dtf_chunk(H.read(os.path.join(base, name + '.DTF')), 0)
        with open(os.path.join(d, name.lower() + '.inf'), 'wb') as f:
            f.write(chunk)
    print('level scripts  -> %s' % d)

    # pictures
    for name in containers(base):
        hurlgfx.cmd_png(base, name, os.path.join(out, 'pics', name.lower()))
        hurlgfx.cmd_sheet(base, name,
                          os.path.join(out, 'pics', name.lower() + '.png'))
    for name in ('GRAPH', 'CUT', 'INTRO'):
        hurlgfx.cmd_res(base, name, os.path.join(out, 'pics', name.lower()))
    hurlgfx.cmd_font(base, os.path.join(out, 'pics', 'font.png'))
    hurlgfx.fli_frames(os.path.join(base, 'MLOGO.FLI'),
                       os.path.join(out, 'pics', 'mlogo'))

    # raw archive members, for anything the decoders miss
    hurlres.main(['', base, 'all', os.path.join(out, 'res')])

    # audio
    hurlaudio.cmd_snd(base, os.path.join(out, 'sfx'), rate)
    hurlaudio.cmd_banks(base, os.path.join(out, 'speech'), rate)

    print('\ndone -> %s' % out)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
