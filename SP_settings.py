# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SP_settings.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(250, 220)
        Dialog.setSizeGripEnabled(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.cb_parity = QtWidgets.QComboBox(Dialog)
        self.cb_parity.setObjectName("cb_parity")
        self.gridLayout.addWidget(self.cb_parity, 0, 1, 1, 1)
        self.dsb_timeout = QtWidgets.QDoubleSpinBox(Dialog)
        self.dsb_timeout.setPrefix("")
        self.dsb_timeout.setSuffix("")
        self.dsb_timeout.setDecimals(3)
        self.dsb_timeout.setSingleStep(0.001)
        self.dsb_timeout.setProperty("value", 0.05)
        self.dsb_timeout.setObjectName("dsb_timeout")
        self.gridLayout.addWidget(self.dsb_timeout, 3, 1, 1, 1)
        self.cb_bytesize = QtWidgets.QComboBox(Dialog)
        self.cb_bytesize.setObjectName("cb_bytesize")
        self.gridLayout.addWidget(self.cb_bytesize, 2, 1, 1, 1)
        self.l_read_timeout = QtWidgets.QLabel(Dialog)
        self.l_read_timeout.setObjectName("l_read_timeout")
        self.gridLayout.addWidget(self.l_read_timeout, 3, 0, 1, 1)
        self.l_stopbits = QtWidgets.QLabel(Dialog)
        self.l_stopbits.setObjectName("l_stopbits")
        self.gridLayout.addWidget(self.l_stopbits, 1, 0, 1, 1)
        self.cb_stopbits = QtWidgets.QComboBox(Dialog)
        self.cb_stopbits.setObjectName("cb_stopbits")
        self.gridLayout.addWidget(self.cb_stopbits, 1, 1, 1, 1)
        self.l_bytesize = QtWidgets.QLabel(Dialog)
        self.l_bytesize.setObjectName("l_bytesize")
        self.gridLayout.addWidget(self.l_bytesize, 2, 0, 1, 1)
        self.l_parity = QtWidgets.QLabel(Dialog)
        self.l_parity.setObjectName("l_parity")
        self.gridLayout.addWidget(self.l_parity, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Serial Port settings"))
        self.l_read_timeout.setText(_translate("Dialog", "Timeout (s)"))
        self.l_stopbits.setText(_translate("Dialog", "Stop bits"))
        self.l_bytesize.setText(_translate("Dialog", "Byte size"))
        self.l_parity.setText(_translate("Dialog", "Parity"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
