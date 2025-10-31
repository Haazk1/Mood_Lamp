import network
import socket
import struct
import _thread
from machine import Pin, PWM
import neopixel
import time
import ure

# --- Hardware setup ---
servo = PWM(Pin(0))
servo.freq(50)
touch = Pin(1, Pin.IN)
np = neopixel.NeoPixel(Pin(21), 32)

# --- State variables ---
servo_angle = 0
light_on = True
direction = 0
last_touch = 0
move_delay = 0.5
long_press_time = 1.5
current_color = (255, 100, 0)  # default orange (stored UN-SCALED)
brightness = 100  # brightness percentage (0-100)

# --- Functions ---
def set_angle(angle):
    global servo_angle
    angle = max(0, min(180, angle))
    duty_u16 = int((500 + int((angle / 180) * 2000)) * 65535 / 20000)
    servo.duty_u16(duty_u16)
    servo_angle = angle

def smooth_move(target_angle, step_delay=0.015):
    global servo_angle
    step = 1 if target_angle > servo_angle else -1
    for angle in range(servo_angle, target_angle + step, step):
        set_angle(angle)
        time.sleep(step_delay)
    servo_angle = target_angle

def toggle_servo():
    global direction
    if direction == 0:
        smooth_move(180)
        direction = 1
    else:
        smooth_move(0)
        direction = 0

def apply_brightness_to_tuple(color_tuple):
    """Return a new RGB tuple scaled by current brightness (uses global brightness)."""
    global brightness
    r, g, b = color_tuple
    scale = brightness / 100.0
    return (int(r * scale), int(g * scale), int(b * scale))

def write_color_to_strip(color_tuple):
    """Write an (r,g,b) tuple directly to the strip (assumes values already scaled)."""
    for i in range(32):
        np[i] = color_tuple
    np.write()

def set_light(r, g, b):
    """Set current_color (UN-SCALED) and write to strip applying brightness."""
    global current_color, light_on
    current_color = (r, g, b)  # store the raw/unscaled color
    scaled = apply_brightness_to_tuple(current_color)
    write_color_to_strip(scaled)
    light_on = True

def turn_light_on(color=None):
    """Turn on using provided color (raw) or stored current_color."""
    global light_on
    light_on = True
    if color:
        # color expected raw (0..255)
        set_light(*color)
    else:
        scaled = apply_brightness_to_tuple(current_color)
        write_color_to_strip(scaled)
        light_on = True

def turn_light_off():
    """Turn LEDs off but KEEP current_color so we can restore later."""
    global light_on
    light_on = False
    write_color_to_strip((0, 0, 0))
    # NOTE: do NOT change current_color here (so color is remembered)

# --- Touch handling thread ---
def touch_task():
    global last_touch
    while True:
        if touch.value() == 1 and last_touch == 0:
            press_start = time.ticks_ms()
            last_touch = 1
            long_pressed = False
            while touch.value() == 1:
                if (time.ticks_ms() - press_start) / 1000 > long_press_time:
                    long_pressed = True
                    break
                time.sleep(0.05)
            if long_pressed:
                turn_light_off()
            else:
                toggle_servo()
                turn_light_on()
            while touch.value() == 1:
                time.sleep(0.05)
            time.sleep(move_delay)
        elif touch.value() == 0:
            last_touch = 0
        time.sleep(0.05)

# --- Wi-Fi Access Point ---
ap = network.WLAN(network.AP_IF)
ap.active(False)
ap.config(essid="ESP32_HaazMoodlamp", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
ap.active(True)

while not ap.active():
    time.sleep(0.1)
print("Hotspot ready. Connect to:", ap.ifconfig()[0])

# --- HTML Page (brightness client-side removed; we send raw color to server) ---
html = """<!DOCTYPE html>
<html>
<head>
<title>ESP32 Mood Lamp</title>
<style>
body {{ text-align:center; font-family:Arial; background:#222; color:#fff; }}
h2 {{ color:#FFA500; }}
button {{ padding:15px 35px; margin:12px; font-size:18px; border:none; border-radius:10px; cursor:pointer; transition:0.2s; }}
#servo {{ background:#2196F3; color:white; }}
#led {{ background:#FF9800; color:white; }}
#off {{ background:#f44336; color:white; }}
button:hover {{ opacity:0.85; transform:scale(1.05); }}
input[type=color] {{
  width: 150px;
  height: 150px;
  border: none;
  border-radius: 50%;
  margin-top: 20px;
  cursor: pointer;
}}
input[type=range] {{
  width: 200px;
  margin-top: 20px;
}}
</style>
<script>
function updateColor(color) {{
  // Send the raw RGB values (no client-side brightness scaling).
  let r = parseInt(color.substring(1,3), 16);
  let g = parseInt(color.substring(3,5), 16);
  let b = parseInt(color.substring(5,7), 16);
  fetch('/color?r=' + r + '&g=' + g + '&b=' + b)
    .then(response => console.log('Color set:', color))
    .catch(err => console.error(err));
}}

function updateBrightness(val) {{
  // Tell server the new brightness (0-100). Server will reapply current_color at new brightness.
  fetch('/brightness?value=' + val)
    .then(response => console.log('Brightness set to', val))
    .catch(err => console.error(err));
}}
</script>
</head>
<body>
<h2>ESP32 Mood Lamp & Servo Control</h2>
<p>Servo angle: <b>{servo_angle}°</b><br>Light: <b>{light_state}</b></p>

<button id="servo" onclick="fetch('/servo')">Toggle Servo</button>
<button id="led" onclick="fetch('/led')">Toggle LED (Orange)</button>

<br><br>
<h3>🎨 Choose a Color</h3>
<input type="color" id="colorPicker" onchange="updateColor(this.value)">
<br><br>
<label for="brightness">💡 Brightness:</label>
<input type="range" id="brightness" min="0" max="100" value="100" onchange="updateBrightness(this.value)">
<br><br>
<button id="off" onclick="fetch('/off')">Turn Everything OFF</button>
</body>
</html>
"""

# --- Fake DNS Server ---
def dns_server():
    dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns.bind(('', 53))
    print("Fake DNS running...")
    while True:
        try:
            data, addr = dns.recvfrom(512)
            response = data[:2] + b'\x81\x80' + data[4:6]*2 + b'\x00\x00\x00\x00' + data[12:]
            response += b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 60, 4)
            response += bytes(map(int, ap.ifconfig()[0].split('.')))
            dns.sendto(response, addr)
        except:
            pass

# --- Web Server ---
def web_server():
    global brightness
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('', 80))
    except OSError:
        print("Port 80 busy. Restarting...")
        s.close()
        time.sleep(2)
        return web_server()
    s.listen(3)
    print("Web server running on http://192.168.4.1")

    while True:
        conn, addr = s.accept()
        try:
            req = conn.recv(2048).decode()

            # Handle color picker
            if "GET /color?" in req:
                match = ure.search("r=(\\d+)&g=(\\d+)&b=(\\d+)", req)
                if match:
                    r = int(match.group(1))
                    g = int(match.group(2))
                    b = int(match.group(3))
                    # Server applies brightness internally
                    set_light(r, g, b)
                    turn_light_on()
                conn.send("HTTP/1.1 204 No Content\r\n\r\n")
                conn.close()
                continue

            # Handle brightness
            if "GET /brightness?" in req:
                match = ure.search("value=(\\d+)", req)
                if match:
                    brightness = int(match.group(1))
                    # re-apply the stored current_color with new brightness
                    if light_on:
                        scaled = apply_brightness_to_tuple(current_color)
                        write_color_to_strip(scaled)
                conn.send("HTTP/1.1 204 No Content\r\n\r\n")
                conn.close()
                continue

            # Handle buttons
            if "GET /servo" in req:
                toggle_servo()
            elif "GET /led" in req:
                # turn on orange RAW color (server will scale it)
                turn_light_on((255, 100, 0))
            elif "GET /off" in req:
                turn_light_off()

            light_state = "ON" if light_on else "OFF"
            page = html.format(servo_angle=servo_angle, light_state=light_state)
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.sendall(page)
        except Exception as e:
            print("Web error:", e)
        finally:
            try:
                conn.close()
            except:
                pass

# --- Start threads ---

_thread.start_new_thread(touch_task, ())
_thread.start_new_thread(dns_server, ())
web_server()

