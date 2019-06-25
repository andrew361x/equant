import logging
import sys,os
from multiprocessing import Queue, Process


class MyHandlerText(logging.StreamHandler):
    '''put log to Tkinter Text'''
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self) # initialize parent
        self.textctrl = textctrl

    def emit(self, record):
        msg = self.format(record)
        self.textctrl.config(state="normal")
        self.textctrl.insert("end", msg + "\n")
        self.flush()
        self.textctrl.config(state="disabled")


class MyHandlerQueue(logging.StreamHandler):
    def __init__(self, gui_queue, sig_queue, err_queue, trade_log):
        logging.StreamHandler.__init__(self)  # initialize parent
        self.gui_queue = gui_queue
        self.sig_queue = sig_queue
        self.err_queue = err_queue
        self.trade_log = trade_log

    def emit(self, record):
        #最多等待1秒
        # TODO: 先判断msg的消息体（json?)
        target = record.msg[1]
        record.msg = record.msg[0]
        msg = self.format(record)
        if target == 'S':
            self.sig_queue.put(msg, block=False, timeout=1)
        elif target == 'E':
            self.err_queue.put(msg, block=False, timeout=1)
        elif target == 'T':
            self.trade_log.write(msg+"\n")
            self.trade_log.flush()
        else:
            self.gui_queue.put(msg, block=False, timeout=1)


class Logger(object):
    def __init__(self):
        #process queue
        self.log_queue = Queue()
        self.gui_queue = Queue()
        # 信号队列
        self.sig_queue = Queue()
        self.err_queue = Queue()
        
    def _initialize(self):

        self.logpath = r"./log/"
        if not os.path.exists( self.logpath):
            os.makedirs( self.logpath) 
            
        #交易日志
        self.trade_log = open(self.logpath + "trade.dat", mode='a', encoding='utf-8')
        #self.trade_log.write('我在这儿')
        #self.trade_log.flush()

        #logger config
        self.logger = logging.getLogger("equant")
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("[%(levelname)7s][%(asctime)-15s]: %(message)s")

        self.level_dict = {"DEBUG":logging.DEBUG, "INFO":logging.INFO, "WARN":logging.WARN, "ERROR":logging.ERROR}
        self.level_func = {"DEBUG":self.logger.debug, "INFO":self.logger.info, "WARN": self.logger.warning, "ERROR": self.logger.error}
        
        self.add_handler()

    def run(self):
        #在子进程中做初始化，否则打印失效
        self._initialize()
        '''从log_queue中获取日志，刷新到文件和控件上'''
        while True:
            data_list = self.log_queue.get()
            if data_list is None: break
            #数据格式不对
            if len(data_list) !=3: continue
            self.level_func[data_list[0]](data_list[1:])

    def _log(self, level, target, s):
        data = []
        data.append(level)
        data.append(target)
        data.append(s)
        self.log_queue.put(data)

    def get_log_queue(self):
        return self.log_queue

    def getGuiQ(self):
        return self.gui_queue

    def getSigQ(self):
        return self.sig_queue

    def getErrQ(self):
        return self.err_queue

    def add_handler(self):
        #设置文件句柄
        file_handler = logging.FileHandler(self.logpath + "equant.log", mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        #设置窗口句柄
        gui_handler = MyHandlerQueue(self.gui_queue, self.sig_queue, self.err_queue, self.trade_log)
        gui_handler.setLevel(logging.DEBUG)
        gui_handler.setFormatter(self.formatter)
        self.logger.addHandler(gui_handler)
        #设置控制台句柄
        cout_handler = logging.StreamHandler(sys.stdout)
        cout_handler.setLevel(logging.DEBUG)
        cout_handler.setFormatter(self.formatter)
        self.logger.addHandler(cout_handler)

    def debug(self, s, target=""):
        self._log("DEBUG", s, target)

    def info(self, s, target=""):
        self._log("INFO", s, target)

    def warn(self, s, target=""):
        self._log("WARN", s, target)

    def error(self, s, target=""):
        self._log("ERROR", s, target)

    def sig_info(self, s, target='S'):
        self.info(s, target)
        
    def trade_info(self, s, target='T'):
        self.info(s, target)

    # 策略错误
    def err_error(self, s, target='E'):
        self.error(s, target)
