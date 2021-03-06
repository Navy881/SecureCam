# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(840, 511)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ImgWidget = QtWidgets.QWidget(self.centralwidget)
        self.ImgWidget.setGeometry(QtCore.QRect(9, 9, 571, 431))
        self.ImgWidget.setObjectName("ImgWidget")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(590, 420, 75, 23))
        self.startButton.setObjectName("startButton")
        self.closeButton = QtWidgets.QPushButton(self.centralwidget)
        self.closeButton.setGeometry(QtCore.QRect(750, 420, 75, 23))
        self.closeButton.setObjectName("closeButton")
        self.statusLabel = QtWidgets.QLabel(self.centralwidget)
        self.statusLabel.setGeometry(QtCore.QRect(590, 10, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.statusLabel.setFont(font)
        self.statusLabel.setObjectName("statusLabel")
        self.textField = QtWidgets.QTextBrowser(self.centralwidget)
        self.textField.setGeometry(QtCore.QRect(590, 80, 231, 211))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.textField.setFont(font)
        self.textField.setObjectName("textField")
        self.pauseButton = QtWidgets.QPushButton(self.centralwidget)
        self.pauseButton.setGeometry(QtCore.QRect(670, 420, 75, 23))
        self.pauseButton.setObjectName("pauseButton")
        self.timeLabel = QtWidgets.QLabel(self.centralwidget)
        self.timeLabel.setGeometry(QtCore.QRect(590, 40, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.timeLabel.setFont(font)
        self.timeLabel.setObjectName("timeLabel")
        self.edgesCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.edgesCheckBox.setEnabled(True)
        self.edgesCheckBox.setGeometry(QtCore.QRect(590, 330, 151, 23))
        self.edgesCheckBox.setObjectName("edgesCheckBox")
        self.signalCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.signalCheckBox.setGeometry(QtCore.QRect(590, 300, 141, 23))
        self.signalCheckBox.setObjectName("signalCheckBox")
        self.botStartButton = QtWidgets.QPushButton(self.centralwidget)
        self.botStartButton.setEnabled(True)
        self.botStartButton.setGeometry(QtCore.QRect(590, 390, 90, 23))
        self.botStartButton.setObjectName("botStartButton")
        self.nnDetectionCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.nnDetectionCheckBox.setEnabled(True)
        self.nnDetectionCheckBox.setGeometry(QtCore.QRect(590, 360, 151, 23))
        self.nnDetectionCheckBox.setObjectName("nnDetectionCheckBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 840, 31))
        self.menubar.setObjectName("menubar")
        self.parametersMenu = QtWidgets.QMenu(self.menubar)
        self.parametersMenu.setObjectName("parametersMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.parametersAction = QtWidgets.QAction(MainWindow)
        self.parametersAction.setObjectName("parametersAction")
        self.parametersMenu.addAction(self.parametersAction)
        self.menubar.addAction(self.parametersMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Detector"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.closeButton.setText(_translate("MainWindow", "Close"))
        self.statusLabel.setText(_translate("MainWindow", "Status"))
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.timeLabel.setText(_translate("MainWindow", "Time"))
        self.edgesCheckBox.setText(_translate("MainWindow", "Show red edges"))
        self.signalCheckBox.setText(_translate("MainWindow", "Hide video"))
        self.botStartButton.setText(_translate("MainWindow", "Start bot"))
        self.nnDetectionCheckBox.setText(_translate("MainWindow", "Object detection"))
        self.parametersMenu.setTitle(_translate("MainWindow", "Settings"))
        self.parametersAction.setText(_translate("MainWindow", "Parameters"))

