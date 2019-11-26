import PIL.Image
import numpy
import requests
from pprint import pprint
import time
from cv2 import *

TENSORFLOW_SERVING_URL = 'http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09:predict'
MOOSE_REPORT_URL = 'https://mooseetws.herokuapp.com/api/pi/v1/'
LIGHT_POLE_ID = 1

# hardcode potential threats id and label mapping, took from mscoco_complete_label_map.pbtxt
obj_dict = {17: 'cat', 18: 'dog', 19: 'horse',
            20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear', 24: 'zebra', 25: 'giraffe'}


def report_db(name, score):
    print('#### report to db: ', name, score, LIGHT_POLE_ID)
    payload = {'objectType': name,
               'confidence': score, 'poleId': LIGHT_POLE_ID}
    start = time.perf_counter()
    res = requests.post(MOOSE_REPORT_URL, json=payload)
    print(f'Took {time.perf_counter()-start:.2f}s')
    pprint(res.json())


def read_camera():
    # read image from usb camera with opencv
    cam = VideoCapture(0)   # 0 -> index of camera
    s, img = cam.read()
    cam.release()
    image_np = cvtColor(img, COLOR_BGR2RGB)

    # construct post message to use tensorflow service
    payload = {'instances': [image_np.tolist()]}
    start = time.perf_counter()
    res = requests.post(TENSORFLOW_SERVING_URL, json=payload)
    print(f'Took {time.perf_counter()-start:.2f}s')
    # pprint(res.json())

    # parse returned json data
    predictions = res.json()['predictions']
    print('----Found', len(predictions), 'prediction results')
    parsedData = []
    for prediction in predictions:
        print('----numer of detections:', prediction['num_detections'])
        for i in range(int(prediction['num_detections'])):
            obj_class = prediction['detection_classes'][i]
            obj_score = prediction['detection_scores'][i]
            # According to mscoco_complete_label_map, big animals are identified from 17-25
            if obj_class > 16 and obj_class < 26:
                print("----optential threat:", obj_dict[obj_class],
                      obj_score)
                if obj_score > 0.5:
                    print('--warning !!! found animal, potentially it is a',
                          obj_dict[obj_class])
                    report_db(obj_dict[obj_class], obj_score)
            else:
                print('----found safe object:', obj_class, obj_score)


while True:
    read_camera()
