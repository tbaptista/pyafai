from setuptools import setup
from pyafai import __version__

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyafai',
    version=__version__,
    description='Python Agent Framework for Artificial Intelligence',
    long_description = long_description,
    url='none',
    author='Tiago Baptista',
    author_email='baptista@dei.uc.pt',
    packages=['pyafai'],
    install_requires = ['pyglet'],
    license='LICENSE.txt'
)