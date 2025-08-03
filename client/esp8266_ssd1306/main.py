import machine # type: ignore
import ssd1306 # type: ignore
import time

DISPLAY_SCL = 4
DISPLAY_SDA = 5
LED_PIN = 2

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
    raise RuntimeError("Display not found")\
  
  display = ssd1306.SSD1306_I2C(128, 64, i2c)
  display.fill(0)
  
  return display

def run():
  try:
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    led.off()
    display = connect_display(DISPLAY_SCL, DISPLAY_SDA)
    display.text("wrecze ci", 0, 0)
    display.text("mandacik", 0, 10)
    display.text("za przekroczenie", 0, 20)
    display.text("pieknosci", 0, 30)
    display.show()
    time.sleep(10)
    display.poweroff()
    led.on()
  except Exception as e:
    show_error()

run()