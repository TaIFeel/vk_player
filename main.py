from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5 import QtGui, QtWidgets, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QApplication
import auth
import player_vk
import sys
import vkapis
import time
import json
import os
import urllib
import keyboard
import urllib.request



v = "2.1"
volume = 100
tracks = []

app = QApplication(sys.argv)
app.setStyle('Fusion')

            

class Auth(QtWidgets.QMainWindow, auth.Ui_Auth):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.login_vk.clicked.connect(self.go)
        self.login_vk.setShortcut("Return")


    def go(self):

        login = self.login.text()
        password = self.password.text()

        result_music = vkapis.auth(login, password)


        #if str(type(result_music)) == "<class 'vkaudiotoken.TokenException.TokenException'>":
            #code, ok = QInputDialog.getText(
            #self,
            #"Подтвердите номер",
            #"Мы отправили SMS с кодом на номер")

            #if ok:
                #result_music = vkapis.get_music(login, password, code)


        for track in result_music['response']['items']:
            tracks.append([{"title": track['title'],
            "artist": track['artist'],
            "photo": track['album']['thumb']['photo_600'],
            "duration": track['duration'], 
            "url": track["url"]}])


        data = {"volume": 100, "token": vkapis.token, "v": v}
        with open('player_cfg.json', 'w') as f:
            json.dump(data, f)

        self.window = Player()
        self.hide()
        self.window.show()

class other(QThread):
    global tracks, volume

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
        self.player.setVolume(volume)


    def run(self):
        url = QUrl.fromLocalFile(tracks[int(self.table_item)][0]['url'])
        content = QMediaContent(url)
        
        self.player.setMedia(content)
        self.player.play()

        self.update_play_data.emit(int(self.table_item))
        self.played_id = int(self.table_item)


    def update(self, update):
        self.update_duration.emit(update)

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

            url = QUrl.fromLocalFile(tracks[int(self.played_id)][0]['url'])
            content = QMediaContent(url)
                
            self.player.setMedia(content)
            self.player.play()

            self.update_other_data.emit(self.played_id)


    def update_pos(self, update):
        self.update_position.emit(update)


class Player(QtWidgets.QMainWindow, player_vk.Ui_MainWindow):
    global tracks, volume

    play_key = pyqtSignal()
    stop_key = pyqtSignal()
    forward_key = pyqtSignal()
    rewind_key = pyqtSignal()



    def __init__(self):
        super().__init__()

        self.keyboard = keyboard

        self.play_key.connect(self.play_pause_button)
        self.stop_key.connect(self.stop_button)
        self.forward_key.connect(self.forward_button)
        self.rewind_key.connect(self.rewind_button)


        
        self.setupUi(self)
        self.title.setText("")
        self.artist.setText("")
        self.ico.setPixmap(QtGui.QPixmap(""))
        self.verticalSlider.setValue(volume)

        QtWidgets.QTreeWidget.clear(self.tableWidget)

            
        for i, track in enumerate(tracks):
            tree = QtWidgets.QTreeWidgetItem(self.tableWidget)

            tree.setText(0, str(i))
            tree.setText(1, track[0]['title'])
            tree.setText(2, track[0]['artist'])
            tree.setText(3, str(time.strftime("%H:%M:%S", time.gmtime(track[0]['duration']))))


        


        self.thread = other()
        self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(0))



        self.tableWidget.itemDoubleClicked.connect(self.start_play)

        self.thread.update_duration.connect(self.duration_change)
        self.thread.update_position.connect(self.position_change)
        self.thread.update_other_data.connect(self.update_other_data)
        self.thread.update_play_data.connect(self.update_play_data)

        self.duration_slider.valueChanged.connect(self.thread.update_slider_pos)
        self.verticalSlider.valueChanged.connect(self.thread.update_volume)

        

        self.play_pause.clicked.connect(self.play_pause_button)
        self.pushButton_4.clicked.connect(self.stop_button)
        self.pushButton_5.clicked.connect(self.forward_button)
        self.pushButton_3.clicked.connect(self.rewind_button)
        self.pushButton_6.clicked.connect(self.update_track_list)

        self.pushButton_6.setShortcut('F5')



        self.keyboard.add_hotkey(-179, self.play_key.emit, args = None,  suppress=True)
        self.keyboard.add_hotkey(-177, self.rewind_key.emit,args = None, suppress=True)
        self.keyboard.add_hotkey(-176, self.forward_key.emit,args = None, suppress=True)
        self.keyboard.add_hotkey(-178, self.stop_key.emit,args = None, suppress=True)


    def start_play(self):
        self.thread.table_item = self.tableWidget.currentItem().text(0)
        self.thread.start()

    def update_play_data(self, table_item):

        print(table_item)
        print(self.thread.table_item)

        self.title.setText(tracks[int(table_item)][0]['title'])
        self.artist.setText(tracks[int(table_item)][0]['artist'])

        data = urllib.request.urlopen(tracks[int(table_item)][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_pause.setIcon(icon)

    def duration_change(self, duration):
        if duration == 0:
            return print('passed')
            
        print(duration/1000)
        self.duration_slider.setMaximum(duration)

    def position_change(self, update):
        self.duration_slider.blockSignals(True)
        self.duration_slider.setValue(update)
        self.duration_slider.blockSignals(False)

    def update_other_data(self, played_id):
        self.title.setText(tracks[played_id][0]['title'])
        self.artist.setText(tracks[played_id][0]['artist'])

        data = urllib.request.urlopen(tracks[played_id][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))
        self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(played_id))





    def update_track_list(self, args = None):
        a = open("player_cfg.json", "r")
        data = json.load(a)
        token = data['token']

        print('1')
        self.tableWidget.clear()
        print('2')
        tracks.clear()
        print('3')

        result_music = vkapis.get_music_token(token)

        for i, track in enumerate(result_music['response']['items']):
            tracks.append([{"title": track['title'],
            "artist": track['artist'],
            "duration": track['duration'],
            "photo": track['album']['thumb']['photo_600'],
            "url": track["url"]}])

        for i, track in enumerate(tracks):
            tree = QtWidgets.QTreeWidgetItem(self.tableWidget)

            tree.setText(0, str(i))
            tree.setText(1, track[0]['artist'])
            tree.setText(2, track[0]['title'])
            tree.setText(3, str(time.strftime("%H:%M:%S", time.gmtime(track[0]['duration']))))




    def play_pause_button(self, args = None):
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

    def stop_button(self, args = None):
        try:
            self.thread.player.stop()
            self.thread.paused = True

            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("assets/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.play_pause.setIcon(icon)

        except:
            pass

    def rewind_button(self, args = None):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_pause.setIcon(icon)

        if self.thread.player.position() >= 5000:
            print('1')
            print(self.thread.player.position())
            self.duration_slider.blockSignals(True)
            self.duration_slider.setValue(0)
            self.duration_slider.blockSignals(False)
            return self.thread.player.setPosition(0)


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
        
        self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(self.thread.played_id))


    def forward_button(self, args = None):
        print(self)
        print(args)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_pause.setIcon(icon)

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

        self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(self.thread.played_id))



exists_config = os.path.exists("player_cfg.json")

if exists_config == False:
    ex = Auth()
    ex.show()
    sys.exit(app.exec_())

elif exists_config == True:
    a = open("player_cfg.json", "r")
    data = json.load(a) 

    token = data['token']
    volume = data["volume"]

    result_music = vkapis.get_music_token(token)

    for track in result_music['response']['items']:
        tracks.append([{"title": track['title'],
        "artist": track['artist'],
        "duration": track['duration'],
        "photo": track['album']['thumb']['photo_300'],
        "url": track["url"]}])

    if v == data['v']:
        pass

    else:
        data['v'] = v

        with open('player_cfg.json', 'w') as f:
            json.dump(data, f)

    ex = Player()
    ex.show()
    sys.exit(app.exec_())


else:
    sys.exit(1)