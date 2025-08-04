import machine # type: ignore
import ssd1306 # type: ignore
import network # type: ignore
import urequests # type: ignore
import ujson # type: ignore
import time
import my_secrets

DISPLAY_SCL = 4
DISPLAY_SDA = 5
LED_PIN = 2

WIFI_SSID = my_secrets.WIFI_SSID
WIFI_PASSWORD = my_secrets.WIFI_PASSWORD
API_URL = "https://bimba.orzehhowski.pl"

def show_error():
  led = machine.Pin(LED_PIN, machine.Pin.OUT)
  for i in range(3):
    led.on()
    time.sleep(0.25)
    led.off()
    time.sleep(0.25)
  led.on()

def connect_display(display_scl: int, display_sda: int) -> ssd1306.SSD1306_I2C:
  i2c = machine.I2C(scl=display_scl, sda=display_sda)
  if 60 not in i2c.scan():
    raise RuntimeError("Display not found")
  
  display = ssd1306.SSD1306_I2C(128, 64, i2c)
  display.fill(0)
  
  return display

def print_message(display: ssd1306.SSD1306_I2C, message: str) -> None:
  display.fill(0)
  i = 0
  while i < 5 and i * 16 < len(message):
    display.text(message[i * 16: i * 16 + 16], 0, i*10)
    i += 1
  display.show()

def connect_wifi(display: ssd1306.SSD1306_I2C = None) -> network.WLAN:
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(WIFI_SSID, WIFI_PASSWORD)

  if display:
    print_message(display, "connecting to wifi...")
  while not wlan.isconnected():
    time.sleep(0.5)

  if display:
    print_message(display, "connected! IP address: {}".format(wlan.ifconfig()[0]))

  return wlan


def run():
  try:
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    led.off()
    display = connect_display(DISPLAY_SCL, DISPLAY_SDA)
    connect_wifi(display)
    time.sleep(10)
    display.poweroff()
    led.on()
  except Exception as e:
    show_error()

run()