# ac-nesrom-save-generator

## `patcher.py`

Example usage of `patcher.py`:

    $ ./patcher.py Patcher /dev/null zuru_mode_2.gci -p 80206F9c 0000007D

Each `-p`/`--patch` option inserts a small ROM tag patch (251 bytes or less) within
the address range `0x80000000` - `0x807FFFFF`.

The input ROM file argument can be non-ROM data or empty (`/dev/null`) if it's not needed.
Larger patches can be stored here for use with a loader set up through ROM tag patches.

Directly patching code may not working due to instruction caching.
The `ICInvalidateRange` function can be used to refresh instructions after patching, but
requires some initial loader setup to call. This can be achieved by overwriting a function
pointer to point to a small subroutine.
