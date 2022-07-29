# coding:utf-8

import random
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QStyleFactory, QStatusBar, QGraphicsEffect, QAction
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
import time

import serialport_widget
import ethernet_widget
import dialog_con_type
from Command_module import *
from utility import *
import new


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle('Connection Master v0.3.1')
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel('hello')
        self.status_bar_layout = QHBoxLayout()
        self.status_bar.setLayout(self.status_bar_layout)
        self.status_bar_layout.addWidget(self.status_label)

        self.file_menu = self.menuBar().addMenu('&File')
        self.view_menu = self.menuBar().addMenu("&View")
        self.con_type_menu = self.menuBar().addMenu("&Connection type")

        self.create_cmd_viewer_docker()
        self.create_con_interface()
        self.create_monitor_docker()
        # self.create_preselector_docker()
        self.create_urp_docker()
        self.create_status_bar()

        self.inteface_widget.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.inteface_widget.signal_info.connect(self.show_info, Qt.QueuedConnection)
        self.cmd_viewer.signal_bytes.connect(self.cmd_signal_byte_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal_info.connect(self.show_info, Qt.QueuedConnection)

        self.docker_urp.setVisible(False)
        self.docker_monitor.setVisible(False)

    def create_status_bar(self):
        self.file_menu.addAction(QIcon(r'icons/folder.svg'), 'Open', self.cmd_viewer.open_file_dialog,
                                 shortcut='Ctrl+O')
        self.file_menu.addAction(QIcon(r'icons/save.svg'), 'Save', self.cmd_viewer.save_file_changes, shortcut='Ctrl+S')
        self.file_menu.addAction(QIcon(r'icons/save.svg'), 'Save to..', self.cmd_viewer.save_to)
        self.file_menu.addSeparator()
        self.file_menu.addAction(QIcon(r'icons/x.svg'), 'Exit', self.close, shortcut='Ctrl+Q')
        self.con_type_menu.triggered.connect(self.set_new_con_interface)
        self.con_type_menu.addAction('Serial').setCheckable(True)
        self.con_type_menu.addAction('Ethernet').setCheckable(True)
        self.con_type_menu.actions()[0].setChecked(True)

    def create_con_interface(self):
        # popup window for choose connection type
        # self.settings_ui = dialog_con_type.Ui_Dialog()
        # self.settings_dialog = QDialog()
        # self.settings_ui.setupUi(self.settings_dialog)
        # self.settings_dialog.show()
        # self.inteface_widget = ethernet_widget.Widget()
        # state = self.settings_dialog.exec()
        # if state == QDialog.Accepted:
        #     if self.settings_ui.cb_parity.currentText() == 'Serial':
        #         self.inteface_widget = serialport_widget.Widget()
        self.inteface_widget = serialport_widget.Widget()
        self.setCentralWidget(self.inteface_widget)

    @pyqtSlot(QAction)
    def set_new_con_interface(self, action: QAction):
        for act in self.con_type_menu.actions():
            act.setChecked(False)
        action.setChecked(True)
        if self.inteface_widget.connection.is_open():
            self.inteface_widget.connection.close()
        self.inteface_widget.close()
        if action.text() == 'Ethernet':
            self.inteface_widget = ethernet_widget.Widget()
        elif action.text() == 'Serial':
            self.inteface_widget = serialport_widget.Widget()

        self.setCentralWidget(self.inteface_widget)

    def create_cmd_viewer_docker(self):
        self.cmd_viewer = CmdViewerWidget()
        self.docker_cmd_viewer = QDockWidget('Command viewer', self)
        self.docker_cmd_viewer.setWidget(self.cmd_viewer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_cmd_viewer)
        self.view_menu.addAction(self.docker_cmd_viewer.toggleViewAction())

    def create_monitor_docker(self):
        self.monitor = new.Monitor(count=3, names=['Out', 'LO1', 'LO2'])
        self.docker_monitor = QDockWidget('Temperature monitoring', self)
        self.docker_monitor.setWidget(self.monitor)
        self.monitor.set_left_lable('Temperature', '°C')
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_monitor)
        self.view_menu.addAction(self.docker_monitor.toggleViewAction())

    def create_preselector_docker(self):
        self.preselector = new.Preselector()
        self.docker_preselector = QDockWidget('Preselector ', self)
        self.docker_preselector.setWidget(self.preselector)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_preselector)
        self.view_menu.addAction(self.docker_preselector.toggleViewAction())

    def create_urp_docker(self):
        self.urp = new.URP()
        self.docker_urp = QDockWidget('URP', self)
        self.docker_urp.setWidget(self.urp)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_urp)
        self.view_menu.addAction(self.docker_urp.toggleViewAction())

    @pyqtSlot()
    def sp_signal_handling(self, signal):
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    @pyqtSlot(signal_cmd)
    def cmd_signal_byte_handling(self, signal: signal_cmd):
        if signal.name == 'send_cmd':
            self.inteface_widget.write(signal.value)

    def monitor_signal_handling(self):
        if self.inteface_widget.connection.is_open():
            try:
                temp_out = int(self.inteface_widget.write_read(b'\x00\x0A\x00')[2])
                temp_lo1 = int(self.inteface_widget.write_read(b'\x10\x0A\x00')[2])
                temp_lo2 = int(self.inteface_widget.write_read(b'\x11\x0A\x00')[2])
                self.monitor.appendData([temp_out, temp_lo1, temp_lo2])
            except:
                print("monitor_signal_handling: IndexError: index out of range")

    @pyqtSlot(signal_info)
    def show_info(self, signal: signal_info):
        if signal.font is None:
            self.status_bar.setFont(self.font())
        else:
            self.status_bar.setFont(signal.font)
        self.status_bar.showMessage(signal.text, 8000)

    @pyqtSlot()
    def closeEvent(self, event):
        if self.cmd_viewer.check_changes():
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
