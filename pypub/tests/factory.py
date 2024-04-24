"""
Chapter Factory Unit Tests
"""
import os
import logging
import tempfile
from typing import Optional
import unittest

from . import LOCAL_IMAGE
from ..chapter import create_chapter_from_html, htmltostring
from ..factory import RenderCtx, SimpleChapterFactory

#** Variables **#
__all__ = ['FactoryTests']


#: basic testing logging instance
logger = logging.getLogger('pypub.test')

#: chapter factory instance used to generate chapters
factory = SimpleChapterFactory()

image_html_sample1 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <img src=""></img>
    </body>
</html>
"""

image_html_sample2 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <img src=""></img>
        <img></img>
        <img/>
    </body>
</html>
"""

article_html_sample1 = b"""
<html>
    <head></head>
    <body>
        <article>Hello! I am a test</article>
    </body>
</html>
"""

article_html_sample2 = b"""
<html>
    <head></head>
    <body>
        <div>dsfasfadfasdfasdf</div>
        <article>Hello! I am a test</article>
    </body>
</html>
"""

article_html_sample3 = b"""
<html>
    <head></head>
    <body>
        <article><video></video>Hello! I am a test</article>
    </body>
</html>
"""

complete_html_sample1 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <div>Hello </div>
    </body>
</html>
"""

complete_html_sample2 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <div>Hello </div>
        <script>Uh oh...it's an evil script!</script>
    </body>
</html>
"""

complete_html_sample3 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <div>Hello </div>
    </body>
    <video>Play me!</video>
</html>
"""

complete_html_sample4 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <video>
        <div>Hello </div>
        </video>
    </body>
    <video>Play me!</video>
</html>
"""

complete_html_sample5 = b"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <video>
            <div>Hello&nbsp;</div>
        </video>
    </body>
    <video>Play me!</video>
</html>
"""

local_image_html_sample1 = f"""
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
       <p>This is a test</p>
       <img src="file://{LOCAL_IMAGE}">
    </body>
</html>
""".encode()

#** Functions **#

def cleanup(content: bytes) -> bytes:
    """
    clean and produce finalized pypub chapter content
    """
    etree = factory.cleanup_html(content)
    for elem in etree.iter():
        elem.tail = None
        elem.text = elem.text.strip() if elem.text else ''
    return htmltostring(etree)

#** Tests **#

class FactoryTests(unittest.TestCase):
    """Epub Ebook Factory UnitTests"""

    def setUp(self):
        """create tempdir default of none"""
        self.tempdir: Optional[tempfile.TemporaryDirectory] = None

    def render_ctx(self, content: bytes) -> RenderCtx:
        """generate render context for more factory tests"""
        chapter = create_chapter_from_html(content)
        etree   = factory.cleanup_html(chapter.content)
        self.tempdir = tempfile.TemporaryDirectory()
        return RenderCtx(
            logger=logger, 
            chapter=chapter, 
            etree=etree, 
            imagedir=self.tempdir.name, 
            template=None, #type: ignore
        )

    def tearDown(self) -> None:
        """ensure teardown of temporary directory"""
        if self.tempdir is not None:
            self.tempdir.cleanup()

    def test_clean_images(self):
        """ensure etree cleaning works as intended to filter bad images"""
        clean1 = cleanup(image_html_sample1)
        clean2 = cleanup(image_html_sample2)
        self.assertEqual(clean1, clean2)

    def test_clean_article(self):
        """test that non-whitelisted tags get removed from html snippet"""
        s1 = cleanup(article_html_sample1)
        s2 = cleanup(article_html_sample2)
        s3 = cleanup(article_html_sample3)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)

    def test_clean_html(self):
        """test entire html grouping can be cleaned properly"""
        s1 = cleanup(complete_html_sample1)
        s2 = cleanup(complete_html_sample2)
        s3 = cleanup(complete_html_sample3)
        s4 = cleanup(complete_html_sample4)
        s5 = cleanup(complete_html_sample5)
        self.assertEqual(s1, s2)
        self.assertEqual(s1, s3)
        self.assertEqual(s1, s4)
        self.assertEqual(s1, s5)

    def test_local_image(self):
        """test local image resolution works as intended"""
        # attempt to hydrate local image
        ctx = self.render_ctx(local_image_html_sample1)
        factory.hydrate(ctx)
        # ensure image exists and is registered
        assert self.tempdir is not None
        src  = ctx.etree.find('//img/@src') or 'images/notfound.png'
        name = os.path.basename(src)
        fpath = os.path.join(self.tempdir.name, name)
        self.assertTrue(os.path.exists(fpath), 'local image not converted')

#** Main **#

if __name__ == '__main__':
    unittest.main()
