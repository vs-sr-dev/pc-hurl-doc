"""The audio side: raw .SND effects, XMIDI music, the OPL patch bank.

    python tools/hurlaudio.py <install> snd   <outdir> [rate]
    python tools/hurlaudio.py <install> banks <outdir> [rate]   # BOB*/END/INTRO
    python tools/hurlaudio.py <install> xmi                     # music inventory
    python tools/hurlaudio.py <install> opl                     # FAT.OPL bank
    python tools/hurlaudio.py <install> drivers                 # DIGPAK/MIDPAK
"""
import glob
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402

# .SND files carry no header at all, so the rate is the caller's business.
# 11025 Hz is the usual DIGPAK rate for this era and gives plausible lengths.
DEFAULT_RATE = 11025


def cmd_snd(base, outdir, rate):
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(os.path.join(base, '*.SND'))):
        raw = H.read(p)
        out = os.path.basename(p)[:-4].lower() + '.wav'
        with open(os.path.join(outdir, out), 'wb') as f:
            f.write(H.snd_to_wav(raw, rate))
        n += 1
    print('wrote %d effects to %s at %d Hz' % (n, outdir, rate))


def cmd_banks(base, outdir, rate):
    """The per-level speech banks: BOB1..BOB10, plus END and the intro."""
    for tab in sorted(glob.glob(os.path.join(base, '*.TAB'))):
        name = os.path.basename(tab)[:-4]
        members = list(H.res_entries(base, name))
        if not any(m.lower().endswith('.snd') for m, _ in members):
            continue
        d = os.path.join(outdir, name.lower())
        os.makedirs(d, exist_ok=True)
        for nm, blob in members:
            if not nm.lower().endswith('.snd'):
                continue
            with open(os.path.join(d, nm[:-4] + '.wav'), 'wb') as f:
                f.write(H.snd_to_wav(blob, rate))
        print('%-8s %2d clips -> %s' % (name, len(members), d))


def xmi_info(data):
    """Sub-song count and total FORM XMID size of a Miles XMIDI file."""
    if data[:4] != b'FORM' or data[8:12] != b'XDIR':
        return None
    nsongs = struct.unpack_from('<H', data, 0x14)[0]
    songs = data.count(b'FORM') - 1
    return nsongs, songs


def cmd_xmi(base):
    import hashlib
    seen = {}
    print('%-14s %8s %6s  %s' % ('file', 'bytes', 'songs', 'note'))
    for p in sorted(glob.glob(os.path.join(base, '*.XMI'))):
        d = H.read(p)
        info = xmi_info(d)
        h = hashlib.sha1(d).hexdigest()
        note = ''
        if h in seen:
            note = 'byte-identical to %s' % seen[h]
        else:
            seen[h] = os.path.basename(p)
        print('%-14s %8d %6s  %s' % (os.path.basename(p), len(d),
                                     info[0] if info else '?', note))


def cmd_opl(base):
    """FAT.OPL: a flat patch directory followed by fixed-size FM records."""
    d = H.read(os.path.join(base, 'FAT.OPL'))
    first = struct.unpack_from('<HI', d, 0)[1]
    ndir = first // 6
    entries = [struct.unpack_from('<HI', d, i * 6) for i in range(ndir)]
    sizes = set()
    for i, (_p, off) in enumerate(entries):
        nxt = entries[i + 1][1] if i + 1 < len(entries) else len(d)
        sizes.add(nxt - off)
    print('FAT.OPL  %d bytes' % len(d))
    print('  directory: %d records of {uint16 patch, uint32 offset} = %d bytes'
          % (ndir, ndir * 6))
    print('  patch data starts at %#x, record size(s) %s'
          % (first, sorted(sizes)))
    print('  patch numbers %d..%d' % (entries[0][0], entries[-1][0]))
    melodic = [p for p, _o in entries if p < 128]
    print('  %d melodic (0..127), %d further patches (%s)'
          % (len(melodic), ndir - len(melodic),
             ', '.join(str(p) for p, _o in entries[len(melodic):][:8]) + ' ...'))


def cmd_drivers(base):
    """Identify the DIGPAK / MIDPAK .COM drivers and the Miles .ADV set."""
    print('=== DIGPAK / MIDPAK loadable drivers (*.COM) ===')
    for p in sorted(glob.glob(os.path.join(base, '*.COM'))):
        d = H.read(p)
        strs = [m.group().decode('latin1')
                for m in re.finditer(rb'[\x20-\x7e]{6,}', d[:512])]
        kind = 'MIDPAK' if any('MIDPAK' in s for s in strs) else (
            'DIGPAK' if any('DIGPAK' in s for s in strs) else '?')
        desc = strs[1] if len(strs) > 1 else ''
        print('  %-13s %6d  %-7s %s' % (os.path.basename(p), len(d), kind,
                                        desc))
    print('\n=== Miles AIL music drivers (*.ADV + *.ADD) ===')
    for p in sorted(glob.glob(os.path.join(base, '*.ADD'))):
        add = H.read(p).decode('latin1').splitlines()
        adv = p[:-4] + '.ADV'
        title = ''
        if os.path.exists(adv):
            m = re.search(rb'[\x20-\x7e]{12,}', H.read(adv)[40:400])
            title = m.group().decode('latin1').strip() if m else ''
        print('  %-13s %-32s %s' % (os.path.basename(p),
                                    add[0].strip() if add else '', title))


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    rate = int(argv[4]) if len(argv) > 4 else DEFAULT_RATE
    if cmd == 'snd':
        cmd_snd(base, argv[3], rate)
    elif cmd == 'banks':
        cmd_banks(base, argv[3], rate)
    elif cmd == 'xmi':
        cmd_xmi(base)
    elif cmd == 'opl':
        cmd_opl(base)
    elif cmd == 'drivers':
        cmd_drivers(base)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
