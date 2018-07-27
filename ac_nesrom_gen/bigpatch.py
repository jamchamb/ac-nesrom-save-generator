import struct


class BigPatchGenerator:

    def __init__(self, flags=0):
        self.global_flags = flags
        self.patches = []

    def add_patch(self, target, flags, data):
        if flags > 0xFFFFFFFF:
            raise Exception('invalid flags value')

        info = struct.pack(
            '>III',
            target,
            len(data),
            flags
        )
        self.patches.add(info + data)

    def compile(self):
        header = struct.pack(
            '>HH',
            self.global_flags,
            len(self.patches)
        )

        result = header + ''.join(self.patches)
        return result
