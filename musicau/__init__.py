"""
Test of the Computer-Assisted Musicology module MusiCAU, commissioned by the
Institute of Musicology at the University of Kiel.
"""

import sys

minPythonVersion = (3, 10)
minPythonVersionStr = '.'.join([str(x) for x in minPythonVersion])
if sys.version_info < minPythonVersion:
    raise ImportError('''
    MusiCAU v.0.1+ is a Python {}+ only library.
    '''.format(minPythonVersionStr))
del sys
del minPythonVersion
del minPythonVersionStr


DEFAULT_CORPUS_NAME = "MusiCAU.Demo"


__all__ = [
    'analysis',
    'tools'
]

from musicau import *
