# -*-coding:utf-8-*-
# показ остатков товара
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
import csv
import tkinter.filedialog as tkFileDialog
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.ext_lib.ttk import *

from app.plugins.ext_lib.MultiListbox import MultiListbox
from app.plugins.ext_lib.date_time import date_now, norm_date

name = 'Остатки товара'
frame = 1


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        self.win.title(name)
        x, y = 600, 500
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.add_f = LabelFrame(self.win, text='Остатки товара по отделу...')
        self.add_f.pack(expand=YES, fill=X, anchor=N, padx=5, pady=5)
        self.init_deps()

        self.rb_var = IntVar()
        self.rb = Radiobutton(self.add_f, text='Показать все', value=0, variable=self.rb_var, command=self.callback)
        self.rb.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        self.rb2 = Radiobutton(self.add_f, text='Показать меньше ', value=1, variable=self.rb_var,
                               command=self.callback)
        self.rb2.grid(row=0, column=2, sticky=W, padx=5, pady=5)

        self.rate_ent = Entry(self.add_f, width=5, cursor='xterm')
        self.rate_ent.grid(row=0, column=3)
        self.rate_ent.insert(END, '3')
        self.rate_ent.bind('<KeyRelease>', self.callback1)

        self.lst = MultiListbox(self.win, (('Товар', 50), ('Остаток', 5), ('Стоимость', 6)), font=('normal', 11),
                                height=19)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)
        self.lab_var = StringVar()

        self.all_label = Label(self.win, textvariable=self.lab_var, font=('bold', 12))
        self.all_label.pack(padx=5)
        self.pdf_but = Button(self.win, text='В pdf', image=self.app.app.img['pdf'], compound='left',
                              command=self.generate_pdf)
        self.pdf_but.pack(side='left', padx=5, pady=5, anchor=W)

        self.csv_but = Button(self.win, text='В csv', image=self.app.app.img['csv'], compound='left',
                              command=self.generate_csv)
        self.csv_but.pack(side='left', padx=5, pady=5, anchor=W)

        self.callback()

    def init_deps(self):
        """ меня с отделами, как мне надоело это писать """

        self.deps = []
        self.app.app.db.execute('select name from dep')
        for n, name in enumerate(self.app.app.db.fetchall()):
            self.deps.append('%s %s' % (n + 1, name[0]))

        self.cur_dep = 0
        self.dep_str = StringVar()
        self.dep_str.set(self.deps[0])
        Style().configure("TMenubutton", font=('bold', 13))
        self.otd = Menubutton(self.add_f, textvariable=self.dep_str,
                              width=19, image=self.app.app.img['deps'], compound='left')
        self.otd.grid(row=0, column=0, pady=5, padx=5)
        self.otd.menu = Menu(self.otd,
                             font=("bold", 13), bg='white', relief='flat', tearoff=0)
        for n, x in enumerate(self.deps):
            if len(x) > 3:
                self.otd.menu.add_command(label=x.ljust(25), command=lambda z=n: self.deps_hand(z))
        self.otd['menu'] = self.otd.menu

    def deps_hand(self, n):
        """ вызывается при выборе отдела """
        self.cur_dep = n
        self.dep_str.set(self.deps[n])
        self.cat_id = -1
        self.callback()

    def callback1(self, event=None):
        """ при смене количества """
        self.rb_var.set(1)
        self.callback()

    def callback(self, event=None):
        """ при смене чекбатонна, заполняем таблицу заново """
        self.lst.delete(0, END)
        r = self.rb_var.get()
        rate = self.rate_ent.get()

        if r == 0:
            self.app.app.db.execute('select id,rate,sum,type from article where dep=?', (self.cur_dep + 1,))
        else:
            try:
                rate = int(rate)
            except:
                return
            self.app.app.db.execute('select id,rate,sum,type from article where dep=? and rate<?',
                                    (self.cur_dep + 1, rate))
        rez1 = self.app.app.db.fetchall()

        all_rate = 0
        all_sum = 0
        for x in rez1:

            t = []
            flag = True
            self.app.app.db.execute('select name,edit,sum,parent from article where id=?', (x[0],))
            s = self.app.app.db.fetchall()[0]
            par = s[3]
            t.append(s[0])
            if par == -1: flag = 0
            while flag:
                self.app.app.db.execute('select name,parent from article where id=?', (par,))
                rez = self.app.app.db.fetchall()[0]
                if rez[1] == -1:
                    t.append(rez[0])
                    flag = False
                else:
                    t.append(rez[0])
                    par = rez[1]
            cat_lst = ' > '.join(t[::-1])
            if x[3] == 'item':
                self.lst.insert(END, [cat_lst, x[1], x[2]])
                all_rate += x[1]
                all_sum += x[1] * x[2]

        self.lab_var.set('Наименований: %s, количество: %s, на сумму %s' % (len(rez1), all_rate, all_sum))

    def generate_pdf(self):
        """ генерация pdf """
        try:
            path = self.app.app.sets.save_pdf
        except:
            path = ''
        filename = 'Остатки по отделу %s на %s.pdf' % (self.cur_dep + 1, norm_date(date_now()))
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename)
        if not f: return
        f = f.replace('\\', '/')
        self.app.app.sets.save_pdf = '/'.join(f.split('/')[:-1])
        doc = pdf.Pdf(title='Остатки товара', fname=f)

        r = self.rb_var.get()
        rate = self.rate_ent.get()
        self.app.app.db.execute('select name from dep where id=?', (self.cur_dep + 1,))

        dep_name = self.app.app.db.fetchall()[0][0]

        if r == 0:
            self.app.app.db.execute('select id,rate,sum,type from article where dep=?', (self.cur_dep + 1,))
            doc.string(u'Все остатки по отделу %s %s' % (self.cur_dep + 1, dep_name))
        else:
            try:
                rate = int(rate)
            except:
                return
            self.app.app.db.execute('select id,rate,sum,type from article where dep=? and rate<?',
                                    (self.cur_dep + 1, rate))
            doc.string(u'Остатки по отделу %s %s, количество товара меньше %s' % (self.cur_dep + 1, dep_name, rate))
        rez1 = self.app.app.db.fetchall()

        all_rate = 0
        all_sum = 0
        doc.table([('Товар', 300), ('Остаток', 80), ('Стоимость', 80)])
        for x in rez1:

            t = []
            flag = True
            self.app.app.db.execute('select name,edit,sum,parent from article where id=?', (x[0],))
            s = self.app.app.db.fetchall()[0]
            par = s[3]
            t.append(s[0])
            if par == -1: flag = 0
            while flag:
                self.app.app.db.execute('select name,parent from article where id=?', (par,))
                rez = self.app.app.db.fetchall()[0]
                if rez[1] == -1:
                    t.append(rez[0])
                    flag = False
                else:
                    t.append(rez[0])
                    par = rez[1]
            cat_lst = ' > '.join(t[::-1])
            if x[3] == 'item':
                doc.table([(cat_lst, 300), (x[1], 80), (x[2], 80)], font=10)
                all_rate += x[1]
                all_sum += x[1] * x[2]

        self.lab_var.set('Наименований: %s, количество: %s, на сумму %s' % (len(rez1), all_rate, all_sum))
        doc.enter()
        doc.string('Всего наименований: %s' % (len(rez1)))
        doc.string('Всего количество: %s, на сумму %s' % (all_rate, all_sum))
        doc.end()
        self.win.deiconify()

    def generate_csv(self):
        """ генерация csv """
        try:
            path = self.app.app.sets.save_pdf
        except:
            path = ''
        filename = 'Остатки по отделу %s на %s.csv' % (self.cur_dep + 1, norm_date(date_now()))
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename)
        if not f: return
        f = f.replace('\\', '/')
        self.app.app.sets.save_pdf = '/'.join(f.split('/')[:-1])
        doc = csv.writer(open(f, 'w'), delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
        doc.writerow([u'Товар'.encode('cp1251'), u'Остаток'.encode('cp1251'), u'Стоимость'.encode('cp1251')])

        r = self.rb_var.get()
        rate = self.rate_ent.get()
        self.app.app.db.execute('select name from dep where id=?', (self.cur_dep + 1,))

        dep_name = self.app.app.db.fetchall()[0][0]

        if r == 0:
            self.app.app.db.execute('select id,rate,sum,type from article where dep=?', (self.cur_dep + 1,))
        else:
            try:
                rate = int(rate)
            except:
                return
            self.app.app.db.execute('select id,rate,sum,type from article where dep=? and rate<?',
                                    (self.cur_dep + 1, rate))
        rez1 = self.app.app.db.fetchall()

        all_rate = 0
        all_sum = 0
        for x in rez1:

            t = []
            flag = True
            self.app.app.db.execute('select name,edit,sum,parent from article where id=?', (x[0],))
            s = self.app.app.db.fetchall()[0]
            par = s[3]
            t.append(s[0])
            if par == -1: flag = 0
            while flag:
                self.app.app.db.execute('select name,parent from article where id=?', (par,))
                rez = self.app.app.db.fetchall()[0]
                if rez[1] == -1:
                    t.append(rez[0])
                    flag = False
                else:
                    t.append(rez[0])
                    par = rez[1]
            cat_lst = ' > '.join(t[::-1])
            if x[3] == 'item':
                doc.writerow([cat_lst.encode('cp1251'), x[1], x[2]])

                all_rate += x[1]
                all_sum += x[1] * x[2]

        self.lab_var.set('Наименований: %s, количество: %s, на сумму %s' % (len(rez1), all_rate, all_sum))

        self.win.deiconify()
