# coding:utf-8
# экран выбора пользователся
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
import tkMessageBox as box
from Tkinter import *
from ttk import *

import md5py

import about_win


class Main:
    def __init__(self, app):
        self.app = app

        self.win = Frame(self.app.win)
        self.win.place(relx=0.5, rely=0.5, anchor=CENTER)
        Label(self.win, image=self.app.img['note']).pack()
        self.frame = LabelFrame(self.win, text='Выбор пользователя', height=400)
        self.frame.pack()

        self.app.db.execute('select name from users')
        self.buttons = []
        Style().configure("TButton", font=('bold', 14))
        # добавляем кнопки с пользователями
        for x, name in enumerate(self.app.db.fetchall()):
            self.buttons.append(
                Button(self.frame, text=name[0].ljust(100), image=self.app.img['people'], compound='left',
                       command=lambda z=name[0]: self.set_usr(z), width=25, cursor='hand2'))
            self.buttons[x].grid(row=x, column=0, columnspan=2, padx=10, pady=3)

        Label(self.frame, text='Пароль').grid(row=x + 1, column=0, padx=5)
        self.passw = Entry(self.frame, cursor='xterm', show="*", width=19)
        self.passw.grid(row=x + 1, column=1, padx=5)
        self.passw.bind('<KeyPress-Return>', self.set_enter)
        Style().configure("TButton", font=(10))
        self.enter = Button(self.frame, text='Войти', command=self.set_enter, width=25, cursor='hand2')
        self.enter.grid(row=x + 2, column=0, columnspan=2, pady=5)
        self.passw['state'] = 'disable'
        self.enter['state'] = 'disable'

        self.b = Button(self.app.root, text='О программе', image=self.app.img[
            'about'], compound='left', command=self.show_about)
        self.b.place(relx=0.5, rely=0.93, anchor=CENTER)

    def show_about(self):
        s = about_win.Main(self)

    def set_usr(self, name):
        self.passw.delete(0, END)
        self.app.db.execute('select passw from users where name=?', (name,))
        s = self.app.db.fetchone()[0]
        # если пароль не требуется, "заходим", иначе требуем
        if not s:
            self.app.set_user(name)
            return
        self.passw['state'] = 'normal'
        self.enter['state'] = 'normal'
        self.enter['text'] = 'Войти (%s)' % name.encode('utf-8')
        self.name = name
        self.passw.focus()

    def set_enter(self, event=None):
        passw = md5py.new(self.passw.get().encode('utf-8')).hexdigest()
        self.app.db.execute('select passw from users where name=?', (self.name,))
        # проверяем правильность пароля
        if self.app.db.fetchone()[0] == passw:
            self.app.set_user(self.name)
        else:
            box.showerror(title='Ошибка!', message='Не верный пароль')
            self.passw.delete(0, END)
            self.passw.focus()
