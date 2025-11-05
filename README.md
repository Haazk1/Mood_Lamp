#  ESP32 Mood Lamp + Servo Control (MicroPython)

<img src="https://github.com/user-attachments/assets/e22a4b9c-cee3-4951-87cc-31d4348f103e" alt="WhatsApp Image" width="300">

<p align="center">
  <video src="https://github.com/user-attachments/assets/7df755ba-183c-41ee-971e-18b6a3c5d00b" width="45%" controls></video>
  <video src="https://github.com/user-attachments/assets/346f4d84-1831-438e-9086-24329e00f488" width="45%" controls></video>
</p>



This project turns your ESP32 into a **Wi-Fi hotspot** that hosts a web-based control panel for:
- Changing RGB NeoPixel colors using a **color wheel** 🎨  
- Controlling a **servo motor** smoothly between open and close positions 🔄  
- Toggling light ON/OFF 💡  
- Long-press touch input to turn off light 🔘  

---

## 🧠 Features

- 🔥 **Captive portal-like behavior** — automatically resolves DNS queries to `192.168.4.1`
- 🌐 **Built-in Wi-Fi Access Point**
  - SSID: `ESP32_HaazMoodlamp`
  - Password: `12345678`
- 🎨 **Web Interface**
  - Live RGB color picker
  - Buttons for servo and light control
- 🤖 **Smooth servo motion**
- 🖐 **Touch button control**
  - Short press → Toggle servo + light ON
  - Long press (>1.5s) → Turn off light
- 💡 **NeoPixel support** for up to 32 LEDs

---

## ⚙️ Hardware Connections

<img width="3000" height="2346" alt="circuit_image" src="https://github.com/user-attachments/assets/b5122c32-5327-4189-b1fa-3a53a2b9631f" />

| Component        | Pin (ESP32) | Description         |
|------------------|-------------|---------------------|
| Servo Motor      | GPIO 0      | PWM control signal  |
| Touch Sensor     | GPIO 1      | Input for touch     |
| NeoPixel Strip   | GPIO 21     | RGB data pin        |
| Power Supply     | 5V + GND    | Shared with all devices |

> ⚠️ Make sure to use an external 5V power source for servo + NeoPixels to avoid brownouts.

---

## 📲 How to Use

1. Flash the provided MicroPython script to your **ESP32** using **Thonny** or **ampy**.  
2. Once flashed, reboot the ESP32.
3. Connect your phone or laptop to the Wi-Fi network:

   ```
   SSID: ESP32_HaazMoodlamp
   Password: 12345678
   ```

4. Open your browser and go to:
   ```
   http://192.168.4.1
   ```

5. Use the web controls to:
   - Toggle servo movement
   - Turn light ON/OFF
   - Adjust the LED color with the color wheel
   - Adjust  brightness using control slider
   

---

## 🌈 Web Interface Preview

The web interface includes:
- Buttons:
  - “Toggle (Servo + Light ON)”
  - “Turn Light OFF”
  - “Toggle Servo Only”
- RGB Color Wheel:
  - Instantly updates the NeoPixel color.

---

## 🧩 File Overview

| File | Description |
|------|--------------|
| `main.py` | Main MicroPython program for ESP32 (includes Wi-Fi, servo, LED, and web server logic) |
| `README.md` | This documentation file |

---

## 🧰 Dependencies

- MicroPython (latest build for ESP32)
- Libraries:
  - `machine`
  - `neopixel`
  - `_thread`
  - `network`
  - `socket`
  - `time`
  - `struct`

---

## 🚀 Future Improvements


- Enable OTA updates for easier firmware upgrades
- Add presets for color moods
---

## 🧑‍💻 Author

**Haaziq Raif**  
Created using ESP32 SuperMini C3 with MicroPython  
For educational and IoT experimentation 🌍

---

## 📝 License

Feel free to use and modify
