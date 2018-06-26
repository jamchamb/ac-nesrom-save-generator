#!/usr/bin/env python
import argparse
import gci


BLOCK_SZ = 0x2000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('game_name', type=str, help='Game name')
    parser.add_argument('rom_file', type=str, help='NES Rom')
    parser.add_argument('in_file', type=str, help='Input GCI')
    parser.add_argument('out_file', type=str, help='Output GCI')
    args = parser.parse_args()

    blank_gci = gci.read_gci(args.in_file)

    comments_addr = blank_gci['m_gci_header']['CommentsAddr']

    romfile = open(args.rom_file, 'rb').read()

    new_count = 0
    while (new_count * BLOCK_SZ) < len(romfile):
        new_count += 1

    print 'Need %u blocks to contain %s' % (new_count, args.rom_file)

    blank_gci['m_gci_header']['Filename'] = 'DobutsunomoriP_F_%s' % ((args.game_name[0:4]).upper())
    blank_gci['m_gci_header']['BlockCount'] = new_count

    # Copy beginning of NES SAVE file (includes save icon, game name)
    old_data = blank_gci['m_save_data']
    new_data_tmp = bytearray(BLOCK_SZ * new_count)
    new_data_tmp[0:0x640] = old_data[0][0:0x640]

    # Set description to name of the game
    new_data_tmp[comments_addr+32:comments_addr+64] = ('NES ROM: %s' % (args.game_name)).ljust(32)

    # Set title of game as shown in game menu
    new_data_tmp[0x640:0x650] = 'ZZ%s' % (args.game_name.ljust(16))
    new_data_tmp[(0x640+0x1A)] = '\x01'
    new_data_tmp[(0x640+0x12)] = '\x01'

    # Copy in the NES ROM
    new_data_tmp[0x660:0x660+len(romfile)] = romfile

    checksum = 0
    for b in new_data_tmp:
        checksum += (b % 256)
        checksum = checksum % (2**32)

    checkbyte = 256 - (checksum % 256)

    if (checksum + checkbyte) % 256 == 0:
        print 'Checksum: 0x%08x' % (checksum)
        print 'Check byte: 0x%02x' % (checkbyte)

    new_data_tmp[(BLOCK_SZ * new_count)-1] = checkbyte

    blank_gci['m_save_data'] = str(new_data_tmp)

    with open(args.out_file, 'wb') as outfile:
        data = gci.write_gci(blank_gci)
        outfile.write(data)


if __name__ == '__main__':
    main()
