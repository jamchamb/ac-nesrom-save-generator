import struct


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
