import os
import sys
sys.path.append("..")

import tkinter as tk
import tkinter.ttk as ttk

from utils.utils import *
from utils.language import Language
from .language import Language

from report.windowconfig import center_window


class QuantFrame(object):
    '''通用方法类'''
    def __init__(self):
        pass
        
    def addScroll(self, frame, widgets, xscroll=True, yscroll=True):
        xsb,ysb = None, None

        if xscroll:
            xsb = tk.Scrollbar(frame, orient="horizontal")
            widgets.config(xscrollcommand=xsb.set)
            xsb.config(command=widgets.xview, bg=rgb_to_hex(255,0,0))
            xsb.pack(fill=tk.X, side=tk.BOTTOM)

        if yscroll:
            ysb = tk.Scrollbar(frame, orient="vertical")
            widgets.config(yscrollcommand=ysb.set)
            ysb.config(command=widgets.yview, bg=rgb_to_hex(255,0,0))
            ysb.pack(fill=tk.Y, side=tk.RIGHT)

        return xsb, ysb


class QuantToplevel(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self._master = master
        self.language = Language("EquantMainFrame")
        self.setPos()
        #图标
        self.iconbitmap(bitmap=r"./icon/epolestar ix2.ico")

    def setPos(self):
        # 获取主窗口大小和位置，根据主窗口调整输入框位置
        ws = self._master.winfo_width()
        hs = self._master.winfo_height()
        wx = self._master.winfo_x()
        wy = self._master.winfo_y()

        #计算窗口位置
        w, h = 400, 120
        x = (wx + ws/2) - w/2
        y = (wy + hs/2) - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.minsize(200, 120)

    def display(self):
        """显示并设置模态窗口"""
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.wait_window()


class NewFileToplevel(QuantToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.attributes("-toolwindow", 1)
        self.title("新建文件")
        self.createWidgets()

    def createWidgets(self):
        f1, f2, f3 = tk.Frame(self), tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.TOP, fill=tk.X)
        f3.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        name_label = tk.Label(f1, text=self.language.get_text(14), width=10)
        self.nameEntry = tk.Entry(f1, width=23)
        type_label = tk.Label(f2, text=self.language.get_text(15), width=10)
        self.type_chosen = ttk.Combobox(f2, state="readonly", width=20)
        self.type_chosen["values"] = [".py"]
        self.type_chosen.current(0)

        self.saveBtn = tk.Button(f3, text=self.language.get_text(19))
        self.cancelBtn = tk.Button(f3, text=self.language.get_text(20))
        name_label.pack(side=tk.LEFT, expand=tk.NO)
        self.nameEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        type_label.pack(side=tk.LEFT, expand=tk.NO)
        self.type_chosen.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, padx=20)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.nameEntry.focus_set()
        self.wait_window()


class NewDirToplevel(QuantToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.attributes("-toolwindow", 1)
        self.title("新建文件夹")
        self.createWidget()

    def createWidget(self):
        f1, f2, f3 = tk.Frame(self), tk.Frame(self), tk.Frame(self)
        f4, f5 = tk.Frame(f3), tk.Frame(f3)

        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.TOP, fill=tk.X)
        f3.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        f4.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        f5.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        nameLabel = tk.Label(f1, text="输入分组名称：")
        self.nameEntry = tk.Entry(f2)
        self.saveBtn = tk.Button(f4, text="保存")
        self.cancelBtn = tk.Button(f5, text="取消")

        nameLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
        self.nameEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, padx=10)
        self.cancelBtn.pack(side=tk.LEFT, expand=tk.NO, padx=10)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.nameEntry.focus_set()
        self.wait_window()


class RenameToplevel(QuantToplevel):
    def __init__(self, path, master=None):
        super().__init__(master)
        self.path = path
        self.attributes("-toolwindow", 1)
        self.title("重命名")
        self.createWidget()

    def createWidget(self):
        f1, f2 = tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=15)
        f2.pack(side=tk.BOTTOM, fill=tk.X)

        if os.path.isfile(self.path):
            newLabel = tk.Label(f1, text=self.language.get_text(28))
            self.newEntry = tk.Entry(f1, width=15)
            self.newEntry.insert(tk.END, os.path.basename(self.path))

            self.saveBtn = tk.Button(f2, text="确定")
            self.cancelBtn = tk.Button(f2, text="取消")

            newLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
            self.newEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)

            self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
            self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)

        if os.path.isdir(self.path):
            newLabel = tk.Label(f1, text=self.language.get_text(30))
            self.newEntry = tk.Entry(f1, width=15)
            self.newEntry.insert(tk.END, os.path.basename(self.path))

            self.saveBtn = tk.Button(f2, text="确定", bd=0)
            self.cancelBtn = tk.Button(f2, text="取消", bd=0)

            newLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
            self.newEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)

            self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
            self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.newEntry.focus_set()
        self.wait_window()


class DeleteToplevel(QuantToplevel):
    def __init__(self, path, master=None):
        super().__init__(master)
        self.path = path
        self.attributes("-toolwindow", 1)
        # self.wm_attributes("-topmost", 1)
        self.title("删除")
        self.createWidget()

    def createWidget(self):
        f1, f2 = tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.BOTTOM, fill=tk.X)
        label = tk.Label(f1)
        label["text"] = self.language.get_text(34)
        path = self.path
        if len(self.path) > 1:
            label["text"] = "即将删除被选中项"
        else:
            if os.path.isdir(self.path[0]):
                label["text"] = self.language.get_text(35) + os.path.basename(self.path[0]) + "?"
            if os.path.isfile(self.path[0]):
                label["text"] = self.language.get_text(34) + \
                                os.path.join(os.path.basename(os.path.dirname(self.path[0])),
                                             os.path.basename(self.path[0])) + "?"

        self.saveBtn = tk.Button(f2, text=self.language.get_text(33))
        self.cancelBtn = tk.Button(f2, text=self.language.get_text(20))

        label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15, pady=15)
        self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)


def Singleton(cls):
    # 单例模式
    _instance = {}

    def __singleton(*args, **kw):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kw)
        return _instance[cls]

    return __singleton


# @Singleton
class HistoryToplevel(QuantToplevel):
    def __init__(self, view, master=None):
        super().__init__(master)
        # self.withdraw()
        self.wm_attributes("-topmost", 0)  # 窗口置顶
        self._view = view
        self._master = master
        self.set_config()
        self.withdraw()

    def set_config(self):
        self.title('回测报告')
        center_window(self, 1000, 600)
        self.minsize(1000, 600)

    def display_(self):
        self.update()
        self.deiconify()
