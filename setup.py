# from distutils.core import setup
from setuptools import find_packages, setup
import py2exe

import sys
from distutils.dir_util import copy_tree
import os
from os.path import join, dirname
import re
import xlwt
import xlrd
import xltpl
import xlsxtpl
import openpyxl
import jinja2
import markupsafe
import html5lib

distDir = "distmyselling"

def py2exe_datafiles():
    data_files = {}
    data_files['app\\updates'] = []

    for root, dirnames, filenames in os.walk('app'):
        for filename in filenames:
            if not re.match(r'.*(\.pyc|\.db|\.pyo|\~)$', filename):
                data_files.setdefault(root, []).append(join(root, filename))

    return data_files.items()

# xlrd
xlrdPath = join(distDir, "xlrd")
copy_tree(xlrd.__path__[0], xlrdPath )

# xlwt
xlwtPath = join(distDir, "xlwt")
copy_tree(xlwt.__path__[0], xlwtPath )

# xltpl
xltplPath = join(distDir, "xltpl")
copy_tree(xltpl.__path__[0], xltplPath )

# xlsxtpl
xlsxtplPath = join(distDir, "xlsxtpl")
copy_tree(xlsxtpl.__path__[0], xlsxtplPath )

# openpyxl
openpyxlPath = join(distDir, "openpyxl")
copy_tree(openpyxl.__path__[0], openpyxlPath )

# Jinja2
jinja2Path = join(distDir, "jinja2")
copy_tree(jinja2.__path__[0], jinja2Path )

# MarkupSaf
markupsafePath = join(distDir, "markupsafe")
copy_tree(markupsafe.__path__[0], markupsafePath )

# html5lib
html5libPath = join(distDir, "html5lib")
copy_tree(html5lib.__path__[0], html5libPath )


packages = [
    'xlwt',
    'xlrd',
    'xltpl',
    'xlsxtpl',
    'openpyxl',
    'jinja2',
    'markupsafe',
    'html5lib',
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

includes = [
    ]

requires=[
    'chevron',
    'xhtml2pdf',
    'webencodings',
    'reportlab',
    'PyPDF2',
    'Pillow',
    'jdcal',
    'et-xmlfile',
    'xlwt',
    'xlrd',
    'openpyxl',
    'Jinja2',
    'MarkupSaf',
    'html5lib',
    ]

setup(name='my-selling',
      version='3.0',
      windows=[{'script': 'start.pyw'}],
      zipfile = r'library.zip',
      packages=find_packages(),
      install_requires=requires,
      options={
          "py2exe": {"packages": packages,
                     "includes": includes,
                     # "excludes": ['jinja2.asyncsupport'],
                     "compressed":  0,
                     "bundle_files": 3,
                     "optimize": 0,
                     "dist_dir": distDir,
                     "xref": False,
                     "skip_archive": True,
                     }
      },
      data_files = py2exe_datafiles()
      )
