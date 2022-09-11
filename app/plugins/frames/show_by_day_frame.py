# -*-coding:utf-8-*-
# просмотр продаж за дату
"""
    Copyright (C) 2010 Kozlov Igor <igor.kaist@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


"""
import time
import tkFileDialog
from Tkinter import *
from ttk import *

import pdf
from MultiListbox import MultiListbox
from calend import TkCalendar
from date_time import date_now, norm_date

name = 'Просмотреть продажи'
frame = 0


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        x, y = 800, 450
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')
        year, month = time.localtime()[0:2]
        self.date_t = StringVar()
        self.date_t.set(date_now())
        self.c_date = date_now()
        self.cal = TkCalendar(self.win, year, month, self.date_t, command=self.calend_handler)
        self.cal.grid(row=0, column=0, padx=5, pady=10, sticky=N)

        self.content_frame = Frame(self.win)
        self.content_frame.grid(row=0, column=1, rowspan=3, sticky=N)

        self.tool_frame = Labelframe(self.win, text='Итог')
        self.tool_frame.grid(row=1, column=0, sticky=N + W)
        Label(self.content_frame, text='Приход:', font=('normal', 12)).pack(fill=BOTH)
        self.lst = MultiListbox(self.content_frame, (
        ('Время', 8), ('Отдел', 5), ('Товар', 32), ('Сумма', 5), ('Кол.во', 1), ('Итог', 5), ('Продавец', 12)),
                                font=('normal', 10), height=15)
        self.lst.pack(fill=BOTH, expand=1)
        Label(self.content_frame, text='Расход:', font=('normal', 12)).pack(fill=BOTH)
        self.lst2 = MultiListbox(self.content_frame, (('Время', 8), ('Причина', 35), ('Сумма', 5), ('Продавец', 12)),
                                 font=('normal', 10), height=6)
        self.lst2.pack(fill=BOTH, expand=1)

        s = 'За дату: %s' % (norm_date(date_now()))
        self.d_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.d_label.grid(row=0, columnspan=2, sticky=N + W)

        s = 'Доход: 0'
        self.in_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.in_label.grid(row=1, columnspan=2, sticky=N + W)

        s = 'Расход: 0'
        self.out_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.out_label.grid(row=2, columnspan=2, sticky=N + W)

        s = 'Остаток: 0'
        self.all_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.all_label.grid(row=3, columnspan=2, sticky=N + W)

        self.scr1 = Scrollbar(self.tool_frame, orient=VERTICAL)
        self.scr1.grid(row=4, column=1, sticky=N + S, pady=5)
        self.list_1 = Listbox(self.tool_frame, width=27, height=5,
                              font=("normal", 9),
                              yscrollcommand=self.scr1.set)
        self.list_1.grid(row=4, column=0, pady=5)
        self.scr1['command'] = self.list_1.yview

        self.pdf_but = Button(self.win, text='В pdf', image=self.app.app.img['pdf'], compound='left',
                              command=self.generate_pdf)
        self.pdf_but.grid(row=2, column=0, sticky=N)

        self.update_lists()

    def calend_handler(self, date):
        """ при щелчке на дату в календаре """
        self.c_date = date
        self.update_lists()

    def update_lists(self):
        """ заполняем таблицы """
        self.lst.delete(0, END)
        self.app.app.db.execute('select time,dep,article,sum,rate,name,art_id,edit from income where date=?',
                                (self.c_date,))
        income_all = 0
        for x in self.app.app.db.fetchall():
            out = list(x)
            if out[7] <> 0:
                out[1] = str(out[1]) + ' (≈)'
            if out[6] <> -1:
                out[1] = str(out[1]) + ' →'
            out.insert(5, round(x[3] * x[4], 2))
            income_all += x[3] * x[4]
            self.lst.insert(END, out)
        self.lst.see(END)
        outcome_all = 0
        self.lst2.delete(0, END)
        self.app.app.db.execute('select time,article,sum,name,art_id,edit from outcome where date=?', (self.c_date,))
        for x in self.app.app.db.fetchall():
            out = list(x)
            if out[5] <> 0:
                out[1] = u'(≈) ' + out[1]
            self.lst2.insert(END, out)
            outcome_all += out[2]
        self.lst2.see(END)
        self.in_label['text'] = 'Доход: %s' % (income_all)
        self.out_label['text'] = 'Расход: %s' % (outcome_all)
        self.all_label['text'] = 'Остаток: %s' % (income_all - outcome_all)
        s = 'За дату: %s' % (norm_date(self.c_date))
        self.d_label['text'] = s

        deps = {}
        deps_sum = {}
        self.app.app.db.execute('select name from dep')

        self.deps = []

        for n, name in enumerate(self.app.app.db.fetchall()):
            if name:
                deps_sum[n + 1] = 0
                self.deps.append('%s' % (name[0]))

        self.app.app.db.execute('select dep,sum,rate from income where date=?', (self.c_date,))
        out = self.app.app.db.fetchall()
        in_all = 0
        for x in out:
            in_all += float(x[1]) * float(x[2])
            deps_sum[x[0]] += float(x[1]) * float(x[2])

        self.list_1.delete(0, END)

        for x in deps_sum:
            if deps_sum[x]:
                self.list_1.insert(END, str(x) + ' ' + self.deps[x - 1] + u'→ ' + str(deps_sum[x]))

    def generate_pdf(self):
        """ генерация pdf. Ваш К.О. """
        try:
            path = self.app.app.sets.save_pdf
        except:
            path = ''
        filename = 'Продажи за %s.pdf' % (norm_date(self.c_date))
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename)
        if not f: return
        f = f.replace('\\', '/')
        self.app.app.sets.save_pdf = '/'.join(f.split('/')[:-1])
        doc = pdf.Pdf(title='Продажи за %s' % (norm_date(self.c_date)), fname=f)
        doc.string('Доходы:')

        doc.table(
            [('Время', 45), ('Отд', 35), ('Товар', 220), ('Сум.', 40), ('К-во', 30), ('Итого', 40), ('Продавец', 90)])

        self.app.app.db.execute('select time,dep,article,sum,rate,name,art_id,edit from income where date=?',
                                (self.c_date,))
        income_all = 0
        for x in self.app.app.db.fetchall():
            out = list(x)
            if out[7] <> 0:
                out[1] = str(out[1]) + u' (≈)'
            if out[6] <> -1:
                out[1] = str(out[1]) + u' →'
            out.insert(5, x[3] * x[4])
            income_all += x[3] * x[4]

            doc.table(
                [(out[0], 45), (out[1], 35), (out[2], 220), (out[3], 40), (out[4], 30), (out[5], 40), (out[6], 90)],
                font=10)
        doc.enter()
        doc.string('Расходы:')
        outcome_all = 0

        doc.table([('Время', 45), ('Причина', 220), ('Сум.', 40), ('Продавец', 90)])
        self.app.app.db.execute('select time,article,sum,name,art_id,edit from outcome where date=?', (self.c_date,))
        for x in self.app.app.db.fetchall():
            out = list(x)
            if out[5] <> 0:
                out[1] = u'(≈) ' + out[1]
            doc.table([(out[0], 45), (out[1], 220), (out[2], 40), (out[3], 90)], font=10)
            outcome_all += out[2]

        doc.enter()
        doc.string('Всего доходов: %s' % (income_all))
        doc.string('Всего расходов: %s' % (outcome_all))
        doc.string('Остаток: %s' % (income_all - outcome_all))
        doc.end()
        self.win.deiconify()
