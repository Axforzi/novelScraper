import os
import unittest
from typing import Set

from . import LOCAL_IMAGE, STATIC
from ..epub import Epub
from ..chapter import create_chapter_from_file

#** Variables **#
__all__ = ['EpubTests']

#: example html from static test-files directory
EXAMPLE_HTML = os.path.join(STATIC, 'example.html')

#: example book file-tree from static test-files directory
EXAMPLE_BOOK = os.path.join(STATIC, 'example_book')

#** Tests **#

class EpubTests(unittest.TestCase):
    """Epub Complete Book Generation UnitTests"""

    def setUp(self):
        """generate epub object for testing"""
        chapter   = create_chapter_from_file(EXAMPLE_HTML)
        self.epub = Epub('title')
        self.epub.add_chapter(chapter)

    def _walk(self, path: str) -> Set[str]:
        """generate a list of files included in tree"""
        tree = set()
        for root, _, files in os.walk(path):
            fpath = root.split(path, 1)[1]
            for file in files:
                tree.add(os.path.join(fpath, file))
        return tree

    def test_create_epub(self):
        """generate an epub directory-tree ready for zipping"""
        try:
            edir  = self.epub.build_epub_dir()
            tree1 = self._walk(edir)
            tree2 = self._walk(EXAMPLE_BOOK)
            self.assertEqual(tree1, tree2)
        finally:
            self.epub.builder.cleanup()
 
    def test_custom_cover(self):
        """ensure custom cover generation works as intended"""
        self.epub.cover = LOCAL_IMAGE
        try:
            edir  = self.epub.build_epub_dir()
            fname = os.path.basename(self.epub.cover)
            fpath = os.path.join(edir, f'OEBPS/images/{fname}')
            self.assertTrue(os.path.exists(fpath), 'no such cover')
        finally:
            self.epub.builder.cleanup()

#** Main **#

if __name__ == '__main__':
    unittest.main()
