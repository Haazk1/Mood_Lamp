import network
import socket
import struct
import _thread
from machine import Pin, PWM
import neopixel
import time

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

# --- Functions ---
def set_angle(angle):
    """Instantly set servo angle"""
    global servo_angle
    angle = max(0, min(180, angle))
    duty_u16 = int((500 + int((angle / 180) * 2000)) * 65535 / 20000)
    servo.duty_u16(duty_u16)
    servo_angle = angle

def smooth_move(target_angle, step_delay=0.01):
    """Move servo smoothly to target angle"""
    global servo_angle
    step = 1 if target_angle > servo_angle else -1
    for angle in range(servo_angle, target_angle + step, step):
        set_angle(angle)
        time.sleep(step_delay)
    servo_angle = target_angle

def toggle_servo():
    """Toggle servo smoothly between 0° and 180°"""
    global direction
    if direction == 0:
        smooth_move(180, 0.015)  # slow smooth motion
        direction = 1
    else:
        smooth_move(0, 0.015)
        direction = 0

def set_light(r, g, b):
    for i in range(32):
        np[i] = (r, g, b)
    np.write()

def turn_light_on():
    global light_on
    light_on = True
    set_light(255, 100, 0)

def turn_light_off():
    global light_on
    light_on = False
    set_light(0, 0, 0)

def toggle_light():
    if light_on:
        turn_light_off()
    else:
        turn_light_on()

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

# --- HTML Page ---
html = """<!DOCTYPE html>
<html>
<head>
<title>ESP32 Mood Lamp</title>
<style>
body {{ text-align:center; font-family:Arial; background:#222; color:#fff; }}
h2 {{ color:#FFA500; }}
button {{ padding:20px 40px; margin:15px; font-size:18px; border:none; border-radius:10px; cursor:pointer; transition:0.2s; }}
#toggle {{ background:#4CAF50; color:white; }}
#off {{ background:#f44336; color:white; }}
#servo {{ background:#2196F3; color:white; }}
button:hover {{ opacity:0.8; transform:scale(1.05); }}
</style>
</head>
<body>
<h2>ESP32 Mood Lamp & Servo Control</h2>
<p>Servo angle: <b>{servo_angle}°</b><br>Light: <b>{light_state}</b></p>
<a href="/toggle"><button id="toggle">Toggle (Servo + Light ON)</button></a>
<a href="/off"><button id="off">Turn Light OFF</button></a>
<a href="/servo"><button id="servo">Toggle Servo Only</button></a>
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
            req = conn.recv(1024).decode()
            if "GET /toggle" in req:
                toggle_servo()
                turn_light_on()
            elif "GET /off" in req:
                turn_light_off()
            elif "GET /servo" in req:
                toggle_servo()

            light_state = "ON" if light_on else "OFF"
            page = html.format(servo_angle=servo_angle, light_state=light_state)
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.sendall(page)
        except Exception as e:
            print("Web error:", e)
        finally:
            conn.close()

# --- Start threads ---
_thread.start_new_thread(touch_task, ())
_thread.start_new_thread(dns_server, ())
web_server()
