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
version = 'Мои продажи 2.0beta'
import glob
import os
import sys

sys.path.append('app/plugins/ext_lib')
sys.path.append('app/plugins/main')
sys.path.append('app/plugins/frames')
sys.path.append('app/plugins/income')
sys.path.append('app/plugins/outcome')
sys.path.append('app/plugins/execute')

from Tkinter import *
from ttk import *
from PIL import ImageTk
import sqlite3 as sql

import login_win
import main_win
import settings
import updates
import sync_win
from date_time import date2int


class App():
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

        # включение сочетания клавиш копирования на других раскладках
        root.bind_all("<Key>", self._onKeyRelease, "+")

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

        # провереряем, есть ли сохраненные апдейты,если есть, апдейтимся
        upd = os.listdir('app/updates')
        if len(upd) > 0:
            s = updates.Main(self)
        else:
            self.change_user()
        # запускаем execute  плагины
        s = os.listdir('app/plugins/execute')
        self.t_pl = {}
        for n, x in enumerate(s):
            if x.endswith('.py'):
                obj = __import__(x[:-3])
                self.t_pl[n] = getattr(obj, 'Plugin')(self)

                pass

    def change_user(self):
        """Смена пользователя"""
        self.win.destroy()
        self.win = Frame(self.root)
        self.win.pack(expand=YES, fill=BOTH)
        s = login_win.Main(self)

    def set_user(self, usr):
        """Вызывается модулем change_user"""
        self.user = usr.encode('utf-8')
        self.win.destroy()
        self.win = Frame(self.root)
        self.win.pack(expand=YES, fill=BOTH)
        self.root.title(self.title % (self.user))
        self.add_win = main_win.Main(self)

    @staticmethod
    def _onKeyRelease(event):
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")
