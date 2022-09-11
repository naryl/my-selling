# coding:utf-8
import sys

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from reportlab.pdfgen import canvas

try:
    if sys.platform == 'win32':
        font = ttfonts.TTFont('Arial', 'arial.ttf')
    else:
        font = ttfonts.TTFont('Arial', '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf')
except ttfonts.TTFError:
    font = ttfonts.TTFont('Arial', 'app/fonts/DejaVuSans.ttf')
pdfmetrics.registerFont(font)


class Pdf:

    def next(self, font=12):
        # переход на следующую страницу
        self.sk = 280
        self.pdf.showPage()
        self.pdf.setFont('Arial', font)

    def __init__(self, title='Это тест', fname='out.pdf'):
        self.sk = 280
        self.fname = fname
        if sys.platform == 'win32':
            self.pdf = canvas.Canvas(fname.encode('cp1251'))
        else:
            self.pdf = canvas.Canvas(fname.encode('utf-8'))

        self.pdf.setFont('Arial', 14)
        self.pdf.drawString(60 * mm, self.sk * mm, title)
        self.sk -= 12

    def string(self, text, font=12, x=20):
        #
        self.pdf.setFont('Arial', font)
        self.pdf.drawString(x * mm, self.sk * mm, text)
        self.sk -= 5
        if self.sk < 20:
            self.next(font)

    def table(self, list, font=12):
        self.pdf.setFont('Arial', font)
        self.tb = [20 * mm]
        last = 20 * mm
        for x in list:
            self.tb.append((x[1] + last))
            last += x[1]

        self.pdf.grid(self.tb, [self.sk * mm, self.sk * mm - 18])

        for x in range(len(self.tb[:-1])):
            t = list[x][0]
            if type(t) == int or type(t) == float: t = str(t)

            self.pdf.drawString(self.tb[x] + 4, self.sk * mm - 12, t)
        self.sk -= 6.3
        if self.sk < 20:
            self.next(font=12)

    def enter(self):
        self.sk -= 10
        if self.sk < 20:
            self.next(font=12)

    def end(self):
        self.pdf.save()
