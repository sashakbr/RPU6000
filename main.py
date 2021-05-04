import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt5.QtCore import Qt, pyqtSignal
import time

import SerialPortDriver
from Command_module import *
from service import *


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.view_menu = self.menuBar().addMenu("&View")
        self.create_sp()
        self.create_cmd_viewer_docker()
        self.create_cmd_creator_docker()
        self.sp.signal.connect(self.sp_signal_handling, Qt.QueuedConnection)
        self.cmd_viewer.signal.connect(self.cmd_signal_handling, Qt.QueuedConnection)

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
        print(signal.name, signal.value)
        if signal.name == 'cmd':
            print(self.cmd_viewer.cmdtree.currentIndex().row())

    def cmd_signal_handling(self, signal):
        if signal.name == 'send_cmd':
            read_cmd = self.sp.write_read(signal.value, len(signal.value))
            pref = self.cmd_viewer.prefix_check.isChecked()
            self.sp.log_info(cmd_parser(signal.value, self.cmd_viewer.cmd_data, is_prefix_on=pref), 'black')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
