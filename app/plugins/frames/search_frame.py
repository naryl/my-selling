# -*-coding:utf-8-*-
# поиск  товаров, продаж и расходов
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
from Tkinter import *
from ttk import *

from MultiListbox import MultiListbox
from date_time import norm_date

name = 'Поиск'
frame = 2


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        x, y = 800, 400
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.nb = Notebook(self.win)
        self.nb.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.income_frame = Income(self)
        self.outcome_frame = Outcome(self)

        self.art_frame = Art(self)

        self.nb.add(self.income_frame.win, text='Поиск по продажам', padding=3, image=self.app.app.img['plus'],
                    compound='left')
        self.nb.add(self.outcome_frame.win, text='Поиск по расходам', padding=3, image=self.app.app.img['minus'],
                    compound='left')
        self.nb.add(self.art_frame.win, text='Поиск по товарам', padding=3, image=self.app.app.img['dep_db'],
                    compound='left')


class Income:
    def __init__(self, app):
        """ фрейм с поиском товаров """
        self.app = app
        self.win = Frame(self.app.win)
        self.frame = LabelFrame(self.win, text='Что ищем?')
        self.frame.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.search = Entry(self.frame, width=20, cursor='xterm')
        self.search.grid(row=0, column=0, padx=5, pady=5)
        self.search.bind('<KeyRelease>', self.callback)

        self.lab_var = StringVar()
        Label(self.frame, textvariable=self.lab_var).grid(row=0, column=1, padx=20)

        self.lst = MultiListbox(self.win, (
        ('Дата', 10), ('Время', 10), ('Отдел', 2), ('Товар', 50), ('Сумма', 5), ('Кол.во', 5), ('Продавец', 10)),
                                font=('normal', 9), height=15)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)

    def callback(self, event=None):
        """ вызывается при изменении содержимого entry """
        txt = '%%%s%%' % self.search.get().lower()
        self.lst.delete(0, END)
        if len(txt) < 3:
            self.lab_var.set('')
            return
        self.lab_var.set('Поиск....')
        self.win.update()
        self.app.app.app.db.execute(
            'select date,time,dep,article,sum,rate,name,art_id,edit from income where myLower(article) like ?', (txt,))
        k = 0
        all_sum = 0
        for x in self.app.app.app.db.fetchall():
            x = list(x)
            x[0] = norm_date(x[0])
            if x[8] <> 0:
                x[2] = str(x[2]) + ' (≈)'
            if x[7] <> -1:
                x[2] = str(x[2]) + ' →'
            all_sum += x[4] * x[5]
            self.lst.insert(END, x)
            k += 1
        self.lab_var.set('Найдено %s совпадений, на сумму %s' % (k, all_sum))


class Outcome:
    def __init__(self, app):
        """ ПОиск по расходам """
        self.app = app
        self.win = Frame(self.app.win)
        self.frame = LabelFrame(self.win, text='Что ищем?')
        self.frame.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.search = Entry(self.frame, width=20, cursor='xterm')
        self.search.grid(row=0, column=0, padx=5, pady=5)
        self.search.bind('<KeyRelease>', self.callback)

        self.lab_var = StringVar()
        Label(self.frame, textvariable=self.lab_var).grid(row=0, column=1, padx=20)

        self.lst = MultiListbox(self.win,
                                (('Дата', 10), ('Время', 10), ('Причина', 50), ('Сумма', 5), ('Продавец', 10)),
                                font=('normal', 9), height=15)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)

    def callback(self, event=None):
        """ Вызывается при смене содержимого entry """
        txt = '%%%s%%' % self.search.get().lower()
        self.lst.delete(0, END)
        if len(txt) < 3:
            self.lab_var.set('')
            return
        self.lab_var.set('Поиск....')
        self.win.update()
        self.app.app.app.db.execute('select date,time,article,sum,name,edit from outcome where myLower(article) like ?',
                                    (txt,))
        k = 0
        all_sum = 0
        for x in self.app.app.app.db.fetchall():
            x = list(x)
            x[0] = norm_date(x[0])
            if x[5] <> 0:
                x[2] = u'(≈) ' + x[2]

            self.lst.insert(END, x)
            all_sum += x[3]
            k += 1
        self.lab_var.set('Найдено %s совпадений, на сумму %s' % (k, all_sum))


class Art:
    def __init__(self, app):
        """ поиск по товарам """
        self.app = app
        self.win = Frame(self.app.win)
        self.frame = LabelFrame(self.win, text='Что ищем?')
        self.frame.pack(fill=BOTH, expand=1, padx=5, pady=5)

        self.search = Entry(self.frame, width=20, cursor='xterm')
        self.search.grid(row=0, column=0, padx=5, pady=5)
        self.search.bind('<KeyRelease>', self.callback)

        self.lab_var = StringVar()
        Label(self.frame, textvariable=self.lab_var).grid(row=0, column=1, padx=20)

        self.lst = MultiListbox(self.win, (('Товар', 70), ('Остаток', 10), ('Стоимость', 10)), font=('normal', 10),
                                height=15)
        self.lst.pack(fill=BOTH, expand=1, padx=5, pady=5)

    def callback(self, event=None):
        """ вызывается при смене содержимого entry """
        txt = '%%%s%%' % self.search.get().lower()
        self.lst.delete(0, END)
        if len(txt) < 3:
            self.lab_var.set('')
            return
        self.lab_var.set('Поиск....')
        self.win.update()
        self.app.app.app.db.execute('select id,rate,sum from article where myLower(name) like ? order by name', (txt,))
        k = 0
        for x in self.app.app.app.db.fetchall():
            x = list(x)

            t = []
            flag = True
            self.app.app.app.db.execute('select name,edit,sum,parent,type from article where id=?', (x[0],))
            s = self.app.app.app.db.fetchall()[0]
            par = s[3]
            t.append(s[0])
            if s[4] == 'stick':
                is_cat = True
            else:
                is_cat = False
            if par == -1:
                flag = 0

            while flag:
                self.app.app.app.db.execute('select name,parent from article where id=?', (par,))
                rez = self.app.app.app.db.fetchall()[0]
                if rez[1] == -1:
                    t.append(rez[0])
                    flag = False
                else:
                    t.append(rez[0])
                    par = rez[1]
            cat_lst = ' > '.join(t[::-1])

            if is_cat:
                x[1] = ''
                x[2] = '[категория]'
            self.lst.insert(END, [cat_lst, x[1], x[2]])
            k += 1
        self.lab_var.set('Найдено %s совпадений' % (k))
