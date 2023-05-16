#!/usr/bin/env python
# pylint: disable=too-many-public-methods, invalid-name, missing-docstring, wildcard-import
import os
import unittest


from .main import *


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.url = "http://www.example.com"
        self.output_file = "/tmp/example.pdf"

    def test_htmltopdf(self):
        h = HTMLURLToPDF(self.url, self.output_file)
        h.render()
        self.assertTrue(os.path.exists(self.output_file))

    def test_urltopdf(self):
        obj = urltopdf(self.url, self.output_file)
        self.assertTrue(obj.rendered)
        self.assertTrue(os.path.exists(self.output_file))

    def test_htmlfromstring(self):
        html = """
        <!DOCTYPE html>
        <html>
            <body>
            <h1>Hello World</h1>
            </body>
        </html>
        """

        h = HTMLToPDF(html, self.output_file)

        self.assertTrue(os.path.exists(self.output_file))
        self.assertTrue(h.rendered)

    def test_withhtmlfromstring(self):
        html = """
        <!DOCTYPE html>
        <html>
            <body>
            <h1>Hello World</h1>
            </body>
        </html>
        """
        with HTMLToPDF(html, self.output_file) as pdf:
            with open('/tmp/e.pdf', 'w') as out:
                out.write(pdf.read())
        self.assertFalse(os.path.exists(self.output_file))

    def tearDown(self):
        try:
            os.remove(self.output_file)
        except OSError:
            pass


if __name__ == '__main__':
    unittest.main()
