from quart import Quart, request, render_template_string
import asyncio
from bleak import BleakScanner
from cheshire.hal.devices import connect_to_ble_device
from cheshire.compiler.state import LightState
from cheshire.generic.command import BrightnessCommand, RGBCommand

app = Quart(__name__)

# Store connections and last state globally; simplification for demonstration.
connections = []
last_state = {"brightness": 0, "r": 0, "g": 0, "b": 0}

@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        form = await request.form
        if "set_color" in form:
            r = int(form['r'])
            g = int(form['g'])
            b = int(form['b'])
        elif "purple" in form:
            r, g, b = 128, 0, 128  # RGB values for purple
        brightness = int(form['brightness'])
        last_state.update({"brightness": brightness, "r": r, "g": g, "b": b})
        await update_device(brightness, r, g, b)
        return await render_template_string(INDEX_HTML, **last_state, result="Settings Updated!")
    return await render_template_string(INDEX_HTML, **last_state, result="")

async def update_device(brightness: int, r: int, g: int, b: int):
    state = LightState()
    state.update(BrightnessCommand(brightness))
    state.update(RGBCommand(r, g, b))

    if not connections:
        # Attempt to connect if not already connected
        device = await BleakScanner.find_device_by_name(name='KS03~61385A')
        if device:
            connection = await connect_to_ble_device(device)
            if connection:
                print(f"Connected to {device.name}")
                connections.append(connection)

    # Push light state to connected devices
    for c in connections:
        await c.apply(state)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BLE Light Control</title>
</head>
<body>
    <h1>BLE Light Control</h1>
    <form method="post">
        <label for="brightness">Brightness:</label>
        <input type="range" id="brightness" name="brightness" min="0" max="255" value="{{brightness}}">
        <br>
        <label for="r">Red:</label>
        <input type="number" id="r" name="r" min="0" max="255" value="{{r}}">
        <label for="g">Green:</label>
        <input type="number" id="g" name="g" min="0" max="255" value="{{g}}">
        <label for="b">Blue:</label>
        <input type="number" id="b" name="b" min="0" max="255" value="{{b}}">
        <br>
        <input type="submit" name="set_color" value="Update Settings">
        <button type="submit" name="purple" value="purple">Set Purple</button>
    </form>
    {{ result }}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)