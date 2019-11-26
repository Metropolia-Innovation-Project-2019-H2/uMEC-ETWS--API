# mooseetws-edge-computing
Object detection based on tensorflow serving REST API, risk identification and reporting.

#### Containers

- Tensorflow serving

    - Serve pre-trained models using tensorflow serving REST API
    - Used ssdlite_mobilenet_v2_coco_2018_05_09 
    - API endpoint:
    
    ```
    curl --request GET \
      --url http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09
    ```
    
    - Predict API:
    
    ```
    curl --request POST \
      --url http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09:predict \
      --header 'content-type: application/json' \
      --data '{  "instances": [ "foo", "bar", "baz" ]}'
      
    ```

- Camera feeding
    - Periodically scan usb camera and use tensorflow API to detect potential threats.
    - Post notification to cloud service when risks are identified.

#### Reference: 
- Tensorflow serving for ARM: https://hub.docker.com/r/emacski/tensorflow-serving
- Tensorflow serving documentation: https://www.tensorflow.org/tfx/serving/docker




### Moose camera detector setup for raspberry pi 3B+
First clone into this directory which has been setup by pengdev https://github.com/mooseetws/mooseetws-tensorflow-detection.git
and then pull the project to your local machine.
Run the following on your command line
```
git clone https://github.com/mooseetws/mooseetws-tensorflow-detection.git

git pull
```
Now that you have the project on your local machine you would want to update and upgrade your raspberry pi and install all necessary dependencies.
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install libffi-dev libssl-dev

sudo apt-get install -y python python-pip

```
since the project is running on docker we would need to install docker-compose to run camera container.
```
sudo pip install docker-compose

```
Next step is to download the tensorflow model. Do that by running the following on your command line

```
cd mooseetws-tensorflow-detection/tensorflow-serving/models/
nano fetch_model.sh
```
copy the commands from the shell script and paste to your command line
```
wget http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar$
tar -xzvf ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz
cd ssdlite_mobilenet_v2_coco_2018_05_09
mv saved_model 1

```
Because Camera-feed uses opencv for capturing camera image, and even when opencv-python was installed on docker for raspberry pi it  had failed to recognize opencv module.
Due to this bug we decided to test already saved images using pillow BY creating a moose-test folder to mimic camera-feed folder.

### NB on ubuntu this project works fine with opencv. At the end of this documentation you will find steps to run this on ubuntu.


Navigate back to the  /mooseetws-tensorflow-detection-master/ directory  and RUn the following command
```
nano docker-compose.yml
```
make sure your compose file looks like this
```
version: "2.2"
services:
  tensorflow-serving:
    # if running on raspberry pi
    image: emacski/tensorflow-serving:latest-arm32v7
    # if running on x86 pc or mac
    #image: tensorflow/serving:latest
    container_name: "serve_base"
    security_opt:
      - apparmor:unconfined
    stdin_open: true
    tty: true
    volumes:
      - ./tensorflow-serving/models:/models
      #- ./tensorflow-serving/models_config:/models/models.config
    environment:
      - MODEL_NAME=ssdlite_mobilenet_v2_coco_2018_05_09
    ports:
      - "8500:8500"
      - "8501:8501"
    healthcheck:
      test:
        [
          "CMD",
          "curl",
          "--fail",
          "http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09",
        ]
      interval: 10s
      timeout: 10s
      retries: 3

    
  moose-test:

    build: ./moose_test
    container_name: "moose_test"

    volumes:
      - ./moose_test/images:/images
    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined
    stdin_open: true
    tty: true
    ports:
      - "5000:5000"

```
After this save your file and navigate to the moose-test folder
 Create a folder called images and move the cats.jpg and moose-test.jpeg to the images folder
 open the dockerfile with nano text-editor and Make sure it looks like this
 
```
# if running on rapberry pi
FROM arm32v7/python:3
# if running on x86 based PC
#FROM python:3.7

RUN apt-get update
RUN apt-get upgrade -y
RUN apt install python3-pip
RUN pip install Pillow
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install pprintpp

COPY test.py /home/pi/Moose/mooseetws-tensorflow-detection-master/moose_test/test.py

CMD ["python3", "/home/pi/Moose/mooseetws-tensorflow-detection-master/moose_test/test.py"]
```
After this save the Dockerfile and open the test.py with a text-editor.
In this python file we totally eliminate the use of opencv and use pillow instead to read and process the images
Make sure your test.py looks like this!
```

#!/usr/bin/env python3
import PIL.Image
import numpy
import requests
from pprint import pprint
import time
import os
import glob


#filename = 'moose_test.jpeg'
TENSORFLOW_SERVING_URL = 'http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09:predi$
filename = os.path.join('images/moose_test.jpeg')
# hardcode potential threats id and label mapping, took from mscoco_complete_label_map.pbtxt
obj_dict = {17: 'cat', 18: 'dog', 19: 'horse',
            20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear', 24: 'zebra', 25: 'giraffe'}

#read image from file
image = PIL.Image.open(filename)
image_np = numpy.array(image)

# read image from usb camera with opencv
#cam = VideoCapture(0)   # 0 -> index of camera
#s, img = cam.read()
#cam.release()
#image_np = cvtColor(img, COLOR_BGR2RGB)

# construct post message to use tensorflow service
payload = {"instances": [image_np.tolist()]}
start = time.perf_counter()
res = requests.post(TENSORFLOW_SERVING_URL, json=payload)
res.status_code
print(f"Took {time.perf_counter()-start:.2f}s")
#pprint(res.json())

# parse returned json data
predictions = res.json()['predictions']
print("Found", len(predictions), "prediction results")
parsedData = []
for prediction in predictions:
    print("numer of detections:", prediction['num_detections'])
    for i in range(int(prediction['num_detections'])):
        obj_class = prediction['detection_classes'][i]
        obj_score = prediction['detection_scores'][i]
        # According to mscoco_complete_label_map, big animals are identified from 17-25
        if obj_class > 16 and obj_class < 26:
            print(obj_dict[obj_class],
                  obj_score)
            if obj_score > 0.5:
                print("warning !!! found animal, potentially it is a",
                      obj_dict[obj_class])
        else:
            print("found safe object:", obj_class, obj_score)



```
After this we are ready to build the docker container.
Run the following command!
```
docker-compose build
docker-compose up

```
You might get a connection error  because tensorflow-serving url is activated on localhost on the local machine but you are trying to curl from docker which has a different network- namespace.
The problem has not been fixed yet so to check that ur image detection is working
Open a new terminal
### Note: leave the docker-compose up command running and open new terminal
Navigate to the moose-test folder and run
```
python3 test.py
```
You should get a result of your prediction directly to your terminal
### RUNNING THE MOOSE DETECTION ON UBUNTU

Navigate back to the  /mooseetws-tensorflow-detection-master/ directory  and RUn the following command
```
nano docker-compose.yml
```
make sure your compose file looks like this
```
version: "2.2"
services:
  tensorflow-serving:
    # if running on raspberry pi
    image: emacski/tensorflow-serving:latest-arm32v7
    # if running on x86 pc or mac
    #image: tensorflow/serving:latest
    container_name: "serve_base"
    security_opt:
      - apparmor:unconfined
    stdin_open: true
    tty: true
    volumes:
      - ./tensorflow-serving/models:/models
      #- ./tensorflow-serving/models_config:/models/models.config
    environment:
      - MODEL_NAME=ssdlite_mobilenet_v2_coco_2018_05_09
    ports:
      - "8500:8500"
      - "8501:8501"
    healthcheck:
      test:
        [
          "CMD",
          "curl",
          "--fail",
          "http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09",
        ]
      interval: 10s
      timeout: 10s
      retries: 3

    
  camera-feed:

    build: ./camera-feed
    container_name: "camera-feed"

    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined
    stdin_open: true
    tty: true
    ports:
      - "5000:5000"
```
After this save your file and navigate to the camera-feed folder
 open the dockerfile with nano text-editor and Make sure it looks like this
 
```
# if running on rapberry pi
FROM arm32v7/python:3
# if running on x86 based PC
#FROM python:3.7

RUN apt-get update
RUN apt-get upgrade -y
RUN apt install python3-pip
RUN pip install Pillow
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install pprintpp
RUN pip install opencv-python

COPY start.py /home/demo/start.py

CMD ["python3", "/home/demo/start.py"]
```
after this save the Dockerfile and open the start.py with a text-editor.
Make sure your start.py looks like this!
```
import PIL.Image
import numpy
import requests
from pprint import pprint
import time
from cv2 import *

TENSORFLOW_SERVING_URL = 'http://localhost:8501/v1/models/ssdlite_mobilenet_v2_coco_2018_05_09:predi$
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

time.sleep(5)
print('waited for a min.')
r = requests.get(TENSORFLOW_SERVING_URL)
pprint(r.json())

while True:

        read_camera()


```
After this we are ready to build the docker container.
RUn the following command!
```
docker-compose build
docker-compose up

```
You also get a connection error  because tensorflow-serving url is activated on localhost on the local machine but you are trying to curl from docker which has a different network- namespace.
The problem has not been fixed yet so to check that ur camera detection is working
Open a new terminal
### Note: leave the docker-compose up command running and open new terminal
Navigate to the camera-feed folder and run
```
python3 start.py
```
You should see texts of prediction showing on your terminal

# OpenAPI generated server

## Overview
This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. By using the
[OpenAPI-Spec](https://openapis.org) from a remote server, you can easily generate a server stub.  This
is an example of building a OpenAPI-enabled Flask server.
<br>
## What is this project?

This is a student project that was made in collaboration with Nokia.
The goal was to create a localhost server with OpenAPI Generator, that utilizes a usb camera to take pictures remotely and uploads the images to the localhost server.


This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.5.2+
<br>
Raspberry Pi
<br>
Laptop
<br>
Usb Camera

# The Following Instructions are for Recreating the Entire Project


OpenAPI Specification is an API description format, formerly known as Swagger Specification
npm is a software registry that contains the required code package to install OpenAPI. 


#### First create a folder OpenApi, then go to that folder
```
mkdir /home/pi/OpenApi
cd OpenApi
apt-get install npm
```
#### Then install OpenApi Generator
```
npm install @openapitools/openapi-generator-cli -g
```
#### Create parts.yaml with command: 
```
touch parts.yaml. 
```
#### Then paste the following code into that file.
```
openapi: 3.0.0
info:
  version: '1'
  title: 'Moose-etws'
  description: 'api for getting images from server'
servers:
  - url: https://localhost:8080
	description: Tensorflow Server

paths:
  /camera:
	get:
  	summary: Get image.
  	description: Retrieve the current camera image.
 	# parameters:
  	#  - name: image_id
   	#  required: true
    	#  description: the UUID of the image
     	# schema:
      	#  type: string
        
  	responses:
    	"200":
      	description: Status 200
      	content:
        	image/jpeg:
          	schema:
            	type: string
            	format: binary
            	description: The current camera image.
```
#### Then run the following command into command line interface (CLI):
```
openapi-generator generate -i parts.yaml -g python-flask -o /Openapi/local
```
-i specifies what file contains your openapi specification

-g specifies what programming language you are generating for your client or server code

-o specifies what directory the code should be generated.(if not specified the code is generated in the current working directory)

#### This will provide a readme file in the current folder, the “ls” command will confirm. Follow its instructions to get the localhost web server running.
### You can skip the below step and follow the instructions on the Readme for a little bit more challenge. But continue onwards with this documentation for detailed instruction on how to run the server


## Usage
To run the server, execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m openapi_server
```

and open your browser to here:

```
http://localhost:591/ui/
```

Your OpenAPI definition lives here:

```
http://localhost:591/openapi.json
```
## Note: The default port for the previous steps is 8080 but the port was occupied so 591 was used. To change the port you want your server to run. follow the below step
```
cd openaapi_server
touch __main__.py
```
## navigate to the *app.run(port=591)* code inside the main func(): and put your desired port number

 
To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

There should be several files and folders within the openapi folder. Open the “openapi_server” folder and then “controllers” . Once inside create file named default_controller.py

#### Type
```
cd openapi_server/controllers/

Type touch default_controller.py

```
### Before you run the bellow code install opencv library for reading your raspberry pi camera
```
pip3 install opencv-python
```

#### Paste the following code when inside the default_controller.py:
```
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
```

 After this navigate to your browser and enter this url. http://localhost:yourPort/camera
 (http://194.110.231.138:591/camera)
  Everytime you reload the page the server receives a get image requests and u can see your current image being captured and displayed on server.
 ## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```
bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```
<br>
<br>
