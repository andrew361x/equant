#-*-coding:utf-8
import threading
import tkinter as tk


class AlarmWin(tk.Toplevel):
    _instance_lock = threading.Lock()
    __instance = None
    __has_initialization = False

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls.__instance:
                cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, strategyId=None, strategyName=None, master=None):
        if not AlarmWin.__has_initialization:
            super().__init__(master)
            self._master = master
            self._textWgt = None
            self._textRecords = []
            self._onPage = 1
            self._pages = 1
            self._autoPages = True

            self._initImage()
            self._setPos(strategyId, strategyName)
            self._createFrames()
            AlarmWin.__has_initialization = True
            self.protocol("WM_DELETE_WINDOW", self._closeWin)
        # self.updateTextRecords(text)
        #
        # if self._autoPages:
        #     self.updateOnPage()
        #     self._insertSpecificPageText(text)
        # self.updatePages()
        # self._updatePagesLabel()
        # self.update()

    def __call__(self, new_text):
        # self._textRecords.append(new_text)
        self.showAlarm()
        self.updateTextRecords(new_text)

        if self._autoPages:
            self.updateOnPage()
            self._insertSpecificPageText(new_text)
        self.updatePages()
        self._updatePagesLabel()
        self.update()

    def showAlarm(self):
        self.update()
        self.deiconify()

    def _closeWin(self):
        self.withdraw()
        # return
        # self.rebuild()
        # self.destroy()

    def _initImage(self):
        self.topImage1 = r'./icon/top1.gif'
        self.btmImage1 = r'./icon/bottom1.gif'
        self.befImage1 = r'./icon/before1.gif'
        self.nxtImage1 = r'./icon/next1.gif'

        self.topImage2 = r'./icon/top2.gif'
        self.btmImage2 = r'./icon/bottom2.gif'
        self.befImage2 = r'./icon/before2.gif'
        self.nxtImage2 = r'./icon/next2.gif'

    def _setPos(self, strategyId, strategyName):
        self.title(f"下单提醒-{strategyId}-{strategyName}")
        icon = r'./icon/epolestar ix2.ico'
        self.iconbitmap(bitmap=icon)
        self.bitmap = icon
        #
        self.wm_attributes("-toolwindow", 1)
        self.wm_attributes("-topmost", 1)
        self.wm_resizable(0, 0)

        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()

        #计算窗口位置
        w, h = 400, 400
        x = ws/2 - w/2
        y = hs/2 - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        # self.minsize(400, 400)

    def _createFrames(self):
        textFrame = tk.Frame(self, width=400, height=370)
        textFrame.pack(side=tk.TOP, padx=1)
        textFrame.pack_propagate(False)
        btnFrame = tk.Frame(self, width=400, height=30, padx=1)
        btnFrame.pack(side=tk.TOP, padx=1)
        textFrame.pack_propagate(False)
        self._createTextWgt(textFrame)
        self._createBtn(btnFrame)

    def _createTextWgt(self, frame):
        self.textWgt = tk.Text(frame, bg="black")
        self.textWgt.config(state="disabled", font=("Consolas", 16), fg="white")
        self.textWgt.pack(fill=tk.BOTH, expand=tk.YES)

    def _insertSpecificPageText(self, text):
        self.textWgt.config(state="normal")
        self.textWgt.delete(0.0, "end" + "-1c")
        self.textWgt.insert(tk.END, text)
        self.textWgt.see(tk.END)
        self.textWgt.config(state="disabled")

    def _createBtn(self, frame):
        topImage1 = tk.PhotoImage(file=self.topImage1)
        btmImage1 = tk.PhotoImage(file=self.btmImage1)
        befImage1 = tk.PhotoImage(file=self.befImage1)
        nxtImage1 = tk.PhotoImage(file=self.nxtImage1)

        self.topBtn = tk.Label(frame, text="top", image=topImage1)
        self.btmBtn = tk.Label(frame, text="bottom", image=btmImage1)
        self.befBtn = tk.Label(frame, text="before", image=befImage1)
        self.nxtBtn = tk.Label(frame, text="next", image=nxtImage1)
        self.pageLabel = tk.Label(frame, text="%d/%d" % (self._onPage, self._pages))

        self.topBtn.pack(side=tk.LEFT, padx=4, pady=4)
        self.befBtn.pack(side=tk.LEFT, padx=4, pady=4)
        self.pageLabel.pack(side=tk.LEFT, padx=4, pady=4)
        self.nxtBtn.pack(side=tk.LEFT, padx=4, pady=4)
        self.btmBtn.pack(side=tk.LEFT, padx=4, pady=4)

        self.topBtn.bind("<Button-1>", self._toTop)
        self.btmBtn.bind("<Button-1>", self._toBottom)
        self.befBtn.bind("<Button-1>", self._toBefore)
        self.nxtBtn.bind("<Button-1>", self._toNext)

        self.topBtn.image = topImage1
        self.btmBtn.image = btmImage1
        self.befBtn.image = befImage1
        self.nxtBtn.image = nxtImage1

    def _updatePagesLabel(self):
        self.pageLabel.config(text="%d/%d" % (self._onPage, self._pages))

    def updateOnPage(self):
        self._onPage = len(self._textRecords)

    def updateTextRecords(self, text):
        self._textRecords.append(text)

    def updatePages(self):
        self._pages = len(self._textRecords)
        if self._onPage == self._pages:
            for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage2, self.btmImage2]):
                self._setBtnImage(wgt, image)
            if self._onPage == 1:
                for wgt, image in zip([self.topBtn, self.befBtn], [self.topImage2, self.befImage2]):
                    self._setBtnImage(wgt, image)
            else:
                for wgt, image in zip([self.topBtn, self.befBtn], [self.topImage1, self.befImage1]):
                    self._setBtnImage(wgt, image)
        else:
            for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage1, self.btmImage1]):
                self._setBtnImage(wgt, image)

    def _toTop(self, event):
        self._onPage = 1
        self._autoPages = False
        for wgt, image in zip([self.topBtn, self.befBtn], [self.topImage2, self.befImage2]):
            self._setBtnImage(wgt, image)
        if self._onPage != self._pages:
            for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage1, self.btmImage1]):
                self._setBtnImage(wgt, image)

        self._updatePagesLabel()
        self._insertSpecificPageText(self._textRecords[self._onPage-1])

    def _toBottom(self, event):
        self._autoPages = True
        self._onPage = len(self._textRecords)
        # if self._onPage != self._onPage:
        if self._onPage != 1:
            for wgt, image in zip([self.topBtn, self.befBtn], [self.topImage1, self.befImage1]):
                self._setBtnImage(wgt, image)

        for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage2, self.btmImage2]):
            self._setBtnImage(wgt, image)
        self._updatePagesLabel()
        self._insertSpecificPageText(self._textRecords[self._onPage-1])

    def _toBefore(self, event):
        # 在最左侧的情况
        self._autoPages = False
        if self._onPage != 1:
            self._onPage -= 1
        if self._onPage == 1:
            for wgt, image in zip([self.befBtn, self.topBtn], [self.befImage2, self.topImage2]):
                self._setBtnImage(wgt, image)
        if self._pages != 1:
            for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage1, self.btmImage1]):
                self._setBtnImage(wgt, image)

        self._updatePagesLabel()
        self._insertSpecificPageText(self._textRecords[self._onPage-1])

    def _toNext(self, event):
        if self._onPage < self._pages:
            self._onPage += 1
        if self._onPage == self._pages:
            for wgt, image in zip([self.nxtBtn, self.btmBtn], [self.nxtImage2, self.btmImage2]):
                self._setBtnImage(wgt, image)
            if self._onPage != 1:
                for wgt, image in zip([self.befBtn, self.topBtn], [self.befImage1, self.topImage1]):
                    self._setBtnImage(wgt, image)
        # if self._pages != self._onPage:
        #     for wgt, image in zip([self.befBtn, self.topBtn], [self.befImage1, self.topImage1]):
        #         self._setBtnImage(wgt, image)

        self._updatePagesLabel()
        self._insertSpecificPageText(self._textRecords[self._onPage-1])

    def _setBtnImage(self, widget, image):
        iimage = tk.PhotoImage(file=image)
        widget.config(image=iimage)
        widget.image = iimage

    @classmethod
    def rebuild(cls):
        cls.__instance = None
        cls.__has_initialization = False


def createAlarmWin(text, strategyId=None, strategyName=None):
    A = AlarmWin(strategyId, strategyName)
    if text:
        A(text)



