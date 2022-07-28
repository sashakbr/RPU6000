from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):

    def ok_clicked(self):
        self.Dialog.accept()


    def setupUi(self, Dialog):
        self.Dialog = Dialog
        self.Dialog.setObjectName("Dialog")
        Dialog.resize(170, 90)
        self.Dialog.setSizeGripEnabled(False)
        self.Dialog.setWindowTitle('Connection type')
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cb_parity = QtWidgets.QComboBox(Dialog)
        self.cb_parity.addItems(('Serial', 'Ethernet'))
        self.verticalLayout.addWidget(self.cb_parity)
        self.buttonBox = QtWidgets.QPushButton('Ok')
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.buttonBox.clicked.connect(self.ok_clicked)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
