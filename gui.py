import asyncio
from bleak import BleakScanner
from cheshire.compiler.state import LightState
from cheshire.generic.command import BrightnessCommand, RGBCommand, SwitchCommand
from cheshire.hal.devices import connect_to_ble_device
import PySimpleGUI as sg

async def main():
    # Attempt to connect to the BLE device
    device = await BleakScanner.find_device_by_name(name='KS03~61385A')
    connection = None
    if device:
        connection = await connect_to_ble_device(device)
        if connection:
            print(f"Connected to {device.name}")
        else:
            print("Failed to connect to the device.")
            return
    else:
        print("Device not found.")
        return

    async def send_all(connection, state):
        # Push light state to the connected device
        await connection.apply(state)

    # Define the layout of the GUI
    layout = [
        [sg.Text('Brightness (0-255):'), sg.Slider(range=(0, 255), orientation='h', size=(34, 20), default_value=50)],
        [sg.Text('R:'), sg.Slider(range=(0, 255), orientation='h', size=(10, 20), default_value=255),
         sg.Text('G:'), sg.Slider(range=(0, 255), orientation='h', size=(10, 20), default_value=255),
         sg.Text('B:'), sg.Slider(range=(0, 255), orientation='h', size=(10, 20), default_value=255)],
        [sg.Button('Apply'), sg.Button('Turn Off'), sg.Button('Exit')]
    ]

    # Create the Window
    window = sg.Window('LED Controller', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == 'Apply':
            # Update desired light state to turn on with specified brightness and color
            state = LightState()
            state.update(SwitchCommand(on=True))  # Ensure the lights are turned on
            brightness = int(values[0])
            r, g, b = int(values[1]), int(values[2]), int(values[3])

            state.update(BrightnessCommand(brightness))
            state.update(RGBCommand(r, g, b))

            await send_all(connection, state)

        if event == 'Turn Off':
            # Update desired light state to turn off
            state = LightState()
            state.update(SwitchCommand(on=False))  # Turn the lights off

            await send_all(connection, state)

    window.close()

# Ensure the event loop runs the main coroutine
if __name__ == "__main__":
    asyncio.run(main())
