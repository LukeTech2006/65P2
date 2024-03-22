from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize

setup(
    name='65P2 - A 6502 Emulator',
    ext_modules=cythonize([Extension("processor", ["processor.py"]), Extension("parser", ["parser.py"]), Extension("run", ["run.py"])])
)