# coding:utf-8
# главное  окно приложения
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
import os
import time
import tkMessageBox as box
from Tkinter import *

from MultiListbox import MultiListbox
from edit_log import Log
from ttk import *

from number_to_string import get_string_by_number
from act_tovar import Act


def date_now():
    t = time.localtime()
    return time.strftime('%Y-%m-%d', t)


def time_now():
    t = time.localtime()
    return time.strftime('%H:%M:%S', t)


class Main:
    def __init__(self, app):
        self.app = app
        self.log = Log(self.app)
        self.cat_id = -1
        self.init_add()
        self.init_tools()
        self.lst = MultiListbox(self.app.win, (
            ('Время', self.app.sets.col_width_main_time),
            ('Отдел', self.app.sets.col_width_main_dep),
            ('Товар -> Услуги', self.app.sets.col_width_main_art),
            ('Сумма', self.app.sets.col_width_main_sum),
            ('Кол.во', self.app.sets.col_width_main_rate),
            ('Итог', self.app.sets.col_width_main_total),
            ('Продавец', self.app.sets.col_width_main_user)),
                                font=('bold', 13))
        self.lst.pack(fill=BOTH, expand=1)
        self.update_list()
        self.build_tree()
        self.init_plugins()

    def init_add(self):
        """Верхняя панель с добавлением продажи """
        self.add_f = LabelFrame(self.app.win, text='Продажа')
        self.add_f.pack(expand=YES, fill=X, anchor=N)
        self.init_deps()
        Style().configure("mini2.TButton", font=('bold', 11))
        Style().configure("mini.TButton", font=('bold', 7))
        Style().configure("maxi.TButton", font=('normal', 20))

        # Сохранение по <Enter>
        def return_handler(_):
            min_size = 1
            if len(self.sum_ent.get()) >= min_size:
                self.add_handler()

        self.cat_but = Button(self.add_f, style='mini.TButton', image=self.app.img['dep_db'], compound='top',
                              text='Товары', command=self.cat_handler)
        self.cat_but.pack(side='left')
        Style().configure("TButton", font=('bold', 13))
        self.cat_but.bind("<Return>", return_handler)

        self.clear_but = Button(self.add_f, image=self.app.img['clear'], compound='image', command=self.clear_handler)
        self.clear_but.pack(side='right')

        self.add_but = Button(self.add_f, text='Добавить', image=self.app.img['add'], compound='left',
                              command=self.add_handler)
        self.add_but.pack(side='right')
        self.add_but.bind("<Return>", return_handler)

        self.total_var = StringVar()
        self.total_ent = Entry(self.add_f, width=8, font=('bold', 20), cursor='xterm',
                               state="readonly", textvariable=self.total_var)
        self.total_ent.pack(side='right', padx=5)

        self.rate_var = StringVar()
        self.rate_v = Combobox(self.add_f, width=6, font=('bold', 16),
                               textvariable=self.rate_var)
        self.rate_v.set('1')
        self.rate_v.pack(side='right', padx=10)
        self.rate_v['values'] = range(1, 101)
        self.rate_v.bind("<Return>", return_handler)
        self.rate_var.trace('w', self.update_total)

        self.sum_var = StringVar()
        self.sum_ent = Entry(self.add_f, width=6, font=('bold', 20), cursor='xterm',
                             textvariable=self.sum_var)
        self.sum_ent.pack(side='right')
        self.sum_ent.bind("<Return>", return_handler)
        self.sum_var.trace('w', self.update_total)

        # act of completion & tovar chek
        self.act_tovar_f = Frame(self.add_f)
        self.act_tovar_f.pack(fill=X, side='right')

        self.act_print_var = IntVar()
        act_but_text_var = str(getattr(self.app.sets, 'act_but_text', 'Act').encode('utf-8'))
        self.act_print_chk = Checkbutton(self.act_tovar_f, variable=self.act_print_var, onvalue=1, offvalue=0, 
                command=self.clear_tovar_print_chk)
        self.act_print_chk.grid(row=0, column=1, padx=2, pady=2, sticky=NW)
        Label(self.act_tovar_f, text=act_but_text_var).grid(row=0, column=0, padx=2, pady=2, sticky=NW)

        self.tovar_print_var = IntVar()
        tovar_but_text_var = str(getattr(self.app.sets, 'tovar_but_text', 'Check').encode('utf-8'))
        self.tovar_print_chk = Checkbutton(self.act_tovar_f, variable=self.tovar_print_var, onvalue=1, offvalue=0, 
                command=self.clear_act_print_chk)
        self.tovar_print_chk.grid(row=1, column=1, padx=2, pady=2, sticky=NW)
        Label(self.act_tovar_f, text=tovar_but_text_var).grid(row=1, column=0, padx=2, pady=2, sticky=NW)

        self.dep_name = Text(self.add_f, height=2, font=(15))
        self.dep_name.pack(side='left', padx=10, fill=BOTH, pady=5)
        self.dep_name.bind("<Tab>", self.focus_next_widget)
        self.dep_name.bind("<Return>", return_handler)

        # Меняем порядок перехода при нажатии <Tab>
        new_order = (self.otd, self.cat_but, self.dep_name, self.act_print_chk, self.tovar_print_chk, self.sum_ent, self.rate_v, self.add_but, self.clear_but)
        for widget in new_order:
            widget.lift()

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return ("break")

    def update_total(self, _1, _2, _3):
        rate_val = self.rate_v.get()
        sum_val = self.sum_ent.get()
        if self.is_number(rate_val) and self.is_number(sum_val):
            total = float(rate_val) * float(sum_val)
            self.total_var.set('{0:.2f}'.format(total))
        else:
            self.total_var.set('')

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def init_deps(self):
        """Инициализация меню с отделами """
        self.deps = []
        self.app.db.execute('select name from dep')
        for n, name in enumerate(self.app.db.fetchall()):
            self.deps.append('%s %s' % (n + 1, name[0]))

        self.cur_dep = 0
        self.dep_str = StringVar()
        self.dep_str.set(self.deps[0])
        Style().configure("TMenubutton", font=('bold', 13))
        self.otd = Menubutton(self.add_f, textvariable=self.dep_str,
                              width=19, image=self.app.img['deps'], compound='left')
        self.otd.pack(pady=10, side='left', padx=10)
        self.otd.menu = Menu(self.otd,
                             font=("bold", 13), bg='white', relief='flat', tearoff=0)
        for n, x in enumerate(self.deps):
            if len(x) > 3:
                self.otd.menu.add_command(label=x.ljust(25), command=lambda z=n: self.deps_hand(z))
        self.otd['menu'] = self.otd.menu

    def deps_hand(self, n):
        """Вызывается при щелчке на отдел """
        self.cur_dep = n
        self.dep_str.set(self.deps[n])
        self.cat_id = -1
        self.build_tree()

    def update_list(self):
        """ Обновляется список текущих продаж  """
        self.lst.delete(0, END)
        self.app.db.execute('select time,dep,article,sum,rate,name,art_id,edit from income where date=?', (date_now(),))
        for x in self.app.db.fetchall():
            out = list(x)
            if out[7] <> 0:
                out[1] = str(out[1]) + ' (≈)'
            if out[6] <> -1:
                out[1] = str(out[1]) + ' →'

            out.insert(5, round(x[3] * x[4], 2))
            self.lst.insert(END, out)
        self.lst.see(END)


    def clear_handler(self):
        """ Вызывается при нажатии "очистить" """
        self.dep_name['state'] = 'normal'
        self.sum_ent['state'] = 'normal'

        self.dep_name.delete(0.0, END)

        self.sum_ent.delete(0, END)
        self.rate_v.set('1')
        self.cat_id = -1

        # clear act print checkbutton
        self.act_print_var.set(False)
        self.tovar_print_var.set(False)


    def clear_act_print_chk(self):
        self.act_print_var.set(False)


    def clear_tovar_print_chk(self):
        self.tovar_print_var.set(False)


    def add_handler(self):
        """ Добавление продажи """
        try:
            razves = ast.literal_eval(self.app.sets.razves)[self.cur_dep]
        except AttributeError:
            razves = 0

        try:
            sum = float(self.sum_ent.get().replace(',', '.'))
            total = float(self.total_ent.get().replace(',', '.'))
        except:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            return
        try:
            if razves:
                rate = float(self.rate_v.get().replace(',', '.'))
            else:
                rate = int(self.rate_v.get().replace(',', '.'))
        except:
            box.showerror(title='Ошибка', message='Не верное количество!')
            return
        if sum <= 0:
            box.showerror(title='Ошибка', message='Не верная сумма!')
            return
        if rate <= 0:
            box.showerror(title='Ошибка', message='Не верное количество!')
            return
        txt = self.dep_name.get('0.0', END).replace('\r', '').replace('\n', ' ').replace('\t', ' ')

        if self.cat_id <> -1:
            self.app.db.execute('select warning from dep where id=?', (int(self.cur_dep) + 1,))
            k = self.app.db.fetchall()[0][0]
            if k > 0:
                self.app.db.execute('select rate from article where id=?', (self.cat_id,))
                if self.app.db.fetchall()[0][0] - rate < 0:
                    if k == 1:
                        if not box.askyesno(title='Внимание!',
                                            message='Количества товара не достаточно для продажи.\nСохранить продажу все равно?'): return
                    else:
                        box.showerror(title='Ошибка', message='Товара в наличии недостаточно для продажи')
                        return

        dt, tm = date_now(), time_now()
        self.app.db.execute('insert into income values (?,?,?,?,?,?,?,?,0)',
                            (dt, tm, int(self.cur_dep) + 1, txt, self.cat_id, sum, rate, self.app.user.decode('utf-8')))

        # forming payload for act print
        act_print = self.act_print_var.get()
        tovar_print = self.tovar_print_var.get()
        if act_print == 1 or tovar_print == 1:
            art_id = -1
            act_info = {
                    'act_number': 0,
                    'act_date': dt,
                    'p_num': 1,
                    'service_name': txt,
                    'garanty': u'3 года',
                    'q': rate,
                    'price': sum,
                    'amount': total,
                    'total': total,
                    'total_as_text': get_string_by_number(total),
                    }

            act_payloads = [act_info]
            self.act = Act(self.app)

        if self.cat_id <> -1:
            self.app.db.execute('select rate from article where id=?', (self.cat_id,))
            rate = self.app.db.fetchall()[0][0] - rate
            self.app.db.execute('update article set rate=? where id=?', (rate, self.cat_id,))
            art_id = self.cat_id

        self.app.con.commit()
        self.clear_handler()

        cashbox_value = float(self.app.sets.cashbox)
        cashbox_value += sum
        self.app.sets.cashbox = cashbox_value

        self.update_list()
        self.build_tree()
        self.update_tools()


        if act_print == 1:
            self.act.generate_act(act_payloads, 'app/templates/act_tpl.xlsx', dt, tm, art_id, 'act', self.add_f)

        if tovar_print == 1:
            self.act.generate_act(act_payloads, 'app/templates/tovar_tpl.xlsx', dt, tm, art_id, 'tovar', self.add_f)

        self.init_add_plugins(dt, tm)


    def build_tree(self):
        """ Рекурсивное построение дерева товаров """
        self.popup = Menu(self.app.win, tearoff=0, font=('normal', 12))

        def get_menu(id):
            self.app.db.execute('select id,name,type from article where dep=? and parent=? order by type DESC, name',
                                (self.cur_dep + 1, id,))
            popup = Menu(self.app.win, tearoff=0, font=('normal', 12))
            for x in self.app.db.fetchall():
                if x[2] == 'item':
                    popup.add_command(label=x[1], command=lambda z=x[0]: self.command_handler(z))
                else:
                    popup.add_cascade(label=x[1], menu=get_menu(x[0]))
            return popup

        # Сначала  проходимся по товарам в корне
        self.app.db.execute('select id,name,type from article where dep=? and parent=-1 order by type DESC, name',
                            (self.cur_dep + 1,))

        for x in self.app.db.fetchall():
            if x[2] == 'item':
                self.popup.add_command(label=x[1], command=lambda z=x[0]: self.command_handler(z))
            else:
                self.popup.add_cascade(label=x[1], menu=get_menu(x[0]))

    def command_handler(self, id):
        """ Вызывается при щелчке на наименование товара """
        self.cat_id = id
        t = []
        flag = True
        # строится полное название товара, включая подкатегории
        self.app.db.execute('select name,edit,sum,parent from article where id=?', (id,))
        s = self.app.db.fetchall()[0]
        par = s[3]
        t.append(s[0])
        if par == -1:
            flag = 0
        while flag:
            self.app.db.execute('select name,parent from article where id=?', (par,))
            rez = self.app.db.fetchall()[0]
            if rez[1] == -1:
                t.append(rez[0])
                flag = False
            else:
                t.append(rez[0])
                par = rez[1]
        # и заполняются поля в продаже
        cat_lst = ' > '.join(t[::-1])
        self.dep_name['state'] = 'normal'
        self.dep_name.delete(0.0, END)
        self.dep_name.insert(0.0, cat_lst)
        if s[1] == 0:
            self.dep_name['state'] = 'disable'
        self.sum_ent['state'] = 'normal'
        self.sum_ent.delete(0, END)
        self.sum_ent.insert(0, s[2])
        if s[1] == 0:
            self.sum_ent['state'] = 'disable'
        # переход на ввод суммы
        self.sum_ent.focus()
        self.sum_ent.select_range(0, END)
        self.sum_ent.icursor(END)

    def cat_handler(self):
        self.popup.tk_popup(self.cat_but.winfo_rootx() + 30, self.cat_but.winfo_rooty() + 55, 0)

    def init_tools(self):
        """ Формируется нижняя панель с подитогом """
        self.tools_f = Frame(self.app.win)
        self.tools_f.pack(fill=BOTH, side='bottom', expand=1)
        self.k = LabelFrame(self.tools_f, text='Подитог')
        self.k.pack(side='left')
        self.income_all = StringVar()
        self.income_all.set('Доход')
        self.outcome_all = StringVar()
        self.outcome_all.set('Расход')
        self.all_all = StringVar()
        self.all_all.set('Остаток')
        self.cashbox_all = StringVar()
        self.cashbox_all.set('Касса')
        Label(self.k, textvariable=self.income_all, font=('bold', 12)).grid(row=0, column=0, columnspan=2, sticky=NW)
        Label(self.k, textvariable=self.outcome_all, font=('bold', 12)).grid(row=1, column=0, columnspan=2, sticky=NW)
        Label(self.k, textvariable=self.all_all, font=('bold', 12)).grid(row=2, column=0, columnspan=2, sticky=NW)
        self.cashbox_lbl = Label(self.k,
                                 textvariable=self.cashbox_all,
                                 font=('bold', 12))
        self.cashbox_lbl.grid(row=3, column=0, columnspan=2, sticky=NW)
        self.scr1 = Scrollbar(self.k, orient=VERTICAL)
        self.scr1.grid(row=4, column=1, sticky=N + S)
        self.list_1 = Listbox(self.k, width=30, height=5,
                              font=("Arial", 10, "bold"),
                              yscrollcommand=self.scr1.set)
        self.list_1.grid(row=4, column=0)
        self.scr1['command'] = self.list_1.yview

        self.update_tools()

    def update_tools(self):
        """ Считается подитог """
        deps = {}
        deps_sum = {}
        self.app.db.execute('select name from dep')
        for n, name in enumerate(self.app.db.fetchall()):
            if name: deps_sum[n + 1] = 0

        self.app.db.execute('select dep,sum,rate from income where date=?', (date_now(),))
        out = self.app.db.fetchall()
        in_all = 0
        for x in out:
            in_all += float(x[1]) * float(x[2])
            deps_sum[x[0]] += float(x[1]) * float(x[2])
        self.income_all.set('Доход: %s' % (in_all))
        self.list_1.delete(0, END)

        for x in deps_sum:
            if deps_sum[x]:
                self.list_1.insert(END, self.deps[x - 1] + u'→ ' + str(deps_sum[x]))

        self.app.db.execute('select sum from outcome where date=?', (date_now(),))
        out = self.app.db.fetchall()
        out_all = 0
        for x in out:
            out_all += float(x[0])
        self.outcome_all.set('Расход: %s' % (out_all))
        self.all_all.set('Остаток: %s' % (in_all - out_all))
        cashbox_value = self.app.sets.cashbox
        cashbox_value_str = str(cashbox_value)
        self.cashbox_all.set('Касса: %s' % (cashbox_value_str))
        cashbox_color = 'red' if cashbox_value > 1000.0 else 'black'
        self.cashbox_lbl.config(foreground=cashbox_color)

    def log_at_work(self):
        """ Добавить запись о нажатии кнопки "На месте" """
        self.log.at_work(date_now(), time_now(), self.app.user.decode('utf-8'))
        self.at_work_button.config(state='disabled')
        self.refresh_at_work_btn(date_now())

    def check_at_work(self):
        """ Проверить, есть ли запись о присутствии за сегодня для пользователя """
        user = self.app.user.decode('utf-8')
        date = date_now()
        self.app.db.execute('select event from edit_log where title=? and event=? and date=?',
                            (u'Пользователь на месте', user, date))
        res = self.app.db.fetchall()
        return len(res) > 0

    def refresh_at_work_btn(self, date):
        try:
            cur_date = date_now()
            if date != cur_date:
                self.at_work_button.config(state='enabled')
            else:
                self.app.root.after(1800000, lambda: self.refresh_at_work_btn(date))
        except TclError:
            pass

    def init_plugins(self):
        """ Панель с плагинами """
        plugins = self.load_plugins()

        # Загружаем список доступных плагинов для пользователя
        self.app.db.execute('select caps from users where name=?', (self.app.user.decode('utf-8'),))
        caps_str = self.app.db.fetchall()[0][0].replace('\n', ' ').replace('\r', '')
        caps = ast.literal_eval(caps_str)

        # Проверяем, нужно ли отображать табы (если все плагины с одного таба - не нужно)
        frames = [plugin['fr'] for plugin in plugins if plugin['name'] in caps or self.app.user == 'Администратор']
        show_tabs = not (len(set(frames)) <= 1)

        self.t_plugins_frame = LabelFrame(self.tools_f, text='Действия')
        self.t_plugins_frame.pack(fill=BOTH, side='left', expand=1)
        if show_tabs:
            self.nb = Notebook(self.t_plugins_frame)
            self.nb.pack(fill=BOTH, expand=1, pady=5)

            self.plugins_frame = range(3)
            # 3 вкладки
            imgs = ['sale', 'dep_db', 'misc']
            for x, name in enumerate(['Продажи', 'Товар', 'Прочее']):
                self.plugins_frame[x] = Frame(self.t_plugins_frame)
                self.plugins_frame[x].pack(fill=BOTH, side='left', expand=1)
                self.nb.add(self.plugins_frame[x], text=name, padding=3, image=self.app.img[imgs[x]], compound='left')

        self.end_frame = Frame(self.tools_f)
        self.end_frame.pack(side='left')
        self.end_button = Button(self.tools_f, style='mini.TButton', text='      Сменить\nпользователя',
                                 image=self.app.img['people'], compound='top', command=self.app.change_user,
                                 cursor='hand2')
        self.end_button.pack(side='bottom', pady=10, padx=5)
        self.at_work_button = Button(self.tools_f, style='mini.TButton', text='На месте',
                                     image=self.app.img['check'], compound='top', command=self.log_at_work,
                                     cursor='hand2')
        self.at_work_button.pack(side='bottom', pady=10, padx=5)
        if self.check_at_work():
            self.at_work_button.config(state='disabled')
            self.refresh_at_work_btn(date_now())

        # тут начинается самое интересное :)
        row = [0, 0, 0]
        column = [0, 0, 0]
        self.plugin_list = []
        self.pl_buttons = {}
        for plugin in plugins:
            obj = plugin['obj']
            name = plugin['name']
            fr = plugin['fr']
            icon = plugin['icon']
            plugins_frame = self.plugins_frame[fr] if show_tabs else self.t_plugins_frame
            self.plugin_list.append(name)
            # проверяем, есть ли допуск юзера к плагину, или "Администратор"
            if name in caps or self.app.user == 'Администратор':
                # собственно добавляем кнопку
                self.pl_buttons[(row[fr], column[fr])] = Button(plugins_frame,
                                                                text=name.ljust(100), style='maxi.TButton',
                                                                image=self.app.img[icon], compound='left', width=23)
                self.pl_buttons[(row[fr], column[fr])].grid(row=row[fr], column=column[fr], sticky=NW, padx=5,
                                                            pady=2)
                self.pl_buttons[(row[fr], column[fr])]['command'] = lambda pl=obj: self.show_plugin(pl)
                column[fr] = column[fr] + 1
                if column[fr] > 2:
                    column[fr] = 0
                    row[fr] = row[fr] + 1

    @staticmethod
    def load_plugins():
        s = os.listdir('app/plugins/frames')

        plugins = []
        for x in s:
            if x.endswith('.py'):
                # импортируем, и получаем имя, название иконки, номер вкладки
                obj = __import__(x[:-3])
                name = getattr(obj, 'name')
                fr = getattr(obj, 'frame')
                if hasattr(obj, 'icon'):
                    icon = getattr(obj, 'icon')
                else:
                    icon = 'plugins'
                plugin = {'obj': obj, 'name': name, 'fr': fr, 'icon': icon}
                plugins.append(plugin)
        return plugins

    def show_plugin(self, obj):
        """ Вызывается при нажитию на кнопку плагина. Запускаем метод run плагина """
        cl = getattr(obj, 'Plugin')(self)
        cl.run()

    def init_add_plugins(self, dt, tm):
        """ Вызывается после добавления """
        s = os.listdir('app/plugins/income')
        for x in s:
            if x.endswith('.py'):
                obj = __import__(x[:-3])
                cl = getattr(obj, 'Plugin')(self, dt, tm)
