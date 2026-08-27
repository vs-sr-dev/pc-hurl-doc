# 04 — The maps

Chunk 1 of every `.DTF` is the map. The layout below is not inferred from the
data: it is the sequence of `fread` calls in `AckReadMapFile`, which sits at
`0x1c270` in the loaded image and can be read directly
([01-executables.md](01-executables.md) explains how to get there).

```sh
python tools/hurlmap.py "<install>" info
python tools/hurlmap.py "<install>" ascii   LEV1 0
python tools/hurlmap.py "<install>" png     LEV1 lev1.png
python tools/hurlmap.py "<install>" walls
python tools/hurlmap.py "<install>" tail    LEV1
python tools/hurlmap.py "<install>" shared
python tools/hurlmap.py "<install>" objects LEV1
```

## Layout

Six reads, in this order, of exactly these sizes:

| # | Bytes | Destination in the loader | Role |
|---:|---:|---|---|
| 1 | 8,192 | `*(void**)0x40e88` | the **map** grid — collision, the automap, the flag tests |
| 2 | 8,192 | `*(void**)0x40e58` | **ObjGrid** — object instance numbers |
| 3 | **8,712** | caller's buffer + 0 | **xGrid** |
| 4 | **8,712** | caller's buffer + 8,712 | **yGrid** |
| 5 | 8,192 | `0x36f6c` | **floor** |
| 6 | 8,192 | `0x34b6c` | **ceiling** |

then a `uint16` count and that many 5-byte records.

```
offset   size            contents
0        8192            uint16 map[4096]
8192     8192            uint16 objects[4096]
16384    8712            uint16 xGrid[4356]
25096    8712            uint16 yGrid[4356]
33808    8192            uint16 floor[4096]
42000    8192            uint16 ceiling[4096]
50192    2               uint16 count
50194    count * 5       records
```

Total is `50194 + 5 * count`, which reproduces all four sizes that occur —
50219, 50244, 50284 and 50299 — exactly, for all eleven files.

**xGrid and yGrid are 4,356 entries, not 4,096.** 4356 = 66 × 66: the grid is
allocated with a one-cell guard band, and the map file stores the whole array.
Only the first 4,096 entries are addressed as the 64 × 64 grid. The remaining
260 are empty in eighteen of the twenty-two shipped arrays and hold a handful
of stray values in the other four. The same 4,356 sizing shows up again in the
in-memory layout, where the per-cell record arrays are 4,356 × 4 bytes each.

## Cell size and world extent

The X ray-caster bounds-checks its ray before every grid lookup:

```
cmp edx, 0x1000        ; x limit  = 4096
cmp eax, 0x10000000    ; y limit  = 4096.0 in 16.16
sar eax, 0x10          ; y integer
and eax, 0xffffffc0    ; (y >> 6) * 64
sar edx, 6             ; x >> 6
add eax, edx           ; cell index, row-major
```

So the world is **4096 × 4096 units over a 64 × 64 grid — 64 units per cell**,
row-major, and the level scripts' `xPlayer:`/`yPlayer:` are world units.

## The six grids

| Grid | Cells set (LEV1) | What reads it |
|---|---:|---|
| map | 747 | the movement/line-of-sight test at `0x1858b`, the automap at `0x18c4c`, the flag tests |
| objects | 76 | both ray-casters, first lookup: the value is an object instance number |
| xGrid | 691 | X ray-caster, second lookup (`*(void**)0x40ebc`) |
| yGrid | 726 | Y ray-caster, second lookup (`*(void**)0x40e70`) |
| floor | **4096** | the floor renderer, and the `Hitgrid:` damage test |
| ceiling | 90 | the ceiling renderer |

**The object grid is confirmed by both ends.** Its non-zero values are exactly
the `Number:` values of the level's object definitions, each appearing at most
once, and the caster reads it first at every step:

```
mov ebx, [0x40e58]          ; ObjGrid
mov ax,  [ebx+eax]
or  ax, ax / je  no_object
and eax, 0xff               ; object number is the low byte
cmp ax, 0xff / je panic     ; "Screw up in XRAY$"
...append to ObjectsSeen[] at 0x3ab8c, count at 0x424d0...
```

`ObjectsSeen` and its 255 sentinel are the same names that appear in the
retail build's assertion strings (`DANGER: ObjectsSeen[%d] is 255`).

**xGrid and yGrid split by orientation**, which the loader's naming implies and
the data confirms. Mean run length, horizontal against vertical:

| Level | Grid | h-run | v-run |
|---|---|---:|---:|
| LEV1 | xGrid | 2.36 | **2.92** |
| LEV1 | yGrid | **3.88** | 2.05 |
| LEV2 | xGrid | 2.53 | **2.97** |
| LEV2 | yGrid | **4.03** | 2.36 |
| LEV6 | xGrid | 2.64 | **3.43** |
| LEV6 | yGrid | **3.43** | 2.66 |

xGrid favours vertical runs — north–south walls, the ones a ray travelling in
X hits — and yGrid favours horizontal ones, in every level.

**The floor is fully covered in every level** — 4,096 of 4,096 cells, with
four to twenty-five distinct tiles. The ceiling is what varies: 90 cells in
the outdoor level 1, all 4,096 in level 3 and 4,033 in level 7, the two levels
whose scripts also set `TopColor: 0`. Those are the indoor levels.

`Hitgrid:` is checked against the **floor** grid, at `0x14f4c`:

```
mov dx, [edx*2 + 0x36f6c]   ; floor[cell]
cmp ebx, edx / jne skip
cmp word [0x31426], 0       ; god mode?
jne skip
mov edx, 2                  ; two points of damage
call 0x18448
```

So `Hitgrid:` names a **floor** tile you take damage for standing on — which
is exactly what the designers' comment in the level script says, and why the
`-g` switch skips it.

## Wall cell encoding

Most non-zero cells are a small number, a slot in the level script's wall
table. 2,176 cells across the game are larger than 255, and they decode as
`flags << 8 | slot`. Three flags are settled by the engine code, two more by
what they land on:

| Flags | Cells | Engine evidence | Reading |
|---:|---:|---|---|
| `0x10` | 308 | `test cx, 0x3000` in both casters enters the door path | **door** |
| `0x50` | 142 | same path; 132 of 142 land on the slot the level gave `RedDoor:`/`GreenDoor:`/`BlueDoor:` | **locked door** |
| `0x20` | 23 | shares the door path, but the draw code gives it a 0x3f travel where a `0x10` door gets 0x1f | **sliding/secret wall** |
| `0x08` | 1,321 | the drawer stashes the cell value, **writes 0 into the grid** so the ray carries on, and chains a second draw record | **see-through wall** |
| `0x09` | 185 | `0x08` plus a bit the automap tests with `and ch, 1` | see-through, drawn differently on the map |
| `0x02` `0x04` | 173, 20 | only `XRAYMULTI`/`YRAYMULTI` look at them: `test cx, 0x600`, then the low byte is compared against a height global | **multi-height wall** |
| `0x18` | 4 | `0x10` + `0x08` | a see-through door |

Nothing in the game ever sets `0x80`, and the `0x8000` path in the caster is
therefore dead code.

The rare flags are worth listing in full, because they are so few:

| Level | Flag | Cells | Textures |
|---|---:|---:|---|
| LEV8 | `0x02` | 25 | `LOCKER2/3/4.GIF`, `CLASS-1*.GIF` — the school |
| LEV10 | `0x02` | 32 | `wall2.gif`, `wall2b.gif` |
| LEV10 | `0x04` | 4 | `marb1a.gif`, at (29,33) (39,33) (29,42) (39,42) — the four corners of one block |
| LEV2 | `0x20` | 4 | `sidetile`, and two adjacent `hedge` cells at (2,36) (2,37) |
| LEV4 | `0x20` | 3 | `SIDETILE.GIF`, two adjacent `LIBRARY4.GIF` at (57,20) (57,21) |
| LEV10 | `0x20` | 2 | two adjacent `trlr-5h.gif` |
| LEV5 | `0x18` | 2 | two adjacent `door3.GIF` |

Every `0x20` group is a two-cell run of hedge, bookcase or trailer siding —
the shape of a secret passage, and there are exactly nine of them in the game.

## The trailing records

`AckReadMapFile` finishes with:

```
fread(&count, 1, 2, fp)
for i in 0..count-1:
    fread(&cell, 1, 2, fp)      ; uint16
    p = malloc(4)
    ptrA[cell] = ptrA[cell+1] = p
    ptrB[cell] = ptrB[cell+64] = p
    fread(buf, 1, 3, fp)        ; three bytes
    buf[3] = 0
    n = min(strlen(buf), 3)
    p[0] = n;  memcpy(p+1, buf, n)
```

So a record is **`uint16 cell` followed by three bytes treated as a
NUL-terminated string** — a list of one to three byte values, stored
length-prefixed. It is hung off four per-cell pointer arrays: `cell` and
`cell+1` in one, `cell` and `cell+64` in the other — the east and south
neighbours, i.e. the four faces the two wall grids see. The renderer installs
those two arrays at `0x84ed8` and `0x84edc`, and the see-through path reads a
third at `0x84ee4`.

The values are wall slots. In `LEV1` the records at (26,29) through (30,29)
carry 22, 21, 17, 18, 20 over five consecutive cells whose own textures are
`stat2.gif`, `sign1.gif`, `sign2.gif`, `stat2a.gif`, `stat2b.gif` — a stack of
further wall bitmaps for cells that already have one. Together with the
`0x02`/`0x04` flags and the `XRAYMULTI` routines this is the engine's
**multi-height wall** support; the exact vertical placement is not verified
here.

### Ten records are copied boilerplate

`tools/hurlmap.py shared` sorts them by how many level files contain them:

| Copies | Cell | Payload |
|---:|---|---|
| **11** | 449 (1, 7) | *(empty — length 0)* |
| **11** | 647 (7, 10) | 5 |
| **11** | 661 (21, 10) | 6, 3 |
| **11** | 771 (3, 12) | 2, 5, 6 |
| **11** | 2278 (38, 35) | 16, 49, 36 |
| 7 | 804 (36, 12) | 25 |
| 7 | 1071 (47, 16) | 13 |
| 7 | 1074 (50, 16) | 13 |
| 7 | 1990 (6, 31) | 22 |
| 7 | 2246 (6, 35) | 20 |

Counting each file's records against that boilerplate set:

| File | Records | Boilerplate | Its own |
|---|---:|---:|---:|
| LEV1 | 21 | 10 | **11** |
| LEV10 | 18 | 10 | **8** |
| LEV3, LEV5, LEV6, LEV7, LEV9 | 10 | 10 | 0 |
| LEV2, LEV4, LEV8, PICS | 5 | 5 | 0 |

**Nine of the eleven map files contain nothing but copied boilerplate.** Only
levels 1 and 10 add records of their own, and in most files the cells the
boilerplate names are empty in all three wall grids — the records point at
nothing at all. Somebody built a template level early on, and every level
since carried its leftovers to the retail disc.
