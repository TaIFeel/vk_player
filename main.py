from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5 import QtGui, QtWidgets, QtMultimedia
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPropertyAnimation
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
import global_variable as gv
from other import other


# #2269ba

volume = 100
v = "2.1"


app = QApplication(sys.argv)
app.setApplicationVersion(v)
app.setStyle("Fusion")

def add_to_data_track(music_list):
    for track in music_list['response']['items']:
        gv.tracks.append([{"title": track['title'],
        "artist": track['artist'],
        "duration": track['duration'],
        "photo": track['album']['thumb']['photo_600'],
        "url": track["url"]}])

            
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


        add_to_data_track(result_music)


        data = {"volume": 100, "token": vkapis.token, "v": v}
        with open('player_cfg.json', 'w') as f:
            json.dump(data, f)

        self.window = Player()
        self.hide()
        self.window.show()



class Player(QtWidgets.QMainWindow, player_vk.Ui_MainWindow):
    global volume

    play_key = pyqtSignal()
    stop_key = pyqtSignal()
    forward_key = pyqtSignal()
    rewind_key = pyqtSignal()
    quit_event = pyqtSignal()



    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.keyboard = keyboard
        self.thread = other()

        self.thread.player.setVolume(volume)

        self.verticalSlider.setValue(volume)

        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        self.play_key.connect(self.play_pause_button)
        self.stop_key.connect(self.stop_button)
        self.forward_key.connect(self.forward_button)
        self.rewind_key.connect(self.rewind_button)
        self.quit_event.connect(self.quit_app)

        self.fill_table()


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



        self.keyboard.add_hotkey(-179, self.play_key.emit, args = None,  suppress=True, trigger_on_release=True)
        self.keyboard.add_hotkey(-177, self.rewind_key.emit,args = None, suppress=True, trigger_on_release=True)
        self.keyboard.add_hotkey(-176, self.forward_key.emit,args = None, suppress=True, trigger_on_release=True)
        self.keyboard.add_hotkey(-178, self.stop_key.emit,args = None, suppress=True, trigger_on_release=True)


    def fill_table(self):
        for i, track in enumerate(gv.tracks):
            tree = QtWidgets.QTreeWidgetItem(self.tableWidget)

            tree.setText(0, str(i))
            tree.setText(1, track[0]['title'])
            tree.setText(2, track[0]['artist'])
            tree.setText(3, str(time.strftime("%H:%M:%S", time.gmtime(track[0]['duration']))))

    def quit_app(self):
        app.exit()

    def closeEvent(self, event):
        event.ignore()

        self.animation.setDuration(1000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        self.animation.finished.connect(self.quit_event.emit)



    def start_play(self):
        self.thread.table_item = self.tableWidget.currentItem().text(0)
        self.thread.start()

    def update_play_data(self, table_item):

        self.title.setText(gv.tracks[int(table_item)][0]['title'])
        self.artist.setText(gv.tracks[int(table_item)][0]['artist'])

        data = urllib.request.urlopen(gv.tracks[int(table_item)][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.play_pause.setIcon(icon)

    def duration_change(self, duration):
        if duration == 0:
            return
            
        self.duration_slider.setMaximum(duration)

    def position_change(self, update):
        self.duration_slider.blockSignals(True)
        self.duration_slider.setValue(update)
        self.duration_slider.blockSignals(False)

    def update_other_data(self, played_id):
        self.title.setText(gv.tracks[played_id][0]['title'])
        self.artist.setText(gv.tracks[played_id][0]['artist'])

        data = urllib.request.urlopen(gv.tracks[played_id][0]['photo'])

        self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))
        self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(played_id))


    def update_track_list(self):
        a = open("player_cfg.json", "r")
        data = json.load(a)
        token = data['token']

        self.tableWidget.clear()
        gv.tracks.clear()

        result_music = vkapis.get_music_token(token)

        add_to_data_track(result_music)

        self.fill_table()


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
        try:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.play_pause.setIcon(icon)

            if self.thread.player.position() >= 5000:

                self.duration_slider.blockSignals(True)
                self.duration_slider.setValue(0)
                self.duration_slider.blockSignals(False)

                return self.thread.player.setPosition(0)


            if self.thread.played_id == 0:
                self.thread.played_id = len(gv.tracks) - 1

            else:
                self.thread.played_id -= 1


            url = QUrl.fromLocalFile(gv.tracks[int(self.thread.played_id)][0]['url'])
            content = QMediaContent(url)
                    
            self.thread.player.setMedia(content)
            self.thread.player.play()

            self.title.setText(gv.tracks[self.thread.played_id][0]['title'])
            self.artist.setText(gv.tracks[self.thread.played_id][0]['artist'])

            data = urllib.request.urlopen(gv.tracks[self.thread.played_id][0]['photo'])

            self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))
            
            self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(self.thread.played_id))

        except:
            pass


    def forward_button(self):
        try:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap("assets/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.play_pause.setIcon(icon)

            if self.thread.played_id == len(gv.tracks) - 1:
                self.thread.played_id = 0

            else:
                self.thread.played_id += 1


            url = QUrl.fromLocalFile(gv.tracks[int(self.thread.played_id)][0]['url'])
            content = QMediaContent(url)
                    
            self.thread.player.setMedia(content)
            self.thread.player.play()

            self.title.setText(gv.tracks[self.thread.played_id][0]['title'])
            self.artist.setText(gv.tracks[self.thread.played_id][0]['artist'])

            data = urllib.request.urlopen(gv.tracks[self.thread.played_id][0]['photo'])

            self.ico.setPixmap(QtGui.QPixmap(QtGui.QImage.fromData(data.read())))

            self.tableWidget.setCurrentItem(self.tableWidget.topLevelItem(self.thread.played_id))

        except:
            pass



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

    add_to_data_track(result_music)

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