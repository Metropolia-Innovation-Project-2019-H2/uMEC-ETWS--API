import connexion
import six
import requests
from flask import send_file
from openapi_server import util
from cv2 import *
def camera_get():
    cam = VideoCapture(0)   # 0 -> index of camera
    s, img = cam.read() #read cam and take picture as img
    cam.release()
    imwrite("image.jpg",img) #save img file as jpg
    f = open("image.jpg", "rb")  # open in binary mode
    """
    GET image 

    Retrieve the current camera image. # noqa: E501


    :rtype: file
    """
    return send_file(f, mimetype='image/jpeg')

