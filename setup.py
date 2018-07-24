from setuptools import setup

setup(
    name='ac_nesrom_gen',
    version='0.1',
    packages=['ac_nesrom_gen'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'ac-nesrom-gen = ac_nesrom_gen.__main__:main'
        ]
    }
)
