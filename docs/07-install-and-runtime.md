# 07 — Installing and running

H.U.R.L. runs **from the CD**. The installer copies about a megabyte of sound
drivers to the hard disk, writes two batch files, and runs the sound setup;
the game itself, the levels and all the art stay on the disc.

## `INSTALL.DAT` — the installer script

`INSTALL.EXE` is Knowledge Dynamics' *The Installer*, and `INSTALL.DAT` is its
script — 4,707 bytes of readable source with C-style comments, shipped as-is.

```
// Installation program for HURL. Only for DOS.

@DefineProject
   @Name     = "H.U.R.L."
   @Version  = "1.0"
   @Subdir   = "\\hurl\\"
   @OutDrive = C
   @Group    = "A"
   @Terse
   @Immediate = 1
@EndProject
```

It declares `@NEEDK = 1000000` (1 MB required), suppresses floppy and CD-ROM
drives from the destination list with `@Suppress(0,17)`, and copies exactly
**60 files** — every `.COM` driver, every `.ADV`/`.ADD` pair, `FAT.OPL`,
`README.TXT` and the three setup programs. No game data at all.

The `@Finish` block writes the two launchers by hand:

```
@Write("HURL.BAT","wt","@CDRomFirst:\n")
@Write("HURL.BAT","at","cd \\\n")
@Write("HURL.BAT","at","h -d @Outdrive:\\@Subdir\\ %1 %2 %3 %4 %5 %6 %7 \n")
@Write("HURL.BAT","at","@Outdrive:\n")
```

so the generated `HURL.BAT` switches to the CD, runs `H.EXE` with `-d` pointing
back at the hard-disk directory that holds the drivers, and returns. A second
file, `HURL4MEG.BAT`, does the same with `DOS4GVM=@NEW4G.VMC` set around it.
Finally it runs `SETSOUND.EXE`.

## Command line

| Switch | Effect |
|---|---|
| `-d <path>` | where the sound drivers and the configuration live |
| `-s` | run without sound (documented in both readmes) |

`H.EXE` also prints `No Intro` and `God Mode!` for two more switches whose
letters are compared in code and do not survive as strings
([01-executables.md](01-executables.md)).

## `NEW4G.VMC` — the low-memory profile

```
minmem=512
maxmem=4096
virtualsize=4096
deleteswap
swapname=c:\dos4gvm.swp
```

A DOS/4GW virtual-memory configuration capping the extender at 4 MB and
swapping to `C:\DOS4GVM.SWP`, used by the `4 MEG` launcher for machines that
have the 4 MB the game wants but not free.

## Memory

`README.TXT` asks for a 386/33, VGA, **550 K free conventional memory** and
**4 MB free XMS**. `HURLDOC.TXT` — the manual text, and a different document —
says a 386SX/33 minimum with a 486/25 recommended, 500 K base memory, and
gives Deep River's support numbers in the 207 (Maine) area code plus a
CompuServe address, `71055,3436`.

The corresponding failure messages in `H.EXE`:

```
ERROR: Not enough free low DOS memory.
Found %ld but need %ld / Free up %ld more bytes
ERROR:Not Enough Memory.
Slob Zone needs at least 3Mb free.  Please check your configuration and try again.
Psst!: Out of low memory selectors.
```

The third of those is the game's own, and it still says *Slob Zone*.

## Configuration

`H.EXE` refers to `soundrv` and `midpak` — the names DIGPAK/MIDPAK use for the
saved driver choice — and builds save-game names from `%s%d.gam` with a
matching `%s%d.pic` thumbnail. None of those files exists on the disc; they
are created on the hard-disk directory named by `-d`.

The in-game controls, from `trshscrn.gif`:

| Key | Action |
|---|---|
| arrow keys | move |
| `Alt` | throw the current object |
| `1` `2` `3` | select water balloon / soap / deodorant |
| `Space` | use a door, phone, shower or vending machine |
| `Enter` | spin 180° |
| `Esc` | menu |
| `P` | pause |
| `D` | turn floor and ceiling off — the game's one performance control |
| `Q` | quit |
| `+` `-` | music volume |

`HURLDOC.TXT` recommends `D` by name as the fix for "HURL runs on my computer
but it's really slow", which matches the level scripts: `Floors: ON` in all
eleven, and floor and ceiling casting is the expensive part.
