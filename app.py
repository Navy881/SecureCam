from importlib import import_module
import os
from datetime import datetime
from flask import Flask, render_template, Response, request

from src.camera import Camera
from src.tools.video_record import create_video
from src.tools.param_manage import getDetectionParameters, setDetectionParameters, getBotParameters, setBotParameters
from src.tools.faces_manage import load_know_faces

app = Flask(__name__)

running = False
show_edges = False
pause = False
hide_video = False
alarm_bot_status = False
recog_faces_status = True

vfilename = ''
show_edges_state = ''

starttime = datetime.now().replace(microsecond=0)

# Получаем параметры детектора из json конфига
min_area, blur_size, blur_power, threshold_low = getDetectionParameters()

# Получаем параметры бота из json конфига при каждом открытие окна с параметрами
bot_token, _, chat_id, proxy_url, sending_period = getBotParameters()

# Загрузка известных изоражений лиц
known_face_encodings, known_face_names = load_know_faces()

# Номер веб-камеры
cam = 0

# Видео-файл
out, vfilename = create_video()

@app.route('/')
def index():
    
    """Video streaming home page."""        
    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);


def gen(camera, out, vfilename):
    """Video streaming generator function."""
    while (running):
        img, jpeg, status = camera.motion_detect(running,
                                                 out, show_edges,
                                                 alarm_bot_status,
                                                 recog_faces_status,
                                                 known_face_encodings,
                                                 known_face_names,
                                                 int(min_area),
                                                 int(blur_size),
                                                 int(blur_power),
                                                 int(threshold_low),
                                                 int(sending_period)) # получение кадра с обнаруженным движением
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')


@app.route('/start', methods=['POST'])
def start():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token, chat_id, proxy_url, sending_period

    if running == False:
        running = True
            
    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);


@app.route('/stop', methods=['POST'])
def stop():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token, chat_id, proxy_url, sending_period

    if running == True:
        running = False
            
    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);


@app.route('/refresh', methods=['POST'])
def refresh():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token, chat_id, proxy_url, sending_period
        
    if request.form.get('Show_edges'):
        show_edges = True
        show_edges_state = "checked"
    if not request.form.get('Show_edges'):
        show_edges = False
        show_edges_state = "unchecked"
            
    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);


@app.route('/bot', methods=['POST'])
def bot():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token, chat_id, proxy_url, sending_period

    if alarm_bot_status == False:
        alarm_bot_status = True
            
    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);


@app.route('/update_settings', methods=['POST'])
def update_settings():
    global running, show_edges, show_edges_state, vfilename, min_area, blur_size, blur_power, threshold_low, bot_token, chat_id, proxy_url, sending_period
            
    '''

    '''

    return render_template('index.html',
                           show_edges_state = show_edges_state,
                           vfilename = vfilename,
                           min_area = min_area,
                           blur_size = blur_size,
                           blur_power = blur_power,
                           threshold_low = threshold_low,
                           bot_token = bot_token,
                           chat_id = chat_id,
                           proxy_url = proxy_url,
                           sending_period = sending_period);

    
@app.route('/video_feed')
def video_feed():
    
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(cam), out, vfilename),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(threaded=True)
    
