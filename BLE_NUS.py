# Bluetooth LE Nordic UART Service
# connect this ESP32 BLE through "Serial Bluetooth Terminal" app in your phone
import time
from machine import Pin
from machine import Timer
from time import sleep_ms
import ubluetooth, json, binascii

ble_msg = ""


class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.led_show_disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def led_show_connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def led_show_disconnected(self):
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg
        print(f'BLE IRQ: {event} {data}')
        if event == 1:  # _IRQ_CENTRAL_CONNECT:
            # A central (phone) has connected to this peripheral
            self.led_show_connected()

        elif event == 2:  # _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            self.advertiser()
            self.led_show_disconnected()

        elif event == 3:  # _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
        elif event == 28: # _IRQ_ENCRYPTION_UPDATE:
            conn_handle, encrypted, authenticated, bonded, key_size = data
            print("encryption update", conn_handle, encrypted, authenticated, bonded, key_size)
        elif event == 31: # _IRQ_PASSKEY_ACTION:
            conn_handle, action, passkey = data
            print("passkey action", conn_handle, action, passkey)
            if action == 4: # _PASSKEY_ACTION_NUMCMP:
                accept = int(input("accept? "))
                self.ble.gap_passkey(conn_handle, action, accept)
            elif action == 3: # _PASSKEY_ACTION_DISP:
                print("displaying 123456")
                self.ble.gap_passkey(conn_handle, action, 123456)
            elif action == 2: # _PASSKEY_ACTION_INPUT:
                print("prompting for passkey")
                passkey = int(input("passkey? "))
                self.ble.gap_passkey(conn_handle, action, passkey)
            else:
                print("unknown action")
        elif event == 20: # _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data
        elif event == 30: # _IRQ_SET_SECRET:
            sec_type, key, value = data
            key = sec_type, bytes(key)
            value = bytes(value) if value else None
            print("set secret:", key, value)
            if value is None:
                if key in self._secrets:
                    del self._secrets[key]
                    return True
                else:
                    return False
            else:
                self._secrets[key] = value
            return True
        elif event == 29: #_IRQ_GET_SECRET:
            sec_type, index, key = data
            print("get secret:", sec_type, index, bytes(key) if key else None)
            if key is None:
                i = 0
                for (t, _key), value in self._secrets.items():
                    if t == sec_type:
                        if i == index:
                            return value
                        i += 1
                return None
            else:
                key = sec_type, bytes(key)
                return self._secrets.get(key, None)
        """
        _IRQ_CENTRAL_CONNECT = const(1)
        _IRQ_CENTRAL_DISCONNECT = const(2)
        _IRQ_GATTS_WRITE = const(3)
        _IRQ_MTU_EXCHANGED = const(21)
        _IRQ_CONNECTION_UPDATE = const(27)
        """

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART,)
        ((self.tx, self.rx,),) = self.ble.gatts_register_services(SERVICES)
        self.ble.config(mtu=256)
        self.ble.gatts_write(self.rx, bytes(100))

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        # print("\r\n")
        # adv_data
        # raw: 0x02010209094553503332424C45
        # b'\x02\x01\x02\t\tESP32BLE'
        # 0x02: Length, 0x01 - AD_Type FLAG, 0x02 - General discoverable mode
        # \t is 0x09: Length, 0x09: AD_Type Name

        # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
        # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics


def buttons_irq(pin):
    led.value(not led.value())
    ble.send(f'LED state will be toggled to {led.value()}.')
    print('[Out] LED state toggled.')


led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")
but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)

usage_msg = 'Usage: read_LED to get status of LED; LED_off to turn off LED'

print('\nWaiting for bluetooth connection...\n\
connect ESP32 BLE through "Serial Bluetooth Terminal" app in your phone\n\
press Button 0 to toggle LED')

try:
    while True:
        if ble_msg:
            print(f'[In{len(ble_msg)}] {ble_msg}')
            if ble_msg == 'read_LED':
                msg = '[Out] ' + 'LED is ON.' if led.value() else 'LED is OFF.'
            elif ble_msg == 'LED_off':
                led.value(0)
                msg = '[Out] LED turns off.'
            else:
                msg = usage_msg
            print('[Out] '+msg)
            ble.send(msg)
            ble_msg = ''
        sleep_ms(100)

except:
    if ble.ble.active():
        ble.ble.active(False)
    ble.led_show_connected()
    print('\n\n=============== BLE NUS closed')
