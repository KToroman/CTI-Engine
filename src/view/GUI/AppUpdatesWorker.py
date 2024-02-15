from PyQt5.QtCore import QObject

class AppUpdatesWorker(QObject):
    visualize: bool = False
    update_status: bool = False
    def run(self):
        pass
