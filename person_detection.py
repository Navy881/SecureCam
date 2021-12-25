# -*- coding: utf-8 -*-

import cv2
import numpy as np
from datetime import datetime

from src.camera import Camera
from src.tools.config import config
from src.tools.video_record import create_video

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


def main():
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe(net_arch, net_model)

    camera = Camera(camera_idx=CAM,
                    fps=FPS,
                    net=net,
                    detection_classes=classes,
                    confidence=float(net_confidence),
                    detection_period_in_seconds=1)
    camera.start()

    video_out, v_filename = create_video()
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    while True:

        rg_frame = camera.person_detection_on_video()

        # rg_frame, jpeg, detection_status, person_in_image = camera.motion_detect(running=True,
        #                                                                          video_file=video_out,
        #                                                                          show_edges=False,
        #                                                                          dnn_detection_status=True,
        #                                                                          net=net,
        #                                                                          classes=classes,
        #                                                                          colors=colors,
        #                                                                          given_confidence=float(confidence),
        #                                                                          min_area=int(min_area),
        #                                                                          blur_size=int(blur_size),
        #                                                                          blur_power=int(blur_power),
        #                                                                          threshold_low=int(threshold_low))

        cv2.imshow('frame', rg_frame)

        # if len(detected_objects) > 0:
        #     for obj in detected_objects:
        #         image = detected_objects[obj]
        #         # TODO: Save crop images just with persons

        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_out.release()
            camera.stop()
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    print('Over')
    cv2.destroyAllWindows()
