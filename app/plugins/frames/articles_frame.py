# -*-coding:utf-8-*-
# окно с редактированием товаров
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
from Tkinter import *
from ttk import *
import tkMessageBox as box

name = 'Товар'
frame = 1


# icon='clear'

class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):

        self.win = Toplevel(self.app.app.win)
        self.win.title(name)
        x, y = 620, 450
        pos = self.win.wm_maxsize()[0] / 2 - x / 2, self.win.wm_maxsize()[1] / 2 - y / 2
        self.win.geometry('%sx%s+%s+%s' % (x, y, pos[0], pos[1] - 25))
        self.win.maxsize(width=x, height=y)
        self.win.minsize(width=x, height=y)
        if sys.platform == 'win32': self.win.iconbitmap('app/images/icon.ico')

        Label(self.win, text='Отдел', font=('normal', 14)).grid(row=0, column=0, padx=5, pady=5)
        self.node_list = {}
        self.node_ext = {}
        self.init_deps()
        self.tree_frame = Frame(self.win, width=550)
        self.tree_frame.grid(row=1, column=0, columnspan=2, sticky=E + W, padx=5)
        self.tools_frame = Labelframe(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2)
        self.init_tree()
        self.build_tree()

    def init_deps(self):
        """ Меню с отделами """
        self.deps = []
        self.app.app.db.execute('select name from dep')
        for n, name in enumerate(self.app.app.db.fetchall()):
            self.deps.append('%s %s' % (n + 1, name[0]))

        self.cur_dep = 0
        self.dep_str = StringVar()
        self.dep_str.set(self.deps[0])
        Style().configure("TMenubutton", font=('bold', 13))
        self.otd = Menubutton(self.win, textvariable=self.dep_str,
                              width=19, image=self.app.app.img['deps'], compound='left')
        self.otd.grid(row=0, column=1, sticky=N + E, padx=5, pady=5)
        self.otd.menu = Menu(self.otd,
                             font=("bold", 13), bg='white', relief='flat', tearoff=0)
        for n, x in enumerate(self.deps):
            if len(x) > 3:
                self.otd.menu.add_command(label=x.ljust(25), command=lambda z=n: self.deps_hand(z))
        self.otd['menu'] = self.otd.menu

    def deps_hand(self, n):
        """ Вызывается при выборе отдела  """
        self.cur_dep = n
        self.dep_str.set(self.deps[n])
        self.cat_id = -1
        self.tools_frame.destroy()
        self.tools_frame = Labelframe(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2)
        self.build_tree()

    def init_tree(self):
        """ фрейм с товарами """
        self.vsb = Scrollbar(self.tree_frame, orient="vertical")

        # self.hsb = Scrollbar(self.tree_frame,orient="horizontal")

        def autoscroll(sbar, first, last):
            first, last = float(first), float(last)
            sbar.set(first, last)

        self.tree = Treeview(self.tree_frame, yscrollcommand=lambda f, l: autoscroll(self.vsb, f, l), height=18)

        self.vsb['command'] = self.tree.yview

        self.tree.column('#0', width=275)

        self.tree.grid(column=0, row=0, sticky=E + W)
        self.vsb.grid(column=1, row=0, sticky='ns')

        self.tree.bind('<Double-Button-1>', self.see_item)

    def build_tree(self):
        """ Построение дерева товаров """
        for x in self.node_list:
            try:
                self.tree.delete(x)
            except:
                pass
        for x in self.node_ext:
            try:
                self.tree.delete(x)
            except:
                pass
        self.node_list = {}
        self.node_ext = {}

        def get_menu(node):
            self.app.app.db.execute(
                'select id,name,type from article where dep=? and parent=? order by type DESC, name',
                (self.cur_dep + 1, self.node_list[node],))
            for x in self.app.app.db.fetchall():
                if x[2] == 'item':
                    node1 = self.tree.insert(node, 'end', text=x[1], tags='norm')
                    self.node_list[node1] = x[0]
                else:
                    node5 = self.tree.insert(node, 'end', text=x[1], tags='big')
                    self.node_list[node5] = x[0]
                    get_menu(node5)
            node2 = self.tree.insert(node, 'end', text='Добавить', tags=('ext'))
            self.node_ext[node2] = self.node_list[node]

        self.app.app.db.execute('select id,name,type from article where dep=? and parent=-1 order by type DESC, name',
                                (self.cur_dep + 1,))

        for x in self.app.app.db.fetchall():
            if x[2] == 'item':
                node = self.tree.insert('', 'end', text=x[1], tags='norm')
                self.node_list[node] = x[0]
            else:
                node = self.tree.insert('', 'end', text=x[1], tags='big')
                self.node_list[node] = x[0]
                get_menu(node)
        node5 = self.tree.insert('', 'end', text='Добавить', tags=('ext'))
        self.node_ext[node5] = -1
        self.tree.tag_configure('big', font=('bold', 12), foreground='#A32022')
        self.tree.tag_configure('ext', foreground='#A3CCA0')

    def see_item(self, event):
        """ Вызывается при щелчке на позиции во фрейме товаров """
        try:
            sel = self.tree.selection()[0]
        except:
            return
        if sel in self.node_ext:
            self.build_add_frame(self.node_ext[sel])
        elif sel in self.node_list:
            self.buld_edit_frame(self.node_list[sel])

    def build_add_frame(self, id):
        """ Если щелкнули на добавить, создаем форму с добавленением """
        self.tools_frame.destroy()
        self.tools_frame = Frame(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2, sticky=N, pady=40, padx=5)

        self.add_cat_frame = Labelframe(self.tools_frame, text='Добавить категорию')
        self.add_cat_frame.pack()
        self.add_cat_ent = Entry(self.add_cat_frame, width=20, cursor='xterm')
        self.add_cat_ent.grid(column=0, row=0, padx=5, pady=5)
        self.add_cat_but = Button(self.add_cat_frame, text='Добавить', image=self.app.app.img['add_cat'],
                                  compound='left', width=9, command=self.add_cat)
        self.add_cat_but.grid(row=0, column=1, padx=5)

        self.add_art_frame = Labelframe(self.tools_frame, text='Добавить товар')
        self.add_art_frame.pack(pady=20)

        Label(self.add_art_frame, text='Наименование').grid(row=0, column=0, padx=5, pady=5)
        self.add_art_ent = Entry(self.add_art_frame, width=20, cursor='xterm')
        self.add_art_ent.grid(column=1, row=0, padx=5, pady=5)

        Label(self.add_art_frame, text='Стоимость').grid(row=1, column=0, padx=5, pady=5)
        self.add_sum_ent = Entry(self.add_art_frame, width=10, cursor='xterm')
        self.add_sum_ent.grid(column=1, row=1, padx=5, pady=5, sticky=W)
        self.edit_var = IntVar()
        self.edit_var.set(True)
        self.add_art_ch = Checkbutton(self.add_art_frame, text='Разрешить правки при добавлении продажи',
                                      variable=self.edit_var)
        self.add_art_ch.grid(row=2, column=0, padx=5, columnspan=2, sticky=W)

        self.add_art_but = Button(self.add_art_frame, text='Добавить', image=self.app.app.img['add_art'],
                                  compound='left', width=9, command=self.add_art)
        self.add_art_but.grid(row=3, column=0, padx=5, columnspan=2, pady=5)
        self.current_id = id

    def add_cat(self):
        """ Добавление категории """
        txt = self.add_cat_ent.get()
        if not txt:
            box.showerror(title='Ошибка', message='Вы должны ввести название категории!')
            self.win.deiconify()
            return
        self.app.app.db.execute('select max(id) from article')
        try:
            id = self.app.app.db.fetchall()[0][0] + 1
        except:
            id = 1
        self.app.app.db.execute('insert into article values (?,?,?,?,?,?,?,?)',
                                (id, txt, self.cur_dep + 1, self.current_id, 'stick', 1, 0, 0))
        self.app.app.con.commit()
        self.redraw()

    def add_art(self):
        """ Добавление товара """
        txt = self.add_art_ent.get()
        summa = self.add_sum_ent.get()

        if not txt:
            box.showerror(title='Ошибка', message='Вы должны ввести название товара!')
            self.win.deiconify()
            return
        try:
            summa = float(summa)
            if summa < 0: raise
        except:
            box.showerror(title='Ошибка', message='Не корректная сумма!')
            self.win.deiconify()
            return
        edit = self.edit_var.get()

        self.app.app.db.execute('select max(id) from article')
        try:
            id = self.app.app.db.fetchall()[0][0] + 1
        except:
            id = 1
        self.app.app.db.execute('insert into article values (?,?,?,?,?,?,?,?)',
                                (id, txt, self.cur_dep + 1, self.current_id, 'item', edit, summa, 0))
        self.app.app.con.commit()
        self.redraw()

    def buld_edit_frame(self, sel):
        """ Если щелкнули на товар или категорию то показываем фрейм редактирования """
        self.current_id = sel
        self.tools_frame.destroy()
        self.tools_frame = Frame(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2, sticky=N, pady=40, padx=5)

        self.app.app.db.execute('select name,type,sum,edit from article where id=?', (sel,))
        name, t, summa, edit = self.app.app.db.fetchall()[0]
        # если это товар
        if t == 'item':
            self.edit_frame = Labelframe(self.tools_frame, text='Редактировать')
            self.edit_frame.pack()

            Label(self.edit_frame, text='Наименование').grid(row=0, column=0, padx=5, pady=5)
            self.add_art_ent = Entry(self.edit_frame, width=20, cursor='xterm')
            self.add_art_ent.grid(column=1, row=0, padx=5, pady=5)

            Label(self.edit_frame, text='Стоимость').grid(row=1, column=0, padx=5, pady=5)
            self.add_sum_ent = Entry(self.edit_frame, width=10, cursor='xterm')
            self.add_sum_ent.grid(column=1, row=1, padx=5, pady=5, sticky=W)
            self.edit_var = IntVar()
            self.edit_var.set(edit)
            self.add_art_ch = Checkbutton(self.edit_frame, text='Разрешить правки при добавлении продажи',
                                          variable=self.edit_var)
            self.add_art_ch.grid(row=2, column=0, padx=5, columnspan=2, sticky=W)

            self.add_art_but = Button(self.edit_frame, text='Сохранить', image=self.app.app.img['save'],
                                      compound='left', width=9, command=self.edit_art)
            self.add_art_but.grid(row=3, column=0, padx=5, columnspan=2, pady=5)
            self.add_sum_ent.insert(END, summa)
            self.add_art_ent.insert(END, name)
        # или если категория...
        else:
            self.edit_frame = Labelframe(self.tools_frame, text='Редактировать')
            self.edit_frame.pack()

            Label(self.edit_frame, text='Категория').grid(row=0, column=0, padx=5, pady=5)
            self.add_art_ent = Entry(self.edit_frame, width=20, cursor='xterm')
            self.add_art_ent.grid(column=1, row=0, padx=5, pady=5)

            self.add_art_but = Button(self.edit_frame, text='Сохранить', image=self.app.app.img['save'],
                                      compound='left', width=9, command=self.edit_cat)
            self.add_art_but.grid(row=3, column=0, padx=5, columnspan=2, pady=5)

            self.add_art_ent.insert(END, name)

        self.del_but = Button(self.tools_frame, text='Удалить', image=self.app.app.img['delete'], compound='left',
                              width=9, command=self.del_art)
        self.del_but.pack(pady=20)

        self.app.app.db.execute('select * from article where parent=?', (sel,))
        if self.app.app.db.fetchall():
            self.del_but['state'] = 'disable'

    def edit_art(self):
        """ Сохраняем измененный товар """
        txt = self.add_art_ent.get()
        summa = self.add_sum_ent.get()

        if not txt:
            box.showerror(title='Ошибка', message='Вы должны ввести название товара!')
            self.win.deiconify()
            return
        try:
            summa = float(summa)
            if summa < 0: raise
        except:
            box.showerror(title='Ошибка', message='Не корректная сумма!')
            self.win.deiconify()
            return
        edit = self.edit_var.get()
        self.app.app.db.execute('update article set name=?, sum=?, edit=? where id=?',
                                (txt, summa, edit, self.current_id))
        self.app.app.con.commit()
        self.redraw()

    def del_art(self):
        """ Удаляем товар или категорию"""
        self.app.app.db.execute('delete from article where id=?', (self.current_id,))
        self.app.app.con.commit()
        self.build_tree()
        self.tools_frame.destroy()
        self.tools_frame = Labelframe(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2)

    def edit_cat(self):
        """ Сохраняем измененную категорию """
        txt = self.add_art_ent.get()

        if not txt:
            box.showerror(title='Ошибка', message='Вы должны ввести название товара!')
            self.win.deiconify()
            return

        self.app.app.db.execute('update article set name=? where id=?', (txt, self.current_id))
        self.app.app.con.commit()
        self.redraw()

    def redraw(self):
        """ Перерисовывает дерево элементов, сохраняя текущее выделение """
        c = None
        self.build_tree()
        for x in self.node_list:
            if self.node_list[x] == self.current_id: c = x

        self.tools_frame.destroy()
        self.tools_frame = Labelframe(self.win)
        self.tools_frame.grid(row=0, column=2, rowspan=2)
        if c <> None:
            self.tree.see(c)
            self.tree.selection_set(c)

        try:
            self.buld_edit_frame(self.current_id)
        except IndexError:
            pass
