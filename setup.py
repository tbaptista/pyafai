from distutils.core import setup
from pyafai import __version__

setup(
    name='pyafai',
    version=__version__,
    description='Python Agent Framework for Artificial Intelligence',
    url='none',
    author='Tiago Baptista',
    author_email='baptista@dei.uc.pt',
    packages=['pyafai'],
    license='LICENSE.txt',
    long_description=open('README.rst').read(),
)