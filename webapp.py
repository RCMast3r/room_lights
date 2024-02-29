from flask import Flask, request, render_template_string, redirect, url_for, flash
import asyncio
from threading import Thread
from bleak import BleakScanner
from cheshire.compiler.state import LightState
from cheshire.generic.command import BrightnessCommand, RGBCommand, SwitchCommand
from cheshire.hal.devices import connect_to_ble_device

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global variable to manage connection
global_connection = {'conn': None, 'status': 'Disconnected'}

# Enhanced HTML with connection status and a connect button
HTML = '''
<!doctype html>
<html>
<head><title>Light Control</title></head>
<body>
  <h2>Control Lights</h2>
  <p>Connection status: {{status}}</p>
  <form action="/connect" method="post">
    <input type="submit" value="Connect">
  </form>
  <form action="/set_light" method="post">
    Brightness (0-255): <input type="number" name="brightness" min="0" max="255" value="255"><br>
    R: <input type="number" name="r" min="0" max="255" value="255">
    G: <input type="number" name="g" min="0" max="255" value="255">
    B: <input type="number" name="b" min="0" max="255" value="255"><br>
    <input type="submit" value="Apply">
    <button formaction="/turn_off" formmethod="post">Turn Off</button>
  </form>
</body>
</html>
'''

def run_coroutine_threadsafe(coroutine):
    
    asyncio.set_event_loop(loop)

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coroutine)
    thread = Thread(target=run)
    thread.start()
    thread.join()

async def connect_device():
    device = await BleakScanner.find_device_by_name(name='KS03~61385A')
    if device:
        conn = await connect_to_ble_device(device)
        if conn:
            print(f"Connected to {device.name}")
            global_connection['conn'] = conn
            global_connection['status'] = f"Connected to {device.name}"
        else:
            global_connection['status'] = "Failed to connect to the device."
    else:
        global_connection['status'] = "Device not found."

async def change_light(brightness, r, g, b):
    state = LightState()
    state.update(SwitchCommand(on=True))
    state.update(BrightnessCommand(brightness))
    state.update(RGBCommand(r, g, b))
    await global_connection['conn'].apply(state)
    

@app.route('/')
def home():
    return render_template_string(HTML, status=global_connection['status'])

@app.route('/connect', methods=['POST'])
def connect():
    if global_connection['conn'] is None:
        run_coroutine_threadsafe(connect_device())
    else:
        flash('Already connected to a device.', 'info')
    return redirect(url_for('home'))

@app.route('/set_light', methods=['POST'])
async def set_light():
    if global_connection['conn']:
        brightness = request.form.get('brightness', type=int)
        r = request.form.get('r', type=int)
        g = request.form.get('g', type=int)
        b = request.form.get('b', type=int)
        print(brightness, r, g, b)
        run_coroutine_threadsafe(change_light(brightness, r, g, b))
        flash('Light settings updated!', 'success')
    else:
        flash('No device connected.', 'error')
    return redirect(url_for('home'))

@app.route('/turn_off', methods=['POST'])
async def turn_off():
    if global_connection['conn']:
        state = LightState()
        state.update(SwitchCommand(on=False))

        await global_connection['conn'].apply(state)
        flash('Lights turned off!', 'success')
    else:
        flash('No device connected.', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    app.run(debug=True, host='0.0.0.0', port=5002)
