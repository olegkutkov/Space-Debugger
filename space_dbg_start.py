#!/usr/bin/env python3
#
#   Copyright 2023  Oleg Kutkov <contact@olegkutkov.me>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.  
#
#vim:
#set expandtab
#set tabstop=4


import os
import sys
import subprocess
import platform
import tkinter as tk
import tkinter.ttk as ttk
import sv_ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import gettext
import tempfile

gettext.bindtextdomain('space-debugger', './locales')
gettext.textdomain('space-debugger')

_ = gettext.gettext

def run_space_debugger_with_data(json_file_path, flags=''):
    run_args = []

    if os.name == 'nt':
        run_args.append('space_dbg.exe')
    else:
        run_args.append('python3')
        run_args.append(os.path.join(os.getcwd()) + '/' + 'space_dbg.py')

    run_args.append('-f')
    run_args.append(json_file_path)

    if flags != '':
        run_args.append(flags)

    proc = None

    try:
        proc = subprocess.Popen(run_args)
    except Exception as err:
        messagebox.showerror(_('Failed to run Space Debugger'), err)

    if proc is None:
        return

    proc.communicate(input='\n')

class JsonInputWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('600x400')
        self.title(_('Paste debug data JSON text'))

        p = tk.PhotoImage(file = 'resources/icons/space_debugger_icon.png')
        self.iconphoto(False, p)

        self.resizable(False, False)

        self.text_box = tk.Text(self)

        self.text_box.place(x=0, y=0, width=588, height=350)

        self.vertical_scroll = tk.Scrollbar(self, orient='vertical', command=self.text_box.yview)

        self.text_box.configure(yscrollcommand=self.vertical_scroll.set)

        self.vertical_scroll.pack(side=tk.RIGHT, fill='y')

        self.ok_btn = ttk.Button(self, text=_('Ok'), command=lambda: self.ok_pressed())
        self.ok_btn.place(x=200, y=360, height=30, width=120)

        self.cancel_btn = ttk.Button(self, text=_('Cancel'), command=self.destroy)
        self.cancel_btn.place(x=310, y=360, height=30, width=120)

    def store_data_to_tmp(self, data):
        if not len(data):
            return None

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(data.encode())
        tmp_file_path = tmp.name
        tmp.close()

        return tmp_file_path

    def ok_pressed(self):
        tmp_file_path = self.store_data_to_tmp(self.text_box.get('1.0','end-1c'))

        if tmp_file_path is not None:
            run_space_debugger_with_data(tmp_file_path, '-r')
            self.quit()

class SpaceDebuggerStart(tk.Tk):
    def __init__(self):
        super().__init__()

        sv_ttk.set_theme("light")        

        self.title(_('Space Debugger: select data source'))

        p = tk.PhotoImage(file = 'resources/icons/space_debugger_icon.png')

        self.iconphoto(False, p)

        self.geometry('')
        self.resizable(False, False)

        self.file_open_btn = ttk.Button(self, text=_('Open JSON file'), \
                command=lambda: self.run_open_file(), width=20)

        self.file_open_btn.grid(row=0, column=0, padx=10, pady=20)

        self.text_input_btn = ttk.Button(self, text=_('Paste JSON text'), \
                command=lambda: self.run_paste_text(), width=20)
        self.text_input_btn.grid(row=0, column=1, padx=10, pady=20)

    def run_net_fetch(self):
        print('net fetch')

    def run_open_file(self):
        file_types = ((_('JSON files'), '*.json'), (_('All files'), '*.*'))
        filename = fd.askopenfilename(title=_('Select JSON file'), filetypes=file_types)
        if len(filename) > 0:
            run_space_debugger_with_data(filename)
            self.quit()

    def run_paste_text(self):
        json_win = JsonInputWindow(self)
        json_win.grab_set()
       
if __name__ == "__main__":
    space_dbg_start = SpaceDebuggerStart()
    space_dbg_start.mainloop()

