# -*- coding: utf-8 -*-

import cv2
import numpy as np

from src.camera import Camera
from src.tools.config import config


CAM = config["CameraParameters"]["camera_index"]
FPS = config["CameraParameters"]["fps"]
net_arch = config["NNParameters"]["object"]["architecture"]
net_model = config["NNParameters"]["object"]["model"]
net_confidence = config["NNParameters"]["object"]["confidence"]
classes = config["NNParameters"]["object"]["classes"]

camera = Camera(CAM, FPS)


def main():
    net = cv2.dnn.readNetFromCaffe(net_arch, net_model)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    while True:
        rg_frame, detected_objects = camera.real_time_detection_2(dnn_detection_status=True,
                                                                  net=net,
                                                                  classes=classes,
                                                                  colors=colors,
                                                                  given_confidence=float(net_confidence))
        cv2.imshow('frame', rg_frame)

        # if len(detected_objects) > 0:
        #     for obj in detected_objects:
        #         image = detected_objects[obj]
        #         # TODO: Save crop images just with persons

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    print('Over')
    cv2.destroyAllWindows()