# -*- coding: utf-8 -*-

from Tkinter import *

from calendar import setfirstweekday, monthcalendar


class TkCalendar(Frame):
    def __init__(self, master, y, m, update_var, us=0, command=None):
        self.command = command
        self.no_out = None
        Frame.__init__(self, master, bd=2, relief=GROOVE)
        self.update_v = update_var
        self.year = y
        self.month = m
        self.c_month = m
        self.date = StringVar()

        if us:
            self.dayArray = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
            self.col = 0
            setfirstweekday(6)
        else:
            self.dayArray = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            self.col = 6

        f = Frame(self)
        f.pack(fill=X)
        Button(f,
               text='<',
               command=self.__decrease,
               relief=RAISED).pack(side=LEFT)
        self.lbl = Label(f, text="%.2i.%i" % (self.month, self.year), font=('bold', 16))
        self.lbl.pack(side=LEFT, padx=12)
        Button(f,
               text='>',
               command=self.__increase,
               relief=RAISED).pack(side=RIGHT)

        self.c = Canvas(self,
                        width=140, height=135,
                        bg='white', bd=2, relief=GROOVE, cursor='hand2')
        self.c.bind('<1>', self.__click)

        self.c.pack()
        self.__fill_canvas()

    def __fill_canvas(self):
        m = monthcalendar(self.year, self.month)

        for col in range(len(m[0])):
            for row in range(len(m)):
                if m[row][col] == 0:
                    pass
                else:
                    if col == self.col:
                        self.c.create_text(
                            col * 20 + 12, row * 20 + 30,
                            text="%2i" % m[row][col], fill='red', tags='day', font=('normal', 10))
                    else:
                        tag = self.c.create_text(
                            col * 20 + 12, row * 20 + 30,
                            text="%2i" % m[row][col], tags='day', font=('normal', 10))
                        if m[row][col] == int(self.update_v.get().split('-')[2]) and self.c_month == self.month:
                            self.c.itemconfigure(tag, font=('bold', 14), fill='#4D7228')

        x = 12
        y = 10
        for i in self.dayArray:
            self.c.create_text(x, y, text=i, fill='blue', tags='day', font=('normal', 10))
            x += 20
        self.c.tag_bind("day", "<Enter>", self.fn_on_mouse_over)
        self.c.tag_bind("day", "<Leave>", self.fn_out_mouse_over)

    def fn_on_mouse_over(self, event):
        self.c.itemconfigure(CURRENT, font=('bold', 14), fill='black')

        # self.c.move(CURRENT, -1, -1)
        self.c.update()

    def fn_out_mouse_over(self, event):

        if not self.c.find_below(CURRENT) == self.no_out:
            self.c.itemconfigure(CURRENT, font=('normal', 10), fill='black')
        # self.c.move(CURRENT, 1,1)
        self.c.update()

    def __decrease(self):
        self.c.delete('day')
        if self.month == 1:
            self.year -= 1
            self.month = 12
        else:
            self.month -= 1
        self.lbl.configure(text="%.2i.%i" % (self.month, self.year))
        self.__fill_canvas()

    def __increase(self):
        self.c.delete('day')
        if self.month == 12:
            self.year += 1
            self.month = 1
        else:
            self.month += 1
        self.lbl.configure(text="%.2i.%i" % (self.month, self.year))
        self.__fill_canvas()

    def __click(self, event):
        x = self.c.find_closest(event.x, event.y)[0]
        self.c.itemconfigure(CURRENT, font=('bold', 14), fill='black')
        self.no_out = self.c.find_below(CURRENT)
        for y in self.c.find_all():
            self.c.itemconfigure(y, font=('normal', 10), fill='black')
        self.c.itemconfigure(CURRENT, font=('bold', 14), fill='#4D7228')
        try:
            day = self.c.itemcget(x, 'text')
            self.date.set("%i-%.2i-%.2i" % (self.year, self.month, int(day)))
            self.update_v.set(self.date.get())
            self.c_month = self.month
            # вызываем....
            self.command.__call__(self.date.get())
        except:
            pass


if __name__ == '__main__':
    from time import localtime

    year, month = localtime()[0:2]
    root = Tk()
    date = StringVar()


    def some_function(date_):  # эта функция будет вызываться при щелкании на дату...
        print date_


    # вводим дополнительный пераметр command
    c = TkCalendar(root, year, month, date, command=some_function)
    c.pack()

    root.mainloop()
