# OpenAPI generated server

## Overview
This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. By using the
[OpenAPI-Spec](https://openapis.org) from a remote server, you can easily generate a server stub.  This
is an example of building a OpenAPI-enabled Flask server.
<br>
## What is this project?

This is a student project that was made in collaboration with Nokia.
The goal was to create a localhost server with OpenAPI Generator, that utilizes a usb camera to take pictures remotely and uploads the images to the localhost server.

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
navigate to the *app.run(port=591)* code inside the main func(): and put your desired port number

 
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
