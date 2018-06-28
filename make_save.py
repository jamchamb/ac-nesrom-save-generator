#!/usr/bin/env python
import argparse
import gci
import struct

BLOCK_SZ = 0x2000


def block_align(size, block):
    blocks = 0
    while (block * blocks) < size:
        blocks += 1
    return block * blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('game_name', type=str, help='Game name')
    parser.add_argument('rom_file', type=str, help='NES Rom')
    parser.add_argument('in_file', type=str, help='Input GCI')
    parser.add_argument('out_file', type=str, help='Output GCI')
    parser.add_argument('--banner', type=str, help='Save banner')
    args = parser.parse_args()

    blank_gci = gci.read_gci(args.in_file)

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
    tag_info = 'END\x00'
    tag_info_len = len(tag_info)

    total_len = 0x660 + len(romfile) + banner_len + tag_info_len

    new_count = max(1, block_align(total_len, BLOCK_SZ) / BLOCK_SZ)
    print 'Need %u blocks to contain ROM GCI' % (new_count)

    blank_gci['m_gci_header']['Filename'] = 'DobutsunomoriP_F_%s' % ((args.game_name[0:4]).upper())
    blank_gci['m_gci_header']['BlockCount'] = new_count

    # Copy beginning of NES SAVE file (includes save icon, game name)
    old_data = blank_gci['m_save_data']
    new_data_tmp = bytearray(BLOCK_SZ * new_count)
    new_data_tmp[0:0x640] = old_data[0][0:0x640]

    # Set description to name of the game
    new_data_tmp[comments_addr+32:comments_addr+64] = ('%s ] ROM ' % (args.game_name)).ljust(32)

    # Set title of game as shown in game menu
    new_data_tmp[0x640:0x650] = 'ZZ%s' % (args.game_name.ljust(16))

    # Uncompressed ROM size (0 for none) - divided by 16
    new_data_tmp[0x640+0x12:0x640+0x14] = struct.pack('>H', nes_rom_len)

    # Tag info size
    new_data_tmp[0x640+0x14:0x640+0x16] = struct.pack('>H', tag_info_len)

    # Banner size (0 for none)
    new_data_tmp[0x640+0x1A:0x640+0x1C] = struct.pack('>H', banner_len)

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
    new_data_tmp[0x640+0x16] = 0xC0
    new_data_tmp[0x640+0x17] = 0xDE

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
