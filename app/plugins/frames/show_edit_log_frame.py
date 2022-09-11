# -*-coding:utf-8-*-
# просмотр правок 
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
from Tkinter import *
from ttk import *

from MultiListbox import MultiListbox
from calend import TkCalendar
from date_time import date_now, norm_date

name = 'Просмотреть правки'
frame = 2


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

        self.tool_frame = Frame(self.win)
        self.tool_frame.grid(row=1, column=0, sticky=N + W)
        Label(self.content_frame, text='Список:', font=('normal', 12)).pack(fill=BOTH)
        self.lst = MultiListbox(self.content_frame, (('Дата', 10), ('Время', 9), ('Действие', 45)), font=('normal', 12),
                                height=15, command=self.command_handler)
        self.lst.pack(fill=BOTH, expand=1)
        Label(self.content_frame, text='Правка:', font=('normal', 12)).pack(fill=BOTH)
        self.scroll = Scrollbar(self.content_frame)
        self.txt = Text(self.content_frame, width=68, height=5, font=('normal', 12))
        self.scroll.pack(side=RIGHT, fill=Y)
        self.txt.pack(side=LEFT, fill=Y)
        self.scroll.config(command=self.txt.yview)
        self.txt.config(yscrollcommand=self.scroll.set)

        s = 'За дату: %s' % ('.'.join(date_now().split('-')[::-1]))
        self.d_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.d_label.grid(row=0, columnspan=2, sticky=N + W)
        self.all_button = Button(self.tool_frame, text='Смотреть все', command=self.show_all, width=15)
        self.all_button.grid(row=1, column=0, sticky=N, pady=5)

        self.update_lists()

    def calend_handler(self, date):
        """при выборе даты """
        self.c_date = date
        self.update_lists()
        self.txt.delete(0.0, END)

    def update_lists(self):
        """ обновляем списки """
        self.all_data = []
        self.lst.delete(0, END)
        if self.c_date == 'Все':
            self.app.app.db.execute('select date,time,title,event from edit_log')
        else:
            self.app.app.db.execute('select date,time,title,event from edit_log where date=?', (self.c_date,))
        for x in self.app.app.db.fetchall():
            x = list(x)
            x[0] = norm_date(x[0])
            self.lst.insert(END, x)
            self.all_data.append(x)
        self.lst.see(END)
        if self.c_date == 'Все':
            self.d_label['text'] = 'За дату: ВСЕ'
        else:
            s = 'За дату: %s' % (norm_date(self.c_date))
            self.d_label['text'] = s

    def command_handler(self):
        """ при выборе пункта в таблице, показываем полный текст изменения """
        if not self.lst.curselection(): return
        c = int(self.lst.curselection()[0])
        txt = self.all_data[c][3]
        self.txt.delete(0.0, END)
        self.txt.insert(0.0, txt)

    def show_all(self):
        """ по кнопке "смотреть все" """
        self.c_date = 'Все'
        self.update_lists()
        self.txt.delete(0.0, END)
