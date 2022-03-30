# ESP32 S2

ESP32 is a feature-rich MCU (microcontroller unit) with integrated Wi-Fi and Bluetooth connectivity for a wide-range of applications.
S2 is supported by micropython for fast POC development.

HW: ESP32 S2
FW: MicroPython v1.18


## SD-display.py
### Display numbers in 7-segment Display by ESP32 w/ micropython


- define a dict to store all numbers segment mapping
- mapping ABCDEFGH segments to PINs, one bit by one

Ref: https://docs.sunfounder.com/projects/thales-kit/en/latest/led_segment_display.html#led-segment-display

## SD-74HC595.py
### Display numbers in four 7-segment Display by ESP32 w/ micropython, using 74HC595 shift register IC

74HC595 shift register IC
- use 3 GPIO (clock, latch, data), capable of output 8bits (Q0~Q7) in parallel
diagram：
https://microcontrollerslab.com/esp32-74hc595-4-digit-7-segment-display/

## BLE_NUS.py
ESP32 act as Bluetooth LE BLE NUS app. Receive / Send data to BLE Client (phone or PC)

### ESP32 BLE HID
ESP32 act as mouse, keyboard. ref to: https://www.bilibili.com/read/cv15067064

## AndroidMotorControlBLE.7z 
This is Android 5 app to interact with ESP32 BLE

