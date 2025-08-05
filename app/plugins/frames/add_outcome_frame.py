# -*-coding:utf-8-*-
# добавление расхода
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
import os
import sys
import tkinter.messagebox as box
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.ext_lib.ttk import *

from app.plugins.ext_lib.date_time import date_now, time_now

name = 'Добавить расход'
frame = 0


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        x, y = 600, 110
        pos = self.win.wm_maxsize()[0] // 2 - x // 2, self.win.wm_maxsize()[1] // 2 - y // 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1]))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')
        self.a_win = Frame(self.win)
        self.a_win.pack()
        Label(self.a_win, text='Причина', font=('bold', 14)).grid(row=0, column=0, pady=15, padx=5)
        self.pr_ent = Entry(self.a_win, width=30, font=('bold', 14), cursor='xterm')
        self.pr_ent.grid(row=0, column=1)
        Label(self.a_win, text='Сумма', font=('bold', 14)).grid(row=0, column=2, pady=15, padx=5)
        self.sum_ent = Entry(self.a_win, width=7, font=('bold', 14), cursor='xterm')
        self.sum_ent.grid(row=0, column=3)

        # сохранять при нажатии Enter в поле деталей
        def return_handler(_):
            min_size = 2
            if len(self.sum_ent.get()) >= min_size:
                self.add_handler()

        self.sum_ent.bind("<Return>", return_handler)

        self.add_but = Button(self.win, text='Добавить от %s' % (self.app.app.user), image=self.app.app.img['db_add'],
                              compound='left', command=self.add_handler)
        self.add_but.pack(side=RIGHT, padx=10, pady=5)

    def add_handler(self):
        """ добавление расхода """
        text = self.pr_ent.get()
        try:
            s = float(self.sum_ent.get().replace(',', '.'))
        except:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            self.win.deiconify()
            return
        if s <= 0:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            self.win.deiconify()
            return
        if len(text) < 3:
            box.showerror(title='Ошибка', message='Вы должны ввести причину!')
            self.win.deiconify()
            return
        dt, tm = date_now(), time_now()
        self.app.app.db.execute('insert into outcome values (?,?,?,?,?,?,0)',
                                (dt, tm, text, -1, s, self.app.app.user.encode('utf-8')))
        self.app.app.con.commit()
        self.win.destroy()

        cashbox_value = float(self.app.app.sets.cashbox)
        cashbox_value -= s
        self.app.app.sets.cashbox = cashbox_value

        self.app.update_tools()
        self.init_add_plugins(dt, tm)

    def init_add_plugins(self, dt, tm):
        """ Плагины при добавлении расхода """
        # TODO: Заменить словариком плагинов (Пока их всё равно нет)
        return
        s = os.listdir('app/plugins/outcome')
        for x in s:
            if x.endswith('.py'):
                obj = __import__(x[:-3])
                cl = getattr(obj, 'Plugin')(self, dt, tm)
