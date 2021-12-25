# -*- coding: utf-8 -*-

import random
import cv2
import webbrowser
import numpy as np

from PIL import Image, ImageFont, ImageDraw

from src.camera import Camera
from src.tools.config import config
from src.ZvooqApi import ZvooqApi


CAM = config["CameraParameters"]["camera_index"]
FPS = config["CameraParameters"]["fps"]
MUSIC_SERVICE_URL = config["MusicApiParameters"]["url"]
MUSIC_SERVICE_LOGIN = config["MusicApiParameters"]["email"]
MUSIC_SERVICE_PASS = config["MusicApiParameters"]["password"]

zvooq = ZvooqApi(url=MUSIC_SERVICE_URL,
                 username=MUSIC_SERVICE_LOGIN,
                 password=MUSIC_SERVICE_PASS)


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

    face_net_arch = config["NNParameters"]["face"]["architecture"]
    face_net_model = config["NNParameters"]["face"]["model"]
    face_net_confidence = config["NNParameters"]["face"]["confidence"]

    emotion_net_arch = config["NNParameters"]["emotion"]["architecture"]
    emotion_net_model = config["NNParameters"]["emotion"]["model"]
    emotion_net_confidence = config["NNParameters"]["emotion"]["confidence"]
    emotion_classes = config["NNParameters"]["emotion"]["classes"]

    face_net = cv2.dnn.readNetFromCaffe(face_net_arch, face_net_model)
    emotion_net = cv2.dnn.readNetFromCaffe(emotion_net_arch, emotion_net_model)

    camera = Camera(camera_idx=CAM,
                    fps=FPS,
                    net=face_net,
                    detection_classes=emotion_classes,
                    confidence=float(face_net_confidence),
                    detection_period_in_seconds=0.3)

    camera.start()

    track_info = ''

    while True:
        rg_frame = camera.emotion_detection(emotion_net=emotion_net)

        if len(camera.detected_objects) > 0:
            emotion = camera.detected_objects[0].label

        # if len(emotion_detection) > 0:
        #     emotion_confidence = max(emotion_detection[0])
        #     idx = emotion_detection[0].tolist().index(emotion_confidence)
        #     emotion = camera.emotion_classes[idx]

            if cv2.waitKey(1) & 0xFF == ord('p'):
                track_author, track_name = play_music(emotion)
                track_info = 'Track: {} - {}'.format(track_author, track_name)

        # img_pil = Image.fromarray(rg_frame)
        # font = ImageFont.truetype("Arial Unicode.ttf", size=20)
        # draw = ImageDraw.Draw(img_pil)
        # draw.text((5, 10), track_info, font=font, fill=(0, 0, 255, 0))
        # rg_frame = np.array(img_pil)

        cv2.putText(img=rg_frame,
                    text=track_info,
                    org=(5, 20),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.6,
                    color=[0, 0, 255],
                    thickness=1)

        cv2.imshow('frame', rg_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.stop()
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
