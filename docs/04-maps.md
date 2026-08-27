# 04 — The maps

Chunk 1 of every `.DTF` is the map. It is uncompressed, fixed-layout and, as
shipped, has a 1040-byte hole in the middle of it that nobody ever cleared.

```sh
python tools/hurlmap.py "<install>" info
python tools/hurlmap.py "<install>" ascii   LEV1 0
python tools/hurlmap.py "<install>" png     LEV1 lev1.png
python tools/hurlmap.py "<install>" tail    LEV1
python tools/hurlmap.py "<install>" objects LEV1
python tools/hurlmap.py "<install>" runs
```

## Layout

```
offset   size            contents
0        49152           uint16 plane[6][64][64]
49152    1040            unused - never written, contents are whatever
                         was in the writer's buffer
50192    2               uint16 count
50194    count * 5       trailing records
```

Total size is therefore `50194 + 5 * count`, which reproduces all four sizes
that occur — 50219, 50244, 50284 and 50299 bytes — exactly, for all eleven
files. The `count` field is at offset 50192 in every one of them.

The grid is **64 × 64 cells at 64 world units per cell**, so a level is 4096
units square. That follows from the player start positions in the level
scripts: divide by 64 and ten of the eleven land on an empty wall cell.

## The six planes

| Plane | Cells set (LEV1) | Role |
|---:|---:|---|
| 0 | 747 | walls — the full block outline |
| 1 | 76 | **objects**: the value is an instance number from the level script's `ObjDesc:` block |
| 2 | 691 | walls, biased to **vertical** runs |
| 3 | 609 | walls, biased to **horizontal** runs |
| 4 | 3,693 | floor |
| 5 | 610 | ceiling |

**Plane 1 is unambiguous.** Its non-zero values are exactly the `Number:`
values of the level's object definitions, each appearing at most once — in
`LEV1`, 76 distinct values in 1…104 against 104 definitions. Cross-referencing
is what `hurlmap.py objects` does:

```
  (39,48) #73  PIG-3                  type 1
  (57,51) #22  RED key                type 11
  (13,52) #40  CEREAL BOX-2           type 131
```

Between 76 and 150 of each level's definitions are actually placed; the rest
are never referenced by the grid at all.

**Planes 2 and 3 are the engine's two wall grids.** `H.EXE` prints
`Xwall %d hit` and `Ywall %d hit` as separate debug messages, so the caster
keeps walls perpendicular to X apart from walls perpendicular to Y. Measuring
mean run length in each direction separates them cleanly and consistently
across every level:

| Level | Plane | Mean horizontal run | Mean vertical run |
|---|---|---:|---:|
| LEV1 | 2 | 2.36 | **2.92** |
| LEV1 | 3 | **3.31** | 2.14 |
| LEV2 | 2 | 2.53 | **2.97** |
| LEV2 | 3 | **3.69** | 2.59 |
| LEV6 | 2 | 2.64 | **3.43** |
| LEV6 | 3 | **3.13** | 2.87 |

Plane 2 favours vertical runs (north–south walls, hit by rays travelling in X)
and plane 3 favours horizontal runs. Plane 0 is balanced in both directions
and is neither the union nor the intersection of the other two, so its exact
relationship to them is left open ([10](10-open-questions.md)).

Planes 4 and 5 are floor and ceiling, and they behave the way you would
expect: the floor is almost fully covered in every level (3,640–3,731 of 4,096
cells) with a handful of distinct tiles, while the ceiling varies enormously —
610 cells in the outdoor level 1, **all 4,096** in levels 3 and 7, the two
levels whose scripts also set `TopColor: 0`. Those are the indoor levels.

An ASCII dump of plane 0 of `LEV1` reads as a recognisable trailer park, with
a solid border wall, a bus, a garage, fenced yards and a nine-by-eleven room
in the top-left corner:

```
 0 ################################################################
 1 #........#.....................................................#
 …
11 ##########.....................................................#
…
29 #........................########################..............#
```

That corner room is worth a second look — the object plane places instance
numbers 1–15 and 78–86 inside and above it, including at cells that plane 0
marks as solid border wall. See
[09-easter-eggs-and-leftovers.md](09-easter-eggs-and-leftovers.md).

## Wall cell encoding

Most non-zero cells in the three wall planes are a small number — a slot in
the level script's wall table. 2,176 cells across the game are larger than
255, and they decode as `flags << 8 | slot`:

```
python tools/hurlmap.py "<install>" walls
```

| Flags | Cells | Wall textures the slot names | Reading |
|---:|---:|---|---|
| `0x50` | 142 | `lockred.gif`, `lockgren.gif`, `lockblue.gif` | **locked door** |
| `0x10` | 307 | `DOOR1.GIF`, `door-1/2/3`, `DINRDOOR.GIF`, `HAPYDOOR.GIF` | **door** |
| `0x18` | 4 | `door3.GIF` | door + `0x08` |
| `0x08` | 1,321 | picket fence, pole fence, hedge, grass line, `shower2/3.gif` | **see-through wall** |
| `0x09` | 185 | `arch1.gif`, `black.gif`, `blank.gif`, `BLANK.GIF` | `0x08` + `0x01` |
| `0x02` | 173 | `wall2.gif`, `CLASS-1.GIF`, `LOCKER2/4.GIF` | ? |
| `0x04` | 20 | `marb1a.gif` | ? |
| `0x20` | 23 | `hedge`, `LIBRARY4.GIF`, `SIDETILE.GIF` | ? |

Two of those are settled by the data itself. **`0x10` is a door**: every one
of the 307 cells names a texture whose file is called some kind of door.
**`0x50` is a locked door**: 132 of its 142 cells land on exactly the slot the
level script gave to `RedDoor:`, `GreenDoor:` or `BlueDoor:` — 53 green, 47
red, 32 blue — and the textures are `lockred`, `lockgren`, `lockblue`. So bit
`0x10` marks a door and bit `0x40` marks it as needing a key.

**`0x08` is transparency.** Its 1,321 cells are picket fences, pole fences,
hedges, grass lines and shower curtains — every masked texture in the game and
nothing else. `0x09` adds `0x01` and lands on arches, black and blank tiles,
which are openings rather than surfaces.

`0x01` alone, `0x02`, `0x04` and `0x20` are not resolved
([10-open-questions.md](10-open-questions.md)).

## The 1040-byte hole

Between the grids and the record count there are 1040 bytes — 520 `uint16`
slots — that no level uses. In five of the eleven files they are zero. In the
other six they contain a **single value repeated hundreds of times**:

| File | Filler |
|---|---|
| LEV3, LEV7 | `19` repeated 488 / 515 times |
| LEV4, LEV8 | `29` repeated 44 / 48 times, rest zero |
| LEV6 | `16` repeated 429 times |
| LEV9 | `13` repeated 45 times |

Those are tile indices, and a long run of one tile index is what the tail of a
floor or ceiling plane fill looks like. The writer allocated a buffer larger
than it filled and wrote the whole thing out, so six of the ten shipped levels
carry a fossil of the level compiler's own working memory. What the field was
*meant* to be is unresolved.

## The trailing records

```c
struct MapRecord {         /* 5 bytes, little-endian */
    uint16_t cell;         /* 0..4095, row-major: y = cell / 64, x = cell % 64 */
    uint8_t  value;
    uint16_t extra;
};
```

Records are sorted by ascending `cell` in all eleven files. Counts are small —
5 to 21 per level.

`value` is a wall slot from the level script's wall table, and the cells are
walls. In `LEV1` the records at cells 1882–1886 are five consecutive cells of
one wall run carrying values 22, 21, 17, 18, 20 — which the wall table names
`stat2c.GIF`, `stat2b.gif`, `sign1.gif`, `sign2.gif`, `stat2a.gif`. So the
list overrides the texture of individual wall faces: a shop sign spread across
five tiles of an otherwise brick wall.

`extra` is zero in every record except the two described below.

### Five records are in all eleven files

| Bytes | cell | (x, y) | value | extra |
|---|---:|---|---:|---:|
| `c1 01 00 00 00` | 449 | (1, 7) | 0 | 0 |
| `87 02 05 00 00` | 647 | (7, 10) | 5 | 0 |
| `95 02 06 03 00` | 661 | (21, 10) | 6 | 3 |
| `03 03 02 05 06` | 771 | (3, 12) | 2 | 1541 |
| `e6 08 10 31 24` | 2278 | (38, 35) | 16 | 9265 |

Five more (`804/25`, `1071/13`, `1074/13`, `1990/22`, `2246/20`) appear in
seven of the eleven. The two records with nonsensical `extra` values — 1541
and 9265, where every genuine record has 0 — are also the two that never vary.
The whole prefix is boilerplate inherited from whichever file the designers
copied to start a new level, and it was never removed. See
[09-easter-eggs-and-leftovers.md](09-easter-eggs-and-leftovers.md).
