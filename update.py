import os
import shutil
import requests
import zipfile

#equantUrl    = "https://github.com/epolestar/equant/archive/master.zip"
equantUrl    = "https://github.com/fanliangde/equant/archive/master.zip"
#epolestarUrl = "https://epolestar-master-1255628687.cos.ap-beijing.myqcloud.com/epolestar.zip"
epolestarUrl = "https://epolestar95-1255628687.cos.ap-beijing.myqcloud.com/epolestar.zip"

urls         = [equantUrl, epolestarUrl]
tags         = ["equant", "epolestar"]
zipname      = ["equant.zip", "epolestar.zip"]


# 脚本所在路径
dirPath = os.getcwd()

# 工作路径(appdata所在路径)
# appPath = os.getenv("APPDATA")
if not os.path.exists(os.path.abspath(os.path.join(dirPath, "..\\equant_backups"))):
    os.makedirs(os.path.join(dirPath, "..\\equant_backups"))
os.chdir(os.path.abspath(os.path.join(dirPath, "..\\equant_backups")))

workDir = os.getcwd()

styPath = os.path.join(workDir, "equant-master\\src\\strategy")
cfgPath = os.path.join(workDir, "equant-master\\src\\config")
logPath = os.path.join(workDir, "equant-master\\src\\log")

tempPath1 = os.path.join(dirPath, "src\\strategy")
tempPath2 = os.path.join(dirPath, "src\\config")
tempPath3 = os.path.join(dirPath, "src\\log")


# 备份用户原来文件
def backup(directory, des):
    if os.path.exists(des):
        os.system('rmdir /S /Q "{}"'.format(des))


    if os.path.exists(directory):
        os.system(f"xcopy {directory} {des} /y /e /i /h")
        print("%s 备份成功！" % directory)
        return 1
    else:
        print("Equant or Equant-master directory dosen't exist!")
        return 0


# 关9.5
def killProcess():
    curPid = os.getpid()

    # print("kill")
    # 关掉python进程
    if "python.exe" in os.popen('tasklist /FI "IMAGENAME eq python.exe"').read():
        os.system('taskkill /f /fi "IMAGENAME eq python.exe" /fi "PID ne %d"' % curPid)
    # 关掉9.5进程
    if "epolestar v9.5.exe" in os.popen('tasklist /fi "IMAGENAME eq %s"' % "epolestar v9.5.exe").read():
        # os.system("taskkill /f /im %s" % "epolestar v9.5.exe")
        os.system('taskkill /f /fi "IMAGENAME eq %s"' % "epolestar v9.5.exe")


# 根据版本号判断是否更新
def isNeedUpdate(versionNo):
    with open(os.path.join(dirPath, "update.ini"), 'r') as f:
        context = f.readlines()
        oldVer = context[1][4:]
        if versionNo == oldVer:
            return 1
    return 0


def requestZip(zipUrl, tag):
    """下载"""
    try:
        response = requests.get(zipUrl, timeout=5)
        print("%s download successfully!"%tag)
        response.raise_for_status()
        with open (tag+".zip", "wb") as f:
            f.write(response.content)
        return 1
    except Exception as e:
        print(tag, ":", "There is a exception %s when downloading file!" % (e))
        return 0


def zipFile(filename):
    """解压"""
    if not zipfile.is_zipfile(filename):
        print("%s is not an .zip file" % filename)
        return

    z = zipfile.ZipFile(filename)
    z.extractall()
    print("%s unzip successfully!" % filename)
    z.close()


def delzip(filename):
    """删除"""
    if os.path.exists(filename):
        os.remove(filename)
        print("Delete %s successfully!" % filename)


def delFile(path):
    if os.path.exists(path):
        print('%s存在先删除' % path)
        shutil.rmtree(path, onerror=readonly_handler)
        return 1
    return 0


# 移动文件
def mergeFile(src, dst):
    """

    :param src: 源路径
    :param dst: 目标路径
    :return:
    """
    if not os.path.exists(src):
        return

    if not os.path.exists(dst):
        os.makedirs(dst)

    for sf in os.listdir(src):

        sfPath = os.path.join(src, sf)
        dfPath = os.path.join(dst, sf)

        if os.path.isdir(sfPath):
            if os.path.basename(sfPath) == "__pycache__":
                continue

            if os.path.exists(dfPath):
                mergeFile(sfPath, dfPath)
            else:
                print("Copy %s ===> %s"%(sfPath, dfPath))
                #shutil.copyfile(sfPath, dfPath)
                os.system(f"xcopy {sfPath} {dfPath} /y /e /i /h ")
        elif os.path.isfile(sfPath):
            if os.path.exists(dfPath):
                # shutil.copyfile(sfPath, dfPath)
                os.system(f"xcopy {sfPath} {dfPath} /y /e /i /h")
                print("Cover %s ===> %s" % (sfPath, dfPath))
            else:
                # shutil.copy2(sfPath, dfPath)
                shutil.copy(sfPath, dfPath)
                #os.system(f"xcopy {sfPath} {dfPath} /y /e /i /h")
                print("copy %s ===> %s" % (sfPath, dfPath))

def readonly_handler(func, path, ececinfo):
    os.chmod(path, 128)
    func(path)


def main():
    inp = input("升级前请关闭极星9.5客户端和量化终端，否则将更新失败\n"
                "更新会覆盖本地代码，请做好备份。确认是否升级(y/n): ")
    if inp == 'y' or inp == 'Y':  # 确认升级
        # killProcess()

        # 下载
        for url, tag in zip(urls, tags):
            print("开始下载%s" % tag)
            reqRlt = requestZip(url, tag)
            if reqRlt == 0:   # 下载失败
                 print("下载过程出错，请重新尝试！")
                 return
				 
		
        # 解压并删除压缩包
        for name in zipname:
            zipFile(name)
            delzip(name)

        # 备份文件
        for directory, dest in zip([dirPath, os.path.abspath(os.path.join(dirPath, "..\\epolestar"))],
                                   [os.path.join(workDir, "equant_back"), os.path.join(workDir, "epolestar_back")]):
            bacRlt = backup(directory, dest)
            if bacRlt == 0:    # 路径不存在
                print("备份数据过程出错！")
                return

        # 删除旧版本中的代码部分，保留config, strategy, log文件夹
        for file in os.listdir(os.path.join(dirPath, "src")):
            if file not in ["config", "log", "strategy"]:
                path = os.path.join(dirPath, "src\\%s" % file)
                if os.path.isdir(path):
                    delRet = delFile(path)
                    if delRet == 0:
                        print("%s 文件删除失败！" % path)
                        return
                if os.path.isfile(path):
                    os.remove(path)

        # 删除9.5客户端
        delFile(os.path.abspath(os.path.join(dirPath, "..\\epolestar")))

        src = os.path.join(workDir, "epolestar")
        des = os.path.abspath(os.path.join(dirPath, "..\\epolestar"))
        os.system(f"xcopy {src} {des} /y /e /i /h")

        # 合并config, strategy, log去重
        # TODO：会不会存在合并出错情况
        for src, dst in zip([styPath, cfgPath, logPath],
                            [tempPath1, tempPath2, tempPath3]):
            mergeFile(src, dst)

        # 将最新的代码拷贝到原目录中
        for file in os.listdir(os.path.join(workDir, "equant-master\\src")):
            if file not in ["config", "log", "strategy"]:
                spath = os.path.join(workDir, "equant-master\\src\\%s" % file)
                dpath = os.path.join(dirPath, "src\\%s" % file)
                if os.path.isdir(spath):
                    mergeFile(spath, dpath)
                if os.path.isfile(spath):
                    shutil.copy(spath, dpath)
                    # os.system(f"xcopy {spath} {dpath} /y /e /i /h")

        # 删除现场
        # os.chdir(dirPath)
        # os.system('rmdir /S /Q "{}"'.format(workDir))

        print("更新完成！")

if __name__ == '__main__':
    main()
















