#!/usr/bin/env python
import argparse
import binascii
import gci
import struct

# Memory card block size
BLOCK_SZ = 0x2000


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


def tag_header(tag, size):
    return struct.pack('>3sB', tag, size)


def create_pat(target_addr, payload):
    """Create a PAT tag that can patch data into any address
    between 0x80000000 and 0x807FFFFF.

    The maximum payload size is 255-4 = 251 bytes."""

    if len(payload) > 251:
        raise Exception('payload too big')

    # Calculate address bytes
    off_high = ((target_addr >> 16) & 0xFFFF) - 0x7F80
    off_low = target_addr & 0xFFFF

    tag_data = struct.pack('>BBH', off_high, len(payload), off_low) + payload
    tag_head = tag_header('PAT', len(tag_data))

    return tag_head + tag_data


def create_tag_buffer(tags):
    tag_info = tag_header('ZZZ', 0)  # ignored beginning
    tag_info += ''.join(tags)
    tag_info += tag_header('END', 0)

    return tag_info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('game_name', type=str,
                        help='Game name displayed in NES Console menu')
    parser.add_argument('rom_file', type=str, help='NES ROM image')
    parser.add_argument('out_file', type=str, help='Output GCI')
    parser.add_argument('--banner', type=str, help='Save banner')
    parser.add_argument('-p', '--patch', action='append', nargs=2,
                        metavar=('address', 'bytes'),
                        help="""Hex encoded patch prefixed with location.
                        Multiple patches are allowed. Max size of each payload
                        is 251.""")
    args = parser.parse_args()

    blank_gci = gci.read_gci('blank.gci')

    comments_addr = blank_gci['m_gci_header']['CommentsAddr']

    # Load ROM file
    romfile = open(args.rom_file, 'rb').read()
    # TODO: Figure out size from compressed input ROM
    nes_rom_len = 0x2001

    # Load banner file
    banner_len = 0x0
    banner_file = None
    if args.banner is not None:
        banner_file = open(args.banner, 'rb').read()
        banner_len = len(banner_file)

    # Tag info
    tags = []

    print 'Inserting %u patches' % (len(args.patch))
    for patch in args.patch:
        patch_target = int(patch[0], 16)
        patch_payload = binascii.unhexlify(patch[1])
        print patch
        tags.append(create_pat(patch_target, patch_payload))

    tag_info = create_tag_buffer(tags)
    tag_info_len = len(tag_info)

    total_len = 0x660 + len(romfile) + banner_len + tag_info_len

    new_count = max(1, block_count(total_len, BLOCK_SZ))
    print 'Need %u blocks to contain ROM GCI' % (new_count)

    blank_gci['m_gci_header']['Filename'] = 'DobutsunomoriP_F_%s' % (
        (args.game_name[0:4]).upper())
    blank_gci['m_gci_header']['BlockCount'] = new_count

    # Copy beginning of NES SAVE file (includes save icon, game name)
    old_data = blank_gci['m_save_data']
    new_data_tmp = bytearray(BLOCK_SZ * new_count)
    new_data_tmp[0:0x640] = old_data[0][0:0x640]

    # Set description to name of the game
    new_data_tmp[comments_addr+32:comments_addr+64] = ('%s ] ROM ' % (
        args.game_name)).ljust(32)

    # Set title of game as shown in game menu
    new_data_tmp[0x640:0x650] = 'ZZ%s' % (args.game_name.ljust(16))

    # Uncompressed ROM size (0 for none) - divided by 16
    # Force it to be 0 so the ROM data isn't run
    new_data_tmp[0x640+0x12:0x640+0x14] = pack_short(0)

    # Tag info size
    new_data_tmp[0x640+0x14:0x640+0x16] = pack_short(tag_info_len)

    # Banner size (0 for none)
    new_data_tmp[0x640+0x1A:0x640+0x1C] = pack_short(banner_len)

    # Bit flags
    # high bit: use banner
    # 2 bits: text code (0-3)    default=1, fromcard=2
    # 2 bits: banner code (0-3)  default=1
    # 2 bits: icon code (0-3)    default=1
    new_data_tmp[0x640+0x1C] = 0b11001010

    # Bit flags
    # high bit: ?
    # 2 bits: banner format
    new_data_tmp[0x640+0x1D] = 0b00000000

    # Icon format
    new_data_tmp[0x640+0x16] = 0x00
    new_data_tmp[0x640+0x17] = 0x00

    # Unpacking order: tag info, Banner, NES Rom
    data_offset = 0x660

    # Copy in tag info
    if tag_info_len > 0:
        new_data_tmp[data_offset:data_offset+tag_info_len] = tag_info
        # align on 16 byte boundary
        data_offset += block_align(tag_info_len, 16)

    # Copy in banner
    if banner_len > 0:
        new_data_tmp[data_offset:data_offset+banner_len] = banner_file
        data_offset += block_align(banner_len, 16)

    # Copy in the NES ROM
    if nes_rom_len > 0:
        new_data_tmp[data_offset:data_offset+len(romfile)] = romfile

    checksum = 0
    for b in new_data_tmp:
        checksum += (b % 256)
        checksum = checksum % (2**32)

    # Calculate checksum
    checkbyte = 256 - (checksum % 256)
    new_data_tmp[(BLOCK_SZ * new_count)-1] = checkbyte

    print 'Checksum: 0x%08x' % (checksum)
    print 'Check byte: 0x%02x' % (checkbyte)

    # Save new GCI
    blank_gci['m_save_data'] = str(new_data_tmp)
    with open(args.out_file, 'wb') as outfile:
        data = gci.write_gci(blank_gci)
        outfile.write(data)


if __name__ == '__main__':
    main()
