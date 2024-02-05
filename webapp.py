from flask import Flask, request, render_template_string
import asyncio
from bleak import BleakScanner
from cheshire.compiler.state import LightState
from cheshire.generic.command import BrightnessCommand, RGBCommand, SwitchCommand
from cheshire.hal.devices import connect_to_ble_device

app = Flask(__name__)

# Simple HTML form for light control
HTML = '''
<!doctype html>
<html>
<head><title>Light Control</title></head>
<body>
  <h2>Control Lights</h2>
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

async def update_lights(connection, state):
    if connection:
        await connection.apply(state)

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/set_light', methods=['POST'])
def set_light():
    brightness = request.form.get('brightness', type=int)
    r = request.form.get('r', type=int)
    g = request.form.get('g', type=int)
    b = request.form.get('b', type=int)

    state = LightState()
    state.update(SwitchCommand(on=True))
    state.update(BrightnessCommand(brightness))
    state.update(RGBCommand(r, g, b))

    # Since Flask doesn't support asyncio directly, run the coroutine in the event loop
    loop = asyncio.get_event_loop()
    # Assuming 'connection' is already established; you might need to manage connection differently
    loop.run_until_complete(update_lights(connection, state))

    return 'Light settings updated!', 200

@app.route('/turn_off', methods=['POST'])
def turn_off():
    state = LightState()
    state.update(SwitchCommand(on=False))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_lights(connection, state))

    return 'Lights turned off!', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
