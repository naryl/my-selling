# -*-coding:utf-8-*-
# окно "о программе"
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

import tkFont as tfont
import webbrowser
from ScrolledText import ScrolledText
from Tkinter import *
from ttk import *


class Main:
    def __init__(self, app):
        self.app = app
        self.win = Toplevel(self.app.app.win)
        self.win.title('О программе')
        x, y = 600, 400
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.menu = Menu(self.win, tearoff=0)
        self.menu.add_command(label="Копировать")

        Label(self.win, text=self.app.app.version, font=('bold', 28)).place(x=180, y=20)
        Label(self.win, text='Автор: Игорь aka kAIST', font=('bold', 18)).place(x=180, y=70)
        Label(self.win, text='Сайт:', font=('bold', 18)).place(x=180, y=100)
        Label(self.win, image=self.app.app.img['note']).place(x=20, y=20)

        self.site = Label(self.win, text='http://my-selling.ru', font=tfont.Font(underline=1, size=18),
                          foreground='blue',
                          cursor='hand2')
        self.site.place(x=250, y=100)
        self.site.bind('<ButtonRelease>', self.go_to_the_site)
        self.d_frame = LabelFrame(self.win, text='Поддержи проект', width=590, height=100)
        self.d_frame.place(x=5, y=150)

        Label(self.d_frame, text='Вы можете поддержать проект одним из следующих способов:').grid(row=0, column=0,
                                                                                                  columnspan=10,
                                                                                                  sticky=N, padx=100)
        Label(self.d_frame, text='1. WebMoney').grid(row=1, column=0, padx=5, pady=5, sticky=W)

        self.wm = Entry(self.d_frame, cursor='xterm')
        self.wm.insert(END, 'R415730487974')
        self.wm.grid(row=1, column=1)
        self.wm.bind("<Button-3><ButtonRelease-3>", self.show_context_menu)
        self.wm.bind("<Button-1><ButtonRelease-1>", self.show_context_menu)

        self.wm2 = Entry(self.d_frame, cursor='xterm')
        self.wm2.insert(END, 'Z384919381339')
        self.wm2.grid(row=1, column=2)
        self.wm2.bind("<Button-3><ButtonRelease-3>", self.show_context_menu)
        self.wm2.bind("<Button-1><ButtonRelease-1>", self.show_context_menu)

        Label(self.d_frame, text='1. Яндекс.Деньги').grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.wm3 = Entry(self.d_frame, cursor='xterm')
        self.wm3.insert(END, '4100187212636')
        self.wm3.grid(row=2, column=1)
        self.wm3.bind("<Button-3><ButtonRelease-3>", self.show_context_menu)
        self.wm3.bind("<Button-1><ButtonRelease-1>", self.show_context_menu)
        Label(self.d_frame,
              text='3. Платная СМС на номер 4445 с текстом dam 104966 ВАШЕ_ПОЖЕЛЕНИЕ (цена не более 20 р.)').grid(row=3,
                                                                                                                  column=0,
                                                                                                                  padx=5,
                                                                                                                  pady=5,
                                                                                                                  sticky=W,
                                                                                                                  columnspan=3)
        self.txt = ScrolledText(self.win, width=80, height=6, font=('normal', 10), wrap='word')
        self.txt.place(x=5, y=285)
        t = """ТАК КАК ПРОГРАММА ЛИЦЕНЗИРУЕТСЯ БЕСПЛАТНО, НА ПРОГРАММУ НЕТ ГАРАНТИИ В СТЕПЕНИ, РАЗРЕШЕННОЙ СООТВЕТСВУЮЩИМ ЗАКОНОМ. ЗА ИСКЛЮЧЕНИЕМ СЛУЧАЕВ, КОГДА В ПИСЬМЕННОМ ВИДЕ СКАЗАНО ИНОЕ, ОБЛАДАТЕЛИ АВТОРСКИХ ПРАВ И/ИЛИ ДРУГИЕ СТОРОНЫ ПРЕДОСТАВЛЯЮТ ПРОГРАММУ "КАК ЕСТЬ" БЕЗ ГАРАНТИЙНЫХ ОБЯЗАТЕЛЬСТВ ЛЮБОГО ВИДА, ЯВНЫХ ИЛИ КОСВЕННЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ТОЛЬКО ИМИ, КОСВЕННЫЕ ГАРАНТИЙНЫЕ ОБЯЗАТЕЛЬСТВА, СВЯЗАННЫЕ С ПОТРЕБИТЕЛЬСКИМИ СВОЙСТВАМИ И ПРИГОДНОСТЬЮ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. ВЕСЬ РИСК, СВЯЗАННЫЙ КАК С КАЧЕСТВОМ, ТАК И С ПРОИЗВОДИТЕЛЬНОСТЬЮ ПРОГРАММЫ, ЛЕЖИТ НА ВАС. ЕСЛИ БУДЕТ ДОКАЗАНО, ЧТО В ПРОГРАММЕ ЕСТЬ ДЕФЕКТЫ, ВЫ ПРИМЕТЕ НА СЕБЯ РАСХОДЫ ПО ВСЕМУ НЕОБХОДИМОМУ ОБСЛУЖИВАНИЮ, РЕМОНТУ ИЛИ ИСПРАВЛЕНИЮ.

 НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ, КРОМЕ ТРЕБУЕМЫХ ПО СООТВЕТСВУЮЩЕМУ ЗАКОНУ ИЛИ ОГОВОРЕННЫХ В ПИСЬМЕННОЙ ФОРМЕ, НИ ОДИН ИЗ ОБЛАДАТЕЛЕЙ АВТОРСКИХ ПРАВ И НИ ОДНА ДРУГАЯ СТОРОНА, ИМЕЮЩАЯ ПРАВО ИЗМЕНЯТЬ И/ИЛИ РАСПРОСТРАНЯТЬ ПРОГРАММУ, КАК ЭТО РАЗРЕШЕНО ВЫШЕ, НЕ НЕСЕТ ОТВЕТСТВЕННОСТИ ПЕРЕД ВАМИ ЗА УЩЕРБ, ВКЛЮЧАЯ ЛЮБОЙ ОБЩИЙ, СПЕЦИФИЧЕСКИЙ, СЛУЧАЙНЫЙ ИЛИ ЛОГИЧЕСКИ ВЫТЕКАЮЩИЙ УЩЕРБ, ПОНЕСЕННЫЙ В РЕЗУЛЬТАТЕ ИСПОЛЬЗОВАНИЯ ИЛИ НЕВОЗМОЖНОСТИ ИСПОЛЬЗОВАНИЯ ПРОГРАММЫ (ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ТОЛЬКО ИМИ, ПОТЕРЮ ДАННЫХ ИЛИ НЕТОЧНОСТЬ ОБРАБОТКИ ДАННЫХ ИЛИ ПОТЕРИ, ПОНЕСЕННЫЕ ВАМИ ИЛИ ТРЕТЬИМИ ЛИЦАМИ, ИЛИ НЕСПОСОБНОСТЬ ПРОГРАММЫ РАБОТАТЬ С ЛЮБЫМИ ДРУГИМИ ПРОГРАММАМИ), ДАЖЕ ЕСЛИ ЭТОТ ОБЛАДАТЕЛЬ АВТОРСКИХ ПРАВ БЫЛ ИНФОРМИРОВАН О ВОЗМОЖНОСТИ НАНЕСЕНИЯ ТАКОГО УЩЕРБА."""
        self.txt.insert(0.0, t)

    def go_to_the_site(self, event=None):
        webbrowser.open('http://my-selling.ru')

    # self.s=Entry(self.win)
    # self.s.pack()
    # self.s.bind("<Button-3><ButtonRelease-3>", self.show_context_menu)

    def show_context_menu(self, event):
        w = event.widget
        w.select_range(0, END)
        self.menu.entryconfigure("Копировать", command=lambda: w.event_generate("<<Copy>>"))
        self.menu.tk.call("tk_popup", self.menu, event.x_root, event.y_root)
