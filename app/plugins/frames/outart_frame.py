# -*-coding:utf-8-*-
# окно со списанием товара
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

from app.plugins.ext_lib.date_time import date_now, time_now

name = 'Списание товара'
frame = 1


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        CyrillicKeybindsMixin.enable_cyrillic_keybinds(self.win)
        self.win.title(name)
        x, y = 700, 120
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        self.cur_list = []
        self.add_f = LabelFrame(self.win, text='Товар')
        self.add_f.pack(expand=YES, fill=X, anchor=N)
        self.init_add()

    def init_add(self):
        """ фрейм с выбором товара """
        self.init_deps()
        self.cat_but = Button(self.add_f, style='mini.TButton', image=self.app.app.img['dep_db'], compound='top',
                              text='Товар', command=self.cat_handler)
        self.cat_but.pack(side='left')

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

        self.save_but = Button(self.tools_f, text='Списать', image=self.app.app.img['check'], compound='left',
                               command=self.save_all)
        self.save_but.grid(row=0, column=2)

        Label(self.tools_f, text='Причина списания', font=('normal', 12)).grid(row=0, column=0)

        self.pr_ent = Entry(self.tools_f, width=35, cursor='xterm', font=('normal', 12))
        self.pr_ent.grid(row=0, column=1, padx=10)

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
        """ вызывается при выборе отдела """
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
        """ вызывается при выборе товаров """
        self.cat_id = id
        t = []
        flag = True
        self.app.app.db.execute('select name,edit,sum,parent from article where id=?', (id,))
        s = self.app.app.db.fetchall()[0]
        par = s[3]
        t.append(s[0])
        if par == -1: flag = 0
        # построение полгого имени товара включая подкатегории
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

    def save_all(self):
        """ Сохранияем списание """

        date = date_now()
        tm = time_now()
        user = self.app.app.user.decode('utf-8')
        try:
            razves = ast.literal_eval(self.app.app.sets.razves)[self.cur_dep]
        except AttributeError:
            razves = 0

        txt = self.dep_name.get('0.0', END).replace('\r', '').replace('\n', ' ').replace('\t', ' ')
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
        event = self.pr_ent.get()
        if len(event) < 2:
            box.showerror(title='Ошибка', message='Не введена причина!')
            self.win.deiconify()
            return
        self.app.app.db.execute('insert into out_art values (?,?,?,?,?,?)', (date, tm, txt, event, rate, user))
        self.app.app.db.execute('select rate from article where id=?', (self.cat_id,))
        rate = self.app.app.db.fetchall()[0][0] - rate
        if rate < 0:
            box.showerror(title='Ошибка', message='Товара итак нет!')
            self.win.deiconify()
            return
        self.app.app.db.execute('update article set rate=? where id=?', (rate, self.cat_id))
        self.app.app.con.commit()
        self.win.destroy()
