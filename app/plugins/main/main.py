# coding:utf-8
# основной модуль программы, которые координирует все остальное
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
from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin

version = 'Мои продажи 3.0RC1'
import glob
import os
import sys

from tkinter import *
from app.plugins.ext_lib.ttk import *
from PIL import ImageTk
import sqlite3 as sql

import app.plugins.main.login_win as login_win
import app.plugins.main.main_win as main_win
import app.plugins.main.settings as settings
import app.plugins.main.sync_win as sync_win
from app.plugins.ext_lib.date_time import date2int

import app.plugins.execute.sync_execute as sync_execute


class App:
    def create_images(self):
        """img - словарь содержащий ImageTk изображения.
        Ключи словаря это имена картинок без расширения"""
        self.img = {}
        for i in glob.glob('app/images/*.png'):
            self.img[i.split(os.sep)[-1].split('.')[0]] = ImageTk.PhotoImage(file=i)

    def exit(self, event=None):
        """При закрытии приложения запускаем синхронизацию"""
        if not self.is_exit:
            self.win.destroy()
            self.win = Frame(self.root)
            self.win.pack(expand=YES, fill=BOTH)
            self.is_exit = True
            s = sync_win.Main(self)

    def __init__(self, root):
        self.version = version
        self.is_exit = False
        self.title = '%s - ' + self.version
        root.title(self.title % ('Выбор пользователя'))
        root.minsize(800, 600)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(root)

        if sys.platform == 'win32':
            root.state('zoomed')
            root.iconbitmap('app/images/icon.ico')

        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.con = sql.connect('app/db/main.db')
        self.db = self.con.cursor()

        try:
            self.db.execute('select name from dep')
        except sql.OperationalError:
            # если базы данных нет, то создаем ее из схемы
            self.db.executescript(open('app/db/schema.sql').read())
        # функция для поиска по юникоду в базе данных
        self.con.create_function('myLower', 1, lambda x: x.lower())
        # для поиска по "больше чем дата и время"
        self.con.create_function('myDate', 2, lambda x, y: date2int(x, y))
        self.sets = settings.Settings(self)

        self.create_images()
        self.win = Frame(self.root)
        self.win.pack(expand=YES, fill=BOTH)

        self.change_user()

        sync_execute.Plugin(self)

    def change_user(self):
        """Смена пользователя"""
        self.win.destroy()
        self.win = Frame(self.root)
        self.win.pack(expand=YES, fill=BOTH)
        s = login_win.Main(self)

    def set_user(self, usr):
        """Вызывается модулем change_user"""
        self.user = usr
        self.win.destroy()
        self.win = Frame(self.root)
        self.win.pack(expand=YES, fill=BOTH)
        self.root.title(self.title % (usr))
        self.add_win = main_win.Main(self)
