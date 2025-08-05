from tkinter import *

from app.plugins.ext_lib.ttk import *


class MultiListbox(Frame):
    def __init__(self, master, lists, font=('normal', 14), height=100, command=None):
        self.cl = command
        super().__init__(master)
        self.line = 1
        self.lists = []
        for l, w in lists:
            frame = Frame(self)
            frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED,
                  font=(10)).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,
                         relief=FLAT, exportselection=FALSE, font=font, height=height)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
            # Scroll in X11
            lb.bind('<Button-4>', lambda e, s=self: s._mouse_scroll(e.num, e.delta))
            lb.bind('<Button-5>', lambda e, s=self: s._mouse_scroll(e.num, e.delta))
        # Scroll in win32
        self.bind_all('<MouseWheel>', lambda e, s=self: s._mouse_scroll(e.num, e.delta))
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)
        frame = Frame(self)
        frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand'] = sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        if self.cl: self.cl()
        return 'break'

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'

    def _mouse_scroll(self, e_num, e_delta):
        delta = 0
        if e_num == 5 or e_delta < 0:
            delta = 1
        if e_num == 4 or e_delta > 0:
            delta = -1
        self._scroll(delta)
        return 'break'

    def _bound_to_mousewheel(self, _):
        self.bind_all('<MouseWheel>', lambda e, s=self: s._mouse_scroll(e.num, e.delta))

    def _unbound_to_mousewheel(self, _):
        self.unbind_all("<MouseWheel>")

    def _scroll(self, delta):
        self.line += delta
        if self.line < 0:
            self.line = 0
        if self.lists[0].yview()[1] >= 1.0 and delta > 0:
            self.line -= delta
        for l in self.lists:
            l.yview(self.line)

    def _update_line(self):
        top_part = self.lists[0].yview()[0]
        length = self.index(END)
        self.line = int(top_part * length)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)
        self._update_line()

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first, last))
        if last: return list(map(*([None] + result)))
        return result

    def index(self, index):
        return self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1
        self._update_line()

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)
        self._update_line()

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)

    def itemconfig(self, index, cnf=None, **kw):
        for l in self.lists:
            l.itemconfig(index, cnf, **kw)


def p(): pass


if __name__ == '__main__':
    tk = Tk()
    Label(tk, text='MultiListbox').pack()
    mlb = MultiListbox(tk, p, (('Subject', 40), ('Sender', 20), ('Date', 10)))
    for i in range(1000):
        mlb.insert(END, ('Important Message: %d' % i, 'John Doe', '10/10/%04d' % (1900 + i)))
    mlb.pack(expand=YES, fill=BOTH)
    mlb.see(END)
    tk.mainloop()
