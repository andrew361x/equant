# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'contractSelect.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_contractSelect(object):
    def setupUi(self, contractSelect):
        contractSelect.setObjectName("contractSelect")
        contractSelect.resize(740, 525)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(contractSelect.sizePolicy().hasHeightForWidth())
        contractSelect.setSizePolicy(sizePolicy)
        contractSelect.setMinimumSize(QtCore.QSize(740, 525))
        contractSelect.setMaximumSize(QtCore.QSize(740, 525))
        self.centralwidget = QtWidgets.QWidget(contractSelect)
        self.centralwidget.setObjectName("centralwidget")
        self.contract_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.contract_tree.setGeometry(QtCore.QRect(10, 10, 211, 451))
        self.contract_tree.setObjectName("contract_tree")
        self.contract_tree.headerItem().setText(0, "1")
        self.contract_child_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.contract_child_tree.setGeometry(QtCore.QRect(230, 10, 211, 451))
        self.contract_child_tree.setObjectName("contract_child_tree")
        self.contract_child_tree.headerItem().setText(0, "1")
        self.choice_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.choice_tree.setGeometry(QtCore.QRect(450, 10, 281, 451))
        self.choice_tree.setObjectName("choice_tree")
        self.choice_tree.headerItem().setText(0, "1")
        self.confirm = QtWidgets.QPushButton(self.centralwidget)
        self.confirm.setGeometry(QtCore.QRect(530, 478, 60, 25))
        self.confirm.setObjectName("confirm")
        self.cancel = QtWidgets.QPushButton(self.centralwidget)
        self.cancel.setGeometry(QtCore.QRect(620, 478, 60, 25))
        self.cancel.setObjectName("cancel")
        contractSelect.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(contractSelect)
        self.statusbar.setObjectName("statusbar")
        contractSelect.setStatusBar(self.statusbar)

        self.retranslateUi(contractSelect)
        QtCore.QMetaObject.connectSlotsByName(contractSelect)

    def retranslateUi(self, contractSelect):
        _translate = QtCore.QCoreApplication.translate
        contractSelect.setWindowTitle(_translate("contractSelect", "选择合约"))
        self.confirm.setText(_translate("contractSelect", "确定"))
        self.cancel.setText(_translate("contractSelect", "取消"))
