from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5 import QtGui, QtWidgets, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPropertyAnimation
import global_variable as gv
import json
import time


class other(QThread):

    table_item = 0

    update_duration = pyqtSignal(int)
    update_position = pyqtSignal(int)
    update_other_data = pyqtSignal(int)
    update_play_data = pyqtSignal(int)


    def __init__(self):
        super().__init__()

        self.paused = False
        self.played_id = 0

        self.player = QtMultimedia.QMediaPlayer()

        self.player.durationChanged.connect(self.update)
        self.player.positionChanged.connect(self.update_pos)
        self.player.mediaStatusChanged.connect(self.m_status_triger)
        


    def run(self):
        url = QUrl.fromLocalFile(gv.tracks[int(self.table_item)][0]['url'])
        content = QMediaContent(url)
        
        self.player.setMedia(content)
        self.player.play()

        self.update_play_data.emit(int(self.table_item))
        self.played_id = int(self.table_item)


    def update(self, update):
        self.update_duration.emit(update)

    def update_pos(self, update):
        self.update_position.emit(update)

    def update_slider_pos(self, update):
        self.player.setPosition(update)

    def update_volume(self, update):
        self.player.setVolume(update)

        json_file = open("player_cfg.json", "r")
        json_data = json.load(json_file)
        json_data["volume"] = update

        with open('player_cfg.json', 'w') as f:
            json.dump(json_data, f)

    def m_status_triger(self, update):
        if update == 7:

            if len(gv.tracks) - 1 == self.played_id:
                self.played_id = 0

            else:
                self.played_id += 1

            url = QUrl.fromLocalFile(gv.tracks[int(self.played_id)][0]['url'])
            content = QMediaContent(url)
                
            self.player.setMedia(content)
            self.player.play()

            self.update_other_data.emit(self.played_id)
