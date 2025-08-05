# -*-coding:utf-8-*-
# все любят всякие графики :)
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
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.ext_lib.ttk import *

from app.plugins.ext_lib.calend import TkCalendar
from app.plugins.ext_lib.date_time import date_now, norm_date, all_dates

name = 'Статистика по...'
frame = 2


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        self.win.title(name)
        x, y = 600, 400
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')
        year, month = time.localtime()[0:2]
        self.date_t = StringVar()
        self.date_t.set(date_now())
        self.c_date = date_now()
        Label(self.win, text='Начиная с..').grid(row=0, column=0, padx=5, pady=2)
        self.cal = TkCalendar(self.win, year, month, self.date_t, command=self.calend_handler)
        self.cal.grid(row=1, column=0, padx=5, sticky=N)

        self.frame = Labelframe(self.win, text='Показывать', width=275, height=200)
        self.frame.grid(row=0, column=1, rowspan=2)
        self.win.columnconfigure(1, minsize=275)

        self.date2_t = StringVar()
        self.date2_t.set(date_now())
        self.c_date2 = date_now()
        Label(self.win, text='Заканчивая..').grid(row=0, column=2, padx=5, pady=2)
        self.cal2 = TkCalendar(self.win, year, month, self.date_t, command=self.calend_handler2)
        self.cal2.grid(row=1, column=2, padx=5, sticky=NE)
        self.lab_var = StringVar()
        Label(self.frame, textvariable=self.lab_var, font=('bold', 10)).grid(row=0, column=0, columnspan=2, padx=10,
                                                                             pady=5)

        Label(self.frame, text='По отделу').grid(row=1, column=0, sticky=E)
        self.dep_ent_txt = StringVar()
        self.dep_ent_txt.set('Все отделы')
        self.dep_ent = Combobox(self.frame, width=20, state='readonly', textvariable=self.dep_ent_txt)
        self.dep_ent.grid(row=1, column=1, pady=5)

        Label(self.frame, text='По продавцу').grid(row=2, column=0, sticky=E)
        self.per_ent_var = StringVar()
        self.per_ent_var.set('Все продавцы')
        self.per_ent = Combobox(self.frame, width=20, state='readonly', textvariable=self.per_ent_var)
        self.per_ent.grid(row=2, column=1, pady=5)

        self.show_but = Button(self.frame, text='Показать', image=self.app.app.img['check'], compound='left',
                               command=self.calculate)
        self.show_but.grid(row=3, column=0, columnspan=2, pady=27)

        self.app.app.db.execute('select name from dep')
        self.deps = [u'Все отделы']
        for x in self.app.app.db.fetchall():
            if x[0]: self.deps.append(x[0])
        self.dep_ent['values'] = self.deps

        self.app.app.db.execute('select name from users')
        self.users = [u'Все продавцы']
        for x in self.app.app.db.fetchall(): self.users.append(x[0])
        self.per_ent['values'] = self.users

        self.out_var = StringVar()
        self.out_var.set(' ')
        Label(self.win, textvariable=self.out_var, font=('bold', 12)).grid(row=2, column=0, columnspan=3, sticky=W,
                                                                           padx=15, pady=5)
        self.canvas = Canvas(self.win, width=580, height=150, background='white')
        self.canvas.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.update_label()

    def calend_handler(self, date):
        """выбор начальной даты """
        self.c_date = date
        self.update_label()

    def calend_handler2(self, date):
        """ выбор конечной даты """
        self.c_date2 = date
        self.update_label()

    def update_label(self):
        self.lab_var.set('Показать с  %s  по %s' % (norm_date(self.c_date), norm_date(self.c_date2)))

    def calculate(self):
        """ собственно сама функия сбора статистики """
        self.out_var.set('Идет сбор данных...')
        self.win.update()
        self.canvas.delete(ALL)
        dep = self.dep_ent.get()
        if dep == u'Все отделы':
            dep = -1
        else:
            self.app.app.db.execute('select id from dep where name=?', (dep,))
            dep = self.app.app.db.fetchall()[0][0]
        per = self.per_ent.get()
        # делаем запросы в зависимости от того что хотим посмотреть
        if per == u'Все продавцы': per = -1

        if per == -1 and dep == -1:
            self.app.app.db.execute('select date,sum,rate from income where date between ? and ?',
                                    (self.c_date, self.c_date2))
        elif per == -1 and dep != -1:
            self.app.app.db.execute('select date,sum,rate from income where dep=? and date between ? and ?',
                                    (dep, self.c_date, self.c_date2))
        elif per != -1 and dep == -1:
            self.app.app.db.execute('select date,sum,rate from income where name=? and date between ? and ?',
                                    (per, self.c_date, self.c_date2))
        else:
            self.app.app.db.execute('select date,sum,rate from income where name=? and dep=? and date between ? and ?',
                                    (per, dep, self.c_date, self.c_date2))
        rezult = self.app.app.db.fetchall()
        rez = {}
        for x in all_dates(self.c_date, self.c_date2):
            rez[x] = 0
        all_sum = 0
        for x in rezult:
            rez[x[0]] += x[1] * x[2]
            all_sum += x[1] * x[2]
        try:
            self.out_var.set(
                'Итог за %s дней составляет %s. Среднее за день %s' % (len(rez), all_sum, int(all_sum / len(rez))))
        except ZeroDivisionError:
            self.out_var.set('Конечная дата не может быть меньше начальной')
            return
        k = rez.keys()
        k.sort()
        mx = max(rez.values())

        # вооо... график, который так любят смотреть рукогодители, строим на canvas
        # желаю чтоб не было провалов...
        last_x = 0
        last_y = 0
        k_x = 580.0 / float(len(k))

        for i in k:
            x = k_x + last_x
            try:
                y = float(rez[i]) / mx * 150.0
            except ZeroDivisionError:
                return

            self.canvas.create_line(last_x, 150 - last_y, x, 150 - y, fill='#348442')
            if i.split('-')[2] == '01':
                self.canvas.create_line(x, 0, x, 150, fill='grey')
                self.canvas.create_text(x + 2, 30, text=i.split('-')[1], fill='black', anchor=NW)
            last_x = x
            last_y = y
        self.canvas.create_text(3, 3, text=str(mx), fill='red', anchor=NW)
        self.canvas.create_text(3, 60, text=str(int(mx / 2)), fill='red', anchor=NW)
        self.canvas.create_line(0, 75, 580, 75, fill='grey')
