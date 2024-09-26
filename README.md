# Webcam demo

This is an example of how to use CompreFace face recognition with python sdk.

# Requirements

1. [Python](https://www.python.org/downloads/) (Version 3.7+)
2. [CompreFace](https://github.com/exadel-inc/CompreFace#getting-started-with-compreface)
3. [Compreface-python-sdk](https://github.com/exadel-inc/compreface-python-sdk)
4. [Opencv-python](https://pypi.org/project/opencv-python/)

# Face recognition demo

To run the demo, open `webcam_demo` folder and run:

```commandline
python compreface_webcam_recognition_demo.py --api-key your_api_key --host http://localhost --port 8000
```
* `--api-key` is your Face Recognition service API key. API key for this demo was created on step 5 of [How to Use CompreFace](https://github.com/exadel-inc/CompreFace/blob/master/docs/How-to-Use-CompreFace.md#how-to-use-compreface). Optional value. By default, the value is `00000000-0000-0000-0000-000000000002` - api key with celebrities demo.
* `--host` is the host where you deployed CompreFace. Optional value. By default, the value is `http://localhost`
* `--port` is the port of CompreFace instance. Optional value. By default, the value is `8000`

# Face detection demo

To run the demo, open `webcam_demo` folder and run:

```commandline
python compreface_webcam_detection_demo.py --api-key your_api_key --host http://localhost --port 8000
```
* `--api-key` is your Face Detection service API key. API key for this demo was created on step 5 of [How to Use CompreFace](https://github.com/exadel-inc/CompreFace/blob/master/docs/How-to-Use-CompreFace.md#how-to-use-compreface).
* `--host` is the host where you deployed CompreFace. Optional value. By default, the value is `http://localhost`
* `--port` is the port of CompreFace instance. Optional value. By default, the value is `8000`
python compreface_webcam_recognition_demo.py --api-key your_api_key --host http://localhost --port 8000
py compreface_webcam_recognition_demo.py --api-key 962d731f-1006-4654-8307-c86cfc091b3d --host http://localhost --port 8000
py compreface_webcam_recognition_demo.py --api-key 00000000-0000-0000-0000-000000000002 --host http://localhost --port 8000

# my req
pip install openpyxl pandas opencv-python compreface-sdk sqlalchemy psycopg2
pip install urllib3==1.25.11
Successfully uninstalled urllib3==2.2.3

Package            Version
------------------ -----------
certifi            2024.8.30
charset-normalizer 3.3.2
compreface-sdk     0.6.0
et-xmlfile         1.1.0
greenlet           3.0.3
idna               3.8
numpy              2.1.1
opencv-python      4.10.0.84
openpyxl           3.1.5
pandas             2.2.2
pip                22.0.2
psycopg2           2.9.9
python-dateutil    2.9.0.post0
pytz               2024.1
requests           2.32.3
requests-toolbelt  0.9.1
setuptools         59.6.0
six                1.16.0
SQLAlchemy         2.0.34
typing_extensions  4.12.2
tzdata             2024.1
urllib3            1.25.11

--------------- req ------------
certifi==2024.8.30
charset-normalizer==3.3.2
compreface-sdk==0.6.0
et-xmlfile==1.1.0
greenlet==3.0.3
idna==3.8
numpy==2.1.1
opencv-python==4.10.0.84
openpyxl==3.1.5
pandas==2.2.2
psycopg2==2.9.9
python-dateutil==2.9.0.post0
pytz==2024.1
requests==2.32.3
requests-toolbelt==0.9.1
six==1.16.0
SQLAlchemy==2.0.34
typing_extensions==4.12.2
tzdata==2024.1
urllib3==1.25.11
----------------------

pi req
sudo apt-get install libgl1-mesa-glx
sudo apt-get install libgtk2.0-dev libcanberra-gtk-module

# curl http://192.168.1.149:8000/api/v1/recognition/recognize 

pass@webcam

pi display config ------------
sudo nano /boot/config.txt

add the lines--------
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=16  # You can adjust this for your resolution (16 is 1080p @ 60Hz)

sudo reboot

ssh known_hosts--------------------------
Add correct host key in /home/irfan/.ssh/known_hosts to get rid of this message.
Offending ED25519 key in /home/irfan/.ssh/known_hosts:4
  remove with:
  ssh-keygen -f "/home/irfan/.ssh/known_hosts" -R "192.168.1.161"
Host key for 192.168.1.161 has changed and you have requested strict checking.
Host key verification failed.
irfan@irfan-Latitude-5480:~/autobits$ ssh-keygen -f "/home/irfan/.ssh/known_hosts" -R "192.168.1.161"
# Host 192.168.1.161 found: line 4
/home/irfan/.ssh/known_hosts updated.
Original contents retained as /home/irfan/.ssh/known_hosts.old