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

# --- State ---
servo_angle = 0
light_on = True
direction = 0
last_touch = 0
move_delay = 0.5
long_press_time = 1.5

# --- Servo & Light functions ---
def set_angle(angle):
    global servo_angle
    angle = max(0, min(180, angle))
    duty_u16 = int((500 + int((angle / 180) * 2000)) * 65535 / 20000)
    servo.duty_u16(duty_u16)
    servo_angle = angle

def toggle_servo():
    global direction
    if direction == 0:
        set_angle(180)
        direction = 1
    else:
        set_angle(0)
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

# --- Touch handler ---
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

# --- Wi-Fi AP ---
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_Hotspot", password="12345678")
print("Hotspot IP:", ap.ifconfig()[0])

# --- HTML page ---
html = """<!DOCTYPE html>
<html>
<head>
<title>ESP32 Mood Lamp</title>
<style>
body { text-align:center; font-family:Arial; background:#222; color:#fff; }
h2 { color:#FFA500; }
button { padding:20px 40px; margin:15px; font-size:18px; border:none; border-radius:10px; cursor:pointer; }
#servo { background:#4CAF50; color:white; }
#light { background:#FF8C00; color:white; }
</style>
</head>
<body>
<h2>ESP32 Mood Lamp & Servo Control</h2>
<p>Servo angle: <b>{servo_angle}°</b><br>Light: <b>{light_state}</b></p>
<a href="/servo"><button id="servo">Toggle Servo</button></a>
<a href="/light"><button id="light">Toggle Light</button></a>
</body>
</html>
"""

# --- Fake DNS (Captive Portal) ---
def dns_server():
    dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns.bind(('', 53))
    while True:
        try:
            data, addr = dns.recvfrom(512)
            response = data[:2] + b'\x81\x80' + data[4:6]*2 + b'\x00\x00\x00\x00' + data[12:]
            response += b'\xc0\x0c' + struct.pack('!HHIH', 1,1,60,4)
            response += bytes(map(int, "192.168.4.1".split('.')))
            dns.sendto(response, addr)
        except:
            pass

# --- Web server ---
def web_server():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        req = conn.recv(1024).decode()
        if "GET /servo" in req:
            toggle_servo()
        elif "GET /light" in req:
            toggle_light()
        light_state = "ON" if light_on else "OFF"
        page = html.format(servo_angle=servo_angle, light_state=light_state)
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.sendall(page)
        conn.close()

# --- Start tasks ---
_thread.start_new_thread(touch_task, ())
_thread.start_new_thread(dns_server, ())
web_server()
