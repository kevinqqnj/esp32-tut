# python 3.8
# BLE client app running on PC, to chat with BLE NUS Server on ESP32.
# MTU default is 23, could be configured in BLE

import asyncio
import logging
import time

import aioconsole
from bleak import BleakClient

address = '<your-BLE-address>'


def notify_callback(sender: int, data: bytearray):
    print(f"BLE{sender}: {data.decode('utf8').strip()}")


async def main(address, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        import sys
        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address) as client:
        t = await client.is_connected()
        log.info(f"Connected: {t}")
        TX_UUID, NOTIFY_UUID = '', ''
        for service in client.services:
            log.debug(f"[Service] {service.uuid}: {service.description}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = None
                log.debug(f"\t[Characteristic] {char.uuid}: {char.properties} | "
                         f"Name:{char.description}, Value: {value} ")
                for descriptor in char.descriptors:
                    value = await client.read_gatt_descriptor(descriptor.handle)
                    log.debug(f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)}")

                if "write" in char.properties:
                    TX_UUID = char.uuid
                    await client.write_gatt_char(TX_UUID, b'Info=100', False)
                    log.info('test write')

                if "notify" in char.properties:
                    NOTIFY_UUID = char.uuid
                    await client.start_notify(NOTIFY_UUID, notify_callback)
                    log.debug('notify enabled')

        while True:
            txt = await aioconsole.ainput('Send msg to BLE device: ')
            await client.write_gatt_char(TX_UUID, txt.encode('utf8'), False)
            await asyncio.sleep(.1)

asyncio.run(main(address, True))
