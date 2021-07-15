# -*- coding: utf-8 -*-

import random
import cv2
import webbrowser
import numpy as np

from PIL import Image, ImageFont, ImageDraw

from src.camera import Camera
from src.tools.param_manage import get_nn_parameters
from src.ZvooqApi import ZvooqApi

net_architecture, net_model, classes, confidence = get_nn_parameters()

CAM = 0  # TODO to config
FPS = 20  # TODO to config

camera = Camera(CAM, FPS, True)

url = 'https://sber-zvuk.com/'
email = 'ag881.pst@gmail.com'
password = 'rksm911911Hh'

zvooq = ZvooqApi(url=url, username=email, password=password)


def play_music(query: str):
    result = zvooq.search_tracks(query=query)

    if result is None:
        return

    if len(result['result']['search']['tracks']['items']) < 1:
        return

    track_idx = random.randint(0, len(result['result']['search']['tracks']['items']) - 1)

    track_id = str(result['result']['search']['tracks']['items'][track_idx]['id'])
    track_author = str(result['result']['search']['tracks']['items'][track_idx]['aname'])
    track_name = str(result['result']['search']['tracks']['items'][track_idx]['title'])
    print('INFO: Play track {} "{} - {}" for emotion "{}"'.format(track_id, track_author, track_name, query))

    track_stream = zvooq.get_track_stream(track_id=str(track_id))

    if track_stream is None:
        return

    stream_url = track_stream['result']['stream']

    webbrowser.open_new_tab(stream_url)

    return track_author, track_name


def main():
    net = cv2.dnn.readNetFromCaffe(net_architecture, net_model)
    emotion_net = cv2.dnn.readNetFromCaffe("dnn/emotion_recog_deploy.prototxt", "dnn/EmotiW_VGG_S.caffemodel")

    track_info = ''

    while True:
        rg_frame, emotion_detection = camera.emotion_detection(dnn_detection_status=True,
                                                               net=net,
                                                               given_confidence=float(confidence),
                                                               emotion_net=emotion_net,
                                                               emotion_classes=classes,
                                                               emotion_given_confidence=float("0.5"))

        if len(emotion_detection) > 0:
            emotion_confidence = max(emotion_detection[0])
            idx = emotion_detection[0].tolist().index(emotion_confidence)
            emotion = classes[idx]

            if cv2.waitKey(1) & 0xFF == ord('p'):
                track_author, track_name = play_music(emotion)
                track_info = 'Track: {} - {}'.format(track_author, track_name)

        img_pil = Image.fromarray(rg_frame)
        font = ImageFont.truetype("Arial Unicode.ttf", size=20)
        draw = ImageDraw.Draw(img_pil)
        draw.text((5, 10), track_info, font=font, fill=(0, 0, 255, 0))
        rg_frame = np.array(img_pil)

        # cv2.putText(img=rg_frame,
        #             text=track_info,
        #             org=(5, 20),
        #             fontFace=cv2.FONT_HERSHEY_DUPLEX,
        #             fontScale=0.6,
        #             color=[0, 0, 255],
        #             thickness=1)

        cv2.imshow('frame', rg_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        zvooq.start_client()
        main()
    except Exception as e:
        print(e)

    print('Over')
    cv2.destroyAllWindows()
