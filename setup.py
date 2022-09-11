from distutils.core import setup
import py2exe

packages = [
    'reportlab',
    'reportlab.lib',
    'reportlab.pdfbase',
    'reportlab.pdfgen',
    'chevron',
    'xhtml2pdf',
    'appdirs',
    'packaging',
    'PIL.ImageTk',
    'sqlite3',
    'json',
    'csv',
    'ScrolledText',
    'webbrowser',
    'tkFileDialog',
    'tkFont',
    'tkMessageBox'
]

includes = []

setup(name='my-selling',
      version='3.0',
      windows=[{'script': 'start.pyw'}],
      options={
          "py2exe": {"packages": packages,
                     "includes": includes}
      }
      )
