# -*-coding:utf-8-*-
# экран телефонов и заказов
"""
    Copyright (C) 2020 Sergey Fedorov <shade30@gmail.com>

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
import datetime
import time
import tkFileDialog
import tkMessageBox
from Tkinter import *

import csv
import receipts_frame
from MultiListbox import MultiListbox
from calend import TkCalendar
from date_time import date_now, date_get, time_now, norm_date
from edit_log import Log
from ttk import *

# noinspection PyByteLiteral
name = 'Телефоны и Заказы'
frame = 0
icon = 'phone'


# icon='clear'

# noinspection DuplicatedCode,PyAttributeOutsideInit,PyByteLiteral
class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        self.log = Log(self.app.app)

        if hasattr(self.app, "phones_frame") \
                and self.app.phones_frame.winfo_exists():
            self.app.phones_frame.deiconify()
            self.app.phones_frame.focus()
            self.app.phones_frame.state()
            return 'break'

        self.win = Toplevel(self.app.app.win)
        self.app.phones_frame = self.win
        self.win.title(name)
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        x, y = 1200, 800
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32':
            self.win.iconbitmap('app/images/icon.ico')

        self.content_frame = Frame(self.win)
        self.content_frame.pack(fill=BOTH, expand=1)

        self.init_ui()

        self.update_lists()
        self.list_select()

    def init_ui(self):
        self.filter_frame = Labelframe(self.content_frame, text='Фильтр (Имя/Телефон/Детали; Диапазон Дат)',
                                       width=50, height=100)
        self.filter_frame.pack(fill=X)
        self.filter_entry = Entry(self.filter_frame, width=20, cursor='xterm', font=('normal', 14))
        self.filter_entry.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        self.filter_entry.bind('<Return>', lambda _: self.update_lists())
        self.lst_frame = Frame(self.content_frame)
        self.lst_frame.pack(fill=BOTH, expand=1)
        self.init_common_query_data()
        self.lst = MultiListbox(self.lst_frame, self.columns,
                                font=('bold', 14), height=15, command=self.list_select)
        self.lst.pack(fill=BOTH, expand=1)

        self.init_date_filter_ui()

        self.search_res_lst = MultiListbox(self.lst_frame, self.columns,
                                           font=('bold', 12), height=1, command=self.handle_search_res_click)
        # Результаты поиска по телефону по умолчанию не отображаются
        self.edit_frame_parent = Labelframe(self.content_frame, text='Редактировать',
                                            width=50, height=100)
        self.edit_frame_parent.pack(fill=X)
        self.delete_frame_parent = Labelframe(self.content_frame, text='Удалить',
                                              width=50, height=50)
        self.delete_frame_parent.pack(fill=X)
        self.edit_frame = Frame(self.edit_frame_parent)
        self.edit_frame.pack()
        self.delete_frame = Frame(self.delete_frame_parent)
        self.delete_frame.pack()
        # Цвета для подсветки записей
        self.done_color = '#CFCFC4'
        self.today_color = '#79B47C'
        self.outdated_color = '#FF6961'

    def init_date_filter_ui(self):
        days_delta = -30
        date_start = datetime.datetime.now() + datetime.timedelta(days_delta)
        year, month = (date_start.year, date_start.month)

        self.date_t = StringVar()
        self.date_t.set(date_get(days_delta))
        self.c_date = date_get(days_delta)

        Label(self.filter_frame, text='Начиная с..').grid(row=0, column=1, padx=5, pady=2, sticky=NW)
        self.cal = TkCalendar(self.filter_frame, year, month, self.date_t, command=self.calend_handler)
        self.cal.grid(row=0, column=2, padx=5, sticky=N)

        self.calend_info_frame = Labelframe(self.filter_frame, text='Показывать', width=275, height=200)
        self.calend_info_frame.grid(row=0, column=3, rowspan=2)
        self.filter_frame.columnconfigure(3, minsize=275)

        Label(self.calend_info_frame, text='Показать все').grid(row=1, column=0, padx=2, pady=2)
        self.calend_show_all_var = IntVar()
        self.calend_show_all_chk = Checkbutton(self.calend_info_frame, variable=self.calend_show_all_var,
                                               onvalue=1, offvalue=0)
        self.calend_show_all_chk.grid(row=1, column=1, padx=2, pady=2)

        self.show_but = Button(self.calend_info_frame, text='Показать', image=self.app.app.img['check'],
                               compound='left', command=self.update_lists)
        self.show_but.grid(row=3, column=0, columnspan=2, pady=27)

        year2, month2 = time.localtime()[0:2]

        self.date2_t = StringVar()
        self.date2_t.set(date_now())
        self.c_date2 = date_now()

        Label(self.filter_frame, text='Заканчивая..').grid(row=0, column=4, padx=5, pady=2, sticky=NW)
        self.cal2 = TkCalendar(self.filter_frame, year2, month2, self.date_t, command=self.calend_handler2)
        self.cal2.grid(row=0, column=5, padx=5, sticky=NE)

        self.lab_var = StringVar()
        Label(self.calend_info_frame, textvariable=self.lab_var, font=('bold', 10)).grid(row=0, column=0, columnspan=2,
                                                                                         padx=10, pady=5)

        self.calend_update_label()

    def calend_handler(self, date):
        """выбор начальной даты """
        self.c_date = date
        self.calend_update_label()

    def calend_handler2(self, date):
        """ выбор конечной даты """
        self.c_date2 = date
        self.calend_update_label()

    def calend_update_label(self):
        self.lab_var.set('Показать с  %s  по %s' % (norm_date(self.c_date), norm_date(self.c_date2)))

    def exit(self, _=None):
        """ при выходе обновляем главное окно """
        self.app.update_list()
        self.app.update_tools()
        delattr(self.app, "phones_frame")
        self.win.destroy()

    def init_common_query_data(self):
        # Колонки в таблице
        self.columns = (
            ('Телефон', int(self.app.app.sets.col_width_phone)),
            ('Имя', int(self.app.app.sets.col_width_name)),
            ('Детали', int(self.app.app.sets.col_width_details)),
            ('Дата', int(self.app.app.sets.col_width_date)),
            ('Время', int(self.app.app.sets.col_width_time)),
            ('Дата исп.', int(self.app.app.sets.col_width_done_date)),
            ('Время исп.', int(self.app.app.sets.col_width_done_time)))

        # Запрос к БД со всеми колонками
        self.column_names = 'phone,name,details,date,time,done,done_date,done_time,done_details'
        self.columns_query = 'select ' + self.column_names + ' from phone '

        # Номера колонок
        self.idx_phone = 0
        self.idx_name = 1
        self.idx_details = 2
        self.idx_date = 3
        self.idx_time = 4
        self.idx_done = 5
        self.idx_done_date = 6
        self.idx_done_time = 7
        self.idx_done_details = 8

        # Скрытые колонки
        self.hidden_idxs = [self.idx_done,
                            self.idx_done_details]

    def update_lists(self):
        """ наполняем таблицы """
        self.current_records = []
        self.lst.delete(0, END)
        filter_value = self.filter_entry.get().lower()
        if len(filter_value) > 0:
            self.calend_show_all_var.set(1)
            self.app.app.db.execute(self.columns_query +
                                    'where instr(myLower(phone), ?) > 0 '
                                    'or instr(myLower(name), ?) > 0 '
                                    'or instr(myLower(details), ?) > 0 '
                                    'collate nocase', (filter_value, filter_value, filter_value))
        elif not self.calend_show_all_var.get():
            self.app.app.db.execute(self.columns_query +
                                    'where date between ? and ?', (self.c_date, self.c_date2))
        else:
            self.app.app.db.execute(self.columns_query)

        today = date_now()
        n_days_ago = date_get(-3)
        for x in self.app.app.db.fetchall():
            out = list(x)

            # Скрытие колонок
            out_lst = [value if value is not None else ''
                       for i, value in enumerate(out)
                       if i not in self.hidden_idxs]

            self.lst.insert(END, out_lst)

            # Подсветка записей
            if x[self.idx_date] == today:
                self.lst.itemconfig(END, bg=self.today_color)
            if x[self.idx_date] < n_days_ago:
                self.lst.itemconfig(END, bg=self.outdated_color)
            if x[self.idx_done]:
                self.lst.itemconfig(END, bg=self.done_color)

            self.current_records.append(x)
        self.lst.see(END)

    def list_select(self):
        """ при щелчке на записи """
        self.search_res_lst.pack_forget()
        self.edit_frame.destroy()
        self.edit_frame = Frame(self.edit_frame_parent, height=100)
        self.edit_frame.pack(fill=BOTH)
        if self.delete_frame:
            self.delete_frame.destroy()

        if int(self.app.app.sets.allow_del_phone) == 1:
            self.delete_frame = Frame(self.delete_frame_parent, height=50)
            self.delete_frame.pack(fill=BOTH)
            Label(self.delete_frame, text='Причина удаления').grid(row=0, column=0, padx=10, pady=5)
            self.delete_entry = Entry(self.delete_frame, width=35, cursor='xterm', font=('normal', 12))
            self.delete_entry.grid(row=0, column=1, pady=10)
            self.delete_button = Button(self.delete_frame, text='Удалить', image=self.app.app.img['delete'],
                                        compound='left', command=self.delete_record)
            self.delete_button.grid(row=0, column=2, padx=5)

        # экспорт
        self.csv_button = Button(self.edit_frame, text='В csv', image=self.app.app.img['csv'], compound='left',
                                 command=self.generate_csv)
        self.csv_button.grid(row=3, column=0, columnspan=2, padx=5, sticky=W)

        # валидация телефона
        def isdigit(p):
            if isinstance(p, unicode):
                return unicode.isdigit(p)
            else:
                return str.isdigit(p)

        v_phone_cmd = (self.win.register(lambda p: isdigit(p) or p == ""))

        # ограничение длины текста
        def character_limit(entry_text, limit):
            if len(entry_text.get()) > limit:
                entry_text.set(entry_text.get()[0:limit])
            if len(entry_text.get()) == limit:
                self.name_ent.focus()

        Label(self.edit_frame, text='Телефон').grid(row=0, column=0, padx=2, pady=2)
        self.phone_text = StringVar()
        self.phone_ent = Entry(self.edit_frame, width=13, cursor='xterm', font=('normal', 14),
                               textvariable=self.phone_text,
                               validate='all', validatecommand=(v_phone_cmd, '%P'))
        self.phone_text.trace("w", lambda *args: character_limit(self.phone_text, 11))
        self.phone_ent.grid(row=0, column=1, padx=2, pady=2)

        Label(self.edit_frame, text='Имя').grid(row=0, column=2, padx=2, pady=2)
        self.name_text = StringVar()
        self.name_ent = Entry(self.edit_frame, width=16, cursor='xterm', font=('normal', 14),
                              textvariable=self.name_text)
        self.name_ent.grid(row=0, column=3, padx=2, pady=2)

        Label(self.edit_frame, text='Детали').grid(row=1, column=0, padx=2, pady=2)
        self.details_text = StringVar()
        self.details_ent = Entry(self.edit_frame, width=80, cursor='xterm', font=('normal', 14),
                                 textvariable=self.details_text)
        self.details_ent.grid(row=1, column=1, columnspan=7, padx=2, pady=2)

        Label(self.edit_frame, text='Сделано').grid(row=0, column=4, padx=2, pady=2)
        self.done_var = IntVar()
        self.done_chk = Checkbutton(self.edit_frame, variable=self.done_var, onvalue=1, offvalue=0)
        self.done_chk.grid(row=0, column=5, padx=2, pady=2)

        Label(self.edit_frame, text='Что сделано').grid(row=2, column=0, padx=2, pady=2)
        self.done_details_text = StringVar()
        self.done_details_ent = Entry(self.edit_frame, width=80, cursor='xterm', font=('normal', 14),
                                      textvariable=self.done_details_text)
        self.done_details_ent.grid(row=2, column=1, columnspan=7, padx=2, pady=2)

        if not self.lst.curselection():
            self.create_mode()
        else:
            self.edit_mode()

    def edit_mode(self):
        """ режим редактирования записи """
        self.save_but = Button(self.edit_frame, text='Сохранить', image=self.app.app.img['save'], compound='left',
                               command=self.save_record)
        self.save_but.grid(row=3, column=6, padx=2, pady=2, sticky=E)
        self.cancel_but = Button(self.edit_frame, text='Отмена', image=self.app.app.img['cancel'], compound='left',
                                 command=self.deselect)
        self.cancel_but.grid(row=3, column=7, pady=2)
        self.receipt_but = Button(self.edit_frame, text='Расписка', image=self.app.app.img['sale'], compound='left',
                                  command=self.create_receipt)
        self.receipt_but.grid(row=0, column=7, padx=2, pady=2, sticky=E)

        c = self.current_records[int(self.lst.curselection()[0])]
        self.phone_ent.delete(0, END)
        self.phone_ent.insert(0, c[self.idx_phone])
        self.name_ent.delete(0, END)
        self.name_ent.insert(0, c[self.idx_name])
        self.details_ent.delete(0, END)
        self.details_ent.insert(0, c[self.idx_details])
        self.done_var.set(1 if c[self.idx_done] else 0)
        self.done_details_ent.delete(0, END)
        self.done_details_ent.insert(0, c[self.idx_done_details])

        # отмена после 10 секунд бездействия
        self.timeout = 10
        self.last_edit_time = time.time()

        self.progress_bar = Progressbar(self.edit_frame, mode="determinate", value=100)
        self.progress_bar.grid(row=3, column=5, padx=2, pady=2)

        def check_timeout():
            try:
                if not self.lst.curselection():
                    return
                cur_time = time.time()
                delta = cur_time - self.last_edit_time
                self.progress_bar['value'] = 100 - delta * 10
                if delta >= 10:
                    self.deselect()
                else:
                    self.app.app.root.after(1000, check_timeout)
            except TclError:
                pass

        def reset_timeout_handler(_1, _2, _3):
            self.last_edit_time = time.time()

        self.phone_text.trace('w', reset_timeout_handler)
        self.name_text.trace('w', reset_timeout_handler)
        self.details_text.trace('w', reset_timeout_handler)
        self.done_var.trace('w', reset_timeout_handler)
        self.done_details_text.trace('w', reset_timeout_handler)

        self.app.app.root.after(1000, check_timeout)

    def create_mode(self):
        """ режим создания записи """
        self.save_but = Button(self.edit_frame, text='Добавить', image=self.app.app.img['save'], compound='left',
                               command=self.create_record)
        self.save_but.grid(row=3, column=6, pady=2)
        self.receipt_but = Button(self.edit_frame, text='Расписка', image=self.app.app.img['sale'], compound='left',
                                  command=self.create_receipt)
        self.receipt_but.grid(row=3, column=7, padx=2, pady=2, sticky=E)

        self.phone_text.trace("w", lambda *args: self.search())

        def create_if_ready(entry, min_size):
            if len(entry.get()) > min_size:
                self.create_record()

        # сохранять при нажатии Enter в поле деталей
        self.details_ent.bind("<Return>", lambda _: create_if_ready(self.details_ent, 5))
        self.done_details_ent.bind("<Return>", lambda _: create_if_ready(self.done_details_ent, 5))

    def delete_record(self):
        """ удаление записи """
        if not self.lst.curselection():
            return
        text = self.delete_entry.get()
        if len(text) < 3:
            tkMessageBox.showerror(title='Ошибка', message='Вы должны ввести причину удаления!')
            self.win.deiconify()
            return
        c = self.current_records[int(self.lst.curselection()[0])]
        self.app.app.db.execute('delete from phone where time=? and date=?', (c[self.idx_time], c[self.idx_date]))
        self.app.app.con.commit()
        self.delete_entry.delete(0, END)
        self.update_lists()
        self.log.del_phone(c[self.idx_date], c[self.idx_time], c[self.idx_phone], c[self.idx_name],
                           self.app.app.user.decode('utf-8'), text)

    def save_record(self):
        """ сохранение отредактированной записи """
        if not self.lst.curselection():
            return
        phone = self.phone_ent.get()
        name_val = self.name_ent.get()
        details = self.details_ent.get()
        done = self.done_var.get()
        done_details = self.done_details_ent.get()
        done_dt, done_tm = (None, None)

        if not phone and not name_val and not details:
            return
        c = self.current_records[int(self.lst.curselection()[0])]

        if done:
            if c[self.idx_done_date] and c[self.idx_done_time]:
                done_dt, done_tm = c[self.idx_done_date], c[self.idx_done_time]
            else:
                done_dt, done_tm = date_now(), time_now()

        i = int(self.lst.curselection()[0])
        self.app.app.db.execute('update phone set phone=?,name=?,details=?,done=?, '
                                'done_details=?,done_date=?,done_time=? '
                                'where date=? and time=?',
                                (phone, name_val, details, done, done_details, done_dt, done_tm,
                                 c[self.idx_date], c[self.idx_time]))
        self.app.app.con.commit()
        self.update_lists()
        self.lst.selection_set(i)
        self.log.edit_phone(c[self.idx_date], c[self.idx_time],
                            [c[self.idx_phone], c[self.idx_name], c[self.idx_details]],
                            [phone, name_val, details],
                            self.app.app.user.decode('utf-8'))

    def create_receipt(self):
        """ формирование расписки по текущей записи"""
        if hasattr(self.app, "receipts_frame") \
                and self.app.receipts_frame.winfo_exists():
            tkMessageBox.showerror(title='Ошибка', message='Закройте экран расписок')
            return

        values = {
            'phone_main': '%s %s' % (self.phone_text.get(), self.name_text.get()),
            'phone_additional': '',
            'diag_time': '3',
            'item_device': '',
            'item_serial': '',
            'item_declared_defect': self.details_text.get(),
            'item_existing_damage': '',
            'item_alleged_defect': self.done_details_text.get(),
            'item_repair_time': '2-3 дня(ей)'
        }
        receipt_window = receipts_frame.Plugin(self.app)
        receipt_window.set_initial_values(values)
        receipt_window.run()

    def create_record(self):
        """ создание новой записи """
        dt, tm = date_now(), time_now()
        phone = self.phone_ent.get()
        name = self.name_ent.get()
        details = self.details_ent.get()
        done = self.done_var.get()
        done_details = self.done_details_ent.get()
        done_dt, done_tm = (date_now(), time_now()) if done else (None, None)

        if not phone and not name and not details:
            return
        self.app.app.db.execute('select max(id) from phone')
        try:
            entry_id = self.app.app.db.fetchall()[0][0] + 1
        except TypeError:
            entry_id = 1
        # noinspection SqlInsertValues
        self.app.app.db.execute('insert into phone (id, ' + self.column_names +
                                ') '
                                'values (?,?,?,?,?,?,?,?,?,?)',
                                (entry_id, phone, name, details, dt, tm, done, done_dt, done_tm, done_details))
        self.app.app.con.commit()
        self.update_lists()
        self.list_select()

    def deselect(self):
        self.lst.selection_clear(self.lst.curselection())
        self.list_select()

    def generate_csv(self):
        """ генерация csv """
        try:
            path = self.app.app.sets.save_pdf
        except AttributeError:
            path = ''
        filename = 'Клиенты на %s.csv' % (norm_date(date_now()))
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename, master=self.edit_frame)
        if not f:
            return
        f = f.replace('\\', '/')
        self.app.app.sets.save_pdf = '/'.join(f.split('/')[:-1])
        doc = csv.writer(open(f, 'w'), delimiter=';', lineterminator='\n', quoting=csv.QUOTE_ALL)
        doc.writerow([u'Дата'.encode('cp1251'), u'Время'.encode('cp1251'), u'Телефон'.encode('cp1251'),
                      u'Имя'.encode('cp1251'), u'Детали'.encode('cp1251'), u'Сделано'.encode('cp1251'),
                      u'Дата исп.'.encode('cp1251'), u'Время исп'.encode('cp1251'), u'Детали исп.'.encode('cp1251'),
                      u'ID'.encode('cp1251')])

        self.app.app.db.execute('select ' + self.column_names + ',id from phone')
        result = self.app.app.db.fetchall()

        idx_id = self.idx_done + 1
        for rec in result:
            doc.writerow([rec[self.idx_date], rec[self.idx_time], rec[self.idx_phone].encode('cp1251', 'ignore'),
                          rec[self.idx_name].encode('cp1251', 'ignore'),
                          rec[self.idx_details].encode('cp1251', 'ignore'),
                          rec[self.idx_done], rec[self.idx_done_date], rec[self.idx_done_time],
                          rec[self.idx_done_details].encode('cp1251', 'ignore'), rec[idx_id]])

        self.win.deiconify()

    def search(self):
        search_value = self.phone_text.get().lower()
        if len(search_value) <= 2:
            self.search_res_lst.pack_forget()
            return

        self.search_res_records = []
        self.search_res_lst.delete(0, END)

        self.app.app.db.execute(self.columns_query +
                                'where instr(myLower(phone), ?) > 0 '
                                'collate nocase', (search_value,))

        res = self.app.app.db.fetchall()
        if res:
            for x in res:
                out = list(x)

                # Скрытие колонок
                out_lst = [value if value is not None else ''
                           for i, value in enumerate(out)
                           if i not in self.hidden_idxs]

                self.search_res_lst.insert(END, out_lst)
                self.search_res_records.append(out)
            self.search_res_lst.see(END)
            self.search_res_lst.pack(fill=BOTH, expand=1)
        else:
            self.search_res_lst.pack_forget()

    def handle_search_res_click(self):
        self.fill_matched_entry()

    def fill_matched_entry(self):
        if not self.search_res_lst.curselection():
            return
        c = self.search_res_records[int(self.search_res_lst.curselection()[0])]
        self.phone_ent.delete(0, END)
        self.phone_ent.insert(0, c[0])
        self.name_ent.delete(0, END)
        self.name_ent.insert(0, c[1])
        self.details_ent.focus()

    def get_last_receipt_number(self):
        try:
            num = int(self.app.app.sets.receipt_number)
            self.app.app.sets.receipt_number = num + 1
            return num
        except AttributeError:
            return 0
