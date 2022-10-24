# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Auth(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Авторизация")
        MainWindow.resize(380, 140)
        MainWindow.setMinimumSize(QtCore.QSize(380, 140))
        MainWindow.setMaximumSize(QtCore.QSize(380, 140))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(15, 10, 351, 121))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 331, 101))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.login = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.login.setStyleSheet("")
        self.login.setInputMask("")
        self.login.setDragEnabled(False)
        self.login.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.login.setClearButtonEnabled(False)
        self.login.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.login)
        self.password = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.password.setObjectName("lineEdit_2")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.password)
        self.login_vk = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.login_vk.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.login_vk)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Авторизация"))
        self.login.setPlaceholderText(_translate("MainWindow", "Логин"))
        self.password.setPlaceholderText(_translate("MainWindow", "Пароль"))
        self.login_vk.setText(_translate("MainWindow", "Войти"))

