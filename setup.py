#!/usr/bin/env python3

from subprocess import check_call

from distutils.cmd import Command
from distutils.core import setup
from distutils.command.build import build


class BuildCommand(build):
    def run(self):
        self.run_command('generate_parser')
        build.run(self)


class GenerateParserCommand(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        check_call('./generate_parser.sh')


setup(
    name='lucy',
    version='0.0.1',
    description='Minimal compiler for a small language',
    url='https://github.com/AndreaOrru/Lucy',
    author='Andrea Orru',
    author_email='andreaorru1991@gmail.com',
    license='BSD-2',
    packages=[
        'lucy',
        'lucy.antlr',
    ],
    install_requires=[
        'antlr4-python3-runtime',
        'llvmlite',
    ],
    cmdclass={
        'generate_parser': GenerateParserCommand,
        'build': BuildCommand,
    },
    entry_points={
        'console_scripts': 'lucy=lucy.cli:main',
    })
