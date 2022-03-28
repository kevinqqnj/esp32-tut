"""
show TouchPad value in SSD
HW: ESP32, 4 SSD, 74HC595
1. press BOOT button to call interrupt
2. touch Pin32 to change TouchPad value and show in SSD
"""

from machine import TouchPad, Pin
import time, utime
from machine import Pin
from random import randint

dataPIN, clockPIN, latchPIN = 23, 18, 5
touchPIN = 32
platch = Pin(latchPIN, Pin.OUT)
pclk = Pin(clockPIN, Pin.OUT) 
pdata = Pin(dataPIN, Pin.OUT)

# four 7-seg display selector
pDIG1 = Pin(22, Pin.OUT) 
pDIG2 = Pin(14, Pin.OUT) 
pDIG3 = Pin(12, Pin.OUT) 
pDIG4 = Pin(4, Pin.OUT) 
all_LED = [pDIG1, pDIG2, pDIG3, pDIG4]

pBoot = Pin(0, Pin.IN, Pin.PULL_UP)
pTouch = TouchPad(Pin(touchPIN))
touchValue = pTouch.read()

digitals = [ 0x3f, 0x6, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x7, 0x7f, 0x6f, 0x80]
# display 0-9 and DP. LSB mapping, '0'= 00111111: HGFEDCBA


def screenOff():
    pDIG1.value(1) # 5461AS type, 1 is not selected (OFF)
    pDIG2.value(1)
    pDIG3.value(1)
    pDIG4.value(1)


def showLED():
    # print(f'Touch{pTouch}: {pTouch.read()}') # OFF: 500~600, touched: <200
    screenOff()
    while True:
        tick = touchValue # global var
        # set 4 SSD data individually
        for ind, value in enumerate([digitals[tick//1000%10], digitals[tick//100%10], \
            digitals[tick//10%10], digitals[tick%10]]):
            # LSB mapping: HGFEDCBA, pdata accept MSB first
            # e.g. '7' 00000111, [0, 0, 0, 0, 0, 1, 1, 1]
            bits = [value >> i & 1 for i in range(7, -1, -1)]
            # if need to show DP, set bits[0] = 1
            # print(f'{value:08b}, {bits}')
            for i in range(8):
                pdata.value(bits[i])
                pclk.value(1)
                pclk.value(0)
            screenOff()
            # only one SSD selector enabled at one time
            all_LED[ind].value(0)
            platch.value(1)
            platch.value(0)
            # rotate display in short time
            utime.sleep(0.0060)

            
def handle_interrupt(pin):
    global touchValue
    touchValue = int(pTouch.read())
    print(f'{pin} called intrupt, touch value: {touchValue}')

def main():
    print('\n', '='*20, "Start ...")
    pBoot.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)
    screenOff()
    pdata.value(0)
    pclk.value(0)
    platch.value(0)

    try:
        print(f'TouchPad value: {pTouch.read()}, press BOOT button to show current value...')
        print(f'(Touch Pin{touchPIN} can change value to LOW)')
        showLED()
        print('='*20, 'done!')
    except KeyboardInterrupt:
        print('='*20, 'manual interupted!')
    screenOff()

if __name__ == '__main__':
    main()
