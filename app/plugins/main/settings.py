# coding:utf-8
# класс, реализующий настройки программы из базы данных
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


class Settings():

    def __init__(self, app):
        self.__dict__['app'] = app
        app.db.execute('select * from misc')
        self.__dict__.update(dict(app.db.fetchall()))

    def __getattr(self, a):
        if a not in self.__dict__:
            return None
        else:
            return self.__dict__[a]

    def __setattr__(self, atr, v):
        self.__dict__[atr] = v
        self.app.db.execute('select * from misc where name=?', (atr,))
        if self.app.db.fetchall():
            self.app.db.execute('update misc set value=? where name=?', (v, atr))
        else:
            self.app.db.execute('insert into misc values (?,?)', (atr, v))
        self.app.con.commit()
