"""
Common class for load qss style
"""
class CommonHelper(object):
    def __init__(self):
        pass

    @staticmethod
    def readQss(stylePath):
        with open(stylePath, 'r', encoding="utf-8") as f:
            return f.read()