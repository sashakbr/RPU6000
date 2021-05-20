import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QStyleFactory
from PyQt5.QtCore import Qt, pyqtSignal
import time

import SerialPortDriver
from Command_module import *
from utility import *

from loguru import logger

logger.debug("That's it, beautiful and simple logging!")
logger.add("log\\file_1.log", format="{time} {level} {message}", level="DEBUG", rotation="2 MB")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle('Com Client Gen3')

        self.file_menu = self.menuBar().addMenu('&File')
        self.view_menu = self.menuBar().addMenu("&View")

        self.create_sp()
        self.create_cmd_viewer_docker()
        self.cmd_creator = CmdCreatorWidget()

        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.cmd_creator.signal_cmd.connect(self.cmd_viewer.add_cmd, Qt.QueuedConnection)
        self.cmd_viewer.signal_bytes.connect(self.cmd_signal_byte_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.add_cmd_btn.clicked.connect(self.open_cmd_creator)

        self.file_menu.addAction(QIcon('icons\\folder.svg'), 'Open', self.cmd_viewer.open_file_dialog, shortcut='Ctrl+O')
        self.file_menu.addAction(QIcon('icons\\save.svg'), 'Save', self.cmd_viewer.save_file_changes, shortcut='Ctrl+S')
        self.file_menu.addAction(QIcon('icons\\save.svg'), 'Save to..', self.cmd_viewer.save_to)
        self.file_menu.addSeparator()
        self.file_menu.addAction(QIcon('icons\\x.svg'), 'Exit', self.close, shortcut='Ctrl+Q')

    def open_cmd_creator(self):
        self.cmd_creator.show()
        self.cmd_creator.resize(600, 600)

    def create_sp(self):
        self.sp = SerialPortDriver.SP()
        self.setCentralWidget(self.sp)

    def create_cmd_viewer_docker(self):
        self.cmd_viewer = CmdViewerWidget()
        self.docker_cmd_viewer = QDockWidget('Command viewer', self)
        self.docker_cmd_viewer.setWidget(self.cmd_viewer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_cmd_viewer)
        self.view_menu.addAction(self.docker_cmd_viewer.toggleViewAction())

    def sp_signal_handling(self, signal):
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    def cmd_signal_byte_handling(self, signal):
        if signal.name == 'send_cmd':
            read_cmd = self.sp.write_read(signal.value, len(signal.value))
            if self.sp.cb_parsing.isChecked():
                self.sp.log_info(
                    cmd_parser(read_cmd, self.cmd_viewer.cmd_data, command_num_position=signal.position), 'black')

    def cmd_signal_handling(self, signal):
        print(signal.name)
        if signal.name == 'edit_cmd':
            self.cmd_creator.edit_cmd(signal.value[0], dict([signal.value]))
            self.cmd_creator.show()

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
