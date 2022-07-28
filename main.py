# coding:utf-8

import random
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QStyleFactory, QStatusBar, QGraphicsEffect
from PyQt5.QtCore import Qt, pyqtSignal
import time

import serialport_widget
import ethernet_widget
import dialog_con_type
from Command_module import *
from utility import *
import new

from loguru import logger

logger.debug("That's it, beautiful and simple logging!")
logger.add("log\\file_1.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB")


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
        self.con_type_menu = self.menuBar().addMenu("&Connection")

        self.create_cmd_viewer_docker()
        self.create_con_interface()
        self.cmd_creator = CmdCreatorWidget()
        self.create_monitor_docker()
        # self.create_preselector_docker()
        self.create_urp_docker()
        self.create_status_bar()

        self.con_driver.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.con_driver.signal_info.connect(self.show_info, Qt.QueuedConnection)
        self.cmd_creator.signal_cmd.connect(self.cmd_viewer.add_cmd, Qt.QueuedConnection)
        self.cmd_viewer.signal_bytes.connect(self.cmd_signal_byte_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.add_cmd_btn.clicked.connect(self.open_cmd_creator)
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
        #self.con_type_menu.addAction()

    def open_cmd_creator(self):
        self.cmd_creator.show()
        self.cmd_creator.resize(600, 600)

    def create_con_interface(self):
        self.settings_ui = dialog_con_type.Ui_Dialog()
        self.settings_dialog = QDialog()
        self.settings_ui.setupUi(self.settings_dialog)
        self.settings_dialog.show()
        self.con_driver = ethernet_widget.Widget()
        state = self.settings_dialog.exec()
        if state == QDialog.Accepted:
            if self.settings_ui.cb_parity.currentText() == 'Serial':
                self.con_driver = serialport_widget.Widget()
        self.setCentralWidget(self.con_driver)


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

    def sp_signal_handling(self, signal):
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    def cmd_signal_byte_handling(self, signal):
        if signal.name == 'send_cmd':
            self.con_driver.write(signal.value)

    def monitor_signal_handling(self):
        if self.con_driver.connection.is_open():
            try:
                temp_out = int(self.con_driver.write_read(b'\x00\x0A\x00')[2])
                temp_lo1 = int(self.con_driver.write_read(b'\x10\x0A\x00')[2])
                temp_lo2 = int(self.con_driver.write_read(b'\x11\x0A\x00')[2])
                self.monitor.appendData([temp_out, temp_lo1, temp_lo2])
            except:
                print("monitor_signal_handling: IndexError: index out of range")

    def cmd_signal_handling(self, signal):
        print(signal.name)
        if signal.name == 'edit_cmd':
            self.cmd_creator.edit_cmd(signal.value[0], dict([signal.value]))
            self.cmd_creator.show()

    def show_info(self, signal: signal_info):
        if signal.font is None:
            self.status_bar.setFont(self.font())
        else:
            self.status_bar.setFont(signal.font)
        self.status_bar.showMessage(signal.text, 8000)

    def closeEvent(self, event):
        if self.cmd_viewer.check_changes():
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
