#!/usr/bin/python
# coding:utf-8
# запускалка для py2exe
import os
import sys

if hasattr(sys, "frozen") and sys.frozen == "windows_exe":
    os.chdir(os.path.dirname(sys.executable))

from Tkinter import Tk
from reportlab.pdfgen import canvas
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm

root = Tk()

sys.path.append('app/plugins/main')
m = __import__('main')
cl = getattr(m, 'App')(root)
root.mainloop()
