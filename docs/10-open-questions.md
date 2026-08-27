# 10 — Open questions

The first pass of this repository listed ten open questions. A disassembly of
`H.EXE` — see [01-executables.md](01-executables.md) for how to get at it —
settled most of them, and corrected one answer that was wrong. What follows is
the current state: first what is now closed, then what is still open.

## Closed

| # | Question | Answer | Where |
|---:|---|---|---|
| 1 | What is map plane 0? | The **map** grid: read first, used for the movement and line-of-sight test at `0x1858b`, for the automap at `0x18c4c`, and for the flag tests. The casters use the separate xGrid and yGrid, which are reads 3 and 4. | [04](04-maps.md) |
| 2 | What were the 1040 unused bytes for? | **They do not exist.** xGrid and yGrid are read as 8712 bytes, not 8192 — the array is 4356 uint16 (66 × 66, a guard border) and only the first 4096 are addressed. The apparent gap was a bad assumption about the layout. | [04](04-maps.md), [09](09-easter-eggs-and-leftovers.md) |
| 3 | What is the `extra` field of a map record? | There is no such field. A record is `uint16 cell` plus **three bytes read as a NUL-terminated string**, giving one to three wall values, stored length-prefixed and hung off four per-cell pointer arrays. | [04](04-maps.md) |
| 4 | `LevelType:`, `Timer:`, `Rect:` | All three are fully implemented. `Rect:` `sscanf`s four integers that are read back at `0x14ef8` as a bounding box tested against the object list. An objective system that was never used. | [01](01-executables.md), [09](09-easter-eggs-and-leftovers.md) |
| 5 | 1800 versus 1920 | The engine uses **1800**: the heading is wrapped with `sub …, 0x708` in eighty places and the caster's quadrant boundaries are 450 and 1350. The level scripts' comment is wrong and the designers followed it. | [03](03-level-scripts.md) |
| 6 | How is `God Mode!` triggered? | `-g` or `/g`, case-insensitive, in the switch ladder at `0x131f6`. It sets `0x31426`, which is checked in exactly two places, both guarding the damage call at `0x18448`. Six other switches exist, including `-l<n>` for level select. | [01](01-executables.md) |
| 7 | What sample rate are the `.SND` files? | **11,000 Hz**, written into `SNDSTRUC.frequency` at `0x1caa1`, `0x1cb46` and `0x1cbe1`. | [06](06-audio.md) |
| 8 | Which title screen does the game show? | **Both**, in sequence: `slobtitl.gif`, then `mlogo.fli`, then `hurl.gif`. The intro is a straight-line function at `0x12afe`. | [09](09-easter-eggs-and-leftovers.md) |
| 9 | The wall flag bits | `0x10` door, `0x40` (with `0x10`) locked, `0x20` sliding/secret, `0x08` see-through, `0x02`/`0x04` multi-height. `0x80` never occurs and its code path is dead. | [04](04-maps.md) |
| 10 | What is `LoadType:` for? | An ACK-3D field: `atoi` into a single byte at `ACKENG + 0xe461`. Every level says 1. | [03](03-level-scripts.md) |

## Still open

### A. What does `-c` do?

The seventh command-line switch sets `[0x31428]` to 1, and that global gates
three separate blocks in the main loop at `0x11da3`, `0x11ead` and `0x11ec5`,
each of which is *also* gated on a second per-frame byte. It is not a cheat
message like `-g` or `-n`, and it prints nothing. Tracing what those three
blocks do needs more than a static read.

### B. What exactly do the trailing per-cell records draw?

The structure is settled: one to three wall slots attached to a cell and to
its east and south neighbours, in two pointer arrays that the wall renderer
installs at `0x84ed8` and `0x84edc`, with a third at `0x84ee4` used by the
see-through path. Together with the `0x02`/`0x04` flags and the
`XRAYMULTI`/`YRAYMULTI` routines this is the engine's multi-height wall
support — but the vertical placement of the extra slices, and why nine of the
eleven levels ship only copied boilerplate here, are not established.

### C. What separates flag `0x02` from flag `0x04`?

Both are read only by the multi-height casters, which test them together
(`test cx, 0x600`) and then compare the low byte against a height global at
`0x424c4`/`0x424c6`. `0x02` appears on 173 cells in two levels, `0x04` on 20
cells in one, all `marb1a.gif`. Whether the two bits mean different heights,
different orientations or something else is not resolved.

### D. What is `0x01`, and why only ever with `0x08`?

185 cells carry `0x09` and none carry `0x01` alone. The automap builder tests
exactly this bit (`and ch, 1`) and paints those cells a different colour. The
textures are arches, black tiles and blank tiles — openings rather than
surfaces — which suggests "passable gap", but nothing in the caster confirms
it.

### E. Where did `slobad.gif` go?

It is the first picture the intro loads, and no archive on the disc contains
it. Whether the intro survives the failure or the branch is simply never
reached would need the game running.

### F. The multi-height path in practice

`XRAYMULTI` and `YRAYMULTI` are linked in and the shipped maps do flag cells
for them — 25 in level 8, 36 in level 10. What that looks like on screen is
not documented here.
