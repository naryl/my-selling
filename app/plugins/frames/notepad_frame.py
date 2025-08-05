# -*-coding:utf-8-*-
# экран блокнота
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
import sys
import tkinter.messagebox as box
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.main.edit_log import Log
from app.plugins.ext_lib.ttk import *

# noinspection PyByteLiteral
name = 'Блокнот'
frame = 0
icon = 'notepad'


# noinspection DuplicatedCode,PyAttributeOutsideInit,PyByteLiteral
class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.log = Log(self.app.app)

        if hasattr(self.app, "notepad_frame") \
                and self.app.notepad_frame.winfo_exists():
            self.app.notepad_frame.deiconify()
            self.app.notepad_frame.focus()
            self.app.notepad_frame.state()
            return 'break'

        self.win = Toplevel(self.app.app.win)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        self.app.notepad_frame = self.win
        self.win.title(name)
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        x, y = 1000, 800
        pos = self.win.wm_maxsize()[0] // 2 - x // 2, self.win.wm_maxsize()[1] // 2 - y // 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32':
            self.win.iconbitmap('app/images/icon.ico')

        self.content_frame = Frame(self.win)
        self.content_frame.pack(fill=BOTH, expand=1)

        self.txt_frame = Frame(self.content_frame)
        self.txt_frame.pack(side=TOP, fill=BOTH, expand=1)

        self.txt = Text(self.txt_frame, font=('bold', 14))
        self.scroll = Scrollbar(self.txt_frame)
        self.txt.pack(side=LEFT, fill=BOTH, expand=1)
        self.scroll.pack(side=LEFT, fill=Y)
        self.txt.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.txt.yview)

        self.save_button = Button(self.content_frame, text='Сохранить', command=self.save_text,
                                  image=self.app.app.img['save'], compound='left', width=15)
        self.save_button.pack(side=BOTTOM, anchor=W, padx=5, pady=5)

        self.load_text()

    def exit(self, _=None, quiet=False):
        """ при выходе спрашиваем, обновляем главное окно """
        if not quiet and self.is_text_changed():
            if box.askyesno(title='Закрытие блокнота', message='Сохранить изменения?',
                            parent=self.win):
                self.save_text()
        self.app.update_list()
        self.app.update_tools()
        delattr(self.app, "notepad_frame")
        self.win.destroy()

    def save_text(self):
        """ сохранение текста """
        txt_value = self.txt.get('0.0', END).replace('\t', ' ')
        self.app.app.sets.notepad_text = txt_value

        self.exit(quiet=True)

    def load_text(self):
        """ загрузка текста """
        txt_value = self.app.app.sets.notepad_text
        self.txt.delete(0.0, END)
        self.txt.insert(0.0, txt_value)

    def is_text_changed(self):
        db_txt_value = self.app.app.sets.notepad_text
        txt_value = self.txt.get('0.0', END).replace('\t', ' ')
        return db_txt_value.rstrip() != txt_value.rstrip()
