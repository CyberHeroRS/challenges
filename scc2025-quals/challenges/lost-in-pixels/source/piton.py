from machine import Pin, I2C
import ssd1306
import time

i2c = I2C(0, scl=Pin(1), sda=Pin(0))

oled = ssd1306.SSD1306_I2C(128, 32, i2c)

oled.fill(0)
oled.show()

time.sleep(2)

oled.text('Welcome to SCC', 0, 0)
oled.show()

time.sleep(20)

oled.fill(0)
oled.show()

oled.text('Flag:', 0, 0)
oled.text('SCC{i2c_ssd1306}', 0, 8)
oled.show()

time.sleep(10)

oled.fill(0)
oled.show()
