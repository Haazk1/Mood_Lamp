import network
import socket
import struct
import _thread
from machine import Pin, PWM
import time

# --- Servo setup ---
servo = PWM(Pin(0), freq=50)

def set_angle(angle):
    duty = int((angle / 180) * 102 + 26)
    servo.duty(duty)
    print("Servo angle:", angle)

# --- Access Point setup ---
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_Hotspot", password="12345678")
print("Hotspot started at:", ap.ifconfig()[0])

# --- Simple HTML page ---
html = """<!DOCTYPE html>
<html>
<head><title>ESP32 Servo Control</title></head>
<body style="text-align:center;">
<h2>ESP32 Servo Controller</h2>
<a href="/0"><button style="padding:15px 30px;">Rotate 0°</button></a>
<a href="/180"><button style="padding:15px 30px;">Rotate 180°</button></a>
</body></html>
"""

# --- Fake DNS Server (redirect all domains to ESP32 IP) ---
def dns_server():
    dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns.bind(('', 53))
    print("Fake DNS started on port 53")

    while True:
        try:
            data, addr = dns.recvfrom(512)
            # Build DNS response
            response = data[:2] + b'\x81\x80' + data[4:6] + data[4:6] + b'\x00\x00\x00\x00'
            response += data[12:]
            # Add IP address (ESP32)
            response += b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 60, 4)
            response += bytes(map(int, "192.168.4.1".split('.')))
            dns.sendto(response, addr)
        except Exception as e:
            print("DNS error:", e)

# --- Web Server ---
def web_server():
    s = socket.socket()
    s.bind(('', 80))
    s.listen(5)
    print("Web server started at 192.168.4.1")

    while True:
        conn, addr = s.accept()
        req = conn.recv(1024).decode()
        print("Got request from", addr)

        if "GET /0" in req:
            set_angle(0)
        elif "GET /180" in req:
            set_angle(180)

        # Always return same page
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.sendall(html)
        conn.close()

# --- Start both servers ---
_thread.start_new_thread(dns_server, ())
web_server()
