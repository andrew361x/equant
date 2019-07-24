import threading
import time
import builtins
import keyword
import re
from operator import methodcaller
import os
from tkinter import Text, Menu, ttk
from tkinter import *
from .percolator import Percolator

from api.base_api import BaseApi
from api.api_func import _all_func_
from utils.utils import rgb_to_hex


class ScrolledText(ttk.Frame):
    # 可复用Text部件
    def __init__(self, parent=None, text="", file=None, **kw):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=YES)
        self.make_widgets()
        self.set_text(text, file)
        self.config(kw)

    def make_widgets(self):
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN, bd=0)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, fill=BOTH, expand=YES)
        self.text = text

    def set_text(self, text="", file=None):
        if file:
            text = open(file, 'r').read()
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()

    def get_text(self):
        return self.text.get('1.0', END+'-1c')


def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

def make_pat():
    esunny = []
    tmplist = []
    for value in _all_func_.values():
        for item in value:
            tmplist.append(item[0])
        esunny = esunny + tmplist
    esunny = r"\b" + any("ESUNNY", esunny) + r"\b"
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                                        if not name.startswith('_') and \
                                        name not in keyword.kwlist]

    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(?i:\br|u|f|fr|rf|b|br|rb)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string + "|" + any("SYNC", [r"\n"]) + "|" + esunny

def color_config(text, fontSize=12):
    text.config(
        foreground="#000000",
        background="#ffffff",
        font=('Consolas', fontSize),
        spacing1="6",
        spacing2="6",
        insertbackground="black",
        selectforeground="#000000",
        selectbackground="gray",
        inactiveselectbackground="gray",
    )


tagdefs = {
    "COMMENT"	: {"foreground":"#008000", "background":"#ffffff"},    #绿色 注释
    "KEYWORD"	: {"foreground":"#0000ff", "background":"#ffffff"},    #蓝色 关键字
    "BUILTIN"	: {"foreground":"#0000ff", "background":"#ffffff"},    #蓝色 系统函数
    "STRING" 	: {"foreground":"#818181", "background":"#ffffff"},    #铁红 字符串
    "DEFINITION": {"foreground":"#ff00ff", "background":"#ffffff"},    #紫色 用户函数
    "SYNC"   	: {"foreground":None	 , "background":None	 },
    "TODO"   	: {"foreground":None	 , "background":None	 },
    "ERROR"  	: {"foreground":"#000000", "background":"#ff7777"},
    # The following is used by ReplaceDialog:
    "hit"    	: {"foreground":"#ffffff", "background":"#000000"},    #白色
    "ESUNNY" 	: {"foreground":"#AE2525", "background":"#ffffff"},    #深蓝 程序化函数
}


class ParentText(Text):
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        self.config(state="disabled")
        self.rollFlag = BooleanVar()
        self.rollFlag.set(True)

    def flush(self):
        self.update()

    def setText(self, text="", file=None):
        '''子类重写'''
        raise NotImplementedError

    def get_text(self):
        return self.get('1.0', END+'-1c')

    def createScrollbar(self, vBar=True, hBar=False):

        if vBar:
            vbar = Scrollbar(self.master)
            vbar.config(command=self.yview)
            self.config(yscrollcommand=vbar.set)
            vbar.pack(side=RIGHT, fill=Y)
        if hBar:
            hbar = Scrollbar(self.master)
            hbar.config(command=self.xview)
            self.config(xscrollcommand=hbar.set)
            hbar.pack(side=BOTTOM, fill=X)

    def copy(self, event=None):
        if not self.tag_ranges("sel"):
            return None
        self.event_generate("<<Copy>>")
        return "break"

    def select_all(self, event=None):
        self.tag_add("sel", "1.0", "end-1c")
        self.mark_set("insert", "1.0")
        self.see("insert")
        return "break"

    def clear_all(self, event=None):
        self.config(state="normal")
        self.delete('1.0', 'end+1c')
        self.config(state="disabled")
        self.update()

    def undo(self, event=None):
        self.edit_undo()

    def redo(self, event=None):
        self.edit_redo()

    def cut(self, event=None):
        self.event_generate("<<Cut>>")
        return "break"

    def paste(self, event=None):
        self.event_generate("<<Paste>>")
        self.see("insert")
        return "break"


class ModifiedMixin(object):
    """allow a Text Widget to notice when it's modified"""

    def _init(self):
        self.clearModifiedFlag()
        self.bind_all("<<Modified>>", self._beenModified)

    def _beenModified(self, event=None):
        if self._resettingModifiedFlag:
            return

        self.clearModifiedFlag()
        self.beenModified(event)

    def beenModified(self, event=None):
        pass

    def clearModifiedFlag(self):
        self._resettingModifiedFlag = True

        try:
            self.tk.call(self._w, 'edit', 'modified', 0)
        finally:
            self._resettingModifiedFlag = False


class TextLineNumbers(Canvas):
    """line numbers"""

    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, textWidget):
        self.textwidget = textWidget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1] + 7
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

        self.after(200, self.redraw)

class EditorText(ParentText, ModifiedMixin):
    def __init__(self, master, view, **kw):
        ParentText.__init__(self, master, **kw)
        self._init()

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

        self._view = view
        self._controller = view.control
        self.prog = re.compile(make_pat(), re.S)
        self.idprog = re.compile(r"\s+(\w+)", re.S)
        self.tagdefs = tagdefs
        color_config(self)
        self.config_colors()
        self.percolator = Percolator(self)
        self.bind("<Button-3>", self.create_menu)
        # 双击选中事件
        # self.bind("<Double-Button-1>", self.doubleClickEvent)

        # TODO: 捕获modified需要修改
        self.edit_modified(False)
        self.bind("<<Modified>>", self.beenModified)

        self.config(state="normal")

        #TODO: 增加行号
        self.linenumbers = TextLineNumbers(self.master, width=30)
        self.linenumbers.attach(self)

        self.bind("<<Change>>", self._onChange)
        self.bind("<Configure>", self._onChange)
        self.linenumbers.pack(side=LEFT, fill="y")

    def _onChange(self, event):
        self.linenumbers.redraw()

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        try:
            result = self.tk.call(cmd)
        except Exception:
            return None

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result
        # return None

    def beenModified(self, event=None):
        if not self._view.doubleClickFlag():
            if self.edit_modified():
                if not self._view.doubleClickFlag():
                    strategyPath = self._controller.getEditorText()["path"]
                    text = os.path.basename(strategyPath)
                    self._view.updateEditorHead(text+"*")
                return

    def config_colors(self):
        for tag, cnf in self.tagdefs.items():
            if cnf:
                self.tag_configure(tag, **cnf)
        self.tag_raise('sel')

    def esunny_event(self,event):
        print("esunny_event")

    def show_arrow_cursor(self,event):
        self.config(cursor="hand2")

    def show_xterm_cursor(self, event):
        self.config(cursor='xterm')

    def click(self, event):
        index1 = self.index("current").split(".")
        range1 = self.tag_ranges("ESUNNY")
        start_index = 0
        for i, pos in enumerate(range1):
            posit = pos.string.split(".")
            # if int(index1[0]) == int(posit[0]) and int(index1[1]) <= int(posit[1]):
            if int(index1[0]) == int(posit[0]) and int(index1[1]) < int(posit[1]):
                start_index = i
                posit = pos.string
                break
        funcName = self.get(range1[start_index-1].string, range1[start_index].string)
        if funcName:
            func = globals()['BaseApi'].__dict__[funcName]
            self._controller.set_help_text(funcName, func.__doc__)

    def doubleClickEvent(self, event):
        """双击editor事件"""
        return "break"

    def recolorize_main(self):
        next = "1.0"
        while True:
            item = self.tag_nextrange("TODO", next)
            if not item:
                break
            head, tail = item
            self.tag_remove("SYNC", head, tail)
            item = self.tag_prevrange("SYNC", head)
            if item:
                head = item[1]
            else:
                head = "1.0"

            chars = ""
            next = head
            lines_to_get = 1
            ok = False
            while not ok:
                mark = next
                next = self.index(mark + "+%d lines linestart" %
                                         lines_to_get)
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" in self.tag_names(next + "-1c")
                line = self.get(mark, next)
                ##print head, "get", mark, next, "->", repr(line)
                if not line:
                    return
                for tag in self.tagdefs:
                    self.tag_remove(tag, mark, next)
                chars = chars + line
                m = self.prog.search(chars)

                while m:
                    for key, value in m.groupdict().items():
                        if value:
                            a, b = m.span(key)
                            self.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            if key == "ESUNNY":
                                # self.tag_bind(key, "<Button-1>", self.esunny_event)
                                # self.tag_config(key, underline=True)
                                self.tag_bind(key, '<Enter>', self.show_arrow_cursor)
                                self.tag_bind(key, '<Leave>', self.show_xterm_cursor)
                                self.tag_bind(key, '<ButtonRelease-1>', self.click)

                                # self.tag_bind(key, '<Control-Button-1>', self.click)
                            if value in ("def", "class"):
                                m1 = self.idprog.match(chars, b)
                                if m1:
                                    a, b = m1.span(1)
                                    self.tag_add("DEFINITION", head + "+%dc" % a, head + "+%dc" % b)

                    m = self.prog.search(chars, m.end())
                if "SYNC" in self.tag_names(next + "-1c"):
                    head = next
                    chars = ""
                else:
                    ok = False
                if not ok:
                    # We're in an inconsistent state, and the call to
                    # update may tell us to stop.  It may also change
                    # the correct value for "next" (since this is a
                    # line.col string, not a true mark).  So leave a
                    # crumb telling the next invocation to resume here
                    # in case update tells us to leave.
                    self.tag_add("TODO", next)
                self.update()

    def create_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="撤消", command=self.undo)
        menu.add_command(label="恢复", command=self.redo)
        menu.add_command(label="剪切", command=self.cut)
        menu.add_command(label="复制", command=self.copy)
        menu.add_command(label="粘贴", command=self.paste)
        menu.add_command(label="全选", command=self.select_all)
        menu.post(event.x_root, event.y_root)


class SignalText(ParentText):
    def __init__(self, master, **kw):
        ParentText.__init__(self, master, **kw)
        color_config(self, fontSize=10)
        self.bind("<Button-3>", self.create_menu)

    def write(self, obj):
        self.config(state='normal')
        index1 = self.index("end-1c")
        self.insert(index1, obj)

        if " - INFO " in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")
        elif " - ERROR" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        elif " - WARNING" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        else:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")

        self.see("end")

    def create_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="复制", command=self.copy)
        menu.add_command(label="全选", command=self.select_all)
        menu.add_command(label="清除", command=self.clear_all)
        menu.add_checkbutton(label="自动滚屏", onvalue=True, offvalue=0, variable=self.rollFlag)
        menu.post(event.x_root, event.y_root)

    # TODO:setText重写
    def setText(self, text="", file=None):
        self.config(state="normal")
        self.config(state="normal")
        # self.insert("end", text + "\n")
        self.insert("end", text)
        self.config(state="disabled")
        self.update()
        if self.rollFlag.get():
            self.see("end")
        else:
            self.see("current")
        # self.see("end")

class MonitorText(ParentText):
    def __init__(self, master, **kw):
        ParentText.__init__(self, master, **kw)
        self.setConfig()
        self.bind("<Button-3>", self.create_menu)

    def write(self, obj):
        self.config(state='normal')
        index1 = self.index("end-1c")
        self.insert(index1, obj)
        if " - INFO " in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")
        elif " - ERROR" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        elif " - WARNING" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        else:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")

        self.see("end")

    def setText(self, text="", file=None):
        self.config(state="normal")
        self.config(state="normal")
        # self.insert("end", text + "\n")
        self.insert("end", text)
        self.config(state="disabled")
        self.update()
        if self.rollFlag.get():
            self.see("end")
        else:
            self.see("current")
        # self.see("end")

    def create_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="复制", command=self.copy)
        menu.add_command(label="全选", command=self.select_all)
        menu.add_command(label="清除", command=self.clear_all)
        menu.add_checkbutton(label="自动滚屏", onvalue=True, offvalue=0, variable=self.rollFlag)
        menu.post(event.x_root, event.y_root)


    def setConfig(self, fontSize=10):
        self.config(
            foreground="#000000",
            background="#ffffff",
            font=('monospace', fontSize),
            spacing1="6",
            spacing2="6",
            insertbackground="black",
            selectforeground="#000000",
            selectbackground="gray",
            inactiveselectbackground="gray",
        )


class HelpText(ParentText):
    def __init__(self, master, **kw):
        ParentText.__init__(self, master, **kw)
        self.setConfig()
        self.bind("<Button-3>", self.create_menu)

    def create_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="复制", command=self.copy)
        menu.add_command(label="全选", command=self.select_all)
        menu.post(event.x_root, event.y_root)

    def setConfig(self, fontSize=10):
        self.config(
            foreground="#000000",
            background="#ffffff",
            font=('Microsoft YaHei', fontSize),
            spacing1="6",
            spacing2="6",
            insertbackground="black",
            selectforeground="#000000",
            selectbackground="gray",
            inactiveselectbackground="gray",
        )

    #TODO:setText重写
    def setText(self, text="", file=None):
        self.config(state="normal")
        self.config(state="normal")
        self.delete('1.0', 'end')
        self.insert("end", text + "\n")
        self.config(state="disabled")
        self.update()
        # self.see("end")


class ErrorText(ParentText):
    def __init__(self, master, **kw):
        ParentText.__init__(self, master, **kw)
        color_config(self, fontSize=10)
        self.bind("<Button-3>", self.create_menu)

    def write(self, obj):
        self.config(state='normal')
        index1 = self.index("end-1c")
        self.insert(index1, obj)

        if " - INFO " in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")
        elif " - ERROR" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        elif " - WARNING" in obj:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="red")
        else:
            self.tag_add(obj, index1, "end")
            self.tag_configure(obj, foreground="black")

        self.config(state="disabled")
        self.see("end")

    def create_menu(self, event):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="复制", command=self.copy)
        menu.add_command(label="全选", command=self.select_all)
        menu.add_command(label="清除", command=self.clear_all)
        menu.add_checkbutton(label="自动滚屏", onvalue=True, offvalue=0, variable=self.rollFlag)
        menu.post(event.x_root, event.y_root)

    # TODO:setText重写
    def setText(self, text="", file=None):
        """先清空再写入信息"""
        self.config(state="normal")
        self.delete('1.0', 'end')
        self.insert("end", text + "\n")
        self.config(state="disabled")
        self.update()
        if self.rollFlag.get():
            self.see("end")
        else:
            self.see("current")


class ContractText(ParentText):
    def __init__(self, master, **kw):
        ParentText.__init__(self, master, **kw)
        self.color_config()
        self.bind("<Button-1>", self.textEvent)

    def setText(self, text="", file=None):
        if file:
            text = open(file, 'r').read()
        self.config(state="normal")
        self.insert('end', text+ '\n')
        self.config(state="disabled")
        self.update()
        self.focus()

    def textEvent(self, event):
        """timerText回调事件"""
        self.tag_configure("current_line", background=rgb_to_hex(0, 120, 215), foreground="white")
        self.tag_remove("current_line", 1.0, "end")
        self.tag_add("current_line", "current linestart", "current lineend")

    def color_config(self):
        self.config(
            foreground="#000000",
            background="#ffffff",
            font=('monospace', 10),
            spacing1="6",
            spacing2="6",
            insertbackground="black",
            selectforeground="#000000"
        )















