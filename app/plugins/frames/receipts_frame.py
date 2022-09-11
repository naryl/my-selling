# -*-coding:utf-8-*-
# экран расписок о приёме техники в ремонт
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
import cStringIO
import datetime
import os
import subprocess
import tempfile
import time
import tkMessageBox
from Tkinter import *
from collections import defaultdict

import chevron
from xhtml2pdf import pisa

from MultiListbox import MultiListbox
from calend import TkCalendar
from date_time import date_now, date_get, time_now, norm_date_time, norm_date
from edit_log import Log
from ttk import *

# noinspection PyByteLiteral
name = 'Расписки'
frame = 0
icon = 'contract'


# noinspection DuplicatedCode,PyAttributeOutsideInit,PyByteLiteral
class Plugin:
    def __init__(self, app):
        self.app = app
        self.initial_values = {}

    def set_initial_values(self, values):
        self.initial_values = values

    def run(self):
        self.log = Log(self.app.app)

        if hasattr(self.app, "receipts_frame") \
                and self.app.receipts_frame.winfo_exists():
            self.app.receipts_frame.deiconify()
            self.app.receipts_frame.focus()
            self.app.receipts_frame.state()
            return 'break'

        self.win = Toplevel(self.app.app.win)
        self.app.receipts_frame = self.win
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

    def init_ui(self):
        self.filter_frame = Labelframe(self.content_frame, text='Фильтр (Номер/Телефон; Диапазон Дат)',
                                       width=50, height=100)
        self.filter_frame.pack(fill=X)
        self.filter_entry = Entry(self.filter_frame, width=20, cursor='xterm', font=('normal', 14))
        self.filter_entry.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        self.filter_entry.bind('<Return>', lambda _: self.update_lists())
        self.lst_frame = Frame(self.content_frame)
        self.lst_frame.pack(fill=BOTH, expand=1)
        self.init_common_query_data()
        self.lst = MultiListbox(self.lst_frame, self.columns,
                                font=('bold', 14), height=13, command=self.list_select)
        self.lst.pack(fill=BOTH, expand=1)

        self.init_date_filter_ui()

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
        self.update_lists()
        self.list_select()

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

        self.show_but = Button(self.calend_info_frame, text='Показать', image=self.app.app.img['check'], compound='left',
                               command=self.update_lists)
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
        delattr(self.app, "receipts_frame")
        self.win.destroy()

    def init_common_query_data(self):
        # Колонки в таблице
        self.columns = (
            ('Номер', 5),
            ('Телефон', 10),
            ('Телефон доп.', 10),
            ('Товары', 15),
            ('Дата', 8),
            ('Время', 8),
            ('Сделано', 5))

        # Запрос к БД со всеми колонками
        self.select_column_names = 'number,phone_main,phone_additional,service_center,max_repair_time,' \
                                   'group_concat(device) as item_names,date,time,done,r.id'
        self.insert_column_names = 'number,phone_main,phone_additional,service_center,max_repair_time,' \
                                   'date,time,done'
        self.columns_query = 'select ' + \
                             self.select_column_names +\
                             ' from receipt r ' \
                             ' join receipt_item ri on ri.receipt_id = r.id '
        self.columns_group_clause = \
            ' group by number,phone_main,phone_additional,date,time,done '

        # Номера колонок
        self.idx_number = 0
        self.idx_phone_main = 1
        self.idx_phone_additional = 2
        self.idx_service_center = 3
        self.idx_max_repair_time = 4
        self.idx_item_names = 5
        self.idx_date = 6
        self.idx_time = 7
        self.idx_done = 8
        self.idx_id = 9

        # Скрытые колонки
        self.hidden_idxs = [self.idx_service_center,
                            self.idx_max_repair_time,
                            self.idx_id]

        # Запрос к БД со всеми колонками - receipt item
        self.item_column_names = 'receipt_id,line_number,device,serial,declared_defect,existing_damage,' \
                                 'alleged_defect,repair_time,repair_price,sale_price,warranty_period'
        self.item_columns_query = 'select ' + self.item_column_names + ' from receipt_item'

        # Номера колонок
        self.idx_item_receipt_id = 0
        self.idx_item_line_number = 1
        self.idx_item_device = 2
        self.idx_item_serial = 3
        self.idx_item_declared_defect = 4
        self.idx_item_existing_damage = 5
        self.idx_item_alleged_defect = 6
        self.idx_item_repair_time = 7
        self.idx_item_repair_price = 8
        self.idx_item_sale_price = 9
        self.idx_item_warranty_period = 10

    def update_lists(self):
        """ наполняем таблицы """
        self.current_records = []
        self.lst.delete(0, END)
        filter_value = self.filter_entry.get().lower()
        if len(filter_value) > 0:
            self.calend_show_all_var.set(1)
            self.app.app.db.execute(self.columns_query +
                                    'where instr(myLower(phone_main), ?) > 0 '
                                    'or instr(myLower(phone_additional), ?) > 0 '
                                    'or instr(number, ?) > 0 ' +
                                    self.columns_group_clause +
                                    'collate nocase', (filter_value, filter_value, filter_value))
        elif not self.calend_show_all_var.get():
            self.app.app.db.execute(self.columns_query +
                                    'where date between ? and ?' +
                                    self.columns_group_clause, (self.c_date, self.c_date2))
        else:
            self.app.app.db.execute(self.columns_query + self.columns_group_clause)

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

        # Загрузка receipt items
        self.item_current_records = defaultdict(list)
        self.app.app.db.execute(self.item_columns_query)
        for x in self.app.app.db.fetchall():
            receipt_id = x[self.idx_item_receipt_id]
            self.item_current_records[receipt_id].append(x)

        self.lst.see(END)

    def list_select(self):
        """ при щелчке на записи """
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
                                        compound=LEFT, command=self.delete_record)
            self.delete_button.grid(row=0, column=2, padx=5)

        self.fields_frame = Frame(self.edit_frame, height=100)
        self.fields_frame.grid(row=0, column=0, sticky=W)

        self.receipt_number_var = StringVar()
        self.receipt_number_var.set(self.initial_values.get('receipt_number', ''))
        Label(self.fields_frame, text='Номер').grid(row=0, column=0, padx=5)
        self.receipt_number_ent = Entry(self.fields_frame, width=50, cursor='xterm', font=('normal', 14),
                                        textvariable=self.receipt_number_var)
        self.receipt_number_ent.grid(row=0, column=1)

        self.phone_main_var = StringVar()
        self.phone_main_var.set(self.initial_values.get('phone_main', ''))
        Label(self.fields_frame, text='Телефон, имя').grid(row=1, column=0, padx=5)
        self.phone_main_ent = Entry(self.fields_frame, width=50, cursor='xterm', font=('normal', 14),
                                    textvariable=self.phone_main_var)
        self.phone_main_ent.grid(row=1, column=1)

        self.phone_additional_var = StringVar()
        self.phone_additional_var.set(self.initial_values.get('phone_additional', ''))
        Label(self.fields_frame, text='Дополнительный телефон').grid(row=2, column=0, padx=5)
        self.phone_additional_ent = Entry(self.fields_frame, width=50, cursor='xterm', font=('normal', 14),
                                          textvariable=self.phone_additional_var)
        self.phone_additional_ent.grid(row=2, column=1)

        Label(self.fields_frame, text='Сделано').grid(row=0, column=2, padx=2, pady=2)
        self.done_var = IntVar()
        self.done_chk = Checkbutton(self.fields_frame, variable=self.done_var, onvalue=1, offvalue=0)
        self.done_chk.grid(row=0, column=3, padx=2, pady=2, sticky=W)

        self.diag_time_var = StringVar()
        self.diag_time_var.set(self.initial_values.get('diag_time', ''))
        Label(self.fields_frame, text='Дней на диагностику').grid(row=1, column=2, padx=5)
        self.diag_time_ent = Entry(self.fields_frame, width=50, cursor='xterm', font=('normal', 14),
                                   textvariable=self.diag_time_var)
        self.diag_time_ent.grid(row=1, column=3)

        self.service_center_var = StringVar()
        Label(self.fields_frame, text='Сервисный центр').grid(row=2, column=2, padx=5)
        self.service_center_ent = Entry(self.fields_frame, width=50, cursor='xterm', font=('normal', 14),
                                        textvariable=self.service_center_var)
        self.service_center_ent.grid(row=2, column=3)

        self.init_items_table()

        # Add buttons frame and Print receipt button
        self.buttons_frame = Frame(self.edit_frame)
        self.buttons_frame.grid(row=2, column=0, sticky=E)
        self.receipt_but = Button(self.buttons_frame, text='Расписка', image=self.app.app.img['sale'], compound=LEFT,
                                  command=self.generate_receipt)
        self.receipt_but.grid(row=0, column=2, padx=2, pady=2, sticky=E)

        if not self.lst.curselection():
            self.create_mode()
        else:
            self.edit_mode()

    def init_items_table(self):
        """ показать таблицу с элементами расписки """
        self.items_canvas_frame = Frame(self.edit_frame)
        self.items_canvas_frame.grid(row=1, column=0, sticky=EW)
        # Add non-zero weight to the canvas to allow it to resize with the window
        self.edit_frame.grid_rowconfigure(1, weight=1)
        self.edit_frame.grid_columnconfigure(0, weight=1)
        self.items_canvas_frame.grid_rowconfigure(0, weight=1)
        self.items_canvas_frame.grid_columnconfigure(0, weight=1)
        self.items_canvas_frame.grid_propagate(False)

        self.items_canvas = Canvas(self.items_canvas_frame)
        self.items_canvas.grid(row=0, column=0, sticky=NSEW)

        self.items_vsb = Scrollbar(self.items_canvas_frame, orient=VERTICAL, command=self.items_canvas.yview)
        self.items_vsb.grid(row=0, column=1, sticky=NS)
        self.items_canvas.configure(yscrollcommand=self.items_vsb.set)

        self.items_hsb = Scrollbar(self.items_canvas_frame, orient=HORIZONTAL, command=self.items_canvas.xview)
        self.items_hsb.grid(row=1, column=0, sticky=EW)
        self.items_canvas.configure(xscrollcommand=self.items_hsb.set)

        # Table header
        self.items_frame = Frame(self.items_canvas)
        self.items_canvas.create_window((0, 0), window=self.items_frame, anchor=NW)
        Label(self.items_frame, text='№').grid(row=0, column=1)
        Label(self.items_frame, text='Модель').grid(row=0, column=2)
        Label(self.items_frame, text='Сер. №').grid(row=0, column=3)
        Label(self.items_frame, text='Неисправность').grid(row=0, column=4)
        Label(self.items_frame, text='Повреждения').grid(row=0, column=5)
        Label(self.items_frame, text='Выявл. неиспр.').grid(row=0, column=6)
        Label(self.items_frame, text='Срок рем.').grid(row=0, column=7)
        Label(self.items_frame, text='Цена рем.').grid(row=0, column=8)
        Label(self.items_frame, text='Цена прод.').grid(row=0, column=9)
        Label(self.items_frame, text='Срок гаран.').grid(row=0, column=10)

        # Initialize empty items list
        self.item_vars = []

        # Add one initial item
        self.add_item()

        # Clear initial values after the fields initialization
        self.initial_values = {}

        # Resize canvas to the table size
        self.items_frame.update_idletasks()
        scrollbar_width = 15
        self.items_canvas_frame.config(width=self.items_frame.winfo_width() + scrollbar_width,
                                       height=self.items_frame.winfo_height() + scrollbar_width)
        self.items_canvas.config(scrollregion=self.items_canvas.bbox(ALL))

    def add_item(self):
        num = len(self.item_vars) + 1

        remove_item_but = Button(self.items_frame, text='-', compound=LEFT,
                                 command=lambda: self.remove_item(num - 1))
        remove_item_but.grid(row=num, column=0, padx=2, pady=2)

        add_item_but = Button(self.items_frame, text='+', compound=LEFT,
                              command=self.add_item)
        add_item_but.grid(row=num + 1, column=0, padx=2, pady=2)

        item_number_var = StringVar()
        item_number_var.set(str(num))
        item_number_ent = Entry(self.items_frame, width=5, cursor='xterm', font=('normal', 14),
                                textvariable=item_number_var)
        item_number_ent.grid(row=num, column=1)

        item_device_var = StringVar()
        item_device_var.set(self.initial_values.get('item_device', ''))
        item_device_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                textvariable=item_device_var)
        item_device_ent.grid(row=num, column=2)

        item_serial_var = StringVar()
        item_serial_var.set(self.initial_values.get('item_serial', ''))
        item_serial_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                textvariable=item_serial_var)
        item_serial_ent.grid(row=num, column=3)

        item_declared_defect_var = StringVar()
        item_declared_defect_var.set(self.initial_values.get('item_declared_defect', ''))
        item_declared_defect_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                         textvariable=item_declared_defect_var)
        item_declared_defect_ent.grid(row=num, column=4)

        item_existing_damage_var = StringVar()
        item_existing_damage_var.set(self.initial_values.get('item_existing_damage', ''))
        item_existing_damage_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                         textvariable=item_existing_damage_var)
        item_existing_damage_ent.grid(row=num, column=5)

        item_alleged_defect_var = StringVar()
        item_alleged_defect_var.set(self.initial_values.get('item_alleged_defect', ''))
        item_alleged_defect_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                        textvariable=item_alleged_defect_var)
        item_alleged_defect_ent.grid(row=num, column=6)

        item_repair_time_var = StringVar()
        item_repair_time_var.set(self.initial_values.get('item_repair_time', '2-3 дня(ей)'))
        item_repair_time_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                     textvariable=item_repair_time_var)
        item_repair_time_ent.grid(row=num, column=7)

        item_repair_price_var = StringVar()
        item_repair_price_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                      textvariable=item_repair_price_var)
        item_repair_price_ent.grid(row=num, column=8)

        item_sale_price_var = StringVar()
        item_sale_price_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                    textvariable=item_sale_price_var)
        item_sale_price_ent.grid(row=num, column=9)

        item_warranty_period_var = StringVar()
        item_warranty_period_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                         textvariable=item_warranty_period_var)
        item_warranty_period_ent.grid(row=num, column=10)

        self.item_vars.append((num,
                               item_number_var,
                               item_device_var,
                               item_serial_var,
                               item_declared_defect_var,
                               item_existing_damage_var,
                               item_alleged_defect_var,
                               item_repair_time_var,
                               item_repair_price_var,
                               item_sale_price_var,
                               item_warranty_period_var))

        self.items_frame.update_idletasks()
        self.items_canvas.config(scrollregion=self.items_canvas.bbox(ALL))

    def remove_item(self, num):
        if len(self.item_vars) > 1:
            for var in self.item_vars[num][1:]:
                var.set('')

    def edit_mode(self):
        """ режим редактирования записи """
        self.save_but = Button(self.buttons_frame, text='Сохранить', image=self.app.app.img['save'], compound=LEFT,
                               command=self.save_record)
        self.save_but.grid(row=0, column=0, padx=2, pady=2, sticky=E)
        self.cancel_but = Button(self.buttons_frame, text='Отмена', image=self.app.app.img['cancel'], compound=LEFT,
                                 command=self.deselect)
        self.cancel_but.grid(row=0, column=1, pady=2)

        # Load values
        c = self.current_records[int(self.lst.curselection()[0])]
        items = self.item_current_records[c[self.idx_id]]
        # Fill the values into the fields
        self.receipt_number_var.set(c[self.idx_number])
        self.phone_main_var.set(c[self.idx_phone_main])
        self.phone_additional_var.set(c[self.idx_phone_additional])
        self.done_var.set(c[self.idx_done])
        self.diag_time_var.set(1 if c[self.idx_max_repair_time] else 0)
        self.service_center_var.set(c[self.idx_service_center])
        # Add items if necessary
        for i in range(1, len(items)):
            self.add_item()
        # Fill the values into the table
        for (item, vars_tuple) in zip(items, self.item_vars):
            vars_tuple[self.idx_item_line_number].set(item[self.idx_item_line_number])
            vars_tuple[self.idx_item_device].set(item[self.idx_item_device])
            vars_tuple[self.idx_item_serial].set(item[self.idx_item_serial])
            vars_tuple[self.idx_item_declared_defect].set(item[self.idx_item_declared_defect])
            vars_tuple[self.idx_item_existing_damage].set(item[self.idx_item_existing_damage])
            vars_tuple[self.idx_item_alleged_defect].set(item[self.idx_item_alleged_defect])
            vars_tuple[self.idx_item_repair_time].set(item[self.idx_item_repair_time])
            vars_tuple[self.idx_item_repair_price].set(item[self.idx_item_repair_price])
            vars_tuple[self.idx_item_sale_price].set(item[self.idx_item_sale_price])
            vars_tuple[self.idx_item_warranty_period].set(item[self.idx_item_warranty_period])

    def create_mode(self):
        """ режим создания записи """
        self.save_but = Button(self.buttons_frame, text='Добавить', image=self.app.app.img['save'], compound=LEFT,
                               command=self.create_record)
        self.save_but.grid(row=0, column=0, columnspan=2, pady=2, sticky=E)

        # Set default values
        self.app.app.db.execute('select max(number) from receipt')
        try:
            next_receipt_number = self.app.app.db.fetchall()[0][0] + 1
        except TypeError:
            next_receipt_number = 1
        self.receipt_number_var.set(next_receipt_number)
        self.diag_time_var.set('3')
        vars_tuple = self.item_vars[0]
        vars_tuple[self.idx_item_repair_time].set('2-3 дня(ей)')

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
        self.app.app.db.execute('delete from receipt where id = ?', (c[self.idx_id],))
        self.app.app.db.execute('delete from receipt_item where receipt_id = ?', (c[self.idx_id],))
        self.app.app.con.commit()
        self.delete_entry.delete(0, END)
        self.deselect()
        self.update_lists()
        self.log.del_receipt(c[self.idx_date], c[self.idx_time], c[self.idx_phone_main], c[self.idx_item_names],
                             self.app.app.user.decode('utf-8'), text)

    def save_record(self):
        """ сохранение отредактированной записи """
        if not self.lst.curselection():
            return

        c = self.current_records[int(self.lst.curselection()[0])]
        receipt_id = c[self.idx_id]
        date = c[self.idx_date]
        time = c[self.idx_time]
        receipt_number = self.receipt_number_var.get()
        phone_main = self.phone_main_var.get()
        phone_additional = self.phone_additional_var.get()
        done = self.done_var.get()
        diag_time = self.diag_time_var.get()
        service_center = self.service_center_var.get()

        # Remove old items
        self.app.app.db.execute('delete from receipt_item where receipt_id = ?', (receipt_id,))

        # Get new item id
        self.app.app.db.execute('select max(id) from receipt_item')
        try:
            item_id = self.app.app.db.fetchall()[0][0] + 1
        except TypeError:
            item_id = 1
        # Insert new items
        for vars_tuple in self.item_vars:
            line_number = vars_tuple[self.idx_item_line_number].get()
            if not line_number:
                continue
            device = vars_tuple[self.idx_item_device].get()
            serial = vars_tuple[self.idx_item_serial].get()
            declared_defect = vars_tuple[self.idx_item_declared_defect].get()
            existing_damage = vars_tuple[self.idx_item_existing_damage].get()
            alleged_defect = vars_tuple[self.idx_item_alleged_defect].get()
            repair_time = vars_tuple[self.idx_item_repair_time].get()
            repair_price = vars_tuple[self.idx_item_repair_price].get()
            sale_price = vars_tuple[self.idx_item_sale_price].get()
            warranty_period = vars_tuple[self.idx_item_warranty_period].get()
            # noinspection SqlInsertValues
            self.app.app.db.execute(
                'insert into receipt_item (id, {0}) '
                'values (?,?,?,?,?,?,?,?,?,?,?,?)'.format(self.item_column_names),
                (item_id, receipt_id, line_number, device, serial, declared_defect, existing_damage,
                 alleged_defect, repair_time, repair_price, sale_price, warranty_period))
            item_id += 1

        # Update receipt
        i = int(self.lst.curselection()[0])
        self.app.app.db.execute('update receipt set number=?,phone_main=?,phone_additional=?,service_center=?, '
                                'max_repair_time=?,done=? '
                                'where id = ?',
                                (receipt_number, phone_main, phone_additional, service_center, diag_time, done,
                                 receipt_id))
        self.app.app.con.commit()
        self.update_lists()
        self.lst.selection_set(i)
        self.log.edit_receipt(date, time,
                              [c[self.idx_number], c[self.idx_phone_main], c[self.idx_phone_additional]],
                              [receipt_number, phone_main, phone_additional],
                              self.app.app.user.decode('utf-8'))

    def create_record(self):
        """ создание новой записи """
        # Get values from the fields
        dt, tm = date_now(), time_now()

        receipt_number = self.receipt_number_var.get()
        phone_main = self.phone_main_var.get()
        phone_additional = self.phone_additional_var.get()
        diag_time = self.diag_time_var.get()
        service_center = self.service_center_var.get()
        done = self.done_var.get()

        if not receipt_number or not phone_main:
            return
        self.app.app.db.execute('select max(id) from receipt')
        try:
            receipt_id = self.app.app.db.fetchall()[0][0] + 1
        except TypeError:
            receipt_id = 1
        # noinspection SqlInsertValues
        self.app.app.db.execute('insert into receipt (id, ' + self.insert_column_names +
                                ') '
                                'values (?,?,?,?,?,?,?,?,?)',
                                (receipt_id, receipt_number, phone_main, phone_additional, service_center, diag_time,
                                 dt, tm, done))

        # Get new item id
        self.app.app.db.execute('select max(id) from receipt_item')
        try:
            item_id = self.app.app.db.fetchall()[0][0] + 1
        except TypeError:
            item_id = 1
        # Insert new items
        for vars_tuple in self.item_vars:
            line_number = vars_tuple[self.idx_item_line_number].get()
            if not line_number:
                continue
            device = vars_tuple[self.idx_item_device].get()
            serial = vars_tuple[self.idx_item_serial].get()
            declared_defect = vars_tuple[self.idx_item_declared_defect].get()
            existing_damage = vars_tuple[self.idx_item_existing_damage].get()
            alleged_defect = vars_tuple[self.idx_item_alleged_defect].get()
            repair_time = vars_tuple[self.idx_item_repair_time].get()
            repair_price = vars_tuple[self.idx_item_repair_price].get()
            sale_price = vars_tuple[self.idx_item_sale_price].get()
            warranty_period = vars_tuple[self.idx_item_warranty_period].get()
            # noinspection SqlInsertValues
            self.app.app.db.execute(
                'insert into receipt_item (id, {0})'
                ' values (?,?,?,?,?,?,?,?,?,?,?,?)'.format(self.item_column_names),
                (item_id, receipt_id, line_number, device, serial, declared_defect, existing_damage, alleged_defect,
                 repair_time, repair_price, sale_price, warranty_period))
            item_id += 1

        self.app.app.con.commit()

        self.update_lists()
        self.list_select()

    def prepare_data(self):
        if sys.platform == 'win32':
            arial_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'arial.ttf')
            times_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'times.ttf')
            comic_sans_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'comicbd.ttf')
            fonts = [
                {
                    'family': 'sans-serif',
                    'font': arial_path
                },
                {
                    'family': 'serif',
                    'font': times_path
                },
                {
                    'family': 'cursive',
                    'font': comic_sans_path
                }
            ]
        else:
            fonts = [
                {
                    'family': 'sans-serif',
                    'font': 'app/fonts/DejaVuSans.ttf'
                },
                {
                    'family': 'serif',
                    'font': 'app/fonts/DejaVuSans.ttf'
                }
            ]
        list_items = []
        for item in self.item_vars:
            if item[1].get():
                list_items.append({
                    'number': item[1].get(),
                    'device': item[2].get(),
                    'serial': item[3].get(),
                    'declared_defect': item[4].get(),
                    'existing_damage': item[5].get(),
                    'alleged_defect': item[6].get(),
                    'estimated_repair_time': item[7].get(),
                    'last': True if item[0] == len(list_items) else False
                })

        if self.lst.curselection():
            c = self.current_records[int(self.lst.curselection()[0])]
            date = c[self.idx_date]
            time = c[self.idx_time]
        else:
            date = date_now()
            time = time_now()
        return {
            'fonts': fonts,
            'receipt_number': self.receipt_number_var.get(),
            'list_items': list_items,
            'diag_time': self.diag_time_var.get(),
            'service_center': self.service_center_var.get(),
            'phone_main': self.phone_main_var.get(),
            'phone_additional': self.phone_additional_var.get(),
            'date_time': norm_date_time(date, time)
        }

    def generate_receipt(self):
        """ сгенерировать и распечатать расписку """
        data = self.prepare_data()

        with open('app/templates/receipt.mustache', 'r') as f:
            html_data = chevron.render(f, data)

        pdf_file, pdf_file_path = tempfile.mkstemp(suffix='.pdf')

        pdf = pisa.CreatePDF(
            cStringIO.StringIO(html_data),
            file(pdf_file_path, 'wb'),
            encoding='utf-8'
        )

        os.close(pdf_file)

        if pdf.err:
            print("*** %d ERRORS OCCURRED" % pdf.err)
        else:
            try:
                os.startfile(pdf_file_path)
            except AttributeError:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, pdf_file_path])

    def deselect(self):
        try:
            self.lst.selection_clear(self.lst.curselection())
        except TclError:
            self.lst.selection_clear(0, END)
        self.list_select()
