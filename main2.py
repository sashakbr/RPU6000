import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QStyleFactory, QStatusBar, QGraphicsEffect
from PyQt5.QtCore import Qt, pyqtSignal
import time

import SerialPortDriver2
from Command_module import *
from utility import *
import new

from loguru import logger

logger.debug("That's it, beautiful and simple logging!")
logger.add("log\\file_1.log", format="{time} {level} {message}", level="DEBUG", rotation="2 MB")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle('Com Client Gen3')
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_lable = QLabel('hello')
        self.status_bar_layout = QHBoxLayout()
        self.status_bar.setLayout(self.status_bar_layout)
        self.status_bar_layout.addWidget(self.status_lable)

        self.file_menu = self.menuBar().addMenu('&File')
        self.view_menu = self.menuBar().addMenu("&View")

        self.create_sp()
        self.create_cmd_viewer_docker()
        self.cmd_creator = CmdCreatorWidget()
        self.create_monitor_docker()

        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.sp.signal_info.connect(self.show_info, Qt.QueuedConnection)
        self.cmd_creator.signal_cmd.connect(self.cmd_viewer.add_cmd, Qt.QueuedConnection)
        self.cmd_viewer.signal_bytes.connect(self.cmd_signal_byte_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.add_cmd_btn.clicked.connect(self.open_cmd_creator)
        self.cmd_viewer.signal_info.connect(self.show_info, Qt.QueuedConnection)

        self.file_menu.addAction(QIcon('icons\\folder.svg'), 'Open', self.cmd_viewer.open_file_dialog, shortcut='Ctrl+O')
        self.file_menu.addAction(QIcon('icons\\save.svg'), 'Save', self.cmd_viewer.save_file_changes, shortcut='Ctrl+S')
        self.file_menu.addAction(QIcon('icons\\save.svg'), 'Save to..', self.cmd_viewer.save_to)
        self.file_menu.addSeparator()
        self.file_menu.addAction(QIcon('icons\\x.svg'), 'Exit', self.close, shortcut='Ctrl+Q')

    def open_cmd_creator(self):
        self.cmd_creator.show()
        self.cmd_creator.resize(600, 600)

    def create_sp(self):
        self.sp = SerialPortDriver2.SP2()
        self.setCentralWidget(self.sp)

    def create_cmd_viewer_docker(self):
        self.cmd_viewer = CmdViewerWidget()
        self.docker_cmd_viewer = QDockWidget('Command viewer', self)
        self.docker_cmd_viewer.setWidget(self.cmd_viewer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_cmd_viewer)
        self.view_menu.addAction(self.docker_cmd_viewer.toggleViewAction())

    def create_monitor_docker(self):
        self.monitor = new.Monitor()
        self.docker_monitor = QDockWidget('Monitor', self)
        self.docker_monitor.setWidget(self.monitor)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_monitor)
        self.view_menu.addAction(self.docker_monitor.toggleViewAction())

    def sp_signal_handling(self, signal):
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    def cmd_signal_byte_handling(self, signal):
        if signal.name == 'send_cmd':
            self.sp.write(signal.value)

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
