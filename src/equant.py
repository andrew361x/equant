from ui.control import TkinterController
from utils.logger import Logger
from multiprocessing import Process, Manager, Queue
from engine.engine import StrategyEngine
from capi.py2c import PyAPI
import time
import sys
import requests
import os
import traceback

sys.path.append(".")
sys.path.append("./ui")

VERSION = ""

#URL = "https://raw.githubusercontent.com/fanliangde/equant/master/VerNo.txt"
URL = "https://gitee.com/epolestar/equant/raw/master/VerNo.txt"

def run_log_process(logger):
    logger.run()

def run_engine_process(engine):
    engine.run()

def checkUpdate(logger):
    try:
        if os.path.exists('../VerNo.txt'):
            with open('../VerNo.txt', 'r') as f:
                VERSION = f.read()
        
            lvl = VERSION.split('.')[:-1]
            lmv =  '.'.join(lvl)
        
        rsp = requests.get(URL, timeout=10)
        if rsp.status_code == 200:
            rvstr = rsp.content.decode('utf-8')
            rvl = rvstr.split('.')[:-1]
            rmv = '.'.join(rvl)
            
        logger.info("Start epolestar, version info, equant local version: %s, remote version: %s!" %(VERSION, rvstr))
            
        if (len(lmv) == len(rmv) > 0 and rmv > lmv) or ( 0 < len(lmv) != len(rmv)):
                logger.info("Version need update local: %s, remote: %s" %(lmv, rmv))
                time.sleep(3)
                cmdstr = '"start %s %s.0"' %(os.path.abspath("..") + "\\update.bat ", rmv)
                logger.info("Update cmdstr:%s" %cmdstr)
                curDir = os.getcwd()
                os.chdir(os.path.abspath(os.path.join(curDir, "..")))
                os.system(cmdstr)
                os.chdir(curDir)
        else:
            logger.info("Version don't need update, local:%s, remote:%s" %(lmv, rmv))
    except Exception as e:
       logger.error("checkUpdate Error:%s" %(traceback.format_exc()))

def main():
    # 创建日志模块
    logger = Logger()
    log_process = Process(target=run_log_process, args=(logger,))
    log_process.start()

    # 检查软件更新
    checkUpdate(logger)

    # 创建策略引擎到界面的队列，发送资金数据
    eg2ui_q = Queue(10000)
    # 创建界面到策略引擎的队列，发送策略全路径
    ui2eg_q = Queue(10000)
    
    # 创建策略引擎
    engine = StrategyEngine(logger, eg2ui_q, ui2eg_q)
    engine_process = Process(target=run_engine_process, args=(engine,))
    engine_process.start()

    # 创建主界面
    app = TkinterController(logger, ui2eg_q, eg2ui_q)
    # 等待界面事件
    app.run()

    time.sleep(3)
    import atexit
    def exitHandler():
        # 1. 先关闭策略进程, 现在策略进程会成为僵尸进程
        # todo 此处需要重载engine的terminate函数
        # 2. 关闭engine进程
        engine_process.terminate()
        engine_process.join()
        log_process.terminate()
        log_process.join()
    atexit.register(exitHandler)
