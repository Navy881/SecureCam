# -*- coding: utf-8 -*-

import sys
import subprocess

import cv2
import numpy as np
from threading import Thread
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from datetime import datetime
from multiprocessing import Queue

from src.ui import main_form, config_form  # GUI design
from src.camera import Camera
from src.tools.video_record import create_video
from src.tools.param_manage import get_detection_parameters, set_detection_parameters, get_bot_parameters, \
    set_bot_parameters, get_nn_parameters


running = False
show_edges = False
pause = False
hide_video = False
alarm_bot_status = False
dnn_detection_status = False

capture_thread = None
bot_thread = None
bot_subproc = subprocess.Popen

# ui_form = uic.loadUiType("src/ui/form.ui")[0] # Опиание GUI в .ui
q = Queue()
detection_status = ''
v_filename = ''
start_time = datetime.now().replace(microsecond=0)

min_area, blur_size, blur_power, threshold_low = get_detection_parameters()
bot_token, request_kwargs, private_chat_id, proxy_url, sending_period, username, password = get_bot_parameters()
net_architecture, net_model, classes, confidence = get_nn_parameters()

CAM = 0  # TODO to config
FPS = 60  # TODO to config
camera = Camera(CAM, FPS, True)

max_queue_size = 10  # TODO to config


def grab(camera, queue):
    global v_filename, detection_status, dnn_detection_status

    frame = {}
    v_filename = camera.get_video_filename()

    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(net_architecture, net_model)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    while running:
        img, jpeg, detection_status, person_in_image = camera.motion_detect(running=running,
                                                                            show_edges=show_edges,
                                                                            dnn_detection_status=dnn_detection_status,
                                                                            net=net,
                                                                            classes=classes,
                                                                            colors=colors,
                                                                            given_confidence=float(confidence),
                                                                            min_area=int(min_area),
                                                                            blur_size=int(blur_size),
                                                                            blur_power=int(blur_power),
                                                                            threshold_low=int(threshold_low),
                                                                            sending_period=int(sending_period))

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
            capture_thread.join()
            camera.stop()
            self.startButton.setText('Start')

    # ImgWidget frame behavior
    def update_frame(self):
        if not q.empty():

            self.statusLabel.setText(detection_status)  # Output detection status
            self.timeLabel.setText(str(datetime.now().replace(microsecond=0) - start_time))  # Output timestamp
            self.textField.setText(v_filename)  # Output video filename

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


# ui_form_parameters = uic.loadUiType("src/ui/form_parameters.ui")[0] # Опиание GUI в .ui
class ConfigWindow(QtWidgets.QWidget, config_form.Ui_parametersForm):  # ui_form_parameters):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setupUi(self)

        min_area, blur_size, blur_power, threshold_low = get_detection_parameters()
        # Output values into edits
        self.counterAreaLineEdit.setText(str(min_area))
        self.blurSizeLineEdit.setText(str(blur_size))
        self.blurPowerLineEdit.setText(str(blur_power))
        self.lowThresholdLineEdit.setText(str(threshold_low))

        bot_token, request_kwargs, private_chat_id, proxy_url, sending_period, username, password = get_bot_parameters()
        # Output values into edits
        self.botTokenLineEdit.setText(str(bot_token))
        self.chatIdLineEdit.setText(str(private_chat_id))
        self.proxyUrlLineEdit.setText(str(proxy_url))
        self.sendingPeriodLineEdit.setText(str(sending_period))
        self.proxyUsernameLineEdit.setText(str(username))
        self.proxyPasswordLineEdit.setText(str(password))

        # Initialized buttons
        self.saveButton.clicked.connect(self.save_parameters)
        self.exitButton.clicked.connect(self.close)

    # Button "Save" behavior
    def save_parameters(self):
        global min_area, blur_size, blur_power, threshold_low, bot_token, private_chat_id, proxy_url, sending_period, \
            username, password

        set_detection_parameters(self.counterAreaLineEdit.text(), self.blurSizeLineEdit.text(),
                                 self.blurPowerLineEdit.text(), self.lowThresholdLineEdit.text())

        set_bot_parameters(self.botTokenLineEdit.text(), self.proxyUrlLineEdit.text(),
                           self.chatIdLineEdit.text(), self.sendingPeriodLineEdit.text(),
                           self.proxyUsernameLineEdit.text(), self.proxyPasswordLineEdit.text())

        min_area, blur_size, blur_power, threshold_low = get_detection_parameters
        bot_token, _, private_chat_id, proxy_url, sending_period, username, password = get_bot_parameters()

        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindowClass(None)
    w.show()
    app.exec_()
