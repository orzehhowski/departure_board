import machine # type: ignore
import ssd1306 # type: ignore
import network # type: ignore
import urequests # type: ignore
import ujson # type: ignore
import time
import my_secrets
import gc

DISPLAY_SCL = 4
DISPLAY_SDA = 5
LED_PIN = 2
ADC_PIN = 0

WIFI_SSID = my_secrets.WIFI_SSID
WIFI_PASSWORD = my_secrets.WIFI_PASSWORD
API_URL = "http://bimba.orzehhowski.pl/?n=22"

tick_flag = False

# phisical error indication - 3 rapid LED flashes 
def show_error() -> None:
  led = machine.Pin(LED_PIN, machine.Pin.OUT)
  for _ in range(3):
    led.on()
    time.sleep(0.25)
    led.off()
    time.sleep(0.25)
  led.on()

# connect to SSD1306 display and return it's object
def connect_display(display_scl: int, display_sda: int) -> ssd1306.SSD1306_I2C:
  i2c = machine.I2C(scl=display_scl, sda=display_sda)
  if 60 not in i2c.scan():
    raise RuntimeError("Display not found")
  
  display = ssd1306.SSD1306_I2C(128, 64, i2c)
  display.fill(0)
  
  return display

# print text message on the display
def print_message(display: ssd1306.SSD1306_I2C, message: str) -> None:
  display.fill(0)
  i = 0
  while i < 5 and i * 16 < len(message):
    display.text(message[i * 16: i * 16 + 16], 0, i*10)
    i += 1
  display.show()

# connect to the wifi network with status messages on display 
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

# send HTTP request to API URL
def get_data(display: ssd1306.SSD1306_I2C) -> dict:
  response = urequests.get(API_URL)
  if response.status_code == 200:
    data = ujson.loads(response.text)
    response.close()
    return data
  else:
    print_message(display, "HTTP error: {}".format(response.status_code))
    response.close()

# trim message from polish signs
def strip_polish(text) -> str:
    mapping = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l',
        'ń': 'n', 'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L',
        'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ż': 'Z', 'Ź': 'Z'
    }
    return ''.join(mapping.get(c, c) for c in text)

# pretty-printing departures
def print_departures(display: ssd1306.SSD1306_I2C, departures: list, offset_y: int, primary_offset_x: int, space_available: int) -> None:
  if display:
    display.fill(0)
    for i in range(6):
      if (i + offset_y < len(departures)):
        departure = departures[i + offset_y]
        
        destination = strip_polish(departure[1])

        # if destination fits the space, we don't need to play with offset
        # example: |POLABSKA |
        if len(destination) <= space_available:
          offset_x = 0

        else:
          # here we choose chunk fitting the offset_x
          destination += "   "
          
          offset_x = primary_offset_x % len(destination)

          # variant 1: no need for adding next iteration
          # example for MILOSTOWO: |MILOSTOW|
          if offset_x + space_available < len(destination):
            destination = destination[offset_x:offset_x + space_available]

          # variant 2: we have to add next iteration
          # example for MILOSTOWO: |OWO   MI|
          elif offset_x + space_available >= len(destination):
            left = space_available + offset_x - len(destination)
            destination = destination[offset_x:] + destination[:left]

        message = "{}|{:3}|{}".format(departure[3], departure[0], destination)
        display.text(message[:16], 0, i * 10)
    display.show()

# ints H, M, S
def get_departure_time(departure: list) -> tuple[int, int, int]:

  return tuple([int(x) for x in departure[2].split(":")])

def hms_to_sec(h: int, m: int, s: int) -> int:
  return h * 3600 + m * 60 + s

# Timer handler - sets the tick_flag
def tick(timer: machine.Timer) -> None:
    global tick_flag
    tick_flag = True

# 10 zones - from 0 to 9
def get_adc_zone(adc: machine.ADC) -> int:
  val = adc.read()
  if val < 1000:
    return val // 100
  return 10

def run():
  global tick_flag

  led = machine.Pin(LED_PIN, machine.Pin.OUT)
  potentiometer = machine.ADC(ADC_PIN)
  led.on()
  display = connect_display(DISPLAY_SCL, DISPLAY_SDA)
  try:
    connect_wifi(display)
    departures = get_data(display)["departures"]

    # letters float left every sleep_time * 5
    # adc change checks every sleep_time
    sleep_time = 0.1
    sleep_multiplier = 1 // sleep_time
    import ntptime # type: ignore

    # Start the timer
    timer = machine.Timer(-1)
    timer.init(period=int(sleep_time * 1000), mode=machine.Timer.PERIODIC, callback=tick)

    tick_count = -1
    # main loop
    while True:
      if tick_flag:
        tick_flag = False
        tick_count += 1

        # sync time every hour
        if (tick_count % (3600 * sleep_multiplier) == 0):
          ntptime.settime()

        # get current time
        now = list(time.localtime())[3:6]
        # timezone!
        now[0] += 1
        now[0] %= 24

        # delete obsolete departures
        if (tick_count % (60 * sleep_multiplier) == 0):
          new_departures = [
            dep for dep in departures
            if get_departure_time(dep) >= tuple(now)
          ]
          departures = new_departures

        # fetch new data
        if (len(departures) < 16):
          departures = get_data(display)["departures"]

        # calculate time remaining to departure
        for dep in departures:
          res = ""
          diff = hms_to_sec(*get_departure_time(dep)) - hms_to_sec(*tuple(now))
          # if diff < 0, we've got day switch, so we add 24h and alles gut
          # and one spare minute is useful for some offset situations
          if diff > -60 and diff < 0:
            diff = 0
          if diff < 0:
            diff += 86400

          # switch to minutes
          diff = diff // 60
          
          if diff < 60:
            res = "{:2}m".format(diff)
          else:
            # and now switch to hours
            res = "{:2}h".format(diff // 60)

          # add result as third element
          if len(dep) > 3:
            dep[3] = res
          else:
            dep.append(res)

        # check ADC for offset y
        offset_y = get_adc_zone(potentiometer)

        print_departures(display, departures, offset_y, tick_count // 5, 8)
        gc.collect()

  except Exception as e:
    show_error()
    print_message(display, str(e))

run()
