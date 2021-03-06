# ac-nesrom-save-generator

## Setup

Use `pip` to install dependencies:

```
$ pip install -r requirements.txt
```

Then install the script with:

```
$ python setup.py install
```

You may want to use a [virtual environment](https://virtualenv.pypa.io/en/stable/) for this.

## ROM files

This tool can generate Animal Crossing save files that contain playable NES ROMs.
To create a new file, provide the name of the game, the path to the ROM image, and the path
to the output GCI file.

    $ ac-nesrom-gen "Mega Man" "Mega Man (USA).szs" mega_man_nes.gci
    Need 12 blocks to contain ROM GCI
    Checksum: 0x00973e8e
    Check byte: 0x72

The ROM image can optionally be compressed in "Yaz0" ("szs") format using a tool
like wszstools.

Use a memory card manager to import the GCI file to a memory card, and then use
the "NES Console" item to play the ROM.

If you're playing on Dolphin, disable anti-aliasing when playing NES games to
get a better picture.

## Patcher files

This tool can also be used to generate NES ROM files that contain patch tags. These
tags can be used to patch code and data in memory.

Example usage of the patch options:

    $ ac-nesrom-gen "Zuru2 Patch" /dev/null zuru_mode_2.gci -p 80206F9c 0000007D

Each `-p`/`--patch` option inserts a small ROM tag patch (251 bytes or less) within
the address range `0x80000000` - `0x807FFFFF`.

Larger patches, including code patches, can be inserted into the ROM data section.
Use the `--loader` option to insert a patch loader that automatically loads big patches
from the ROM data section, and supply the path to a patch file where the ROM file path
would normally go.

    $ ac-nesrom-gen --loader "printf" printf_c.patch printf_c.gci

If a patch only needs to run once upon loading, the `--autoheader` option
can be used to generate a header for it automatically. It takes the load address
of the patch as an argument.

    $ ac-nesrom-gen --loader --autoheader 80002000 "Test" test.patch test.gci

See the [ac-patch-loader](https://github.com/jamchamb/ac-patch-loader) repo
for patch format and calling conventions.

## Big patch generator

YAML files describing a series of big patches and settings can be used to generate
the big patch section content automatically.

This example includes two patches. It uses a hex string to overwrite one instruction
at `0x80404E24`, and then loads a larger patch from the file `debug_printf_c.patch`
to be inserted at `0x80002000`.

```yaml
settings:
    jut_console: false

patches:
  - target: 0x80404E24
    bytes: '4BBFD1DD'

  - target: 0x80002000
    file: debug_printf_c.patch
```

This example inserts a patch that will be called immediately after
it's loaded to `0x80002000`. It also enables the in-game debug console
without requiring zuru mode to be enabled.

```yaml
settings:
  jut_console: true

patches:
  - target: 0x80002000
    file: hello_osreport_c.patch
    flags:
      jump: true
```
