#!/usr/bin/env python
"""
All the meaningful code of the module
"""
import os
import uuid

from subprocess import Popen
from subprocess import PIPE

__all__ = ['HTMLURLToPDF', 'HTMLToPDF', 'urltopdf']


class WKOption(object):
    """
    Build an option to be used throughout
    """
    def __init__(self, name, shortcut, otype=str, dest=None, default=None, helptext=None,
                 validate=None, validate_error=None, value=None):
        self.name = name
        self.shortcut = shortcut
        self.otype = bool if (default is True or default is False) else otype
        self.action = "store_true" if self.otype is bool else "store"
        self.dest = dest if dest else name.replace('-', '_')
        self.default = default
        self.help = helptext
        self._validate = validate
        self.validate_error = validate_error

        # if there's a value passed to us use it, else use the default
        if value is not None:
            self.value = value
        else:
            self.value = default

    def long(self):
        """
        Replaces underscore methods for compatibility purposes
        """
        return '--' + self.name.replace('_', '-')

    def to_cmd(self):
        """
        Return the str of this command, bool is just --long, etc
        """
        if self.otype is bool:
            if self.value:
                return self.long()
            else:
                return ""
        else:
            return " ".join([self.long(), str(self.value) if self.value is not None else ""])



OPTIONS = [
    WKOption('enable-plugins', '-F', default=True, helptext="Use flash and other plugins."),
    WKOption('disable-javascript', '-J', default=False, helptext="Disable javascript."),
    WKOption('no-background', '-b', default=False, helptext="Do not print background."),
    WKOption('grayscale', '-g', default=False, helptext="Make greyscale."),
    WKOption(
        'orientation', '-O', default="Portrait", helptext="Set page orientation.",
        validate=lambda x: x in ['Portrait', 'Landscape'],
        validate_error="Orientation argument must be either Portrait or Landscape"
    ),
    WKOption(
        'page-size', '-s', default="A4", helptext="Set page size.",
        validate=lambda x: x in ['A4', 'Letter'],
        validate_error="Page size argument must be A4 or Letter"
    ),
    WKOption('print-media-type', '', default=False, helptext="Set print media type."),

    WKOption('dpi', '-D', default=100, helptext="Set DPI"),
    WKOption('username', '-U', default="", helptext="Set the HTTP username"),
    WKOption('password', '-P', default="", helptext="Set the HTTP password"),
    WKOption('margin-bottom', '-B', default=10, helptext="Bottom page margin."),
    WKOption('margin-top', '-T', default=10, helptext="Top page margin."),
    WKOption('margin-left', '-L', default=10, helptext="Left page margin."),
    WKOption('margin-right', '-R', default=10, helptext="Right page margin."),
    WKOption(
        'disable-smart-shrinking', None, default=False,
        helptext="Disable the intelligent shrinking strategy used by WebKit that makes the pixel/dpi ratio none constant",
    )
]


class HTMLURLToPDF(object):
    """
    Convert an html page via its URL into a pdf.
    """
    def __init__(self, *args, **kwargs):
        self.url = None
        self.output_file = None
        self.rendered = False

        # get the url and output_file options
        try:
            self.url, self.output_file = kwargs['url'], kwargs['output_file']
        except KeyError:
            self.url, self.output_file = args[0], args[1]
        except IndexError:
            pass

        if not self.url or not self.output_file:
            raise Exception("Missing url and output file arguments")

        # save the file to /tmp if a full path is not specified
        output_path = os.path.split(self.output_file)[0]
        if not output_path:
            self.output_file = os.path.join('/tmp', self.output_file)

        # set the options per the kwargs coming in
        for option in OPTIONS:
            try:
                option.value = kwargs[option.dest]  # try to get the value for that kwarg passed to us.
            except KeyError:
                pass  # can't find? just ignore and move on

        self.params = [option.to_cmd() for option in OPTIONS]
        self.screen_resolution = [1024, 768]
        self.color_depth = 24

        if kwargs.get('render') is True:
            self.render()

    def pdf_file(self):
        """
        If the pdf has been already rendered, return the file.
        """
        if not self.rendered:
            self.render()
        return open(self.output_file)

    def read(self):
        """
        Returns the Rendered PDF Object
        """
        return self.pdf_file().read()

    def render(self):
        """
        Render the URL into a pdf and setup the environment if required.
        """

        # setup the environment if it isn't set up yet
        if not os.getenv('DISPLAY'):
            os.system("Xvfb :0 -screen 0 %sx%sx%s & " % (
                self.screen_resolution[0],
                self.screen_resolution[1],
                self.color_depth
            ))
            os.putenv("DISPLAY", '127.0.0.1:0')

        # execute the command
        command = 'wkhtmltopdf %s "%s" "%s" >> /tmp/wkhtp.log' % (
            " ".join([cmd for cmd in self.params]),
            self.url,
            self.output_file
        )
        try:
            comm = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
            stdout, stderr = comm.communicate()
            retcode = comm.returncode

            if retcode == 0:
                # call was successful
                self.rendered = True
                return
            elif retcode < 0:
                raise Exception("Terminated by signal: ", -retcode)
            else:
                raise Exception(stderr)

        except OSError, exc:
            raise exc

    def __enter__(self):
        self.render()
        return self

    def __exit__(self, type, value, traceback):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)


def urltopdf(*args, **kwargs):
    """
    HTMLURLtoPDF class wrapper.
    """
    return HTMLURLToPDF(render=True, *args, **kwargs)


class HTMLToPDF(HTMLURLToPDF):
    """
    Convert an html string into a pdf.
    """
    def __init__(self, *args, **kwargs):
        try:
            self.HTML, self.output_file = kwargs['HTML'], kwargs['output_file']
        except KeyError:
            self.HTML, self.output_file = args[0], args[1]
        except:
            raise Exception('Missing HTML and/or output_file arguments')

        self.tmpfile = '/tmp/' + uuid.uuid4().get_hex() + '.html'

        with open(self.tmpfile, 'w') as tmpf:
            tmpf.write(self.HTML)
        params = {'url': self.tmpfile, 'output_file': self.output_file}
        super(HTMLToPDF, self).__init__(**params)
        self.render()

