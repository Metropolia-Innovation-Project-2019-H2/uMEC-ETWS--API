# if running on rapberry pi
FROM arm32v7/python:3.7
# if running on x86 based PC
#FROM python:3.7

#WORKDIR /home/pi/Moose/mooseetws-tensorflow-detection-master

RUN pip install Pillow
RUN pip3 install numpy
RUN pip3 install requests
RUN pip3 install pprintpp

#RUN pip3 install wheel
#RUN pip3 install opencv-python
#RUN import cv2
#The below code is to manually compile opencv-python inside docker takes about 4-6 hours. But this did not solve the problem it was intended for.
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install apt-utils -y
RUN apt-get install build-essential cmake pkg-config -y
RUN apt-get install libjpeg-dev libtiff5-dev libpng-dev -y
RUN apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
RUN apt-get install libxvidcore-dev libx264-dev -y
RUN apt-get install libgtk2.0-dev libgtk-3-dev -y
RUN apt-get install libatlas-base-dev gfortran -y
RUN apt-get install python3 python3-setuptools python3-dev -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install numpy

WORKDIR /

RUN wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.0.zip && unzip opencv.zip
RUN wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.0.zip && unzip opencv_contrib.zip
RUN mkdir /opencv-3.4.0/build \
&& cd /opencv-3.4.0/build \
&& cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D BUILD_opencv_java=OFF \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=ON \
-D PYTHON_DEFAULT_EXECUTABLE=$(which python3) \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D BUILD_EXAMPLES=ON\
-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.0/modules \
-D WITH_CUDA=OFF \
-D BUILD_TESTS=OFF \
-D BUILD_PERF_TESTS= OFF .. \
&& make install \
&& ldconfig
RUN ln -s \
  /usr/local/python/cv2/python-3.7/cv2.cpython-37m-x86_64-linux-gnu.so \
  /usr/local/lib/python3.7/site-packages/cv2.so

RUN apt-get install python3-opencv -y


COPY start.py /home/pi/start.py


CMD ["python3", "/home/pi/start.py"]
