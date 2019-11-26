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
