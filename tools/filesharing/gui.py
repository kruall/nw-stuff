import inspect
import os
import sys

current_script_path = inspect.getframeinfo(inspect.currentframe()).filename
filesharing_path = os.path.dirname(os.path.abspath(current_script_path))
tools_path = os.path.dirname(filesharing_path)
sys.path.insert(1, tools_path)


assert os.path.basename(filesharing_path) == 'filesharing', "expected this script are in file-sharing"
assert os.path.basename(tools_path) == 'tools', "expected this script are in tools"


import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk

import core.util as util

import filesharing.logic as logic

class tkYFrame:
    def __init__(self, master):
        self.master = master
        self.frame = None

    def __enter__(self):
        self.frame = ttk.Frame(self.master)
        return self.frame

    def __exit__(self, *args):
        self.frame.pack(side=tk.TOP, fill=tk.X)


class UploadFrame:
    def __init__(self, frame):
        self._path_to_file = ''
        self._frame = frame

        with tkYFrame(self._frame) as line:
            self._choose_file_button = tk.Button(line, text='Choose File', command=self._choose_file_click)
            self._choose_file_button.pack(side=tk.LEFT)

        with tkYFrame(self._frame) as line:
            upload_button = tk.Button(line, text='Upload', command=self._upload_click)
            upload_button.pack(side=tk.LEFT)

    def _choose_file_click(self):
        self._path_to_file = filedialog.askopenfilename()
        self._choose_file_button.config(text=self._path_to_file)

    def _upload_click(self):
        logic.upload_file(self._path_to_file, os.path.basename(self._path_to_file))



def build_upload_tab(tab):
    UploadFrame(tab)


class DownloadNameInfoFrame:
    def __init__(self, frame, listbox):
        self._frame = frame
        self._listbox = listbox

        with tkYFrame(frame) as line:
            self._update_button = tk.Button(line, text='Update', command=self._update_click)
            self._update_button.pack(side=tk.LEFT)

        with tkYFrame(frame) as line:
            self._download_button = tk.Button(line, text='Download', command=self._download_click)
            self._download_button.pack(side=tk.LEFT)

    def _download_click(self):
        selection = self._listbox.curselection()
        if not selection:
            return
        if len(selection) == 1:
            file = filedialog.asksaveasfile(mode='wb')
            name = self._listbox.get(selection[0])
            logic.write_file(name, file)
            file.close()
        else:
            dir = filedialog.askdirectory()
            names = tuple(self._listbox.get(sel_idx) for sel_idx in selection)
            logic.download_files(names, dir)
        self._download_button.config(relief=tk.RAISED)

    def _update_click(self):
        self._listbox.delete(0, tk.END)
        for file in logic.list_of_files():
            self._listbox.insert(tk.END, file)


def build_download_tab(tab):
    file_list = tk.Listbox(tab)
    for file in logic.list_of_files():
        file_list.insert(tk.END, file)

    info_frame = ttk.Frame(tab)
    DownloadNameInfoFrame(info_frame, file_list)

    file_list.place(relheight=1, relwidth=0.6)
    info_frame.place(relheight=1, relwidth=0.4, relx = 0.6)


@util.catch_halt_error
def main():
    root = tk.Tk()
    root.title('File sharing')

    tabControl = ttk.Notebook(root)
    upload_tab = ttk.Frame(tabControl)
    download_tab = ttk.Frame(tabControl, height=300, width=400)
    build_upload_tab(upload_tab)
    build_download_tab(download_tab)
    tabControl.add(upload_tab, text='Upload')
    tabControl.add(download_tab, text='Download')

    tabControl.pack(expand=1, fill='both')

    root.mainloop()


if __name__ == '__main__':
    main()
