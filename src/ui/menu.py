import os
import sys
sys.path.append("..")

import shutil
from tkinter import *
from tkinter import messagebox

from utils.language import Language
from .language import Language
from .com_view import NewDirToplevel, NewFileToplevel, RenameToplevel, DeleteToplevel


class StrategyMenu(object):
    def __init__(self, controller, parent=None):
        self._controller = controller
        self.parent = parent
        self.widget = parent.root_tree   # 获取树控件
        self.language = Language("EquantMainFrame")

        self._lClickSelectedItem = None   # 左键选择标签
        self._rightClickPath = ""    # 记录右键弹出菜单时选中的策略路径

        self.menu = Menu(self.widget, tearoff=0)

    def add_event(self):
        new_menu = Menu(self.menu, tearoff=0)
        if len(self._lClickSelectedItem) == 1 and self.widget.parent(self._lClickSelectedItem[0]):  # 保证只选中一个
            # self.menu.add_command(label="运行", command=self.runStrategy, state=DISABLED)
            pass

        self.menu.add_cascade(label="新建", menu=new_menu)
        new_menu.add_command(label=self.language.get_text(41), command=self.newStrategy)
        new_menu.add_command(label=self.language.get_text(42), command=self.newDir)
        if len(self._lClickSelectedItem) == 1:
            self.menu.add_command(label="重命名", command=self.rename)

        # self.menu.add_command(label="移动分组", command=self.move_strategy)
        self.menu.add_command(label="删除", command=self.delete_)
        # self.menu.add_command(label="test", command=self.test)
        self.menu.add_command(label="刷新", command=self.onRefresh)

    def test(self):
        # 用于menu状态测试
        if self.menu.entrycget(0, "state")=="disabled":
            self.menu.entryconfigure(0, state="normal", background='red')
            # self.menu.delete(0)
            print(self.menu.entrycget(0, "state"))
            self.menu.update()
        else:
            self.menu.entryconfigure(0, state="disabled")
            print(self.menu.entrycget(0, "state"))

    def popupmenu(self, event):
        rSelectItem = self.widget.identify_row(event.y)
        self._lClickSelectedItem = event.widget.selection()

        # 记录右键所选择的策略路径
        if rSelectItem:  # 存在选择的策略
            self._rightClickPath = self.widget.item(rSelectItem)["values"][0]

        if self._lClickSelectedItem:
            if rSelectItem:
                if rSelectItem not in self._lClickSelectedItem:
                    self.widget.focus(rSelectItem)
                    self.widget.selection_set(rSelectItem)
                    self._lClickSelectedItem = event.widget.selection()
            self.add_event()
            self.menu.post(event.x_root, event.y_root)
        else:
            if rSelectItem:
                self.widget.focus(rSelectItem)
                self.widget.selection_set(rSelectItem)
                self._lClickSelectedItem = event.widget.selection()
                self.widget.focus(rSelectItem)
                self.widget.selection_set(rSelectItem)
                self.add_event()
                self.menu.post(event.x_root, event.y_root)

    def get_file_path(self):
        select = self._lClickSelectedItem
        file_path = []
        for idx in select:
            file_path.append(self.widget.item(idx)["values"][0])
        return file_path

    def runStrategy(self):
        # 加载策略
        # TODO：进行操作前需要对当前选中的策略进行保存
        self._controller.load(self._rightClickPath)

    def newStrategy(self):
        newFileWin = NewFileToplevel(self._controller.top)

        def save(event=None):
            # 新建策略前先保存当前选中的策略
            self._controller.saveStrategy()
            # TODO：目录树多选时path为list，新建文件的存储位置可能会有问题（总是新建到item最小的文件所在的文件夹）
            temp_path = self.get_file_path()
            path = temp_path[0]
            if os.path.isdir(path):
                dir_path = path
            if os.path.isfile(path):
                dir_path = os.path.dirname(path)
            file_name = newFileWin.nameEntry.get()
            file_type = newFileWin.type_chosen.get()
            if file_name == "":
                messagebox.showinfo(title=self.language.get_text(8), message=self.language.get_text(16), parent=newFileWin)
            else:
                file = file_name + file_type
                if not os.path.exists(os.path.join(dir_path, file)):
                    # TODO：怎么把文件按文件名插入到合适的位置呢？
                    newFileWin.destroy()
                    filePath = os.path.join(dir_path, file)
                    self._controller.newStrategy(filePath)
                else:
                    messagebox.showinfo(self.language.get_text(8),
                                        self.language.get_text(17) + file + self.language.get_text(18), parent=newFileWin)

        def cancel():
            newFileWin.destroy()

        newFileWin.nameEntry.bind("<Return>", save)
        newFileWin.saveBtn.configure(command=save)
        newFileWin.cancelBtn.configure(command=cancel)
        # 模态窗口
        newFileWin.display()

    def newDir(self):
        newTop = NewDirToplevel(self._controller.top)

        def save(event=None):
            # 新建前先保存当前选中的策略
            self._controller.saveStrategy()

            file_name = newTop.nameEntry.get()
            if file_name == "":
                messagebox.showinfo(self.language.get_text(8), self.language.get_text(22), parent=newTop)
            else:
                tempPath = self.get_file_path()
                path = tempPath[0]
                if os.path.isdir(path):
                    # TODO: 新建策略有问题
                    dir_path = path
                    # dir_path = os.path.dirname(path)
                    if self.widget.parent(dir_path) == "":
                        newPath = os.path.abspath(os.path.join(dir_path, "..\\%s" % file_name))
                    else:
                        newPath = os.path.abspath(os.path.join(dir_path, file_name))

                if os.path.isfile(path):
                    dir_path = os.path.dirname(path)
                    newPath = os.path.join(dir_path, file_name)

                if not os.path.exists(newPath):
                    # TODO: insert的位置问题。。。
                    # TODO：新建目录和新建文件在目录树种无法区别
                    newTop.destroy()

                    # filePath = os.path.join(dir_path, file_name)
                    self._controller.newDir(newPath)
                else:
                    messagebox.showinfo(self.language.get_text(8),
                                        self.language.get_text(23) + file_name + self.language.get_text(24),
                                        parent=newTop)

        def cancel():
            newTop.destroy()

        newTop.nameEntry.bind("<Return>", save)
        newTop.saveBtn.config(command=save)
        newTop.cancelBtn.config(command=cancel)
        newTop.display()

    def move_strategy(self):
        """移动文件"""
        # TODO: 可以用treeview的move方法实现吧
        # TODO：进行操作前需要对当前选中的策略进行保存
        pass

    def rename(self):
        """重命名文件"""
        # TODO：RenameToplevel的父控件是不是不太对啊

        tempPath = self.get_file_path()
        path = tempPath[0]
        editorPath = self._controller.getEditorText()["path"]

        renameTop = RenameToplevel(path, self._controller.top)

        def enter(event=None):
            self._controller.saveStrategy()
            newPath = os.path.join(os.path.dirname(path), renameTop.newEntry.get())

            if not os.path.exists(path):
                messagebox.showinfo("提示", "本地文件不存在或已删除", parent=renameTop)
                return
            else:
                if os.path.isfile(path):
                    # print(os.path.splitext(renameTop.newEntry.get()))
                    if os.path.splitext(renameTop.newEntry.get())[0] == "" \
                            or os.path.splitext(renameTop.newEntry.get())[0] == ".py":
                        messagebox.showinfo("提示", "策略文件后缀名不能为空", parent=renameTop)
                        return

                    if os.path.splitext(renameTop.newEntry.get())[1] != ".py":
                        messagebox.showinfo("提示", "策略文件后缀名为.py", parent=renameTop)
                        return

                if os.path.isdir(path):
                    if renameTop.newEntry.get() == "":
                        messagebox.showinfo("提示", "文件名不能为空", parent=renameTop)
                        return

                if not os.path.exists(newPath):
                    self.widget.item(self._lClickSelectedItem, values=[newPath, "!@#$%^&*"])
                    os.rename(path, newPath)

                    if os.path.isfile(newPath):

                        text = renameTop.newEntry.get()
                        self.widget.item(self._lClickSelectedItem, text=text)
                        # TODO:更新标签和model中的editor
                        if path in editorPath:
                            self._controller.setEditorTextCode(newPath)
                            self._controller.updateEditorHead(text)

                    if os.path.isdir(newPath):
                        text = renameTop.newEntry.get()
                        self.widget.tag_configure(self._lClickSelectedItem, text=text)
                    self.widget.update()
                else:
                    messagebox.showinfo("提示", self.language.get_text(32), parent=renameTop)
            renameTop.destroy()

        def cancel():
            renameTop.destroy()

        renameTop.newEntry.bind("<Return>", enter)
        renameTop.saveBtn.config(command=enter)
        renameTop.cancelBtn.config(command=cancel)
        renameTop.display()

    def openDir(self):
        """打开文件夹"""
        # TODO：进行操作前需要对当前选中的策略进行保存
        pass

    def delete_(self):
        """删除文件"""
        # TODO: 若删除文件为当前选中文件，需要更新editor_head和editor_text，重置为空吧
        tempPath = self.get_file_path()
        deleteTop = DeleteToplevel(tempPath, self._controller.top)
        selected_item = self._lClickSelectedItem
        # 当前选中的策略路径
        editorPath = self._controller.getEditorText()["path"]
        def enter(event=None):
            self._controller.saveStrategy()
            
            # 先关闭窗口
            deleteTop.destroy()

            for path, select in zip(tempPath, selected_item):
                if os.path.exists(path):
                    if os.path.isdir(path):
                        for root, dirs, files in os.walk(path):
                            for name in files:
                                deletePath = os.path.join(root, name)
                                if editorPath == deletePath:
                                    # 更新选中策略路径
                                    self._controller.setEditorTextCode("")
                                    # 更新策略编辑界面显示信息
                                    self._controller.updateEditor("")
                                    os.remove(deletePath)
                                    # shutil.rmtree(deletePath)
                            for name in dirs:
                                shutil.rmtree(os.path.join(root, name))
                        # 删除本地文件
                        shutil.rmtree(path)
                        # 删除控件中的条目
                        self.widget.delete(select)
                    else:
                        if editorPath == path:
                            # 更新选中策略路径
                            self._controller.setEditorTextCode("")
                            # 更新策略编辑界面显示信息
                            self._controller.updateEditor("")

                        os.remove(path)
                        self.widget.delete(select)
                else:  # 文件不存在
                    try:
                        self.widget.delete(select)
                    except:
                        pass

        def cancel():
            deleteTop.destroy()

        deleteTop.saveBtn.focus_set()
        deleteTop.bind("<Return>", enter)
        deleteTop.saveBtn.config(command=enter)
        deleteTop.cancelBtn.config(command=cancel)
        deleteTop.display()

    def onRefresh(self):
        """刷新目录"""
        self.parent.update_all_tree()


class RunMenu(object):
    def __init__(self, controller, parent=None):
        self._controller = controller
        self.widget = parent
        self.menu = Menu(parent, tearoff=0)
        self._ClickSelectedItem = None   # 选中条目，鼠标单击或前一次右键选中条目
        self._strategyId = []   # 策略Id列表，弹出右键菜单时赋值

    def add_event(self):
        # self.menu.add_command(label="暂停", command=self.onPause)
        self.menu.add_command(label="启动", command=self.onResume)
        self.menu.add_command(label="停止", command=self.onQuit)
        self.menu.add_command(label="删除", command=self.onDelete)
        self.menu.add_command(label="投资报告", command=self.onReport)
        self.menu.add_command(label="图表展示", command=self.onSignal)
        self.menu.add_command(label="属性设置", command=self.onParam)

    def popupmenu(self, event):
        select = self.widget.identify_row(event.y)
        self._ClickSelectedItem = event.widget.selection()

        # 右键弹出菜单时给strategyId 赋值

        if self._ClickSelectedItem:  # 选中之后右键弹出菜单
            for idx in self._ClickSelectedItem:
                self._strategyId.append(int(idx))
        else:  # 没有选中，直接右键选择
            if select:
                self._strategyId.append(int(select))

        if self._ClickSelectedItem:
            if select:
                if select not in self._ClickSelectedItem:
                    self.widget.focus(select)
                    self.widget.selection_set(select)
                    self._ClickSelectedItem = event.widget.selection()
                    self._strategyId = [int(select)]

            self.add_event()
            self.menu.post(event.x_root, event.y_root)
        else:
            if select:
                self.widget.focus(select)
                self.widget.selection_set(select)
                self._ClickSelectedItem = event.widget.selection()
                self.widget.focus(select)
                self.widget.selection_set(select)
                self.add_event()
                self.menu.post(event.x_root, event.y_root)

    def onPause(self):
        """策略暂停"""
        self._controller.pauseRequest(self._strategyId)

    def onQuit(self):
        """策略停止"""
        self._controller.quitRequest(self._strategyId)

    def onResume(self):
        """策略运行"""
        self._controller.resumeRequest(self._strategyId)

    def onDelete(self):
        """删除策略"""
        if messagebox.askokcancel('提示', '删除策略运行数据也将删除，确定删除么'):
            self._controller.delStrategy(self._strategyId)

    def onReport(self):
        """展示报告"""
        self._controller.generateReportReq(self._strategyId)

    def onSignal(self):
        """查看信号图"""
        # 当查看信号图时，如果策略选择多个，则只显示第一个
        self._controller.signalDisplay(self._strategyId)

    def onParam(self):
        """属性设置"""
        # 选择多个时，则选择第一个策略生效
        self._controller.paramSetting(self._strategyId)
        # param = self._controller.getUserParam(self._strategyId)
        # path = self._controller.getEditorText()["path"]
        # self._controller.load(path, param)
