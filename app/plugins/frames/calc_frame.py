# -*-coding:utf-8-*-
# плагин, запускающий калькулятор
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
import subprocess
import sys

name = 'Калькулятор'
frame = 0
icon = 'calc'


class Plugin:
    def __init__(self, app):
        self.app = app

    def run(self):
        if sys.platform == 'win32':
            calc_app = "calc.exe"
        else:
            calc_app = "kcalc"

        if hasattr(self.app, "calc_proc"):
            self.app.calc_proc.terminate()
        self.app.calc_proc = subprocess.Popen(calc_app)
