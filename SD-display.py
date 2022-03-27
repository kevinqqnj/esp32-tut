
import time
from machine import Pin
from random import randint

led = Pin(2, Pin.OUT) 
switch = Pin(23, Pin.OUT) 

# define 8 GPIO pins to control 7-Segment Display
p1 = Pin(25, Pin.OUT)   # A 
p2 = Pin(4, Pin.OUT)    # B
p3 = Pin(5, Pin.OUT)    # C
p4 = Pin(18, Pin.OUT)  # D
p5 = Pin(19, Pin.OUT)  # E
p6 = Pin(13, Pin.OUT)  # F
p7 = Pin(12, Pin.OUT)  # G
p8 = Pin(27, Pin.OUT)  # H
pins = [p1, p2, p3, p4, p5, p6, p7, p8] # LSB <-

def get_bit_val(byte, index):
    """
    得到某个字节中某一位（Bit）的值
    :param byte: 待取值的字节值
    :param index: 待读取位的序号，从右向左0开始，0-7为一个完整字节的8个位
    :returns: 返回读取该位的值，0或1
    """
    # print(byte, type(byte), index)
    if (byte) & (1 << index):
        return 1
    else:
        return 0


# def set_bit_val(byte, index, val):
#     """
#     更改某个字节中某一位（Bit）的值
#     :param byte: 准备更改的字节原值
#     :param index: 待更改位的序号，从右向左0开始，0-7为一个完整字节的8个位
#     :param val: 目标位预更改的值，0或1
#     :returns: 返回更改后字节的值
#     """
#     if val:
#         return byte | (1 << index)
#     else:
#         return byte & ~(1 << index)

digitals = {
    '0': 0x3f, # 0b00111111 LSB: HGFEDCBA
    '1': 0x6,  # 0x06 will be string during bit shifting, so use 0x6
    '2': 0x5b,
    '3': 0x4f,
    '4': 0x66,
    '5': 0x6d,
    '6': 0x7d,
    '7': 0x7,
    '8': 0x7f,
    '9': 0x6f,
    '.': 0x80,
    'blank': 0,
}

def setp(value):
    for i in range(8): # 0..7
        pins[i].value(get_bit_val(value, i))


# show digital numbers
def blink1(): 
    # for ind, val in enumerate(list1):
    for key, value in digitals.items():
        print(key)
        setp(digitals[key])
        time.sleep(.3)


def main():
    try:
        print('='*20, "Start ...")
        led.off()
        switch.value(1) # other LED off (1)
        setp(digitals['blank'])
        blink1()

        num_string = input('Pls input numbers (e.g.345.01): ')
        for num in num_string:
            setp(digitals[num])
            print(f'{num}: 0b{digitals[num]:08b}')
            time.sleep(1)
        print('='*20, 'done.')
    except KeyboardInterrupt:
        print('='*20, 'manual interrupted!')
    setp(digitals['blank'])

if __name__ == '__main__':
    main()
