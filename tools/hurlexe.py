"""What the executables say about themselves.

    python tools/hurlexe.py <install> strings [H.EXE]   # printable strings
    python tools/hurlexe.py <install> ident             # every binary, named
    python tools/hurlexe.py <install> keywords          # the .INF parser table
    python tools/hurlexe.py <install> trig              # KIT.OVL maths tables
    python tools/hurlexe.py <install> ghosts             # names with no file
"""
import glob
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402

# The .INF parser's keyword table lives in one run of the H.EXE data segment.
# ACK-3D compares its own keywords after upper-casing the token, which is why
# they are stored upper-case; the keywords Deep River added are stored with
# the exact mixed case the shipped .INF files use.
KEYWORD_BLOCK = (0x02a3a7, 0x02a5a0)
COPYRIGHT_BLOCK = (0x02ada0, 0x02af44)

# Recovered by reading the block above.  Upper case = stored upper case,
# which is how ACK-3D's own parser compares tokens; the mixed-case entries
# are the ones Deep River bolted on and compares literally.
KEYWORDS = [
    'NUMBER:', 'CREATE:', 'DESTROY:', 'WALK:', 'ATTACK:', 'INTERACT:',
    'ANIMATE', 'MOVEABLE', 'PASSABLE', 'MULTIVIEW', 'SHOWONCE',
    'END:', 'LOADTYPE:', 'ENDBITMAPS:', 'ENDDESC:', 'BITMAPS:', 'ENDWALLS:',
    'OBJDESC:', 'ENDOBJECTS:', 'WALLS:', 'OBJECTS:', 'MAPFILE:', 'PALFILE:',
    'XPLAYER:', 'YPLAYER:', 'PLAYERANGLE:', 'SCREENBACK:', 'SCROLLBACK:',
    'TOPCOLOR:', 'BOTTOMCOLOR:', 'SHADING:', 'FLOORS:', 'RESOLUTION:',
    'RedDoor:', 'GreenDoor:', 'BlueDoor:', 'Vend:', 'Hitgrid:', 'Exit:',
    'Phone:', 'Shower:', 'LevelType:', 'Timer:', 'Rect:',
]
ACK_MIXED = set()          # none so far: every ACK-3D keyword is upper case


def _inf_keyword_use(base):
    import glob as _g
    seen = {}
    for p in _g.glob(os.path.join(base, '*.DTF')):
        text = H.dtf_chunk(H.read(p), 0).decode('latin1')
        for line in text.splitlines():
            line = line.split(';')[0].strip()
            if ':' in line:
                k = line.split(':')[0].strip().lower()
                seen[k] = seen.get(k, 0) + 1
            for flag in ('ANIMATE', 'MOVEABLE', 'PASSABLE', 'MULTIVIEW',
                         'SHOWONCE'):
                if flag in line:
                    seen[flag.lower()] = seen.get(flag.lower(), 0) + 1
    return seen


def cmd_strings(base, which='H.EXE'):
    d = H.read(os.path.join(base, which))
    for m in re.finditer(rb'[\x20-\x7e]{5,}', d):
        print('%#08x %s' % (m.start(), m.group().decode('latin1')))


def cmd_ident(base):
    marks = [
        (b'ACKVIEW.C', 'ACK-3D engine source (Lary Myers)'),
        (b'RATIONAL DOS/4G', 'Rational Systems DOS/4GW extender'),
        (b'WATCOM C Run-Time', 'Watcom C/C++ runtime'),
        (b'Borland C++', 'Borland C++ 1991 runtime'),
        (b'MS Run-Time Library', 'Microsoft C runtime'),
        (b'Knowledge Dynamics', 'Knowledge Dynamics "The Installer"'),
        (b'John W. Ratcliff', 'DIGPAK / MIDPAK (The Audio Solution)'),
        (b'Miles Design', 'Miles Design AIL driver'),
    ]
    for p in sorted(glob.glob(os.path.join(base, '*.EXE')) +
                    glob.glob(os.path.join(base, '*.COM')) +
                    glob.glob(os.path.join(base, '*.OVL'))):
        d = H.read(p)
        tags = [t for m, t in marks if m in d]
        print('%-14s %8d  %s' % (os.path.basename(p), len(d),
                                 '; '.join(tags) or '-'))


def cmd_keywords(base):
    d = H.read(os.path.join(base, 'H.EXE'))
    # Watcom pooled these strings back to back with no clean separator, so
    # slicing the block automatically produces junk prefixes.  Instead look
    # each candidate up by exact bytes and report where it lands.
    print('parser keywords, located by exact match in H.EXE '
          '(block %#x..%#x):' % KEYWORD_BLOCK)
    inf_use = _inf_keyword_use(base)
    for w in KEYWORDS:
        pos = d.find(w.encode('latin1') + b'\0')
        if pos < 0:
            pos = d.find(w.encode('latin1'))
        kind = 'ACK-3D' if w.isupper() or w in ACK_MIXED else 'Deep River'
        used = inf_use.get(w.rstrip(':').lower(), 0)
        print('  %-16s %-11s %#08x  %s'
              % (w, kind, pos, ('%d uses' % used) if used
                 else 'NEVER USED in any shipped level'))
    lo, hi = COPYRIGHT_BLOCK
    print('\ncopyright block at %#x:' % lo)
    for line in re.findall(rb'[\x20-\x7e]{20,}', d[lo:hi]):
        print('  %s' % line.decode('latin1').strip())


def cmd_trig(base):
    """KIT.OVL chunk 0 is ACK-3D's trig.dat; chunk 1 is a second cosine table."""
    import math
    kit = H.read(os.path.join(base, 'KIT.OVL'))
    t0 = H.dtf_chunk(kit, 0)
    longs = struct.unpack('<%di' % (len(t0) // 4), t0)
    n = 1800
    tables = len(longs) // n
    print('KIT.OVL chunk 0: %d bytes = %d int32 = %d tables of %d entries'
          % (len(t0), len(longs), tables, n))
    print('  %d entries per turn means one step is %.1f degrees'
          % (n, 360.0 / n))
    guesses = ['sin * 65536', 'cos * 65536', 'tan * 65536', 'cot * 65536',
               '(1/cos) * 1048576', '(1/sin) * 1048576', 'cos * 16384']
    for t in range(tables):
        b = longs[t * n:(t + 1) * n]
        print('  table %d  %-20s  [0]=%-12d [225]=%-12d [450]=%-12d'
              % (t, guesses[t] if t < len(guesses) else '?',
                 b[0], b[225], b[450]))
    t1 = H.dtf_chunk(kit, 1)
    v = struct.unpack('<%dh' % (len(t1) // 2), t1)
    err = max(abs(v[i] - round(math.cos(2 * math.pi * i / len(v)) * 16384))
              for i in range(len(v)))
    print('\nKIT.OVL chunk 1: %d int16 = cos * 16384 over %d steps per turn'
          % (len(v), len(v)))
    print('  worst deviation from cos: %d of 16384' % err)
    w, h, _pix, _pal = H.decode_pbm(H.dtf_chunk(kit, 2))
    print('\nKIT.OVL chunk 2: IFF PBM %dx%d - the font the EXE calls "font BBM"'
          % (w, h))


def _everything_on_disc(base):
    """Every name the disc can satisfy: real files, archive members, and the
    .gif names the designers left in the level-script comments."""
    have = set(os.path.basename(p).lower()
               for p in glob.glob(os.path.join(base, '*')))
    for t in glob.glob(os.path.join(base, '*.TAB')):
        for n, _o, _s in H.tab_entries(H.read(t)):
            have.add(n.lower())
    for p in glob.glob(os.path.join(base, '*.DTF')):
        inf = H.parse_inf(H.dtf_chunk(H.read(p), 0).decode('latin1'))
        for k in ('walls', 'objbitmaps'):
            for _slot, _res, comment in inf[k]:
                m = re.match(r'([A-Za-z0-9_\-]+\.(?:gif|GIF))', comment)
                if m:
                    have.add(m.group(1).lower())
    return have


def cmd_ghosts(base):
    """File names H.EXE mentions that nothing on the disc can supply.

    Watcom pooled the string table with no padding, so a match usually picks
    up a junk prefix from the previous string; a name counts as resolved when
    any suffix of it exists.
    """
    d = H.read(os.path.join(base, 'H.EXE'))
    have = _everything_on_disc(base)
    templates, unresolved, resolved = set(), set(), 0
    for m in re.finditer(
            rb'[A-Za-z0-9_%.]{3,20}\.(gif|snd|xmi|res|tab|fli|dat|raw|dtf|ovl)',
            d, re.I):
        tok = m.group().decode('latin1').lower()
        if '%' in tok:
            templates.add(tok)
            continue
        if any(tok[i:] in have for i in range(len(tok))):
            resolved += 1
        else:
            unresolved.add(tok)
    print('%d literal names resolve against the disc' % resolved)
    print('\nname templates the code builds at run time:')
    for t in sorted(templates):
        print('  %s' % t)
    print('\nreferenced but not present anywhere:')
    for u in sorted(unresolved):
        print('  %s' % u)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    if cmd == 'strings':
        cmd_strings(base, argv[3] if len(argv) > 3 else 'H.EXE')
    elif cmd == 'ident':
        cmd_ident(base)
    elif cmd == 'keywords':
        cmd_keywords(base)
    elif cmd == 'trig':
        cmd_trig(base)
    elif cmd == 'ghosts':
        cmd_ghosts(base)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
