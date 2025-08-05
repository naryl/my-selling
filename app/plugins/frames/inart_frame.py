# -*-coding:utf-8-*-
# добавление прихода товара
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
import ast
import tkinter.messagebox as box
from tkinter import *

from app.plugins.ext_lib.cyrillic_keybinds import CyrillicKeybindsMixin
from app.plugins.ext_lib.ttk import *

from app.plugins.ext_lib.MultiListbox import MultiListbox
from app.plugins.ext_lib.date_time import date_now, time_now

name = 'Приход товара'
frame = 1


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        x, y = 800, 350
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.cur_list = []
        self.add_f = LabelFrame(self.win, text='Товар')
        self.add_f.pack(expand=YES, fill=X, anchor=N)
        self.init_add()

        self.lst = MultiListbox(self.win, (('Отдел', 3), ('Товар', 60), ('Количество', 3)), font=('normal', 12))
        self.lst.pack(fill=BOTH, expand=1, padx=5)

    def init_add(self):
        """ фрейм с добавлением товара """
        self.init_deps()
        self.cat_but = Button(self.add_f, style='mini.TButton', image=self.app.app.img['dep_db'], compound='top',
                              text='Товар', command=self.cat_handler)
        self.cat_but.pack(side='left')

        self.add_but = Button(self.add_f, text='Добавить', image=self.app.app.img['add'], compound='left',
                              command=self.add_handler)
        self.add_but.pack(side='right')

        self.rate_v = Combobox(self.add_f, width=6, font=('bold', 16))
        self.rate_v.set('1')
        self.rate_v.pack(side='right', padx=10)
        self.rate_v['values'] = range(1, 21)

        self.dep_name = Text(self.add_f, height=2, font=(15))
        self.dep_name.pack(side='left', padx=10, fill=BOTH, pady=5)
        self.dep_name['state'] = 'disable'

        self.build_tree()

        self.tools_f = Frame(self.win)
        self.tools_f.pack(fill=BOTH, side='bottom', expand=1)

        self.del_but = Button(self.tools_f, text='Удалить текущий', image=self.app.app.img['delete'], compound='left',
                              command=self.del_handler)
        self.del_but.pack(side='left', padx=15, pady=10)

        self.save_but = Button(self.tools_f, text='Сохранить приход', image=self.app.app.img['save'], compound='left',
                               command=self.save_all)
        self.save_but.pack(side='right', padx=15, pady=10)

        self.lab_var = StringVar()
        self.lab_var.set('Позиций: 0 шт.\n Товара: 0 шт.')
        Label(self.tools_f, textvariable=self.lab_var, font=('normal', 12)).pack(side='top')

    def init_deps(self):
        """ меню с отделами """
        self.deps = []
        self.app.app.db.execute('select name from dep')
        for n, name in enumerate(self.app.app.db.fetchall()):
            self.deps.append('%s %s' % (n + 1, name[0]))

        self.cur_dep = 0
        self.dep_str = StringVar()
        self.dep_str.set(self.deps[0])
        Style().configure("TMenubutton", font=('bold', 13))
        self.otd = Menubutton(self.add_f, textvariable=self.dep_str,
                              width=19, image=self.app.app.img['deps'], compound='left')
        self.otd.pack(pady=10, side='left', padx=10)
        self.otd.menu = Menu(self.otd,
                             font=("bold", 13), bg='white', relief='flat', tearoff=0)
        for n, x in enumerate(self.deps):
            if len(x) > 3:
                self.otd.menu.add_command(label=x.ljust(25), command=lambda z=n: self.deps_hand(z))
        self.otd['menu'] = self.otd.menu

    def deps_hand(self, n):
        """ вызывается при смене отдела """
        self.cur_dep = n
        self.dep_str.set(self.deps[n])
        self.cat_id = -1
        self.build_tree()

    def build_tree(self):
        """ построение дерева товаров """
        self.popup = Menu(self.win, tearoff=0, font=('normal', 12))

        def get_menu(id):
            self.app.app.db.execute(
                'select id,name,type from article where dep=? and parent=? order by type DESC, name',
                (self.cur_dep + 1, id,))
            popup = Menu(self.win, tearoff=0, font=('normal', 12))
            for x in self.app.app.db.fetchall():
                if x[2] == 'item':
                    popup.add_command(label=x[1], command=lambda z=x[0]: self.command_handler(z))
                else:
                    popup.add_cascade(label=x[1], menu=get_menu(x[0]))
            return popup

        self.app.app.db.execute('select id,name,type from article where dep=? and parent=-1 order by type DESC, name',
                                (self.cur_dep + 1,))

        for x in self.app.app.db.fetchall():
            if x[2] == 'item':
                self.popup.add_command(label=x[1], command=lambda z=x[0]: self.command_handler(z))
            else:
                self.popup.add_cascade(label=x[1], menu=get_menu(x[0]))

    def cat_handler(self):
        self.popup.tk_popup(self.cat_but.winfo_rootx() + 30, self.cat_but.winfo_rooty() + 55, 0)

    def command_handler(self, id):
        """ при щелчке на товар """
        self.cat_id = id
        t = []
        flag = True
        self.app.app.db.execute('select name,edit,sum,parent from article where id=?', (id,))
        s = self.app.app.db.fetchall()[0]
        par = s[3]
        t.append(s[0])
        if par == -1: flag = 0
        #  построение длинного названия товара, включая подкатегории
        while flag:
            self.app.app.db.execute('select name,parent from article where id=?', (par,))
            rez = self.app.app.db.fetchall()[0]
            if rez[1] == -1:
                t.append(rez[0])
                flag = False
            else:
                t.append(rez[0])
                par = rez[1]
        cat_lst = ' > '.join(t[::-1])
        self.dep_name['state'] = 'normal'
        self.dep_name.delete(0.0, END)
        self.dep_name.insert(0.0, cat_lst)
        self.dep_name['state'] = 'disable'

    def add_handler(self):
        """ добавление товара во временный список """
        txt = self.dep_name.get('0.0', END).replace('\r', '').replace('\n', ' ').replace('\t', ' ')

        try:
            razves = ast.literal_eval(self.app.app.sets.razves)[self.cur_dep]
        except AttributeError:
            razves = 0

        if len(txt) < 2:
            box.showerror(title='Ошибка', message='Не выбран товар!')
            self.win.deiconify()
            return
        try:
            if razves:
                rate = float(self.rate_v.get().replace(',', '.'))
            else:
                rate = int(self.rate_v.get().replace(',', '.'))
        except:
            box.showerror(title='Ошибка', message='Не верное количество!')
            self.win.deiconify()
            return
        if rate <= 0:
            box.showerror(title='Ошибка', message='Не верное количество!')
            self.win.deiconify()
            return
        self.cur_list.append([self.cur_dep + 1, txt, rate, self.cat_id])
        self.update_list()
        self.dep_name['state'] = 'normal'
        self.dep_name.delete(0.0, END)
        self.dep_name['state'] = 'disable'
        self.rate_v.set('1')

    def update_list(self):
        """ обновление таблицы со списком прихода """
        self.lst.delete(0, END)
        for x in self.cur_list:
            self.lst.insert(END, x)
        self.lst.see(END)

        s1 = len(self.cur_list)
        s2 = 0
        for x in self.cur_list:
            s2 += x[2]
        self.lab_var.set('Позиций: %s шт.\n Товара: %s шт.' % (s1, s2))

    def del_handler(self):
        """ удаление товара из временного списка """
        sel = self.lst.curselection()
        if not sel: return
        sel = int(sel[0])
        del self.cur_list[sel]
        self.update_list()

    def save_all(self):
        """ Сохрание прихода и записть в таблицу приходов """
        date = date_now()
        tm = time_now()
        user = self.app.app.user.decode('utf-8')
        self.app.app.db.execute('select max(id) from in_art')
        try:
            id = self.app.app.db.fetchall()[0][0] + 1
        except:
            id = 1

        for x in self.cur_list:
            self.app.app.db.execute('insert into in_art values (?,?,?,?,?,?,?)', (id, date, tm, x[0], x[1], x[2], user))
            self.app.app.db.execute('select rate from article where id=?', (x[3],))
            rate = self.app.app.db.fetchall()[0][0] + x[2]
            self.app.app.db.execute('update article set rate=? where id=?', (rate, x[3]))

        self.app.app.con.commit()
        self.win.destroy()
