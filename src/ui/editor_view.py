import os

from tkinter import *
from tkinter import Frame
import tkinter.font as tkFont
from utils.utils import *
from .language import Language
from .editor import EditorText
from .com_view import *
from .menu import StrategyMenu


class QuantEditorHead(object):
    def __init__(self, frame, control, language):
        self.control = control
        self.language = language
        
        self.head_frame = Frame(frame, bg=rgb_to_hex(245, 245, 245), height=30)
        Label(self.head_frame, bg=rgb_to_hex(245, 245, 245), text=self.language.get_text(1)).pack(side=LEFT)

        self.stateLabel = Label(self.head_frame, bg=rgb_to_hex(245, 245, 245))
        self.stateLabel.pack(side=RIGHT, fill=X, expand=YES, anchor=E)

        self.head_frame.pack_propagate(0)
        self.head_frame.pack(fill=X)
        
class StrategyTree(QuantFrame):
    def __init__(self, frame, control, language):
    
        self.control = control
        self.language = language
        self.root_tree = None
        self.tree_frame = None
        self.tree_menu = None
        self.tree_node_dict = {}   # 刷新父节点用的
        self.strategyTreeScl = None

        # 记录节点的开关状态
        self._openState = {}
        # 记录被选中的节点
        self._selected = None

        # 策略树图标
        # TODO:不加self就不显示image
        self.wfileicon = tk.PhotoImage(file=r'./icon/file_white.gif')
        self.gfileicon = tk.PhotoImage(file=r'./icon/file_grey.gif')
        self.wdiricon  = tk.PhotoImage(file=r'./icon/dir_white.gif')
        self.gdiricon  = tk.PhotoImage(file=r'./icon/dir_grey.gif')
        
        #print("StrategyTree:%d,%d"%(frame['width'], frame['height']))

        # TODO：-28: 监控窗口和函数说明窗口对不齐，暂时先减去一个固定值吧
        self.parent_pane = PanedWindow(frame, orient=HORIZONTAL, sashrelief=GROOVE, sashwidth=1.5,
                                       showhandle=False, opaqueresize=True, height=frame['height']-28, width=frame['width'])
        self.parent_pane.pack(fill=BOTH, expand=YES)
        
        self.root_path = os.path.abspath("./strategy")
        self.logger = control.get_logger()

    def create_tree(self):
        self.tree_frame = Frame(self.parent_pane, relief=RAISED, bg=rgb_to_hex(255, 255, 255), width=218)
        self.tree_frame.pack_propagate(0)
        #生成策略树
        self.insert_tree()
        #显示策略树
        self.parent_pane.add(self.tree_frame, minsize=218, stretch='always')

    def update_all_tree(self):
        """销毁策略目录"""
        if self.root_tree:
            # 获取目录树的开关状态
            self._getOpenState("")
            self._selected = self.root_tree.selection()

            self.root_tree.destroy()
        if self.strategyTreeScl:
            if self.strategyTreeScl[0]:
                self.strategyTreeScl[0].destroy()
            else:
                self.strategyTreeScl[1].destroy()

        self.insert_tree()
        # 恢复策略目录的开关状态
        self._setOpenState("")
        # 恢复选中状态
        if self._selected:
            self.root_tree.selection_set(self._selected)

    def _getOpenState(self, item):
        """遍历树目录的开关状态， 需要循环遍历所有item"""
        for itemId in self.root_tree.get_children(item):
            self._openState[itemId] = self.root_tree.item(itemId)["open"]
            self._getOpenState(itemId)

    def _setOpenState(self, item):
        for itemId in self.root_tree.get_children(item):
            # 不在量化客户端新建策略时，刷新时会出现keyerror
            try:
                self.root_tree.item(itemId, open=self._openState[itemId])
                self._setOpenState(itemId)
            except KeyError:
                pass

    def update_tree(self, fullname):
        '''只刷新父节点'''

        dir_name = os.path.dirname(fullname)
        file_name = os.path.basename(fullname)
        # debug模式下新建文件时会发现新建文件的位置在树上不对，update_all_tree之后才对。

        try:  # 在最外层创建目录
            selectId = self.tree_node_dict[dir_name]
        except:
            selectId = dir_name

        if not selectId:
            messagebox.showinfo("提示", "更新策略树失败")
        else:
            if os.path.isdir(fullname):
                iimage = self.gdiricon
            elif os.path.isfile(fullname):
                iimage = self.gfileicon
            else:
                return

            try:   # 在最外层创建文件夹
                parent = self.root_tree.parent(selectId)
            except:
                parent = ""

            itemId = self.root_tree.insert(parent, 'end', iid=fullname, text=file_name, open=False,
                                           values=[fullname, "!@#$%^&*"],
                                           image=iimage)

            self.tree_node_dict[fullname] = itemId

            # 设置新建的条目选中
            self.root_tree.selection_set(itemId)
            # 设置父条目的开关状态
            self.root_tree.item(self.root_tree.parent(itemId), open=True)
            self.root_tree.item(itemId, open=True)

            # 新建之后排序
            self.update_all_tree()

    def insert_tree(self):
        #作为类成员，用于树更新
        style = ttk.Style()
        style.configure('Filter.Treeview', foreground=rgb_to_hex(51, 51, 51))
        style.layout('Filter.Treeview', [
            ('Treeview.entry', {
                'border': '1', 'children':
                    [('Treeview.padding', {
                        'children':
                            [('Treeview.treearea', {'sticky': 'nswe'})], 'sticky': 'nswe'
                    })],
                'sticky': 'nswe'
            })
        ])

        self.root_tree = ttk.Treeview(self.tree_frame, show="tree", style='Filter.Treeview')
        
        #增加滚动条
        self.strategyTreeScl = self.addScroll(self.tree_frame, self.root_tree, xscroll=False)

        #生成文件
        self.loadTree("", self.root_path)
        #绑定处理事件
        self.root_tree.bind("<Double-1>", self.treeDoubleClick)
        self.root_tree.bind("<Button-3>", self.strategyMenu)
        self.root_tree.bind("<<TreeviewSelect>>", self.selectCallback)
        self.root_tree.pack(fill=BOTH, expand=YES)

        # 策略标签颜色
        # self.root_tree.bind('<Button-1>', self.select_item)
        # self.setup_selection()

    def strategyMenu(self, event):
        """右键弹出菜单"""
        StrategyMenu(self.control, self).popupmenu(event)

    def selectCallback(self, event):
        """策略树选择回调事件，更改图标样式"""
        # 恢复上一次选择的图标样式
        if self._selected:
            for id in self._selected:
                try:
                    path = self.root_tree.item(id)['values'][0]
                    if os.path.isdir(path):
                        iimage = self.gdiricon
                    else:
                        iimage = self.gfileicon
                except TclError:
                    # id 不存在了
                    continue
                else:
                    self.root_tree.item(id, image=iimage)

        # 更改被选择的图标样式
        self._selected = event.widget.selection()
        for id in self._selected:
            path = self.root_tree.item(id)['values'][0]
            if os.path.isdir(path):
                iimage = self.wdiricon
            else:
                iimage = self.wfileicon

            self.root_tree.item(id, image=iimage)

    def loadTree(self, parent, rootpath):
        for path in os.listdir(rootpath):  # 遍历当前目录
            if path == "__pycache__":
                continue
            abspath = os.path.join(os.path.abspath(rootpath), path)  # 连接成绝对路径

            # windows下，此处TreeView有一个bug, len(valaues)==1时， 空格会被拆分成两个值，\\会消失
            if os.path.isdir(abspath):
                iimage = self.gdiricon
            else:
                iimage = self.gfileicon
            oid = self.root_tree.insert(parent, 'end', iid=abspath, text=path, open=False,
                                        values=[abspath, "!@#$%^&*"], image=iimage)
            # TODO: 2000代表一个比较大的数值
            self.root_tree.column("#0", stretch=False, width=2000)
            self.tree_node_dict[abspath] = oid
            if os.path.isdir(abspath):
                self.loadTree(oid, abspath)  # 递归回去
                
    def delete_tree(self, path):
        if not os.path.exists(path):
            return
            
        self.logger.info("delete strategy tree:%s"%path)
        
        if os.path.isfile(path):
            os.remove(path)
        else:
            os.rmdir(path)
            
        if path in self.tree_node_dict:
            self.root_tree.delete(self.tree_node_dict[path])
            self.tree_node_dict.pop(path)
        
    def treeDoubleClick(self, event):
        '''子类重写'''
        raise NotImplementedError


    # -----------------------设置策略树中的条目颜色-----------------------------
    def setup_selection(self, sel_bg=rgb_to_hex(135, 103, 165), sel_fg="white"):
        self._font = tkFont.Font()
        self._canvas = tk.Canvas(self.root_tree, background=sel_bg,
                                 borderwidth=0,
                                 highlightthickness=0)
        self._canvas.text = self._canvas.create_text(0, 0, fill=sel_fg, anchor='w')

    def select_item(self, event):
        self._canvas.place_forget()

        x, y, widget = event.x, event.y, event.widget
        item = widget.item(widget.focus())
        itemText = item['text']
        itemValues = item['values']
        iid = widget.identify_row(y)
        column = event.widget.identify_column(x)

        # Leave method if mouse pointer clicks on Treeview area without data
        if not column or not iid:
            return

        # Leave method if selected item's value is empty
        if not len(itemValues):
            return

        # Get value of selected Treeview cell
        if column == '#0':
            self.cell_value = itemText
        else:
            self.cell_value = itemValues[int(column[1]) - 1]
        #print('column[1] = ', column[1])
        #print('self.cell_value = ', self.cell_value)

        # Leave method if selected Treeview cell is empty
        if not self.cell_value:  # date is empty
            return

        # Get the bounding box of selected cell, a tuple (x, y, w, h), where
        # x, y are coordinates of the upper left corner of that cell relative
        #      to the widget, and
        # w, h are width and height of the cell in pixels.
        # If the item is not visible, the method returns an empty string.
        bbox = widget.bbox(iid, column)
        #print('bbox = ', bbox)
        if not bbox:  # item is not visible
            return

        # Update and show selection in Canvas Overlay
        self.show_selection(widget, bbox, column)

        #print('Selected Cell Value = ', self.cell_value)

    def show_selection(self, parent, bbox, column):
        """Configure canvas and canvas-textbox for a new selection."""
        #print('@@@@ def show_selection(self, parent, bbox, column):')
        x, y, width, height = bbox
        fudgeTreeColumnx = 19 #Determined by trial & error
        fudgeColumnx = 15     #Determined by trial & error

        # Number of pixels of cell value in horizontal direction
        textw = self._font.measure(self.cell_value)
        #print('textw = ',textw)

        # Make Canvas size to fit selected cell
        self._canvas.configure(width=width, height=height)

        # Position canvas-textbox in Canvas
        #print('self._canvas.coords(self._canvas.text) = ', self._canvas.coords(self._canvas.text))
        if column == '#0':
            self._canvas.coords(self._canvas.text,
                                fudgeTreeColumnx,
                                height/2)
        else:
            self._canvas.coords(self._canvas.text,
                                (width-(textw-fudgeColumnx))/2.0,
                                height/2)

        # Update value of canvas-textbox with the value of the selected cell.
        self._canvas.itemconfigure(self._canvas.text, text=self.cell_value)

        # Overlay Canvas over Treeview cell
        self._canvas.place(in_=parent, x=x, y=y)

    # ------------------------暂时不用----------------------------------------------


class Context(object):
    pass


class QuantEditor(StrategyTree):
    '''策略树'''
    def __init__(self, parent_pane, control, language):
        StrategyTree.__init__(self, parent_pane, control, language)
        self.control = control
        self.editor_text = None
        self.editor_text_scroll = None

        # 策略树双击事件标志位
        self._dModifyFlag = False

        # 焦点移出标志位
        self._outFlag = False
        # 记录文件的修改时间
        self._modifyTime = 0

        self._context = Context()

    # 将strategyTree的get_file_path先放在这里
    def get_file_path(self, event):
        select = event.widget.selection()
        file_path = []
        for idx in select:
            file_path.append(self.root_tree.item(idx)["values"][0])
        return file_path
        
    def treeDoubleClick(self, event):
        """设置策略编辑框中的内容"""
        self.saveEditor()        # 切换策略时将原来的策略保存
        self._dModifyFlag = True
        select = event.widget.selection()
        for idx in select:
            path = self.root_tree.item(idx)["values"][0]
            if os.path.isfile(path):
                # 获取策略内容
                # self.editor_file = path
                self.control.setEditorTextCode(path)
                header = self.root_tree.item(idx)['text']
                # self.updateEditorHead(header)
                self.control.setEditorTextCode(path)  # 根据点击事件给editor的文本和路径赋值
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                self.updateEditorText(data)
                self.updateEditorHead(header)
                self._dModifyFlag = False
                # 清空editor的恢复和撤消栈内容
                self.editor_text.edit_reset()

    def doubleClickFlag(self):
        """是否双击策略目录标志位"""
        return self._dModifyFlag

    def updateEditorHead(self, text):
        """设置策略编辑框上方的策略名"""
        self.titleLabel.config(text=text)

    def updateEditorText(self, text):

        editor_text_code = text
        self.editor_text.delete(0.0, END+"-1c")
        self.editor_text.insert(END, editor_text_code)
        self.editor_text.delete(END + "-1c")
        self.editor_text.update()
        self.editor_text.focus_set()
        self.editor_text.see("end")
        self.editor_text.tag_add("TODO", "0.0", "end")
        self.editor_text.recolorize_main()

    def create_editor(self):
        editor_frame = Frame(self.parent_pane, bg=rgb_to_hex(255, 255, 255), width=self.parent_pane['width'])

        editor_head = Frame(editor_frame, bg=rgb_to_hex(255, 255, 255), height=40)
        self.insertEditorHead(editor_head)
        editor_head.pack(fill=X)

        editor_pane = PanedWindow(editor_frame, opaqueresize=True, orient=VERTICAL, sashrelief=GROOVE, sashwidth=4)
        editor_pane.pack(fill=BOTH, expand=YES)

        self.editor_text_frame = Frame(editor_pane, background=rgb_to_hex(255, 255, 255))
        editor_pane.add(self.editor_text_frame)

        self.insertEditorWidget("")
        self.parent_pane.add(editor_frame, stretch='always')
        
    def saveEditor(self, event=None):
        """保存策略"""

        # 保存的策略路径
        path = self.control.getEditorText()["path"]

        # 策略路径为空
        if len(path) == 0:
            return

        # 更新editorHead
        self.updateEditorHead(os.path.basename(path))

        code = self.editor_text.get("0.0", END)
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
        if not os.path.exists(path):
            messagebox.showinfo(self.language.get_text(8), self.language.get_text(9))
        
    def insertEditorHead(self, frame):
        # self.titleLabel = Label(frame, text=os.path.basename(self.root_path), bg=rgb_to_hex(255, 255, 255))
        self.titleLabel = Label(frame, bg=rgb_to_hex(255, 255, 255))

        self.loadingBtn = Button(frame, text="运行", relief=FLAT, padx=10, bg=rgb_to_hex(255, 255, 255),
                            activebackground=rgb_to_hex(103, 150, 236), bd=0, state="disabled", command=self.load)

        saveBtn = Button(frame, text="保存", relief=FLAT, padx=10, bg=rgb_to_hex(255, 255, 255),
                         activebackground=rgb_to_hex(103, 150, 236), bd=0, command=self.saveEditor)

        self.titleLabel.pack(side=LEFT)
        saveBtn.pack(side=RIGHT)
        self.loadingBtn.pack(side=RIGHT)

    def setLoadBtnState(self, state):
        self.loadingBtn.config(state=state)

    def tab_key(self, event):
        self.editor_text.insert(INSERT, " " * 4)
        return 'break'

    #TODO: 先暂时屏蔽掉
    def return_key(self, event):
        line_column = self.editor_text.index('insert')  # 获取当前光标所在行号列号
        line, column = line_column.split(".")
        space_num = 0  # 空格个数
        index = 0

        while True:
            cha = self.editor_text.get(line + '.' + str(index), line + '.' + str(index + 1))
            if cha.isspace():
                space_num += 1
                index += 1
                continue
            break

        self.editor_text.insert("%s.%s" % (line, column), "\n" + " " * space_num)  # 插入空格
        return 'break'  # 阻断自身的换行操作

    def onFocusIn(self, event):
        """获取焦点事件"""
        path = self.control.getEditorText()["path"]
        # 过滤双击事件
        if self._dModifyFlag:
            return

        if not self._outFlag:
            return

        self._outFlag = False

        if path:
            modifyTime = os.path.getmtime(path)
            # 初始化self._modifyTime
            if self._modifyTime == 0:
                self._modifyTime = os.path.getmtime(path)
            if modifyTime == self._modifyTime:
                return

            if messagebox.askokcancel("重新加载", "此策略被另一个程序修改了\n是否重新加载？"):
                self.control.setEditorTextCode(path)
                editorCode = self.control.getEditorText()["code"]
                self.editor_text.delete(0.0, END + "-1c")
                self.updateEditorText(editorCode)
                # self.editor_text.edit_reset()

    def onFocusOut(self, event):
        self._outFlag = True
        path = self.control.getEditorText()["path"]
        if path:
            self._modifyTime = os.path.getmtime(path)

    def buttonDown(self, event):
        """鼠标按下记录按下位置"""
        self.start = self.editor_text.index('@%s, %s' % (event.x, event.y))

    def buttonUp(self, event):
        """鼠标释放记录释放位置"""
        self.stop = self.editor_text.index('@%s, %s' % (event.x, event.y))

        if float(self.start) > float(self.stop):
            self.start, self.stop = self.stop, self.start

    def insertEditorWidget(self, data):

        self.editor_text = EditorText(self.editor_text_frame, self, relief=FLAT, borderwidth=10,
                                      background=rgb_to_hex(255, 255, 255), wrap='none', undo=True)
        self.editor_text_scroll = self.addScroll(self.editor_text_frame, self.editor_text)
        self.editor_text.pack(fill=BOTH, expand=YES)
        # ctrl+s
        self.editor_text.bind("<Control-Key-S>", self.saveEditor)
        self.editor_text.bind("<Control-Key-s>", self.saveEditor)
        # tab
        self.editor_text.bind("<Tab>", self.tab_key)
        # 回车键
        # self.editor_text.bind("<Return>", self.return_key)

        # FocusIn
        self.editor_text.bind("<FocusIn>", self.onFocusIn)

        # FocusOut
        self.editor_text.bind("<FocusOut>", self.onFocusOut)

        # TODO：事件绑定有问题---回车键有bug
        # self.editor_text.bind("<Button-1>", self.buttonDown)
        # for e in ["<ButtonRelease-1>", "<Left>", "<Right>", "<Up>", "<Down>", "<Key>"]:
        #     self.editor_text.bind(e, self.buttonUp)

        self.updateEditorText(data)

    def load(self):
        # 发送信息
        path = self.control.getEditorText()["path"]
        if path:
            self.control.load(path)
            return
        messagebox.showinfo("提示", "未选择加载的策略")
