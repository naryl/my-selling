# coding:utf-8
# выполняется вместе с программой, синхронизируя базу данных в фоне
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
import sqlite3 as sql
import thread
import time
import urllib

from date_time import date_now, time_now, date2int


# import socket


class Plugin:
    def __init__(self, app):
        self.app = app
        self.th()

    def th(self):

        thread.start_new_thread(self.run, ())

    def run(self):

        self.con = sql.connect('app/db/main.db')
        self.con.create_function('myDate', 2, lambda x, y: date2int(x, y))
        self.db = self.con.cursor()

        # если синхронизация не нужна, выходим
        self.db.execute('select value from misc where name="sync_enable"')
        if not self.db.fetchall()[0][0] == '1': return
        # если синхронизация только при выходе из приложения, выходим...
        self.db.execute('select value from misc where name="sync_period"')
        sync_time = int(self.db.fetchall()[0][0])
        if sync_time == 0: return

        self.db.execute('select value from misc where name="sync_point"')
        self.sync_point = self.db.fetchall()[0][0].encode('utf-8')

        self.sync_point = hash(self.sync_point)

        self.db.execute('select value from misc where name="sync_login"')
        self.sync_login = self.db.fetchall()[0][0]

        self.db.execute('select value from misc where name="sync_passw"')
        self.sync_passw = self.db.fetchall()[0][0]

        self.db.execute('select value from misc where name="sync_server"')
        self.sync_server = self.db.fetchall()[0][0]

        while 1:
            time.sleep(sync_time * 60)
            try:
                self.sync()
            except Exception:
                pass

    def sync(self):

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
            return
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
