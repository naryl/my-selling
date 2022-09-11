# -*-coding:utf-8-*-
# экран формирования расписки
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
import os
import subprocess
import tempfile
from Tkinter import *

import chevron
import xhtml2pdf.pisa as pisa

from edit_log import Log
from ttk import *


# TODO remove as unused
# noinspection DuplicatedCode,PyAttributeOutsideInit,PyByteLiteral
class Main:
    def __init__(self, app):
        self.app = app
        self.initial_values = {}

    def run(self):
        self.log = Log(self.app.app)

        self.win = Toplevel(self.app.app.win)
        self.win.title('Расписка')
        self.win.protocol("WM_DELETE_WINDOW", self.exit)
        x, y = 1600, 400
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32':
            self.win.iconbitmap('app/images/icon.ico')

        self.init_ui()

    def init_ui(self):
        self.item_vars = []
        
        self.content_frame = Frame(self.win)
        self.content_frame.grid(row=0, column=0)

        self.receipt_number_var = StringVar()
        self.receipt_number_var.set(self.initial_values.get('receipt_number', ''))
        Label(self.content_frame, text='Номер').grid(row=0, column=0, padx=5)
        self.receipt_number_ent = Entry(self.content_frame, width=50, cursor='xterm', font=('normal', 14),
                                        textvariable=self.receipt_number_var)
        self.receipt_number_ent.grid(row=0, column=1)

        self.save_number_but = Button(self.content_frame, text='Сохранить номер', image=self.app.app.img['save'], compound='left',
                                      command=self.save_receipt_number)
        self.save_number_but.grid(row=0, column=2, padx=2, pady=2)

        self.phone_main_var = StringVar()
        self.phone_main_var.set(self.initial_values.get('phone_main', ''))
        Label(self.content_frame, text='Телефон, имя').grid(row=1, column=0, padx=5)
        self.phone_main_ent = Entry(self.content_frame, width=50, cursor='xterm', font=('normal', 14),
                                    textvariable=self.phone_main_var)
        self.phone_main_ent.grid(row=1, column=1)

        self.phone_additional_var = StringVar()
        self.phone_additional_var.set(self.initial_values.get('phone_additional', ''))
        Label(self.content_frame, text='Дополнительный телефон').grid(row=2, column=0, padx=5)
        self.phone_additional_ent = Entry(self.content_frame, width=50, cursor='xterm', font=('normal', 14),
                                          textvariable=self.phone_additional_var)
        self.phone_additional_ent.grid(row=2, column=1)

        self.diag_time_var = StringVar()
        self.diag_time_var.set(self.initial_values.get('diag_time', ''))
        Label(self.content_frame, text='Дней на диагностику').grid(row=3, column=0, padx=5)
        self.diag_time_ent = Entry(self.content_frame, width=50, cursor='xterm', font=('normal', 14),
                                   textvariable=self.diag_time_var)
        self.diag_time_ent.grid(row=3, column=1)

        self.date_time_var = StringVar()
        self.date_time_var.set(self.initial_values.get('date_time', ''))
        Label(self.content_frame, text='Дата, время').grid(row=4, column=0, padx=5)
        self.date_time_ent = Entry(self.content_frame, width=50, cursor='xterm', font=('normal', 14),
                                   textvariable=self.date_time_var)
        self.date_time_ent.grid(row=4, column=1)

        # Table header
        self.items_frame = Frame(self.win)
        self.items_frame.grid(row=1, column=0)
        Label(self.items_frame, text='№').grid(row=0, column=0)
        Label(self.items_frame, text='Модель').grid(row=0, column=1)
        Label(self.items_frame, text='Сер. №').grid(row=0, column=2)
        Label(self.items_frame, text='Неисправность').grid(row=0, column=3)
        Label(self.items_frame, text='Повреждения').grid(row=0, column=4)
        Label(self.items_frame, text='Выявл. неиспр.').grid(row=0, column=5)
        Label(self.items_frame, text='Срок рем.').grid(row=0, column=6)

        self.add_item()

        self.print_but = Button(self.win, text='Расписка', image=self.app.app.img['save'], compound='left',
                                command=self.generate_receipt)
        self.print_but.grid(row=2, column=0, padx=2, pady=2)

    def add_item(self):
        num = len(self.item_vars) + 1
        
        self.item_number_var = StringVar()
        self.item_number_var.set(str(num))
        self.item_number_ent = Entry(self.items_frame, width=5, cursor='xterm', font=('normal', 14),
                                     textvariable=self.item_number_var)
        self.item_number_ent.grid(row=num, column=0)

        self.item_device_var = StringVar()
        self.item_device_var.set(self.initial_values.get('item_device', ''))
        self.item_device_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                     textvariable=self.item_device_var)
        self.item_device_ent.grid(row=num, column=1)

        self.item_serial_var = StringVar()
        self.item_serial_var.set(self.initial_values.get('item_serial', ''))
        self.item_serial_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                     textvariable=self.item_serial_var)
        self.item_serial_ent.grid(row=num, column=2)

        self.item_declared_defect_var = StringVar()
        self.item_declared_defect_var.set(self.initial_values.get('item_declared_defect', ''))
        self.item_declared_defect_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                              textvariable=self.item_declared_defect_var)
        self.item_declared_defect_ent.grid(row=num, column=3)

        self.item_existing_damage_var = StringVar()
        self.item_existing_damage_var.set(self.initial_values.get('item_existing_damage', ''))
        self.item_existing_damage_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                              textvariable=self.item_existing_damage_var)
        self.item_existing_damage_ent.grid(row=num, column=4)

        self.item_alleged_defect_var = StringVar()
        self.item_alleged_defect_var.set(self.initial_values.get('item_alleged_defect', ''))
        self.item_alleged_defect_ent = Entry(self.items_frame, width=30, cursor='xterm', font=('normal', 14),
                                             textvariable=self.item_alleged_defect_var)
        self.item_alleged_defect_ent.grid(row=num, column=5)

        self.item_repair_time_var = StringVar()
        self.item_repair_time_var.set(self.initial_values.get('item_repair_time', ''))
        self.item_repair_time_ent = Entry(self.items_frame, width=15, cursor='xterm', font=('normal', 14),
                                          textvariable=self.item_repair_time_var)
        self.item_repair_time_ent.grid(row=num, column=6)

        self.remove_item_but = Button(self.items_frame, text='-', compound='left',
                                      command=lambda: self.remove_item(num - 1))
        self.remove_item_but.grid(row=num, column=7, padx=2, pady=2)

        self.add_item_but = Button(self.items_frame, text='+', compound='left',
                                   command=self.add_item)
        self.add_item_but.grid(row=num + 1, column=7, padx=2, pady=2)

        self.item_vars.append((num,
                               self.item_number_var,
                               self.item_device_var,
                               self.item_serial_var,
                               self.item_declared_defect_var,
                               self.item_existing_damage_var,
                               self.item_alleged_defect_var,
                               self.item_repair_time_var))

    def remove_item(self, num):
        if len(self.item_vars) > 1:
            for var in self.item_vars[num][1:]:
                var.set('')

    def exit(self, _=None):
        """ выход """
        self.win.destroy()

    def dump_errors(self, pdf, show_log=True):
        # if showLog and pdf.log:
        #    for mode, line, msg, code in pdf.log:
        #        print "%s in line %d: %s" % (mode, line, msg)
        # if pdf.warn:
        #    print "*** %d WARNINGS OCCURRED" % pdf.warn
        if pdf.err:
            print "*** %d ERRORS OCCURRED" % pdf.err

    def set_initial_values(self, values):
        self.initial_values = values

    def prepare_data(self):
        if sys.platform == 'win32':
            arial_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'arial.ttf')
            times_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'times.ttf')
            fonts = [
                {
                    'family': 'sans-serif',
                    'font': arial_path
                },
                {

                    'family': 'serif',
                    'font': times_path
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

        return {
            'fonts': fonts,
            'receipt_number': self.receipt_number_var.get(),
            'list_items': list_items,
            'diag_time': self.diag_time_var.get(),
            'phone_main': self.phone_main_var.get(),
            'phone_additional': self.phone_additional_var.get(),
            'date_time': self.date_time_var.get()
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
            self.dump_errors(pdf)
        else:
            try:
                os.startfile(pdf_file_path, 'print')
            except AttributeError:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, pdf_file_path])

    def save_receipt_number(self):
        try:
            self.app.app.sets.receipt_number = int(self.receipt_number_var.get())
        except ValueError:
            pass
