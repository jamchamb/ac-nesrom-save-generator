import struct


def block_count(data_size, block_size):
    """The number of blocks of given size required to
    hold the data."""

    blocks = 0
    while (block_size * blocks) < data_size:
        blocks += 1

    return blocks


def block_align(data_size, block_size):
    """Return size of buffer that is a multiple of the
    block size that can contain the data."""
    return block_count(data_size, block_size) * block_size


def pack_byte(value):
    return struct.pack('>B', value)


def pack_short(value):
    return struct.pack('>H', value)


def pack_int(value):
    return struct.pack('>I', value)


def calcsum_byte(data, verbose=False):
    """Calculate check byte for calcSum check"""

    checksum = 0
    for b in data:
        checksum += b & 0xFF
        checksum = checksum & 0xFFFFFFFF

    checkbyte = (256 - (checksum & 0xFF)) & 0xFF

    if verbose:
        print 'Checksum: 0x%08x' % (checksum)
        print 'Check byte: 0x%02x' % (checkbyte)

    return checkbyte


def yaz0_size(data):
    """Get uncompressed size of Yaz0 file"""

    return struct.unpack('>I', data[4:8])[0]
