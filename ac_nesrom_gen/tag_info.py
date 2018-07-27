import struct


MAX_PATCH_SIZE = 251


def tag_header(tag, size):
    return struct.pack('>3sB', tag, size)


class TagInfoGenerator:

    def __init__(self, flags=0):
        self.tags = []
        self.__add_begin()

    def __add_tag(self, tag):
        self.tags.append(tag)

    def __add_begin(self):
        begin = tag_header('ZZZ', 0)
        self.__add_tag(begin)

    def __add_end(self):
        end = tag_header('END', 0)
        self.__add_tag(end)

    def add_patch(self, target_addr, payload):
        """Create a PAT tag that can patch data into any address
        between 0x80000000 and 0x807FFFFF.

        The maximum payload size is 255-4 = 251 bytes."""

        if len(payload) > MAX_PATCH_SIZE:
            return self.add_multi_patch(target_addr, payload)

        # Calculate address bytes
        off_high = ((target_addr >> 16) & 0xFFFF) - 0x7F80
        off_low = target_addr & 0xFFFF

        tag_data = struct.pack('>BBH',
                               off_high,
                               len(payload),
                               off_low) + payload
        tag_head = tag_header('PAT', len(tag_data))

        self.__add_tag(tag_head + tag_data)

    def add_multi_patch(self, target_addr, payload):
        """Use multiple PAT tags to insert a patch larger than
        251 bytes."""

        for pos in range(0, len(payload), MAX_PATCH_SIZE):
            self.add_patch(
                target_addr + pos,
                payload[pos:pos+MAX_PATCH_SIZE]
            )

    def compile(self):
        self.__add_end()
        return ''.join(self.tags)
