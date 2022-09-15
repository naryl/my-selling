# coding:utf-8
# вспомогательный класс для актов и товарных чеков

import os
import tkFileDialog

from number_to_string import get_string_by_number
from xlsxtpl.writerx import BookWriter
from date_time import date_now, date_get, time_now, norm_date
import subprocess, platform


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

    def generate_act(self, payloads, xlsx_tpl, _date, _time, art_id, doctype, cur_frame):
        """
        Generate and save act of completion to xlsx file
        from given xlsx template
        param: payloads List of Dict
        param: xlsx_tpl String path to template file
        """
        try:
            path = self.sets.save_pdf
        except AttributeError:
            path = ''

        self.db.execute('select id from acts where date=? and file like ?', (_date, '%'+doctype+'%'))
        num = len(self.db.fetchall()) + 1
        payloads[0]['act_number'] = num

        filename = '%s_n%s_%s.xlsx' % (doctype, num, _date)
        f = tkFileDialog.asksaveasfilename(initialdir=path, initialfile=filename, master=cur_frame)
        if not f:
            return
        f = f.replace('\\', '/')
        self.sets.save_pdf = '/'.join(f.split('/')[:-1])

        self.db.execute('insert into acts (date,time,art_id,num,file)'
                                'values (?,?,?,?,?)',
                                (_date, _time, art_id, num, f))
        self.con.commit()

        writer = BookWriter(xlsx_tpl)
        writer.jinja_env.globals.update(dir=dir, getattr=getattr)

        writer.render_book(payloads=payloads)
        writer.save(f)
        self.start_file_app(f)

