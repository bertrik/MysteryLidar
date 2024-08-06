# MysteryLidar
Investigation of an inexpensive Lidar bought off Aliexpress

See https://revspace.nl/MysteryLidar

# Preparation
To prepare running the test application:
* make sure you have python3 and pip3 installed:
```
sudo apt install python3-pip
```
* clone the software:
```
git clone https://github.com/bertrik/MysteryLidar
```
* create a python virtual environment and install dependencies:
```
cd MysteryLidar/python
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

# Usage
To run the application:
* if not done already, activate the venv:
```
source .venv/bin/activate
```
* run the application:
```
./lidar.py
```

You should now see a bunch of numbers running on the terminal, one line per packet.
Also you should see a window showing the boundaries of the things around you as seen by the LIDAR.
