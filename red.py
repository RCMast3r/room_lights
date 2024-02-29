import asyncio
from bleak import BleakScanner, BleakClient
from cheshire.compiler.state import LightState
from cheshire.generic.command import *
from cheshire.hal.devices import Connection, connect_to_ble_device

async def main():
    # Discover Bluetooth LE devices
    # discover = await BleakScanner.discover()
    connections: list[Connection] = []

    device = await BleakScanner.find_device_by_name(name='KS03~61385A')
    if connection := await connect_to_ble_device(device):
        print(f"Connected to {device.name}")

        connections.append(connection)

    async def send_all(state: LightState):
        # Push light state to connected devices
        for c in connections:
            await c.apply(state)
            

    # Update desired light state
    state = LightState()
    # state.update(SwitchCommand(on=True))
    state.update(BrightnessCommand(255))
    state.update(RGBCommand(0xff, 0x00, 0x00))
    # state.update(EffectCommand(Effect.JUMP_7))

    await send_all(state)


asyncio.run(main())