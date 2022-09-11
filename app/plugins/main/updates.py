# coding:utf-8
# экран с обновлением программы
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
import subprocess
import sys
import time
import tkMessageBox as box
import zipfile
from Tkinter import *
from ttk import *


class Main:
    def __init__(self, app):
        self.app = app

        self.win = Frame(self.app.win)
        self.win.place(relx=0.5, rely=0.5, anchor=CENTER)

        Label(self.win, text='Выполняется установка обновлений...', font=('bold', 16)).pack()

        self.progress = Progressbar(self.win, length=300, value=0)
        self.progress.pack()
        self.lab_var = StringVar()
        Label(self.win, textvariable=self.lab_var, font=('bold', 16)).pack()

        s = os.listdir('app/updates')
        s.sort()
        it = 1
        k = 100.0 / float(len(s)) - 1
        self.lab_var.set('%s из %s' % (it, len(s)))
        self.win.update()
        # проходимся по файлам
        for x in s:
            self.progress.step(k)
            self.lab_var.set('%s из %s' % (it, len(s)))
            it += 1
            self.update(x)
            time.sleep(1)
            self.win.update()

        self.win.update()
        s = box.askokcancel(title='Обновления завершены',
                            message='После применения обновления\nнеобходимо перезапустить программу\nПерезапустить?')
        if s:
            self.app.root.destroy()
            try:
                subprocess.Popen(sys.argv[0])
            except WindowsError, x:
                subprocess.Popen('pythonw ' + sys.argv[0])
            sys.exit(0)

        self.app.change_user()

    def update(self, name):
        """ тупо распаковываем  """
        z = zipfile.ZipFile('app/updates/' + name)
        l = z.filelist
        for x in l:
            fname = x.filename
            z.extract(fname, '')
        z.close()
        os.remove('app/updates/' + name)
