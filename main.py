import auth
import player_vk
import sys
import vkapis
import time
import json
import os
import urllib
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QApplication, QInputDialog
from PyQt5.QtCore import QThread, QTimer, Qt, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import keyboard
import urllib.request


from PyQt5.QtMultimedia import QMediaContent

v = "1.0.0"
volume = 100
tracks = []

app = QApplication(sys.argv)
app.setStyle('Fusion')

slider_action = False
            

class Auth(QtWidgets.QMainWindow, auth.Ui_Auth):
    

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.go)
        self.pushButton.setShortcut("Return")


    def go(self):

        login = self.lineEdit.text()
        password = self.lineEdit_2.text()

        result_music = vkapis.get_music(login, password)
        if str(type(result_music)) == "<class 'vkaudiotoken.TokenException.TokenException'>":
            code, ok = QInputDialog.getText(
            self,
            "Подтвердите номер",
            "Мы отправили SMS с кодом на номер")

            if ok:
                result_music = vkapis.get_music(login, password, code)


        for i, track in enumerate(result_music['response']['items']):
            tracks.append([{"title": track['title'],
            "artist": track['artist'],
            "photo": track['album']['thumb']['photo_300'],
            "duration": track['duration'], 
            "url": track["url"]}])


        data = {"user_agent": vkapis.user_agent, "volume": 100, "token": vkapis.token, "v": v}
        with open('player_cfg.json', 'w') as f:
            json.dump(data, f)



        self.window = Player()
        self.hide()
        self.window.show()

class other(QThread):
    global tracks, volume

    def __init__(self, data):
        super().__init__()

        
        self.data = data
        self.paused = False
        self.played_id = 0
        self.player = QtMultimedia.QMediaPlayer()
        self.player.durationChanged.connect(self.update)
        self.player.positionChanged.connect(self.update_pos)
        self.player.mediaStatusChanged.connect(self.m_status_triger)
        self.player.setVolume(volume)
        self.data.duration_slider.valueChanged.connect(self.update_slider_pos)
        self.data.verticalSlider.valueChanged.connect(self.update_volume)





    def run(self):
        url = QUrl.fromLocalFile(tracks[int(self.data.tableWidget.currentItem().text(0))][0]['url']) # также вызов метода с параметром path
        content = QMediaContent(url) # вызов метода с параметром url
        
        self.player.setMedia(content) # опять метод
        self.player.play()

        self.data.title.setText(tracks[int(self.data.tableWidget.currentItem().text(0))][0]['title'])
        self.data.artist.setText(tracks[int(self.data.tableWidget.currentItem().text(0))][0]['artist'])

        data = urllib.request.urlopen(tracks[int(self.data.tableWidget.currentItem().text(0))][0]['photo'])

        self.data.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.data.play_pause.setIcon(icon)
        self.played_id = int(self.data.tableWidget.currentItem().text(0))


    def update(self, update):
        self.data.duration_slider.setMaximum(update)

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

            if len(tracks) - 1 == self.played_id:
                self.played_id = 0

            else:
                self.played_id += 1


            url = QUrl.fromLocalFile(tracks[int(self.played_id)][0]['url']) # также вызов метода с параметром path
            content = QMediaContent(url) # вызов метода с параметром url
                
            self.player.setMedia(content) # опять метод
            self.player.play()

            self.data.title.setText(tracks[self.played_id][0]['title'])
            self.data.artist.setText(tracks[self.played_id][0]['artist'])

            data = urllib.request.urlopen(tracks[self.played_id][0]['photo'])

            self.data.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))



    def update_pos(self, update):
        self.data.duration_slider.blockSignals(True)
        self.data.duration_slider.setValue(update)
        self.data.duration_slider.blockSignals(False)



        
class Player(QtWidgets.QMainWindow, player_vk.Ui_MainWindow):
    global tracks, volume

    def __init__(self):
        super().__init__()
        
        self.hook = keyboard.on_press(self.prees_event)
        self.setupUi(self)
        self.title.setText("")
        self.artist.setText("")
        self.ico.setPixmap(QtGui.QPixmap(""))
        self.verticalSlider.setValue(volume)

        QtWidgets.QTreeWidget.clear(self.tableWidget)

        self.tableWidget.setColumnWidth(0, 70)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 170)
        self.tableWidget.setColumnWidth(3, 10)

            
        for i, track in enumerate(tracks):
            tree = QtWidgets.QTreeWidgetItem(self.tableWidget)

            tree.setText(0, str(i))
            tree.setText(1, track[0]['artist'])
            tree.setText(2, track[0]['title'])
            tree.setText(3, str(time.strftime("%H:%M:%S", time.gmtime(track[0]['duration']))))


        self.thread = other(self)

        self.tableWidget.itemDoubleClicked.connect(self.thread.start)

        self.play_pause.clicked.connect(self.play_pause_button)
        self.pushButton_4.clicked.connect(self.stop_button)
        self.pushButton_5.clicked.connect(self.forward_button)
        self.pushButton_3.clicked.connect(self.rewind_button)
  


    def prees_event(self, event):
        if event.name == "play/pause media":
            self.play_pause_button()

        elif event.name == "stop media":
            self.stop_button()

        elif event.name == "next track":
            self.forward_button()

        elif event.name == "previous track":
            self.rewind_button()

        elif event.name == "f5":
            a = open("player_cfg.json", "r")
            data = json.load(a)
            token = data['token']
            self.tableWidget.clear()

            tracks.clear()
            user_agent = data['user_agent']
            result_music = vkapis.get_music_token(token, user_agent)

            for i, track in enumerate(result_music['response']['items']):
                tracks.append([{"title": track['title'],
                "artist": track['artist'],
                "duration": track['duration'],
                "photo": track['album']['thumb']['photo_300'],
                "url": track["url"]}])

            for i, track in enumerate(tracks):
                tree = QtWidgets.QTreeWidgetItem(self.tableWidget)

                tree.setText(0, str(i))
                tree.setText(1, track[0]['artist'])
                tree.setText(2, track[0]['title'])
                tree.setText(3, str(time.strftime("%H:%M:%S", time.gmtime(track[0]['duration']))))



    def play_pause_button(self):
        try:
            if self.thread.paused == False:
                self.thread.player.pause()
                self.thread.paused = True

                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("assets/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.play_pause.setIcon(icon)
            else:
                self.thread.player.play()
                self.thread.paused = False

                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.play_pause.setIcon(icon)

        except:
            pass

    def stop_button(self):
        try:
            self.thread.player.stop()
            self.thread.paused = True

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("assets/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.play_pause.setIcon(icon)

        except:
            pass

    def rewind_button(self):

        if self.thread.played_id == 0:
            self.thread.played_id = len(tracks) - 1

        else:
            self.thread.played_id -= 1


        url = QUrl.fromLocalFile(tracks[int(self.thread.played_id)][0]['url']) # также вызов метода с параметром path
        content = QMediaContent(url) # вызов метода с параметром url
                
        self.thread.player.setMedia(content) # опять метод
        self.thread.player.play()

        self.title.setText(tracks[self.thread.played_id][0]['title'])
        self.artist.setText(tracks[self.thread.played_id][0]['artist'])

        data = urllib.request.urlopen(tracks[self.thread.played_id][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))

    def forward_button(self):

        if self.thread.played_id == len(tracks) - 1:
            self.thread.played_id = 0

        else:
            self.thread.played_id += 1


        url = QUrl.fromLocalFile(tracks[int(self.thread.played_id)][0]['url']) # также вызов метода с параметром path
        content = QMediaContent(url) # вызов метода с параметром url
                
        self.thread.player.setMedia(content) # опять метод
        self.thread.player.play()

        self.title.setText(tracks[self.thread.played_id][0]['title'])
        self.artist.setText(tracks[self.thread.played_id][0]['artist'])

        data = urllib.request.urlopen(tracks[self.thread.played_id][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))



exists_config = os.path.exists("player_cfg.json")

if exists_config == False:
    ex = Auth()
    ex.show()
    sys.exit(app.exec_())

elif exists_config == True:
    a = open("player_cfg.json", "r")
    data = json.load(a) 
    token = data['token']
    user_agent = data['user_agent']
    volume = data["volume"]
    result_music = vkapis.get_music_token(token, user_agent)

    for i, track in enumerate(result_music['response']['items']):
        tracks.append([{"title": track['title'],
        "artist": track['artist'],
        "duration": track['duration'],
        "photo": track['album']['thumb']['photo_300'],
        "url": track["url"]}])

    ex = Player()
    ex.show()
    sys.exit(app.exec_())

        