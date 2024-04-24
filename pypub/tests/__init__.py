"""
Pypub Unit Tests
"""
import os

#** Variables **#
__all__ = ['ChapterTests', 'FactoryTests', 'EpubTests']

#: static testing files directory
STATIC = os.path.realpath(os.path.join(os.path.dirname(__file__), 'static'))

#: sample local file image
LOCAL_IMAGE = os.path.join(STATIC, 'sample.png')

#** Imports **#
from .epub import EpubTests
from .chapter import ChapterTests
from .factory import FactoryTests
