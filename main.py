import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QStyleFactory
from PyQt5.QtCore import Qt, pyqtSignal
import time

import SerialPortDriver
from Command_module import *
from utility import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.view_menu = self.menuBar().addMenu("&View")
        self.create_sp()
        self.create_cmd_viewer_docker()
        self.cmd_creator = CmdCreatorWidget()
        #self.create_cmd_creator_docker()
        # self.setWindowIcon(QIcon('icons\\command.svg.svg'))
        self.setWindowTitle('Com Client Pro Edition LUXURY')
        #self.tabifyDockWidget(self.docker_cmd_creator, self.docker_cmd_viewer)
        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.cmd_creator.signal.connect(self.cmd_creator_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.add_cmd_btn.clicked.connect(self.open_creator)

    def open_creator(self):
        self.cmd_creator.show()

    def create_sp(self):
        self.sp = SerialPortDriver.SP()
        self.setCentralWidget(self.sp)

    def create_cmd_viewer_docker(self):
        self.cmd_viewer = CmdViewerWidget()
        self.docker_cmd_viewer = QDockWidget('Command viewer', self)
        self.docker_cmd_viewer.setWidget(self.cmd_viewer)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_cmd_viewer)
        self.view_menu.addAction(self.docker_cmd_viewer.toggleViewAction())

    def create_cmd_creator_docker(self):
        self.cmd_creator = CmdCreatorWidget()
        self.docker_cmd_creator = QDockWidget('Command creator', self)
        self.docker_cmd_creator.setWidget(self.cmd_creator)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docker_cmd_creator)
        self.view_menu.addAction(self.docker_cmd_creator.toggleViewAction())

    def sp_signal_handling(self, signal):
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    def cmd_signal_handling(self, signal):
        if signal.name == 'send_cmd':
            read_cmd = self.sp.write_read(signal.value, len(signal.value))
            pref = self.cmd_viewer.prefix_check.isChecked()
            self.sp.log_info(cmd_parser(read_cmd, self.cmd_viewer.cmd_data, is_prefix_on=pref), 'black')

    def cmd_creator_signal_handling(self, signal):
        if signal.name == 'saved file':
            self.cmd_viewer.open_file(signal.value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #print(QStyleFactory.keys())
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
