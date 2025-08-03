## setup

This is a setup for (as directory name indicates) ESP8266 microcontroller and SSD1306 screen.

## how to run it

When you have ESP connected to computer and micropython firmware flashed, connect your screen to the board and set variables in main.py file to chosen pins numbers.

Then you can use these commands to run client on the board (at least on linux):

```
cd ./client/esp8266_ssd1306
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
rshell --port [your_device_port] cp ./main.py /pyboard
```

Then restart device, and app should run when device boots.