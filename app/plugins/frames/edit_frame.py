# -*-coding:utf-8-*-
# редактирование продаж
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
import tkMessageBox as box
from Tkinter import *
from ttk import *

from MultiListbox import MultiListbox
from calend import TkCalendar
from date_time import date_now, norm_date
from edit_log import Log
from number_to_string import get_string_by_number
from act_tovar import Act

name = 'Редактировать'
frame = 0


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.log = Log(self.app.app)
        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        x, y = 850, 450
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
        Label(self.content_frame, text='Приход:', font=('normal', 12)).pack(fill=BOTH)
        self.lst = MultiListbox(self.content_frame, (
        ('Время', 8), ('Отдел', 5), ('Товар', 40), ('Сумма', 5), ('Кол.во', 1), ('Итог', 5), ('Продавец', 12)),
                                font=('normal', 10), height=6, command=self.lst1select)
        self.lst.pack(fill=BOTH, expand=1)
        Label(self.content_frame, text='Расход:', font=('normal', 12)).pack(fill=BOTH)
        self.lst2 = MultiListbox(self.content_frame, (('Время', 8), ('Причина', 35), ('Сумма', 5), ('Продавец', 12)),
                                 font=('normal', 10), height=6, command=self.lst2select)
        self.lst2.pack(fill=BOTH, expand=1)

        s = 'За дату: %s' % (norm_date(date_now()))
        self.d_label = Label(self.tool_frame, text=s, font=('bold', 12))
        self.d_label.grid(row=0, columnspan=2, sticky=N + W)

        self.edit_frame_parrent = Labelframe(self.content_frame, text='Редактировать',
                                             width=50, height=100)
        self.edit_frame_parrent.pack(fill=BOTH, expand=1)

        self.delete_frame_parrent = Labelframe(self.content_frame, text='Удалить',
                                               width=50, height=50)
        self.delete_frame_parrent.pack(fill=BOTH, expand=1)

        self.edit_frame = Frame(self.edit_frame_parrent, height=63)
        self.edit_frame.pack()
        self.delete_frame = Frame(self.delete_frame_parrent, height=46)
        self.delete_frame.pack()

        self.update_lists()

    def exit(self, event=None):
        """ при выходе обновляем главное окно """
        self.app.update_list()
        self.app.update_tools()
        self.win.destroy()

    def calend_handler(self, date):
        """ вызывается при щелчке на дату """
        self.c_date = date
        self.edit_frame.destroy()
        self.edit_frame = Frame(self.edit_frame_parrent, height=63)
        self.edit_frame.pack(fill=BOTH, expand=1)
        self.delete_frame.destroy()
        self.delete_frame = Frame(self.delete_frame_parrent, height=46)
        self.delete_frame.pack(fill=BOTH, expand=1)
        self.update_lists()

    def update_lists(self):
        """ наполняем таблицы """
        self.current_income = []
        self.current_outcome = []
        self.lst.delete(0, END)
        self.app.app.db.execute('select time,dep,article,sum,rate,name,art_id,date,edit from income where date=?',
                                (self.c_date,))
        income_all = 0
        for x in self.app.app.db.fetchall():
            out = list(x)

            if out[8] <> 0:
                out[1] = str(out[1]) + ' (≈)'
            if out[6] <> -1:
                out[1] = str(out[1]) + ' →'
            out.insert(5, round(x[3] * x[4], 2))
            income_all += x[3] * x[4]
            self.lst.insert(END, out)
            self.current_income.append(x)
        self.lst.see(END)
        outcome_all = 0
        self.lst2.delete(0, END)
        self.app.app.db.execute('select time,article,sum,name,art_id,date,edit from outcome where date=?',
                                (self.c_date,))
        for x in self.app.app.db.fetchall():
            out = list(x)
            if out[6] <> 0:
                out[1] = u'(≈) ' + out[1]
            self.lst2.insert(END, out)
            self.current_outcome.append(x)
            outcome_all += out[2]
        self.lst2.see(END)

        s = 'За дату: %s' % (norm_date(self.c_date))
        self.d_label['text'] = s

    def lst1select(self):
        """ при  щелчке на продаже """
        if self.lst2.curselection():
            self.lst2.selection_clear(self.lst2.curselection())
        self.edit_frame.destroy()
        self.edit_frame = Frame(self.edit_frame_parrent, height=63)
        self.edit_frame.pack(fill=BOTH, expand=1)
        self.delete_frame.destroy()
        self.delete_frame = Frame(self.delete_frame_parrent, height=46)
        self.delete_frame.pack(fill=BOTH, expand=1)
        Label(self.delete_frame, text='Причина удаления').grid(row=0, column=0, padx=10, pady=5)
        self.delete_entry = Entry(self.delete_frame, width=35, cursor='xterm', font=('normal', 12))
        self.delete_entry.grid(row=0, column=1, pady=10)
        self.delete_button = Button(self.delete_frame, text='Удалить', image=self.app.app.img['delete'],
                                    compound='left', command=self.delete_income)
        self.delete_button.grid(row=0, column=2, padx=5)

        Label(self.edit_frame, text='Отдел').grid(row=0, column=0, padx=2, pady=2)
        self.otd_ent = Entry(self.edit_frame, width=3, cursor='xterm', font=('normal', 12))
        self.otd_ent.grid(row=0, column=1, padx=2, pady=2)
        Label(self.edit_frame, text='Товар').grid(row=0, column=2, padx=2, pady=2)
        self.tov_ent = Entry(self.edit_frame, width=30, cursor='xterm', font=('normal', 12))
        self.tov_ent.grid(row=0, column=3, padx=2, pady=2)
        Label(self.edit_frame, text='Кол-во').grid(row=0, column=4, padx=2, pady=2)
        self.kvo_ent = Entry(self.edit_frame, width=4, cursor='xterm', font=('normal', 12))
        self.kvo_ent.grid(row=0, column=5, padx=2, pady=2)
        Label(self.edit_frame, text='Сумма').grid(row=0, column=6, padx=2, pady=2)
        self.sum_ent = Entry(self.edit_frame, width=7, cursor='xterm', font=('normal', 12))
        self.sum_ent.grid(row=0, column=7, padx=2, pady=2)

        self.act_tovar_f = Frame(self.edit_frame)
        self.act_tovar_f.grid(row=1, column=3)

        act_but_text_var = str(getattr(self.app.app.sets, 'act_but_text', 'Act').encode('utf-8'))
        tovar_but_text_var = str(getattr(self.app.app.sets, 'tovar_but_text', 'Check').encode('utf-8'))

        self.save_but = Button(self.act_tovar_f, text=act_but_text_var, image=self.app.app.img['csv'], compound='left',
                               command=self.print_act)
        self.save_but.grid(row=0, column=0, padx=2, pady=2)

        self.save_but = Button(self.act_tovar_f, text=tovar_but_text_var, image=self.app.app.img['csv'], compound='left',
                               command=self.print_tovar)
        self.save_but.grid(row=0, column=1, padx=2, pady=2)

        self.save_but = Button(self.edit_frame, text='Сохранить', image=self.app.app.img['save'], compound='left',
                               command=self.save_income)
        self.save_but.grid(row=1, column=6, columnspan=2, pady=2)

        if not self.lst.curselection(): return
        c = self.current_income[int(self.lst.curselection()[0])]
        self.otd_ent.delete(0, END)
        self.otd_ent.insert(0, c[1])
        self.tov_ent.delete(0, END)
        self.tov_ent.insert(0, c[2])
        self.kvo_ent.delete(0, END)
        self.kvo_ent.insert(0, c[4])
        self.sum_ent.delete(0, END)
        self.sum_ent.insert(0, c[3])

    def lst2select(self):
        """ при  щелчке на расходе """
        if self.lst.curselection():
            self.lst.selection_clear(self.lst.curselection())
        self.edit_frame.destroy()
        self.edit_frame = Frame(self.edit_frame_parrent, height=63)
        self.edit_frame.pack(fill=BOTH, expand=1)
        self.delete_frame.destroy()
        self.delete_frame = Frame(self.delete_frame_parrent, height=46)
        self.delete_frame.pack(fill=BOTH, expand=1)
        Label(self.delete_frame, text='Причина удаления').grid(row=0, column=0, padx=10, pady=5)
        self.delete_entry = Entry(self.delete_frame, width=35, cursor='xterm', font=('normal', 12))
        self.delete_entry.grid(row=0, column=1, pady=10)
        self.delete_button = Button(self.delete_frame, text='Удалить', image=self.app.app.img['delete'],
                                    compound='left', command=self.delete_outcome)
        self.delete_button.grid(row=0, column=2, padx=5)

        Label(self.edit_frame, text='Причина').grid(row=0, column=0, padx=2, pady=2)
        self.pr_ent = Entry(self.edit_frame, width=48, cursor='xterm', font=('normal', 12))
        self.pr_ent.grid(row=0, column=1, padx=2, pady=2)
        Label(self.edit_frame, text='Сумма').grid(row=0, column=2, padx=2, pady=2)
        self.sum_ent = Entry(self.edit_frame, width=7, cursor='xterm', font=('normal', 12))
        self.sum_ent.grid(row=0, column=3, padx=2, pady=2)

        self.save_but = Button(self.edit_frame, text='Сохранить', image=self.app.app.img['save'], compound='left',
                               command=self.save_outcome)
        self.save_but.grid(row=1, column=2, columnspan=2, pady=2, sticky=E)
        if not self.lst2.curselection(): return
        c = self.current_outcome[int(self.lst2.curselection()[0])]
        self.pr_ent.delete(0, END)
        self.pr_ent.insert(0, c[1])
        self.sum_ent.delete(0, END)
        self.sum_ent.insert(0, c[2])

    def delete_income(self):
        """ удаление продажи """
        if not self.lst.curselection(): return
        text = self.delete_entry.get()
        if len(text) < 3:
            box.showerror(title='Ошибка', message='Вы должны ввести причину удаления!')
            self.win.deiconify()
            return
        c = self.current_income[int(self.lst.curselection()[0])]
        self.app.app.db.execute('delete from income where time=? and date=?', (c[0], c[7]))
        self.app.app.con.commit()
        self.delete_entry.delete(0, END)

        cashbox_value = float(self.app.app.sets.cashbox)
        cashbox_value -= c[3]
        self.app.app.sets.cashbox = cashbox_value

        self.update_lists()
        self.log.del_income(c[7], c[0], c[1], c[2], text, c[3], c[4], self.app.app.user.decode('utf-8'))

    def delete_outcome(self):
        """ Удаление расхода """
        if not self.lst2.curselection(): return
        text = self.delete_entry.get()
        if len(text) < 3:
            box.showerror(title='Ошибка', message='Вы должны ввести причину удаления!')
            self.win.deiconify()
            return
        c = self.current_outcome[int(self.lst2.curselection()[0])]
        self.app.app.db.execute('delete from outcome where time=? and date=?', (c[0], c[5]))
        self.app.app.con.commit()
        self.delete_entry.delete(0, END)

        cashbox_value = float(self.app.app.sets.cashbox)
        cashbox_value += c[2]
        self.app.app.sets.cashbox = cashbox_value

        self.update_lists()
        self.log.del_outcome(c[5], c[0], c[1], c[2], c[3], self.app.app.user.decode('utf-8'), text)

    def save_income(self, act_print=0, tovar_print=0):
        """ сохранение отредактированной продажи """
        if not self.lst.curselection(): return
        dep = self.otd_ent.get()
        art = self.tov_ent.get()
        self.app.app.db.execute('select * from dep where id=?', (dep,))
        if not self.app.app.db.fetchall():
            box.showerror(title='Ошибка', message='Не верный отдел!')
            self.win.deiconify()
            return
        dep = int(dep)
        try:
            kvo = int(self.kvo_ent.get())
        except:
            box.showerror(title='Ошибка', message='Не верное количество!')
            self.win.deiconify()
            return
        try:
            summa = float(self.sum_ent.get().replace(',', '.'))
            if summa <= 0: s = 1 / 0
        except:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            self.win.deiconify()
            return
        c = self.current_income[int(self.lst.curselection()[0])]
        i = int(self.lst.curselection()[0])
        self.app.app.db.execute('update income set dep=?,article=?,rate=?,sum=?,edit=1 where date=? and time=?',
                                (dep, art, kvo, summa, c[7], c[0]))
        self.app.app.con.commit()

        cashbox_value = float(self.app.app.sets.cashbox)
        cashbox_value += summa - c[3]
        self.app.app.sets.cashbox = cashbox_value

        self.update_lists()
        self.lst.selection_set(i)
        self.log.edit_income(c[7], c[0], [c[1], c[2], c[4], c[3]], [dep, art, kvo, summa],
                             self.app.app.user.decode('utf-8'), c[5])

        # forming payload for act print
        total = round(float(kvo) * float(summa), 2)
        if act_print == 1 or tovar_print == 1:
            act_info = {
                    'act_number': 0,
                    'act_date': c[7],
                    'p_num': 1,
                    'service_name': art,
                    'garanty': u'3 года',
                    'q': kvo,
                    'price': summa,
                    'amount': total,
                    'total': total,
                    'total_as_text': get_string_by_number(total),
                    }

            act_payloads = [act_info]

            art_id = -1
            self.app.app.db.execute('select id from article where name=?', (art,))
            if len(self.app.app.db.fetchall()) > 0:
                art_id = self.app.app.db.fetchall()[0][0]
            self.act = Act(self.app.app)

        if act_print == 1:
            self.act.generate_act(act_payloads, 'app/templates/act_tpl.xlsx', c[7], c[0], art_id, 'act', self.edit_frame)

        if tovar_print == 1:
            self.act.generate_act(act_payloads, 'app/templates/tovar_tpl.xlsx', c[7], c[0], art_id, 'tovar', self.edit_frame)

    def print_act(self):
        payloads = self.save_income(1,0)

    def print_tovar(self):
        payloads = self.save_income(0,1)

    def save_outcome(self):
        """ сохранение отредактированного расхода """
        if not self.lst2.curselection(): return
        text = self.pr_ent.get()
        if len(text) < 3:
            box.showerror(title='Ошибка', message='Причина удаления не может быть удалена! (как то так)')
            self.win.deiconify()
            return
        c = self.current_outcome[int(self.lst2.curselection()[0])]
        try:
            summa = float(self.sum_ent.get().replace(',', '.'))
            if summa <= 0: s = 1 / 0
        except:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            self.win.deiconify()
            return
        i = int(self.lst2.curselection()[0])

        self.app.app.db.execute('update outcome set article=?,sum=?,edit=1 where date=? and time=?',
                                (text, summa, c[5], c[0]))
        self.app.app.con.commit()

        cashbox_value = float(self.app.app.sets.cashbox)
        cashbox_value -= summa - c[2]
        self.app.app.sets.cashbox = cashbox_value

        self.update_lists()
        self.lst2.selection_set(i)
        self.log.edit_outcome(c[5], c[0], [c[1], c[2]], [text, summa], self.app.app.user.decode('utf-8'), c[3])
