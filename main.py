# -*- coding: utf-8 -*-

import sys
import subprocess

import cv2
import numpy as np
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
# from multiprocessing import Queue
from src.tools.queue_for_mac import Queue  # For Max OS

from src.ui import main_form, config_form  # GUI design
from src.camera import Camera
from src.tools.config import config


running = False
show_edges = False
pause = False
hide_video = False
alarm_bot_status = False
dnn_detection_status = False
capture_thread = None
bot_thread = None
bot_subproc = subprocess.Popen
max_queue_size = 10
# ui_form = uic.loadUiType("src/ui/form.ui")[0] # Опиание GUI в .ui
detection_status = ''
start_time = datetime.now().replace(microsecond=0)

q = Queue()
config.get_config()

CAM = config["CameraParameters"]["camera_index"]
FPS = config["CameraParameters"]["fps"]
net_arch = config["NNParameters"]["object"]["architecture"]
net_model = config["NNParameters"]["object"]["model"]
net_confidence = config["NNParameters"]["object"]["confidence"]
classes = config["NNParameters"]["object"]["classes"]
min_area = config["DetectionParameters"]["min_area"]
blur_size = config["DetectionParameters"]["blur_size"]
blur_power = config["DetectionParameters"]["blur_power"]
threshold_low = config["DetectionParameters"]["threshold_low"]
bot_token = config["BotParameters"]["token"]
bot_private_chat_id = config["BotParameters"]["chat_id"]
bot_proxy_url = config["BotParameters"]["proxy_url"]
bot_sending_period = config["BotParameters"]["sending_period"]
bot_username = config["BotParameters"]["username"]
bot_password = config["BotParameters"]["password"]

camera = Camera(CAM, FPS, True)


def grab(camera, queue):
    global detection_status, dnn_detection_status

    frame = {}

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(net_arch, net_model)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    while running:
        img, jpeg, detection_status, person_in_image = camera.motion_detect(running=running,
                                                                            show_edges=show_edges,
                                                                            dnn_detection_status=dnn_detection_status,
                                                                            net=net,
                                                                            classes=classes,
                                                                            colors=colors,
                                                                            given_confidence=float(net_confidence),
                                                                            min_area=int(min_area),
                                                                            blur_size=int(blur_size),
                                                                            blur_power=int(blur_power),
                                                                            threshold_low=int(threshold_low),
                                                                            sending_period=int(bot_sending_period))

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


class MyWindowClass(QtWidgets.QMainWindow, main_form.Ui_MainWindow):  # ui_form):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.startButton.clicked.connect(self.start_clicked)  # Initialized button "Start"
        self.pauseButton.clicked.connect(self.pause_clicked)  # Initialized button "Pause"
        self.closeButton.clicked.connect(self.close)  # Initialized button "Close"
        self.botStartButton.clicked.connect(self.start_bot)  # Initialized button "Start bot"

        self.signalCheckBox.stateChanged.connect(self.video_visibility)  # Initialized checkbox "Hide video"
        self.edgesCheckBox.stateChanged.connect(self.edges_visibility)  # Initialized checkbox "Show red edges"
        self.nnDetectionCheckBox.stateChanged.connect(self.object_detection)  # Initialized checkbox "Object detection"

        self.parametersAction.triggered.connect(self.open_config)  # Initialized config window

        self.ConfigWindow = None  # uic.loadUi("form_parameters.ui")

    # Button "Start" behavior
    def start_clicked(self):
        global running, capture_thread

        if running is False:
            running = True
            camera.start()
            capture_thread = Thread(target=grab, args=(camera, q))  # Thread for detection
            capture_thread.start()
            self.startButton.setText('Stop')
        else:
            running = False
            if capture_thread is not None:
                capture_thread.join()
            camera.stop()
            self.startButton.setText('Start')

    # ImgWidget frame behavior
    def update_frame(self):
        if not q.empty():

            self.statusLabel.setText(detection_status)  # Output detection status
            self.timeLabel.setText(str(datetime.now().replace(microsecond=0) - start_time))  # Output timestamp
            self.textField.setText(camera.video_filename)  # Output video filename

            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            if not hide_video:
                image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            if hide_video is True or running is False:
                image = QtGui.QImage(0, width, height, bpl, QtGui.QImage.Format_RGB888)
            if not pause:
                self.ImgWidget.setImage(image)

    # Button "Pause" behavior
    def pause_clicked(self):
        global pause

        if pause is False:
            pause = True
            self.pauseButton.setText('Continue')
        else:
            pause = False
            self.pauseButton.setText('Pause')

    # Button "Close" behavior
    def closeEvent(self, event):
        global running, capture_thread

        running = False
        if capture_thread is not None:
            capture_thread.join()

    # Checkbox "Hide video" behavior
    @staticmethod
    def video_visibility(state):
        global hide_video

        if state == QtCore.Qt.Checked:
            hide_video = True
        else:
            hide_video = False

    # Checkbox "Show red edges" behavior
    @staticmethod
    def edges_visibility(state):
        global show_edges

        if state == QtCore.Qt.Checked:
            show_edges = True
        else:
            show_edges = False

    # Checkbox "Object detection" behavior
    @staticmethod
    def object_detection(state):
        global dnn_detection_status

        if state == QtCore.Qt.Checked:
            dnn_detection_status = True
        else:
            dnn_detection_status = False

    # Config window
    def open_config(self):
        self.ConfigWindow = ConfigWindow(self)
        self.ConfigWindow.show()

    # Button "Start bot" behavior
    def start_bot(self):
        global alarm_bot_status, bot_subproc

        run_bot_command = ('python security_bot_telepot.py')

        if alarm_bot_status is False:
            bot_subproc = subprocess.Popen(run_bot_command, shell=True)  # Run bot subprocess
            alarm_bot_status = True
            self.botStartButton.setText('Stop bot')
        else:
            bot_subproc.kill()  # TODO Process does't kill
            alarm_bot_status = False
            self.botStartButton.setText('Start bot')


# ui_form_parameters = uic.loadUiType("src/ui/form_parameters.ui")[0] # Опиcание GUI в .ui
class ConfigWindow(QtWidgets.QWidget, config_form.Ui_parametersForm):  # ui_form_parameters):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)

        # Output values into edits
        self.counterAreaLineEdit.setText(str(min_area))
        self.blurSizeLineEdit.setText(str(blur_size))
        self.blurPowerLineEdit.setText(str(blur_power))
        self.lowThresholdLineEdit.setText(str(threshold_low))
        self.botTokenLineEdit.setText(str(bot_token))
        self.chatIdLineEdit.setText(str(bot_private_chat_id))
        self.proxyUrlLineEdit.setText(str(bot_proxy_url))
        self.sendingPeriodLineEdit.setText(str(bot_sending_period))
        self.proxyUsernameLineEdit.setText(str(bot_username))
        self.proxyPasswordLineEdit.setText(str(bot_password))

        # Initialized buttons
        self.saveButton.clicked.connect(self.save_parameters)
        self.exitButton.clicked.connect(self.close)

    # Button "Save" behavior
    def save_parameters(self):
        global min_area, blur_size, blur_power, threshold_low, \
            bot_token, bot_private_chat_id, bot_proxy_url, bot_proxy_url, bot_sending_period, bot_username, bot_password

        config["DetectionParameters"]["min_area"] = min_area = self.counterAreaLineEdit.text()
        config["DetectionParameters"]["blur_size"] = blur_size = self.blurSizeLineEdit.text()
        config["DetectionParameters"]["blur_power"] = blur_power = self.blurPowerLineEdit.text()
        config["DetectionParameters"]["threshold_low"] = threshold_low = self.lowThresholdLineEdit.text()
        config["BotParameters"]["token"] = bot_token = self.botTokenLineEdit.text()
        config["BotParameters"]["chat_id"] = bot_private_chat_id = self.proxyUrlLineEdit.text()
        config["BotParameters"]["proxy_url"] = bot_proxy_url = self.chatIdLineEdit.text()
        config["BotParameters"]["sending_period"] = bot_sending_period = self.sendingPeriodLineEdit.text()
        config["BotParameters"]["username"] = bot_username = self.proxyUsernameLineEdit.text()
        config["BotParameters"]["password"] = bot_password = self.proxyPasswordLineEdit.text()

        config.update()

        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindowClass(None)
    w.show()
    app.exec_()
