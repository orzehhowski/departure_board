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
API_URL = "http://bimba.orzehhowski.pl/?n=14"

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

def connect_wifi(display: ssd1306.SSD1306_I2C) -> network.WLAN:
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

def get_data(display: ssd1306.SSD1306_I2C) -> dict:
  if display:
    response = urequests.get(API_URL)
    if response.status_code == 200:
      data = ujson.loads(response.text)
      response.close()
      return data
    else:
      print_message("HTTP error: {}".format(response.status_code))
      response.close()

def strip_polish(text):
    mapping = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l',
        'ń': 'n', 'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L',
        'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ż': 'Z', 'Ź': 'Z'
    }
    return ''.join(mapping.get(c, c) for c in text)

def print_departures(display: ssd1306.SSD1306_I2C, departures: list, offset_y: int, primary_offset_x: int, space_available) -> None:
  if display:
    display.fill(0)
    for i in range(6):
      if (i < len(departures)):
        departure = departures[i]
        
        destination = strip_polish(departure[1])

        # here we choose chunk fitting the offset_x
        destination += "   "
        
        offset_x = primary_offset_x % len(destination)

        # variant 1: no need for adding next iteration
        if offset_x + space_available < len(destination):
          destination = destination[offset_x:offset_x + space_available]

        # variant 2: we have to add next iteration
        elif offset_x + space_available >= len(destination):
          left = space_available + offset_x - len(destination)
          destination = destination[offset_x:] + destination[:left]

        message = "{}|{:3}|{}".format(departure[2][:5], departure[0], destination)
        display.text(message[:16], 0, i * 10)
    display.show()

# ints H, M, S
def get_departure_time(departure: list) -> tuple[int, int, int]:

  return tuple([int(x) for x in departure[2].split(":")])

def run():
  led = machine.Pin(LED_PIN, machine.Pin.OUT)
  led.off()
  display = connect_display(DISPLAY_SCL, DISPLAY_SDA)
  try:
    connect_wifi(display)
    departures = get_data(display)["departures"]

    sleep_time = 0.5
    sleep_multiplier = 1 // sleep_time
    import ntptime # type: ignore
    while True:
      for i in range(60 * 60 * 24 * sleep_multiplier):
          
        # sync time every hour
        if (i % (3600 * sleep_multiplier) == 0):
          ntptime.settime()

        # delete obsolete departures
        if (i % (60 * sleep_multiplier) == 0):
          now = list(time.localtime())[3:6]
          # timezone!
          now[0] += 2
          now[0] %= 24
          new_departures = [
            dep for dep in departures
            if get_departure_time(dep) >= tuple(now)
          ]
          departures = new_departures

        # fetch new data
        if (len(departures) < 9):
          departures = get_data(display)["departures"]

        print_departures(display, departures, 0, i, 6)
        time.sleep(sleep_time)

  except Exception as e:
    print_message(display, e)
    show_error()

run()
