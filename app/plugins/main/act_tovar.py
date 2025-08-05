# coding:utf-8
# вспомогательный класс для актов и товарных чеков

import os
import tkinter.filedialog as tkFileDialog

from xlsxtpl.writerx import BookWriter
import subprocess, platform
from glob import glob
import tkinter.messagebox as box


class Act:
    def __init__(self, app):
        self.db = app.db
        self.con = app.con
        self.sets = app.sets
        # self.app = app

    def start_file_app(self, filepath):
        """
        Runs a file in a native app for specific platform
        """
        isWindows = platform.system() == 'Windows'
        isDarwin = platform.system() == 'Darwin'
        isLinux = platform.system() == 'Linux'

        if isDarwin:       # macOS
            subprocess.call(('open', filepath))

        elif isWindows:    # Windows
            os.startfile(filepath)

        elif isLinux:      # linux variants
            subprocess.call(('xdg-open', filepath))


    def del_tmp_files(self, path, pattern):
        """
        Remove files pattern match
        param: path Directory
        param: pattern File mask
        """
        fileList = glob(os.path.join(path, pattern))
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                box.showerror(title='Ошибка', message='Невозможно удалить файл: %s' % filePath)


    def generate_act(self, payloads, xlsx_tpl, _date, _time, art_id, doctype, cur_frame):
        """
        Generate and save act of completion to xlsx file
        from given xlsx template
        param: payloads List of Dict
        param: xlsx_tpl String path to template file
        """
        try:
            path = self.sets.save_pdf
            if not os.path.exists(path) or not os.path.isdir(path):
                box.showerror("Мои Продажи", f"Не могу сохранить Акт в папку {path}. Пожалуйста, выберите другую.")
                path = tkFileDialog.askdirectory(mustexist=False, title="Укажите папку для сохранения Актов")
                if not os.path.isdir(path):
                    os.makedirs(path, exist_ok=True)
                self.sets.save_pdf = path

            allow_actfile_save = int(self.sets.allow_actfile_save)
            allow_tmpfile_del = int(self.sets.allow_tmpfile_del)
        except AttributeError:
            path = ''
            allow_actfile_save = int(getattr(self.sets, 'allow_actfile_save', True))
            allow_tmpfile_del = int(getattr(self.sets, 'allow_tmpfile_del', False))

        self.db.execute('select id from acts where date=? and file like ?', (_date, '%'+doctype+'%'))
        num = len(self.db.fetchall()) + 1
        payloads[0]['act_number'] = num

        if allow_tmpfile_del == 1:
            sufix = _date+'.tmp'
            self.del_tmp_files(path, '*.tmp.xlsx')
        else:
             sufix = _date   

        filename = '%s_n%s_%s.xlsx' % (doctype, num, sufix)

        if allow_actfile_save == 1:
            f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename, master=cur_frame)
        else:
            f = os.path.join(path, filename)

        if not f:
            return
        f = f.replace('\\', '/')

        self.db.execute('insert into acts (date,time,art_id,num,file)'
                                'values (?,?,?,?,?)',
                                (_date, _time, art_id, num, f))
        self.con.commit()

        writer = BookWriter(xlsx_tpl)
        writer.jinja_env.globals.update(dir=dir, getattr=getattr)

        writer.render_book(payloads=payloads)
        writer.save(f)
        self.start_file_app(f)

