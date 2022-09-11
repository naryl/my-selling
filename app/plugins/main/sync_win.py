# coding:utf-8
# экран синхронизации при выходе
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
import json
import urllib
from Tkinter import *
from ttk import *

from date_time import date_now, time_now, date2int


class Main:
    def __init__(self, app):
        self.app = app

        self.win = Frame(self.app.win)
        self.win.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.lab = Label(self.win, text='', font=('bold', 12))
        self.lab.pack()

        self.work()

    def work(self):
        try:
            self.sync()
        except Exception, x:
            self.lab['text'] = 'Не удалось отправить данных на сервер!'
            self.lab['background'] = 'red'
            self.lab['foreground'] = 'white'
            self.fr = Frame(self.win)
            self.fr.pack()
            self.re_sync = Button(self.fr, text='Повторить', image=self.app.img['repeat'], compound='left',
                                  command=self.repeat)
            self.re_sync.grid(row=0, column=0, padx=5, pady=5)
            self.exit_sync = Button(self.fr, text='Выйти', image=self.app.img['exit'], compound='left',
                                    command=lambda: sys.exit(0))
            self.exit_sync.grid(row=0, column=1, padx=5, pady=5)

    def sync(self):

        self.con = self.app.con
        self.db = self.con.cursor()
        # если не нужно, то выходим
        self.db.execute('select value from misc where name="sync_enable"')
        if self.db.fetchall()[0][0] == '0':
            sys.exit(0)

        self.db.execute('select value from misc where name="sync_period"')
        sync_time = int(self.db.fetchall()[0][0])

        self.db.execute('select value from misc where name="sync_point"')
        self.sync_point = self.db.fetchall()[0][0].encode('utf-8')

        self.sync_point = hash(self.sync_point)

        self.db.execute('select value from misc where name="sync_login"')
        self.sync_login = self.db.fetchall()[0][0]

        self.db.execute('select value from misc where name="sync_passw"')
        self.sync_passw = self.db.fetchall()[0][0]

        self.db.execute('select value from misc where name="sync_server"')
        self.sync_server = self.db.fetchall()[0][0]

        self.db.execute('select value from misc where name="update_date"')
        update_date = self.db.fetchall()[0][0]
        self.db.execute('select value from misc where name="update_time"')
        update_time = self.db.fetchall()[0][0]

        r = {}

        r['auth'] = {'login': self.sync_login, 'passw': self.sync_passw}
        r['db'] = self.sync_point
        out = []
        n_dt = date2int(update_date, update_time)
        self.db.execute('select date,time,dep,article,sum,rate,name from income where myDate(date,time)>=?', (n_dt,))
        for x in self.db.fetchall():
            out.append(['income'] + list(x))

        self.db.execute('select date,time,article,sum,name from outcome where myDate(date,time)>=?', (n_dt,))
        for x in self.db.fetchall():
            out.append(['outcome'] + list(x))

        self.db.execute('select original_date,original_time,title from edit_log where myDate(date,time)>=?', (n_dt,))
        for x in self.db.fetchall():
            if x[2] == u'Отредактирована продажа':
                self.db.execute('select date,time,dep,article,sum,rate,name from income where date=? and time=?',
                                (x[0], x[1]))
                try:
                    out.append(['income'] + list(self.db.fetchall()[0]))
                except IndexError:
                    pass
            elif x[2] == u'Отредактирован расход':
                self.db.execute('select date,time,article,sum,name from outcome where date=? and time=?', (x[0], x[1]))
                try:
                    out.append(['outcome'] + list(self.db.fetchall()[0]))
                except IndexError:
                    pass
            if x[2] == u'Удалена продажа':
                out.append(['del_income', x[0], x[1]])
            if x[2] == u'Удален расход':
                out.append(['del_outcome', x[0], x[1]])
        if len(out) == 0:
            sys.exit(0)
        self.lab['text'] = 'Выполняется отправка данных на сервер...'
        self.lab['background'] = 'green'
        self.lab['foreground'] = 'black'
        self.win.update()

        r['data'] = out
        d = {}
        d['data'] = json.dumps(r)
        self.db.execute('select value from misc where name="sync_server"')
        sync_server = self.db.fetchall()[0][0]
        response = urllib.urlopen(sync_server + '/sync', urllib.urlencode(d)).read()
        if response == '1':
            self.db.execute('update misc set value=? where name="update_date"', (date_now(),))
            self.db.execute('update misc set value=? where name="update_time"', (time_now(),))
            self.con.commit()
            sys.exit(0)
        else:
            raise

    def repeat(self):
        self.fr.destroy()

        self.lab['background'] = 'green'
        self.lab['foreground'] = 'black'
        self.work()
