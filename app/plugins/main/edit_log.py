# coding:utf-8
# вспомогательный класс для записи записи в лог правок
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

from date_time import date_now, time_now, norm_date


class Log:
    def __init__(self, app):
        self.db = app.db
        self.con = app.con

    def del_income(self, date, tm, dep, art, pr, summa, rate, user):
        """Запись об уделании продажи """
        mess = u'Пользователь %s удалил продажу от %s %s\nОтдела #%s\nТовар: %s\nСумма: %s, количество: %s\nПо причине: %s' % (
        user, norm_date(date).decode('utf-8'), tm, dep, art, summa, rate, pr)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Удалена продажа', mess, date, tm))
        self.con.commit()

    def del_outcome(self, date, tm, art, sum, c_user, user, pr):
        """Запись об уделании расхода """
        mess = u'Пользователь %s удалил расход от %s %s\nРасход: %s\nНа сумму: %s\nБыл сделан пользователем %s\nПричина: %s' % (
        user, norm_date(date).decode('utf-8'), tm, art, sum, c_user, pr)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Удален расход', mess, date, tm))
        self.con.commit()

    def edit_income(self, date, tm, old, new, user, c_user):
        """Запись о редактировании продажи """
        ms = []
        if old[0] <> new[0]:
            ms.append(u'Отдел с %s на %s' % (old[0], new[0]))
        if old[1] <> new[1]:
            ms.append(u'Товар с %s на %s' % (old[1], new[1]))
        if old[2] <> new[2]:
            ms.append(u'Количество с %s на %s' % (old[2], new[2]))
        if old[3] <> new[3]:
            ms.append(u'Сумма с %s на %s' % (old[3], new[3]))
        if not ms: return
        mess = u'Пользователь %s изменил продажу от %s %s\nИзменения:\n%s\nБыла сделана пользователем %s' % (
        user, norm_date(date).decode('utf-8'), tm, '\n'.join(ms), c_user)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Отредактирована продажа', mess, date, tm))
        self.con.commit()

    def edit_outcome(self, date, tm, old, new, user, c_user):
        """Запись о редактировании расхода """
        ms = []
        if old[0] <> new[0]:
            ms.append(u'Причина с %s на %s' % (old[0], new[0]))
        if old[1] <> new[1]:
            ms.append(u'Сумма с %s на %s' % (old[1], new[1]))

        if not ms: return
        mess = u'Пользователь %s изменил расход от %s %s\nИзменения:\n%s\nБыл сделан пользователем %s' % (
        user, norm_date(date).decode('utf-8'), tm, '\n'.join(ms), c_user)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Отредактирован расход', mess, date, tm))
        self.con.commit()

    def del_phone(self, date, tm, phone, name, user, pr):
        """Запись об уделании телефона """
        mess = u'Пользователь %s удалил запись о клиенте от %s %s\Телефон: %s\nИмя: %s\nПричина: %s' % (
            user, norm_date(date).decode('utf-8'), tm, phone, name, pr)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Удалена запись', mess, date, tm))
        self.con.commit()

    def edit_phone(self, date, tm, old, new, user):
        """Запись о редактировании телефона """
        ms = []
        if old[0] != new[0]:
            ms.append(u'Телефон с %s на %s' % (old[0], new[0]))
        if old[1] != new[1]:
            ms.append(u'Имя с %s на %s' % (old[1], new[1]))
        if old[2] != new[2]:
            ms.append(u'Детали с %s на %s' % (old[2], new[2]))

        if not ms: return
        mess = u'Пользователь %s изменил запись о клиенте от %s %s\nИзменения:\n%s' % (
            user, norm_date(date).decode('utf-8'), tm, '\n'.join(ms))
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Отредактирована запись', mess, date, tm))
        self.con.commit()

    def del_receipt(self, date, tm, phone, name, user, pr):
        """Запись об уделании расписки """
        mess = u'Пользователь %s удалил запись о расписке от %s %s\Телефон: %s\nИмя: %s\nПричина: %s' % (
            user, norm_date(date).decode('utf-8'), tm, phone, name, pr)
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Удалена запись', mess, date, tm))
        self.con.commit()

    def edit_receipt(self, date, tm, old, new, user):
        """Запись о редактировании расписки """
        ms = []
        if old[0] != new[0]:
            ms.append(u'Телефон с %s на %s' % (old[0], new[0]))
        if old[1] != new[1]:
            ms.append(u'Имя с %s на %s' % (old[1], new[1]))
        if old[2] != new[2]:
            ms.append(u'Детали с %s на %s' % (old[2], new[2]))

        if not ms:
            return
        mess = u'Пользователь %s изменил запись о расписке от %s %s\nИзменения:\n%s' % (
            user, norm_date(date).decode('utf-8'), tm, '\n'.join(ms))
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Отредактирована запись', mess, date, tm))
        self.con.commit()

    def at_work(self, date, tm, user):
        """Запись о нажатии кнопки На месте """
        mess = user
        self.db.execute('insert into edit_log values (?,?,?,?,?,?)',
                        (date_now(), time_now(), u'Пользователь на месте', mess, date, tm))
        self.con.commit()
