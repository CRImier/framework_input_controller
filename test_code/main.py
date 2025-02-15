from machine import Pin, I2C, PWM
from time import sleep

#import usb_hid

i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400_000)
print(i2c.scan())

bl = PWM(Pin(29))
bl.freq(1000)

bl.duty_u16(65536//2)

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

#while True:
for i in range(3):
    for i in [fp_red, fp_white, fp_green, led_caps]:
        shiftOut(i)
        sleep(0.5)

def test_shorts():
    r = [12, 0, 13, 1, 14, 2, 15, 3]
    c = [16, 4, 17, 5, 18, 6, 19, 7, 20, 8, 21, 9, 22, 10, 23, 11]
    o = [24, 25, 26, 27, 28]
    p = r+c+o
    pins = [Pin(x, Pin.IN, Pin.PULL_UP) for x in p]

    r_n = ["KSI"+str(i) for i in range(len(r))]
    c_n = ["KSO"+str(i) for i in range(len(c))]
    o_n = ["TP_ID", "SW", "TP_SDA", "TP_SCL", "TP_INT"]
    p_n = r_n + c_n + o_n

    while True:
        for _ in range(1000000):
            shorted = []
            for i, pin1 in enumerate(pins):
                pin1.init(Pin.OUT)
                pin1.value(False)
                for j, pin2 in enumerate(pins):
                    if i == j:
                        continue
                    if not pin2.value():
                        shorted.append((i, j))
                pin1.init(Pin.IN, Pin.PULL_UP)
            if shorted:
                # see if everything is shorted to everything hehe
                print(_, ",")
                if len(shorted) < len(p)*(len(p)-1) // 2:
                    # just a few shorted, gotta list those
                    for i, j in shorted:
                        print("n: {} ({}) shorted to {} ({})".format(p_n[i], p[i], p_n[j], p[j]))
                else:
                    # most of them shorted, we list exceptions instead
                    l = []
                    for i, j in shorted: # unsophisticated flattening
                        if i not in l: l.append(i)
                        if j not in l: l.append(j)
                    for i, pin in enumerate(p):
                        if i not in l:
                            print("m: {} ({}) not connected".format(p_n[i], pin))
                    #print(shorted)
            sleep(0.05)

def test_keeb():
    r = [12, 0, 13, 1, 14, 2, 15, 3]
    c = [16, 4, 17, 5, 18, 6, 19, 7, 20, 8, 21, 9, 22, 10, 23, 11]
    r_t = [False for i in r]
    c_t = [False for i in c]
    r_n = ["KSI"+str(i) for i in range(len(r))]
    c_n = ["KSO"+str(i) for i in range(len(c))]

    rows = []
    cols = []

    for row in r:
        p = Pin(row, Pin.OUT)
        p.on()
        rows.append(p)

    for col in c:
        p = Pin(col, Pin.IN, Pin.PULL_UP)
        cols.append(p)

    pressed = []
    try:
        while True:
            for ri, row in enumerate(rows):
                row.off()
                for ci, col in enumerate(cols):
                    st = col.value()
                    if not st:
                        name = "{}-{}".format(ri, ci)
                        r_t[ri] = True
                        c_t[ci] = True
                        if name in pressed:
                            pass # print("Already pressed", name, "!")
                        else:
                            print("Pressed:", name)
                            pressed.append(name)
                row.on()
                #sleep(0.01)
            sleep(0.2)
    except KeyboardInterrupt:
        unc_r = [r_n[i] for i, el in enumerate(r_t) if not el]
        unc_c = [c_n[i] for i, el in enumerate(c_t) if not el]
        print("Faulty: ", end='')
        if unc_r+unc_c:
            print(",".join(unc_r+unc_c))
        else:
            print("none")



def test_i2c():
    while True:
      try:
        l = i2c.readfrom(0x2c, 1)[0]
        if l:
            d = i2c.readfrom(0x2c, l)
            if d[2] != 0x01:
                # only forward packets with a specific report ID, discard all others
                print("WARNING")
                print(l, d)
                print("WARNING")
            else:
                d = d[3:]
                print(l, len(d), d)
                #usb_hid.report(usb_hid.MOUSE_ABS, d)
      except OSError:
        # touchpad unplugged? retry in a bit
        sleep(0.01)

#print("short testing!")
#test_shorts()
#test_keeb()
test_i2c()
