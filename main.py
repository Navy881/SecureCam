# -*- coding: utf-8 -*-

import sys
import os
import signal
import subprocess
import cv2
import numpy as np
from threading import Thread
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from datetime import datetime
from multiprocessing import Queue

from src.ui import main_form, config_form # импорт дизайна GUI
from src.camera import Camera
from src.tools.video_record import create_video
from src.tools.param_manage import getDetectionParameters, \
    setDetectionParameters, \
    getBotParameters, \
    setBotParameters,\
    getNNParameters


running = False
show_edges = False
pause = False
hide_video = False
alarm_bot_status = False
recog_faces_status = True
dnn_detection_status = False

capture_thread = None
bot_thread = None
bot_subproc = subprocess.Popen

#ui_form = uic.loadUiType("src/ui/form.ui")[0] # Опиание GUI в .ui
q = Queue()
detection_status = ''
vfilename = ''
starttime = datetime.now().replace(microsecond=0)

# Получаем параметры детектора из json конфига
MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW = getDetectionParameters()
# Получаем параметры бота из json конфига при каждом открытие окна с параметрами
BOT_TOKEN, REQUEST_KWARGS, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD = getBotParameters()
# Получаем параметры NN из json конфига при каждом открытие окна с параметрами
NET_ARCHITECTURE, NET_MODEL, CLASSES, CONFIDENCE = getNNParameters() # Get NN parameters

# Номер веб-камеры
cam = 0  # TODO вывести в настройки
max_queue_size = 10 # TODO вывести в настройки

def grab(camera, queue):
    global vfilename, detection_status, dnn_detection_status

    frame = {} # очередь
    out, vfilename = create_video()

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(NET_ARCHITECTURE, NET_MODEL)
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    while(running):
        #if (dnn_detection_status == False):

        img, jpeg, detection_status = camera.motion_detect(running,
                                                           out,
                                                           show_edges,
                                                           dnn_detection_status,
                                                           net,
                                                           CLASSES,
                                                           COLORS,
                                                           float(CONFIDENCE),
                                                           int(MIN_AREA),
                                                           int(BLUR_SIZE),
                                                           int(BLUR_POWER),
                                                           int(THRESHOLD_LOW),
                                                           int(SENDING_PERIOD)) # получение кадра с обнаруженным движением

        # img = camera.real_time_detection_2(dnn_detection_status, net, CLASSES, COLORS, float(CONFIDENCE))
        #if (dnn_detection_status):
        #    img = camera.real_time_detection(dnn_detection_status, net, CLASSES, COLORS, given_confidence)											

        frame["img"] = img
        if queue.qsize() < max_queue_size:
            queue.put(frame)
        else:
            print("Frame queue size is " + str(queue.qsize()))


class OwnImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class MyWindowClass(QtWidgets.QMainWindow, main_form.Ui_MainWindow): #ui_form):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.startButton.clicked.connect(self.start_clicked) # Нажатие кнопки Start
        self.pauseButton.clicked.connect(self.pause_clicked) # Нажатие кнопки Pause
        self.closeButton.clicked.connect(self.close) # Нажатие кнопки Close
        self.botStartButton.clicked.connect(self.start_bot) # Нажатие кнопки Start bot

        self.signalCheckBox.stateChanged.connect(self.video_visibility) # Включение чекбокса "Hide video"
        self.edgesCheckBox.stateChanged.connect(self.edges_visibility) # Включение чекбокса "Show red edges"
        self.nnDetectionCheckBox.stateChanged.connect(self.object_detection) # Включение чекбокса "Object detection"

        self.parametersAction.triggered.connect(self.open_config) # Открытие диалога праметров

        self.ConfigWindow = None #uic.loadUi("form_parameters.ui") # Диалог настройки параметров


    # Логика нажатия кнопки Start
    def start_clicked(self):
        global running, capture_thread

        if running is False:
            running = True
            capture_thread = Thread(target=grab, args = (Camera(cam), q)) # поток для работы детектора
            capture_thread.start()
            self.startButton.setText('Stop')
        else:
            running = False
            capture_thread.join()
            self.startButton.setText('Start')


    # Логика работы ImgWidget
    def update_frame(self):
        if not q.empty():
            self.statusLabel.setText(detection_status) # Вывод статуса обнаружения
            self.timeLabel.setText(str(datetime.now().replace(microsecond=0) - starttime)) # Вывод времени
            self.textField.setText(vfilename) # Вывод наименования файла

            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            if hide_video == False:
                image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            if hide_video is True or running is False:
                image = QtGui.QImage(0, width, height, bpl, QtGui.QImage.Format_RGB888)
            if pause == False:
                self.ImgWidget.setImage(image)


    # Логика нажатия кнопки Pause
    def pause_clicked(self):
        global pause

        if pause is False:
            pause = True
            self.pauseButton.setText('Continue')
        else:
            pause = False
            self.pauseButton.setText('Pause')


    def closeEvent(self, event):
        global running, capture_thread
        
        running = False
        capture_thread.join()

    # Логика включения чекбокса "Hide video"
    def video_visibility(self, state):
        global hide_video

        if state == QtCore.Qt.Checked:
            hide_video = True
        else:
            hide_video = False

    # Логика включения чекбокса "Show red edges"
    def edges_visibility(self, state):
        global show_edges

        if state == QtCore.Qt.Checked:
            show_edges = True
        else:
            show_edges = False

    # Логика включения чекбокса "Object detection"
    def object_detection(self, state):
        global dnn_detection_status

        if state == QtCore.Qt.Checked:
            dnn_detection_status = True
        else:
            dnn_detection_status = False

    # Открытие диалога с параметрами
    def open_config(self):
        self.ConfigWindow = ConfigWindow(self)
        self.ConfigWindow.show()

    # Логика нажатия кнопки Start bot
    def start_bot(self):
        global alarm_bot_status, bot_subproc

        run_bot_command = ('python security_bot_telepot.py')

        if alarm_bot_status is False:
            bot_subproc = subprocess.Popen(run_bot_command, shell=True) # Run bot subprocess
            alarm_bot_status = True
            self.botStartButton.setText('Stop bot')
        else:
            bot_subproc.kill() #TODO Процесс не завершается
            alarm_bot_status = False
            self.botStartButton.setText('Start bot')


#ui_form_parameters = uic.loadUiType("src/ui/form_parameters.ui")[0] # Опиание GUI в .ui
class ConfigWindow(QtWidgets.QWidget, config_form.Ui_parametersForm):  #ui_form_parameters):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)

        # Получаем параметры детектора из json конфига при каждом открытие окна с параметрами
        MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW = getDetectionParameters()

        # Редактируемые поля для параметров
        self.counterAreaLineEdit.setText(str(MIN_AREA))
        self.blurSizeLineEdit.setText(str(BLUR_SIZE))
        self.blurPowerLineEdit.setText(str(BLUR_POWER))
        self.lowThresholdLineEdit.setText(str(THRESHOLD_LOW))

        # Получаем параметры бота из json конфига при каждом открытие окна с параметрами
        BOT_TOKEN, REQUEST_KWARGS, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD = getBotParameters()

        # Редактируемые поля для параметров
        self.botTokenLineEdit.setText(str(BOT_TOKEN))
        self.chatIdLineEdit.setText(str(MY_CHAT_ID))
        self.proxyUrlLineEdit.setText(str(PROXY_URL))
        self.sendingPeriodLineEdit.setText(str(SENDING_PERIOD))
        self.proxyUsernameLineEdit.setText(str(USERNAME))
        self.proxyPasswordLineEdit.setText(str(PASSWORD))

        # Кнопки
        self.saveButton.clicked.connect(self.save_parameters)
        self.exitButton.clicked.connect(self.close)

    # Логика сохранения параметров детектора
    def save_parameters(self):
        global MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW, BOT_TOKEN, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD

        setDetectionParameters(self.counterAreaLineEdit.text(), self.blurSizeLineEdit.text(),
                               self.blurPowerLineEdit.text(), self.lowThresholdLineEdit.text())
        setBotParameters(self.botTokenLineEdit.text(), self.proxyUrlLineEdit.text(),
                         self.chatIdLineEdit.text(),  self.sendingPeriodLineEdit.text(),
                         self.proxyUsernameLineEdit.text(), self.proxyPasswordLineEdit.text())

        # Получаем параметры детектора из json конфига
        MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW = getDetectionParameters()

        # Получаем параметры бота из json конфига при каждом открытие окна с параметрами
        BOT_TOKEN, REQUEST_KWARGS, MY_CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD = getBotParameters()

        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindowClass(None)
    w.show()
    app.exec_()




