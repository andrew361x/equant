import tkinter as tk
import tkinter.ttk as ttk


class CollapsibleFrame(tk.Frame):
    def __init__(self, parent, labelText, column, heading, height):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self._isOpend = True

        self.upImage = r'./icon/up.gif'
        self.downImage = r'./icon/down.gif'

        header = tk.Frame(self)
        self.graphFrame = tk.Frame(self, relief=tk.FLAT, borderwidth=1)

        header.pack(side=tk.TOP, fill=tk.X)
        self.graphFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = tk.Label(header, text=labelText, bg='#2c6ead', fg='white')
        iimage = tk.PhotoImage(file=self.upImage)
        self.toggleLabel = tk.Label(header, bg='#2c6ead', height=19, width=20, image=iimage)
        self.toggleLabel.image = iimage
        self.toggleLabel.bind("<Button-1>", self.toggle)
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.toggleLabel.pack(side=tk.LEFT)

        self.statisTree = ttk.Treeview(self.graphFrame, columns=column, height=height, selectmode="browse",
                                       show=["headings"], style="Filter.Treeview")

        vbar = tk.Scrollbar(self.graphFrame, orient='vertical')
        vbar.config(command=self.statisTree.yview)
        self.statisTree.config(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.statisTree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for c, head in zip(column, heading):
            self.statisTree.column(c, width=20, anchor="center")
            self.statisTree.heading(c, text=head)

    def toggle(self, event=None):
        if self._isOpend:
            image = tk.PhotoImage(file=self.upImage)
            self.graphFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.toggleLabel.configure(image=image)
            self.toggleLabel.image = image
            self._isOpend = False
        else:
            image = tk.PhotoImage(file=self.downImage)
            self.toggleLabel.configure(image=image)
            self.toggleLabel.image = image
            self.graphFrame.pack_forget()
            self._isOpend = True


def main():
    root = tk.Tk()
    root.geometry("800x600+200+200")

    list_1 = ['年度分析', '季度分析', '月度分析', '周分析', '日分析']

    column = ('a', 'b', 'c', 'd', 'e', 'f', 'g')
    heading = ('日期', '权益', '净利润', '盈利率', '胜率', '平均盈利/亏损', '净利润增长速度')

    aa = [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 1], [3, 1, 1, 1, 1, 1, 1],
          [4, 1, 1, 1, 1, 1, 1], [5, 1, 1, 1, 1, 1, 1], [6, 1, 1, 1, 1, 1, 1], [7, 1, 1, 1, 1, 1, 1],
          [8, 1, 1, 1, 1, 1, 1], [9, 1, 1, 1, 1, 1, 1], [10, 1, 1, 1, 1, 1, 1], [11, 1, 1, 1, 1, 1, 1],
          [12, 1, 1, 1, 1, 1, 1], [13, 1, 1, 1, 1, 1, 1], [14, 1, 1, 1, 1, 1, 1], [15, 1, 1, 1, 1, 1, 1],
          [16, 1, 1, 1, 1, 1, 1], [17, 1, 1, 1, 1, 1, 1]]

    for label, h in zip(list_1, [1, 1, 2, 3, 5]):
        frame = CollapsibleFrame(root, label, column, heading, h)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        # frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        for a in aa:
            frame.statisTree.insert('', 'end', values=a)

    root.mainloop()


if __name__ == "__main__":
    main()