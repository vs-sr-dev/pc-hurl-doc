"""Load the Linear Executable inside H.EXE and disassemble it.

`H.EXE` is a DOS/4GW bound executable: an MZ stub followed by an `LE` image.
This module rebuilds the flat 32-bit address space the extender would create,
so the other reports can talk about real linear addresses.

    python tools/hurlle.py <install> info
    python tools/hurlle.py <install> xref  <addr|string>
    python tools/hurlle.py <install> dis   <addr> [count]
    python tools/hurlle.py <install> func  <addr>          # to the first ret
    python tools/hurlle.py <install> strings                # addr -> text
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hurllib as H  # noqa: E402


class LE(object):
    """A loaded LE image: objects mapped at their relocation bases."""

    def __init__(self, data):
        off = struct.unpack_from('<H', data, 0x3c)[0]
        if data[off:off + 2] != b'LE':
            off = data.find(b'LE\x00\x00')
        if off < 0 or data[off:off + 2] != b'LE':
            raise ValueError('no LE header')
        self.base_off = off
        h = data[off:]
        self.pages = struct.unpack_from('<I', h, 0x14)[0]
        self.eip_obj = struct.unpack_from('<I', h, 0x18)[0]
        self.eip = struct.unpack_from('<I', h, 0x1c)[0]
        self.page_size = struct.unpack_from('<I', h, 0x28)[0]
        self.last_page = struct.unpack_from('<I', h, 0x2c)[0]
        obj_off = struct.unpack_from('<I', h, 0x40)[0]
        self.nobj = struct.unpack_from('<I', h, 0x44)[0]
        map_off = struct.unpack_from('<I', h, 0x48)[0]
        data_off = struct.unpack_from('<I', h, 0x80)[0]

        self.objects = []
        for i in range(self.nobj):
            vsize, base, flags, pidx, pcnt, _r = struct.unpack_from(
                '<6I', h, obj_off + i * 24)
            self.objects.append({'vsize': vsize, 'base': base, 'flags': flags,
                                 'page_index': pidx, 'page_count': pcnt})

        # LE page map entry: 3-byte big-endian page number + 1 flag byte
        self.segments = []
        self.page_of = {}          # global page number -> (object index, addr)
        for oi, o in enumerate(self.objects):
            buf = bytearray(o['vsize'])
            for n in range(o['page_count']):
                e = map_off + (o['page_index'] - 1 + n) * 4
                num = (h[e] << 16) | (h[e + 1] << 8) | h[e + 2]
                size = self.page_size
                if num == self.pages and self.last_page:
                    size = self.last_page
                src = data_off + (num - 1) * self.page_size
                chunk = data[src:src + size]
                buf[n * self.page_size:n * self.page_size + len(chunk)] = chunk
                self.page_of[o['page_index'] + n] = (oi, n * self.page_size)
            self.segments.append([o['base'], bytearray(buf), o['flags']])

        self._fixups(h)
        self.segments = [(b, bytes(s), f) for b, s, f in self.segments]

    def _fixups(self, h):
        """Apply the fixup records, so immediates hold real linear addresses.

        Without this the stored immediates are offsets inside the target
        object and no cross-reference search finds anything.
        """
        fp_off = struct.unpack_from('<I', h, 0x68)[0]
        fr_off = struct.unpack_from('<I', h, 0x6c)[0]
        self.fixups = 0
        for page in range(1, self.pages + 1):
            if page not in self.page_of:
                continue
            oi, page_addr = self.page_of[page]
            start = struct.unpack_from('<I', h, fp_off + (page - 1) * 4)[0]
            end = struct.unpack_from('<I', h, fp_off + page * 4)[0]
            p = fr_off + start
            stop = fr_off + end
            while p < stop:
                src, flags = h[p], h[p + 1]
                p += 2
                srcs = []
                if src & 0x20:                       # source list
                    cnt = h[p]
                    p += 1
                    listp = p
                    p += cnt * 2
                else:
                    srcs = [struct.unpack_from('<h', h, p)[0]]
                    p += 2
                if (flags & 3) != 0:                 # not an internal fixup
                    break
                if flags & 0x40:
                    objnum = struct.unpack_from('<H', h, p)[0]
                    p += 2
                else:
                    objnum = h[p]
                    p += 1
                target = 0
                if (src & 0x0f) != 2:
                    if flags & 0x10:
                        target = struct.unpack_from('<I', h, p)[0]
                        p += 4
                    else:
                        target = struct.unpack_from('<H', h, p)[0]
                        p += 2
                if src & 0x20:
                    srcs = [struct.unpack_from('<h', h, listp + i * 2)[0]
                            for i in range(cnt)]
                if (src & 0x0f) != 7:                # only 32-bit offsets
                    continue
                value = self.objects[objnum - 1]['base'] + target
                for s in srcs:
                    at = page_addr + s
                    buf = self.segments[oi][1]
                    if 0 <= at <= len(buf) - 4:
                        struct.pack_into('<I', buf, at, value)
                        self.fixups += 1

    # ------------------------------------------------------------- addressing

    def read(self, addr, n):
        for base, buf, _f in self.segments:
            if base <= addr < base + len(buf):
                return buf[addr - base:addr - base + n]
        return b''

    def contains(self, addr):
        return any(b <= addr < b + len(s) for b, s, _f in self.segments)

    def find(self, needle):
        """All linear addresses at which `needle` occurs."""
        out = []
        for base, buf, _f in self.segments:
            i = buf.find(needle)
            while i >= 0:
                out.append(base + i)
                i = buf.find(needle, i + 1)
        return out

    def xref(self, addr):
        """Addresses whose 4 bytes equal `addr` - i.e. immediate references."""
        return self.find(struct.pack('<I', addr))

    def code_segment(self):
        return self.segments[0]


def load(base):
    return LE(H.read(os.path.join(base, 'H.EXE')))


# ------------------------------------------------------------ disassembling

def _md():
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = False
    return md


def dis(le, addr, count=40):
    md = _md()
    code = le.read(addr, count * 12 + 32)
    out = []
    for ins in md.disasm(code, addr):
        out.append((ins.address, ins.bytes, ins.mnemonic, ins.op_str))
        if len(out) >= count:
            break
    return out


def dis_func(le, addr, limit=600):
    """Linear sweep until the first `ret` at depth 0, or `limit` instructions."""
    md = _md()
    code = le.read(addr, limit * 12)
    out = []
    for ins in md.disasm(code, addr):
        out.append((ins.address, ins.bytes, ins.mnemonic, ins.op_str))
        if ins.mnemonic in ('ret', 'retf') or len(out) >= limit:
            break
    return out


def fmt(rows, le=None, notes=None):
    lines = []
    for addr, raw, mn, ops in rows:
        note = ''
        if notes:
            for m in re.finditer(r'0x[0-9a-f]+', ops):
                v = int(m.group(), 16)
                if v in notes:
                    note = '  ; ' + notes[v]
                    break
        lines.append('%08x  %-20s %-7s %s%s'
                     % (addr, raw.hex(' '), mn, ops, note))
    return '\n'.join(lines)


def string_map(le, minlen=4):
    """Linear address -> NUL-terminated printable string, for annotation."""
    out = {}
    for base, buf, _f in le.segments:
        for m in re.finditer(rb'[\x20-\x7e]{%d,}\x00' % minlen, buf):
            out[base + m.start()] = m.group()[:-1].decode('latin1')
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    base, cmd = argv[1], argv[2]
    le = load(base)
    if cmd == 'info':
        print('LE header at file offset %#x' % le.base_off)
        print('  pages %d of %d bytes (last %d), entry %d:%#x'
              % (le.pages, le.page_size, le.last_page, le.eip_obj, le.eip))
        for i, o in enumerate(le.objects):
            print('  object %d: base %#010x  vsize %#x (%d)  flags %#x  '
                  'pages %d' % (i + 1, o['base'], o['vsize'], o['vsize'],
                                o['flags'], o['page_count']))
        ep = le.objects[le.eip_obj - 1]['base'] + le.eip
        print('  entry point %#010x' % ep)
    elif cmd == 'strings':
        for a, s in sorted(string_map(le).items()):
            print('%08x  %s' % (a, s))
    elif cmd == 'xref':
        arg = argv[3]
        if arg.startswith('0x'):
            targets = [int(arg, 16)]
        else:
            targets = le.find(arg.encode('latin1') + b'\0')
            print('string %r at %s' % (arg, [hex(t) for t in targets]))
        for t in targets:
            print('references to %#x: %s'
                  % (t, ' '.join(hex(x) for x in le.xref(t))))
    elif cmd == 'dis':
        n = int(argv[4]) if len(argv) > 4 else 40
        print(fmt(dis(le, int(argv[3], 16), n), le, string_map(le)))
    elif cmd == 'func':
        print(fmt(dis_func(le, int(argv[3], 16)), le, string_map(le)))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
