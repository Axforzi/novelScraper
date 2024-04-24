import os
import unittest

from ..chapter import *

#** Variables **#
__all__ = ['ChapterTests']

#: static directory for unit-test related resources
STATIC = os.path.realpath(os.path.join(os.path.dirname(__file__), 'static'))

#** Tests **#

class ChapterTests(unittest.TestCase):
 
    def test_create_chapter_from_text(self):
        """complete test for create_chapter_from_text"""
        c = create_chapter_from_text('Hello\nWorld!\n\n')
        self.assertIn(b'<p>Hello</p>', c.content)
        self.assertIn(b'<p>World!</p>', c.content)

    def test_create_chapter_from_file(self):
        """complete test for create_chapter_from_file"""
        example = os.path.join(STATIC, 'example.html')
        c       = create_chapter_from_file(example)
        self.assertEqual(c.title, 'Business & Co')
        self.assertEqual(c.url, f'file://{os.path.abspath(example)}')

    def test_create_chapter_from_url(self):
        """complete test for create_chapter_from_url"""
        c = create_chapter_from_url('https://www.example.com')
        self.assertEqual(c.title, 'Example Domain')
        self.assertEqual(c.url, 'https://www.example.com')
        self.assertIn(b'illustrative examples', c.content)

    def test_create_chapter_example(self):
        """complete test for readme example"""
        c = create_chapter_from_url('https://en.wikipedia.org/wiki/EPUB')
        self.assertEqual(c.title, 'EPUB - Wikipedia')
        self.assertEqual(c.url, 'https://en.wikipedia.org/wiki/EPUB')
        self.assertIn(b'EPUB 3.2 was announced in 2018', c.content)

#** Main **#

if __name__ == '__main__':
    unittest.main()
