#!/bin/bash

# prepare pretrained model to be used by the tensorflow serving
# need to be executed before the docker-compose start
wget http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz
tar -xzvf ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz
cd ssdlite_mobilenet_v2_coco_2018_05_09
mv saved_model 1