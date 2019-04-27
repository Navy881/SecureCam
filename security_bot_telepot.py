#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
import time
import logging
import telepot
from threading import Thread
from datetime import datetime
from telepot.loop import MessageLoop
#from re import findall # Импортируем библиотеку по работе с регулярными выражениями
#from subprocess import check_output # Импортируем библиотеку по работе с внешними процессами

from src.camera import Camera
from src.tools.param_manage import getDetectionParameters, getBotParameters, getNNParameters
from src.tools.video_record import create_video

running = False
show_edges = False
alarm_bot_status = False
dnn_detection_status = True

capture_thread = None

detection_status = ''
vfilename = ''
starttime = datetime.now().replace(microsecond=0)

# Get config params
MIN_AREA, BLUR_SIZE, BLUR_POWER, THRESHOLD_LOW = getDetectionParameters()
BOT_TOKEN, REQUEST_KWARGS, CHAT_ID, PROXY_URL, SENDING_PERIOD, USERNAME, PASSWORD = getBotParameters()
NET_ARCHITECTURE, NET_MODEL, CLASSES, CONFIDENCE = getNNParameters() # Get NN parameters

# Номер веб-камеры
cam = 0  # TODO вывести в настройки
max_queue_size = 10 # TODO вывести в настройки

# Proxy
SetProxy = telepot.api.set_proxy(PROXY_URL, (USERNAME, PASSWORD))
bot = telepot.Bot(BOT_TOKEN)

cam = 0
camera = Camera(cam)
send_time = datetime.today().timestamp()


def grab():
    global vfilename, detection_status, dnn_detection_status

    out, vfilename = create_video()
    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(NET_ARCHITECTURE, NET_MODEL)
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    while(running):
        #if (dnn_detection_status == False):

        img, jpeg, detection_status = camera.motion_detect(running, out, show_edges,
                                                           dnn_detection_status, net, CLASSES, COLORS, float(CONFIDENCE),
                                                           int(MIN_AREA), int(BLUR_SIZE), int(BLUR_POWER), int(THRESHOLD_LOW), int(SENDING_PERIOD)) # получение кадра с обнаруженным движением
        cv2.imshow("Camera", img)
        # Ожидание нажания клавиши "q"
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


# Start camera
def startCamera(chat_type, chat_id):
    global running, capture_thread

    if running is False:
        print("Starting")
        running = True
        capture_thread = Thread(target=grab, args=()) # поток для работы детектора
        capture_thread.start()
        print("Started")
        message = "Record started..."
    else:
        message = "Record already started..."

    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    bot.sendMessage(chat_id, message)
    print("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id))


# Stop camera
def stopCamera(chat_type, chat_id):
    global running, capture_thread, windowsClose

    if running is True:
        print("Stopping")
        running = False
        capture_thread.join()
        print("Stopped")
        message = "Record stopped..."
    else:
        message = "Nothing running..."

    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    bot.sendMessage(chat_id, message)
    print("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id))


# Send help info
def helpInfo(chat_type, chat_id):
    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    help_message = "Hello, i'm a Sigwart Bot.\n" \
                   "You can use commands:\n" \
                   "/check - checking work,\n" \
                   "/help - help info\n" \
                   "/photo - sending photo in chat\n" \
                   "/start_camera - starting detection and recording\n" \
                   "/stop_camera - stopping detection and recording\n" \
                   "/temp - get temperature value\n"

    bot.sendMessage(chat_id, help_message)
    print ("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id)) 


# Sending message
def checkWork(chat_type, chat_id):
    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    bot.sendMessage(chat_id, text="I'm work")
    print ("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id)) 


# Send photo
def sendPhoto(chat_type, chat_id):
    # Make screenshot from webcam
    camera.screenshot()
    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    # Send saved photo by motionRecoder
    bot.sendPhoto(chat_id, photo=open('photo/bot_screenshot.png', 'rb'))
    print ("{} - bot sent image into {} chat: {}".format(now, chat_type, chat_id))


'''
def getTemp(chat_type, chat_id):
    temp = check_output(["vcgencmd","measure_temp"]).decode() # Выполняем запрос температуры
    temp = float(findall('\d+\.\d+', temp)[0])
    message = "Temperature is " + str(temp) + " C"
    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    bot.sendMessage(chat_id, message)
    print ("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id)) 
'''


# Sending error
def unknowCommand(chat_type, chat_id):
    # Time sending message
    now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
    message = "I don't know this command.\n" \
                   "You can use commands:\n" \
                   "/check - checking work,\n" \
                   "/help - help info\n" \
                   "/photo - sending photo in chat\n" \
                   "/start_camera - starting detection and recording\n" \
                   "/stop_camera - stopping detection and recording\n" \
                   "/temp - get temperature value\n"

    bot.sendMessage(chat_id, text=message)
    print ("{} - bot answered into {} chat: {}".format(now, chat_type, chat_id)) 


# Main method
def alarm():
    global send_time
    while False:
        if os.path.exists('photo/screenshot_temp.png'):
            file_create_time = os.path.getmtime('photo/screenshot_temp.png')
            if send_time != file_create_time:
                time.sleep(1)
                print("sending image...")
                now = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
                bot.sendPhoto(CHAT_ID, photo=open('photo/screenshot_temp.png', 'rb'))
                print ("{} - bot sent image into chat: {}".format(now, CHAT_ID))
                send_time = os.path.getmtime('photo/screenshot_temp.png')


# Commands ##################
commands = {
    "/check": checkWork,
    "/help": helpInfo,
    "/photo": sendPhoto,
    "/start_camera": startCamera,
    "/stop_camera": stopCamera,
    #"/temp": getTemp,
}
#############################


# Main method
def main(msg):
    # Определение типа сообещения, типа чата и id чата
    content_type, chat_type, chat_id = telepot.glance(msg)
    # Если в сообщении текст
    if content_type == 'text':
        command = msg['text']
        if command in commands.keys():
            commands.get(command)(chat_type, chat_id)
        else:
            unknowCommand(chat_type, chat_id)


if __name__ == '__main__':
    try:
        print("bot running...")
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        MessageLoop(bot, main).run_as_thread()
        alarm()
        while 1:
            time.sleep(10)
    except Exception as e:
        print(e)

