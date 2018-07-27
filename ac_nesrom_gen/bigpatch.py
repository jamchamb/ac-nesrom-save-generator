import binascii
import struct
import yaml


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
        self.patches.append(info + data)

    def compile(self):
        header = struct.pack(
            '>HH',
            self.global_flags,
            len(self.patches)
        )

        result = header + ''.join(self.patches)
        return result

    def load_yaml(self, filename):
        with open(filename, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file.read())

            settings = yaml_data['settings']
            patches = yaml_data['patches']

            if settings['jut_console']:
                self.global_flags |= 1

            for patch in patches:
                flags = 0
                if 'flags' in patch:
                    if patch['flags'].get('jump'):
                        flags |= 1

                if 'file' in patch:
                    with open(patch['file'], 'r') as patch_file:
                        data = patch_file.read()
                elif 'bytes' in patch:
                    data = binascii.unhexlify(patch['bytes'])

                self.add_patch(patch['target'],
                               flags,
                               data)
