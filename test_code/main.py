from machine import Pin, I2C, PWM
from time import sleep

i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=100_000)
print(i2c.scan())

bl = PWM(Pin(29))
bl.freq(1000)

#bl.duty_u16(65536//2)

data_p = 24
clock_p = 25
latch_p = 28

# multi-purpose pins
data = Pin(data_p, Pin.IN, Pin.PULL_UP)
clock = Pin(clock_p, Pin.IN, Pin.PULL_UP)
latch = Pin(latch_p, Pin.IN, Pin.PULL_UP)

def shiftOut(byte):
    data = Pin(data_p, Pin.OUT)
    clock = Pin(clock_p, Pin.OUT)
    latch = Pin(latch_p, Pin.OUT)
    latch.off()
    for i in range(8):
        value = byte & 1<<i
        data.value(value)
        clock.on()
        clock.off()
    latch.on()
    data = Pin(data_p, Pin.IN, Pin.PULL_UP)
    clock = Pin(clock_p, Pin.IN, Pin.PULL_UP)
    latch = Pin(latch_p, Pin.IN, Pin.PULL_UP)

fp_red = 0xdf
fp_white = 0xbf
fp_green = 0x7f
led_caps = 0xef

"""
while True:
    for i in [fp_red, fp_white, fp_green]:
        shiftOut(i)
        sleep(0.1)
"""

r = [12, 0, 13, 1, 14, 2, 15, 3]
c = [16, 4, 17, 5, 18, 6, 19, 7, 20, 8, 21, 9, 22, 10, 23, 11]

rows = []
cols = []

for row in r:
    p = Pin(row, Pin.OUT)
    p.on()
    rows.append(p)

for col in c:
    p = Pin(col, Pin.IN, Pin.PULL_UP)
    cols.append(p)

def test():

    for ri, row in enumerate(rows):
        row.off()
        for ci, col in enumerate(cols):
            st = col.value()
            if not st:
                print("Pressed: {}-{}".format(ri, ci))
        row.on()
        #sleep(0.01)
    sleep(0.2)
