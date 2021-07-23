
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, request

from src.camera import Camera
from src.tools.config import config

app = Flask(__name__)

running = False
show_edges = False
pause = False
hide_video = False
alarm_bot_status = False
recog_faces_status = True
vfilename = ''
show_edges_state = ''
dnn_detection_status = True

starttime = datetime.now().replace(microsecond=0)

# Получаем параметры детектора из json конфига
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


@app.route('/')
def index():
    
    """Video streaming home page."""        
    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)


def gen(camera):
    """Video streaming generator function."""
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

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')


@app.route('/start', methods=['POST'])
def start():
    global running

    if not running:
        running = True
            
    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)


@app.route('/stop', methods=['POST'])
def stop():
    global running

    if running:
        running = False
            
    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)


@app.route('/refresh', methods=['POST'])
def refresh():
    global show_edges, show_edges_state
        
    if request.form.get('Show_edges'):
        show_edges = True
        show_edges_state = "checked"
    if not request.form.get('Show_edges'):
        show_edges = False
        show_edges_state = "unchecked"
            
    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)


@app.route('/bot', methods=['POST'])
def bot():
    global alarm_bot_status

    if not alarm_bot_status:
        alarm_bot_status = True
            
    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)


@app.route('/update_settings', methods=['POST'])
def update_settings():
    # global min_area, blur_size, blur_power, threshold_low, \
    #     bot_token, bot_private_chat_id, bot_proxy_url, bot_sending_period
            
    # TODO Update settings

    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=bot_private_chat_id,
                           proxy_url=bot_proxy_url,
                           sending_period=bot_sending_period)

    
@app.route('/video_feed')
def video_feed():
    
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(CAM, FPS)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)
