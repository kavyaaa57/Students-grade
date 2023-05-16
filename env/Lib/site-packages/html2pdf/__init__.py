""""
This modules is a simple python wrapper for wkhtmltopdf forked from python-wkhtmltopdf

Classes:

HTMLURLToPDF -- Provides an elementary class to create a PDF, requires the url and output_file
                parameters to generate a PDF
HTMLToPdf -- Instead of providing the URL provide a HTML parameter with the HTML String and will create
             a PDF

Functions:
urltopdf -- Pass url and output_file parameters and get a HTMLURLToPDF object
"""
from .main import HTMLToPDF, HTMLURLToPDF, urltopdf
