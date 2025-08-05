# -*-coding:utf-8-*-
# показ приходов товара и списание товара
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
import tkinter.filedialog as tkFileDialog
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.ext_lib.ttk import *

import app.plugins.ext_lib.pdf
from app.plugins.ext_lib.MultiListbox import MultiListbox
from app.plugins.ext_lib.date_time import norm_date

name = 'Приходы/Списания товара'
frame = 1


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.win = Toplevel(self.app.app.win)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        self.win.title(name)
        x, y = 700, 450
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.nb = Notebook(self.win)
        self.nb.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.income_frame = Income(self)
        self.outcome_frame = Outcome(self)

        self.nb.add(self.income_frame.win, text='Приходы товаров', padding=3, image=self.app.app.img['plus'],
                    compound='left')
        self.nb.add(self.outcome_frame.win, text='Списания товаров', padding=3, image=self.app.app.img['minus'],
                    compound='left')


class Income:
    def __init__(self, app):
        """ класс с фреймом приходов товара """
        self.app = app
        self.win = Frame(self.app.win, width=20, height=50)
        self.lst = MultiListbox(self.win, (('Дата', 8), ('Время', 5), ('Приход', 50), ('Пользователь', 10)),
                                font=('normal', 10), height=7, command=self.l_command)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.lst2 = MultiListbox(self.win, (('Отдел', 3), ('Товар', 73), ('Количество', 5)), font=('normal', 10),
                                 height=10)
        self.lst2.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.pdf_but = Button(self.win, text='В pdf', image=self.app.app.app.img['pdf'], compound='left',
                              command=self.generate_pdf)
        self.pdf_but.pack(anchor=W)

        self.app.app.app.db.execute('select id,date,time,rate,user from in_art')
        rez = self.app.app.app.db.fetchall()
        self.sums = {}
        self.ids = {}
        self.naim = {}
        self.user = {}
        for x in rez:
            self.ids[x[0]] = [norm_date(x[1]), x[2], x[4]]
            self.sums[x[0]] = self.sums.setdefault(x[0], 0) + x[3]
            self.naim[x[0]] = self.naim.setdefault(x[0], 0) + 1

        k = self.ids.keys()
        k.sort()
        self.c_id = k

        for x in k:
            self.lst.insert(END, [self.ids[x][0], self.ids[x][1],
                                  'Наименований товаров %s шт., общее количество %s шт.' % (self.naim[x], self.sums[x]),
                                  self.ids[x][2]])
        self.lst.see(END)

    def l_command(self):
        """ при выборе прихода, показываем список товаров """
        if not self.lst.curselection(): return
        sel = int(self.lst.curselection()[0])
        id = self.c_id[sel]
        self.lst2.delete(0, END)

        self.app.app.app.db.execute('select dep,name,rate from in_art where id=?', (id,))
        for x in self.app.app.app.db.fetchall():
            self.lst2.insert(END, x)

    def generate_pdf(self):
        """ генерация pdf c выбранным приходом """
        if not self.lst.curselection(): return
        sel = int(self.lst.curselection()[0])
        id = self.c_id[sel]

        self.app.app.app.db.execute('select date,time from in_art where id=?', (id,))
        rez = self.app.app.app.db.fetchall()[0]

        try:
            path = self.app.app.app.sets.save_pdf
        except:
            path = ''
        print(rez)
        filename = ('Приход товара за %s %s.pdf' % (norm_date(rez[0]), str(rez[1]))).replace(':', '-')
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename)
        if not f: return
        f = f.replace('\\', '/')
        self.app.app.app.sets.save_pdf = '/'.join(f.split('/')[:-1])
        doc = pdf.Pdf(title='Приход товара', fname=f)
        doc.string('Приход товара за %s %s' % (norm_date(rez[0]), str(rez[1])))

        self.app.app.app.db.execute('select dep,name,rate from in_art where id=?', (id,))
        doc.table([('Отдел', 45), ('Товар', 350), ('Кол.во', 50)])
        n = 0
        s = 0
        for x in self.app.app.app.db.fetchall():
            n += 1
            doc.table([(x[0], 45), (x[1], 350), (x[2], 50)], font=10)
            s += x[2]
        doc.enter()
        doc.string('Наименований: %s' % (n))
        doc.string('Количество: %s' % (s))

        doc.end()
        self.app.win.deiconify()


class Outcome:
    def __init__(self, app):
        """ список списаний """
        self.app = app
        self.win = Frame(self.app.win)
        self.lst = MultiListbox(self.win,
                                (('Дата', 11), ('Время', 8), ('Товар', 45), ('Причина', 15), ('К-во', 3), ('Кто', 10)),
                                font=('normal', 9), height=17)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)
        self.app.app.app.db.execute('select * from out_art')
        for x in self.app.app.app.db.fetchall():
            x = list(x)
            x[0] = norm_date(x[0])
            self.lst.insert(END, x)
        self.lst.see(END)
