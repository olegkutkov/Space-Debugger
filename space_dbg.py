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


import sys
import os
import argparse
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from PIL import ImageTk,Image
import sv_ttk
import pyperclip
import gettext
import json
import dishy
import router
import device_app
import about

''' Load translation for a locale '''
''' Local dir is used to search and load .mo file '''
gettext.bindtextdomain('space-debugger', './locales')
gettext.textdomain('space-debugger')

_ = gettext.gettext

MIN_PYTHON = (3, 6)

if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

''' Main window implementation '''
class SpaceDebuggerMain(tk.Tk):
    def __init__(self, file_path, remove_file_on_exit):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.json_file = file_path
        self.remove_json_on_exit = remove_file_on_exit
        self.modules = {}

        ''' Configure window and widgets '''
        self.img_canvas_h = 210
        self.img_canvas_w = 210

        sv_ttk.set_theme("light")
        self.title('Space Debugger')
        self.geometry('')

        ''' Set window icon '''
        p = tk.PhotoImage(file = 'resources/icons/space_debugger_icon.png')
        self.iconphoto(False, p)

        self.load_json_data()
        self.read_json_data()

        top_tabs = ttk.Notebook(self)
        top_tabs.pack(pady=10, expand=True)

        self.tab_images = {}
        self.subtab_images = {}

        ''' Load data from modules and draw tabs '''
        for module in sorted(self.modules):
            ''' Create and configure tab frame '''
            module_object = self.modules[module]

            tab_frame = ttk.Frame(top_tabs)
            tab_frame.pack(fill='both', expand=True)
            tab_frame.columnconfigure(1, weight=1, minsize=200)
            tab_name = module_object.get_module_readable_name()

            main_data_frame = ttk.Frame(tab_frame)
            main_data_frame.grid(sticky="N", row=0, column=0, padx=20, pady=15)

            rc = 0
            params = {}

            if module_object.is_reachable():
                module_object.get_readable_params(params)

                for param in params:
                    self.display_params(main_data_frame, rc, param, params[param], 0, 0, 15, 0)
                    rc = rc + 1

                ''' Create canva with device image 
                    The image is resized to fit the window
                    But it's is clickable to see it full size
                '''
                canvas = tk.Canvas(tab_frame, width=self.img_canvas_w, height=self.img_canvas_h)
                canvas.grid(sticky="NE", row=0, column=1, padx=20, pady=20)

                ''' Store image data in the class field '''
                tab_image = module_object.get_device_image_file()
                self.tab_images[tab_name] = ImageTk.PhotoImage(Image.open(tab_image).resize((self.img_canvas_w, self.img_canvas_h), Image.Resampling.LANCZOS))

                canvas.create_image((0,0), anchor=tk.NW, image=self.tab_images[tab_name])

                ''' Bind image click event '''
                canvas.bind("<Button-1>", lambda event, arg=tab_image: self.show_image(arg))

                additional_params = {}

                ''' Load any additional data (if available) '''
                module_object.get_additional_data(additional_params)

                ''' Show additional data as subtabs '''
                if len(additional_params):
                    self.sub_tabs = ttk.Notebook(tab_frame)
                    self.sub_tabs.grid(sticky="NW", row=rc+1, column=0, padx=20, pady=0, columnspan=2)

                    rc = rc + 1

                    for add_param in additional_params:
                        ''' Load params '''
                        add_data_object = additional_params[add_param]
                        subtab_name = add_data_object[0]
                        subtab_params = add_data_object[1]

                        ''' Create subtab frame '''
                        subtab_frame = ttk.Frame(self.sub_tabs)
                        subtab_frame.columnconfigure(1, weight=1, minsize=380)
                        subtab_frame.pack(fill='both', expand=True, padx=10, pady=20)

                        irc = 0

                        for subtab_param in subtab_params:
                            subtab_param_name = subtab_param[0]
                            subtab_param_value = subtab_param[1]

                            ''' Magic word 'image_blob' - load image data and show in a third row '''
                            if subtab_param_name == 'image_blob':
                                if subtab_param_value != None:
                                    cv = tk.Canvas(subtab_frame, width=170, height=170)
                                    cv.grid(sticky="NE", row=0, column=2, rowspan=len(subtab_params))

                                    self.subtab_images[subtab_name] = ImageTk.PhotoImage(subtab_param_value.resize((170, 170), Image.Resampling.LANCZOS))
                                    cv.create_image((0,0), anchor=tk.NW, image=self.subtab_images[subtab_name])

                                    cv.bind("<Button-1>", lambda event, arg=subtab_param_value: self.show_image_mem(arg))
                            else:
                                self.display_params(subtab_frame, irc, subtab_param_name, subtab_param_value, 0, 1, 15, 1)

                            irc = irc + 1

                        self.sub_tabs.add(subtab_frame, text=subtab_name)


            self.display_status_line(module_object, tab_frame, rc)

            top_tabs.add(tab_frame, text=tab_name)

        top_tabs.pack(expand = 1, fill ="both")

    '''  Generic method showing param-value pair as two labels '''
    def display_params(self, frame, rc, param, value_label_txt, param_px, param_py, value_px, value_py):
        param_label_txt = param + ":" if param[0] != ' ' else param
        param_label = tk.Label(master=frame, text=param_label_txt)
        param_label.grid(sticky="W", row = rc, column=0, padx=param_px, pady=param_py)
        value_label = tk.Label(master=frame, text=value_label_txt, cursor="hand1")
        value_label.grid(sticky="W", row = rc, column=1, padx=value_px, pady=value_py)
        value_label.bind("<Button-1>", self.copy_on_click)

    ''' Display colored status line at the bottom '''
    def display_status_line(self, module_object, frame, rc):
        if module_object.is_sx_device():
            bg_color = '#ecf6ff'

            if module_object.is_reachable():
                if module_object.is_local_access():
                    bg_color = '#b4ffd0'
                else:
                    bg_color = '#6ad9ff'
            else:
                bg_color = '#ff6767'

            status_str = _('Reachable') + ': ' + module_object.yes_or_no(module_object.is_reachable()) + \
                            '\t' + _('Access type') + ': '  + module_object.get_access_type()

            status_label = tk.Label(master=frame, text=status_str, bg=bg_color)
            status_label.grid(sticky="news", row=rc+1, column=0, padx=0, pady=10, columnspan=2)

    ''' Copy content of the label clicked '''
    def copy_on_click(self, event):
        text = str(event.widget.cget('text'))
        pyperclip.copy(text)

        display = '"' + text + '"\n' + _('copied to clipboard')
        messagebox.showinfo(title=None, message=display)

    ''' Show image from path '''
    def show_image(self, arg):
        img = Image.open(arg)
        img.show()

    '''  Show image from memory blob '''
    def show_image_mem(self, arg):
        img = arg
        img.show()

    ''' Load Starlink JSON data '''
    def load_json_data(self):
        f = None
        self.json_data = None
        try:
            f = open(self.json_file)
            self.json_data = json.load(f)
        except:
            f = open(self.json_file, encoding="utf8")
            self.json_data = json.load(f)

        if f is None or self.json_data is None:
            messagebox.showerror(_('Failed to load JSON file'), err)
            sys.exit()

        f.close()

    ''' Read and parse Starlink JSON data '''
    def read_json_data(self):
        for entry in self.json_data:
            try:
                ''' Hacky way to keep tabs in required order '''
                if entry == dishy.DISH_KEY:
                    self.modules['A' + entry] = dishy.Dishy(self.json_data[dishy.DISH_KEY])
                elif entry == router.ROUTER_KEY:
                    self.modules['B' + entry] = router.Router(self.json_data[router.ROUTER_KEY])
                elif entry == device_app.DEVICE_KEY:
                    self.modules['C' + entry] = device_app.DeviceApp(self.json_data[device_app.DEVICE_KEY])
            except Exception as err:
                messagebox.showerror(_('Error'), err)
                sys.exit()

        ''' About tab should be last one '''
        self.modules['www'] = about.AboutApp()

    ''' We need close handler to remove tmp file when asked '''
    def on_closing(self):
        if self.remove_json_on_exit:
            os.remove(self.json_file)
        self.destroy()

''' Space Debugger entry point '''
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Space Debugger args')
    parser.add_argument('-f', '--file', help='Input JSON file')
    parser.add_argument('-r', '--remove-file-on-exit', required=False, action='store_true', help='Remove input JSON file on exit')

    args = parser.parse_args()

    if args.file is None:
        print("Please provide JSON file as an argument")
        sys.exit()
       
    space_dbg = SpaceDebuggerMain(args.file, args.remove_file_on_exit)
    space_dbg.mainloop()

