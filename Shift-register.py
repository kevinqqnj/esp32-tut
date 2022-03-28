"""
use 74HC595 shift register IC to drive four SSD (Seven-Segment Display)
HW: ESP32 S2
FW: MicroPython v1.18
by ezhqing@gmail.com 
2022-3-27
"""

import time, utime
from machine import Pin
from random import randint

dataPIN, clockPIN, latchPIN = 23, 18, 5
platch = Pin(latchPIN, Pin.OUT)
pclk = Pin(clockPIN, Pin.OUT) 
pdata = Pin(dataPIN, Pin.OUT)

# four 7-seg display selector
pDIG1 = Pin(22, Pin.OUT) 
pDIG2 = Pin(14, Pin.OUT) 
pDIG3 = Pin(12, Pin.OUT) 
pDIG4 = Pin(4, Pin.OUT) 
all_LED = [pDIG1, pDIG2, pDIG3, pDIG4]


def screenOff():
    pDIG1.value(1) # 5461AS type, 1 is not selected (OFF)
    pDIG2.value(1)
    pDIG3.value(1)
    pDIG4.value(1)


def main():
    print('='*20, "Start ...")
    try:
        screenOff()
        pdata.value(0)
        pclk.value(0)
        platch.value(0)

        digitals = [ 0x3f, 0x6, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x7, 0x7f, 0x6f, 0x80]
        # display 0-9 and DP. LSB mapping, '0'= 00111111: HGFEDCBA
        # if use MSB mapping: '0'=0b11111100 MSB: ABCDEFGH
        # MSB list: 0xfc, 0x60, 0xda, 0xf2, 0x66, 0xb6, 0xbe, 0xe0, 0xfe, 0xf6, 0x1

        while True:
            cnt = 0
            screenOff()
            tick = randint(0, 10000)
            print(tick)
            while cnt < 100:
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
                cnt += 1
        print(time.localtime(), '='*10, 'done!')
    except KeyboardInterrupt:
        print('='*20, 'manual interupted!')
    screenOff()

if __name__ == '__main__':
    main()
