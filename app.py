
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, Response, request

from src.camera import Camera
from src.tools.video_record import create_video
from src.tools.param_manage import get_detection_parameters, set_detection_parameters, get_bot_parameters, \
    set_bot_parameters, get_nn_parameters

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
min_area, blur_size, blur_power, threshold_low = get_detection_parameters()
bot_token, _, chat_id, proxy_url, sending_period, _, _ = get_bot_parameters()
net_architecture, net_model, classes, confidence = get_nn_parameters()

CAM = 0  # TODO to config
FPS = 10  # TODO to config

# Видео-файл
out, v_filename = create_video()


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
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)


def gen(camera, out, v_filename):
    """Video streaming generator function."""
    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(net_architecture, net_model)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    while running:
        img, jpeg, status = camera.motion_detect(running=running,
                                                 video_file=out,
                                                 show_edges=show_edges,
                                                 dnn_detection_status=dnn_detection_status,
                                                 net=net,
                                                 classes=classes,
                                                 colors=colors,
                                                 min_area=int(min_area),
                                                 blur_size=int(blur_size),
                                                 blur_power=int(blur_power),
                                                 threshold_low=int(threshold_low),
                                                 sending_period=int(sending_period))
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')


@app.route('/start', methods=['POST'])
def start():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token,\
        chat_id, proxy_url, sending_period

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
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)


@app.route('/stop', methods=['POST'])
def stop():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token,\
        chat_id, proxy_url, sending_period

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
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)


@app.route('/refresh', methods=['POST'])
def refresh():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token,\
        chat_id, proxy_url, sending_period
        
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
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)


@app.route('/bot', methods=['POST'])
def bot():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token,\
        chat_id, proxy_url, sending_period, alarm_bot_status

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
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)


@app.route('/update_settings', methods=['POST'])
def update_settings():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token,\
        chat_id, proxy_url, sending_period
            
    '''

    '''

    return render_template('index.html',
                           show_edges_state=show_edges_state,
                           vfilename=vfilename,
                           min_area=min_area,
                           blur_size=blur_size,
                           blur_power=blur_power,
                           threshold_low=threshold_low,
                           bot_token=bot_token,
                           chat_id=chat_id,
                           proxy_url=proxy_url,
                           sending_period=sending_period)

    
@app.route('/video_feed')
def video_feed():
    
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(CAM, FPS), out, vfilename),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)
